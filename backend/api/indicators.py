"""
Technical indicators API routes.
Provides endpoints for calculating technical indicators and listing available indicator types.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
import pandas as pd

from database import get_db
from services.indicator_calculator import IndicatorCalculator, IndicatorCalculationError
from services.data_provider import DataProvider, DataSourceError
from repositories.data_repository import DataRepository
from services.cache_service import get_cache_service
from config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Get cache service
cache_service = get_cache_service()

# Create router
router = APIRouter(prefix="/api/indicators", tags=["indicators"])


# Pydantic models for request/response
class IndicatorCalculateRequest(BaseModel):
    """Request model for indicator calculation."""
    stock_code: str = Field(..., description="股票代码")
    indicator_type: str = Field(..., description="指标类型 (MA/MACD/RSI/BOLL)")
    params: Dict[str, Any] = Field(..., description="指标参数")
    start_date: str = Field(..., description="开始日期 (YYYY-MM-DD)")
    end_date: str = Field(..., description="结束日期 (YYYY-MM-DD)")


class IndicatorCalculateResponse(BaseModel):
    """Response model for indicator calculation."""
    indicator_type: str = Field(..., description="指标类型")
    data: Dict[str, Any] = Field(..., description="指标数据")


class IndicatorParam(BaseModel):
    """Parameter definition for an indicator."""
    name: str = Field(..., description="参数名称")
    type: str = Field(..., description="参数类型")
    default: Any = Field(..., description="默认值")
    description: Optional[str] = Field(None, description="参数描述")


class IndicatorType(BaseModel):
    """Indicator type definition."""
    type: str = Field(..., description="指标类型代码")
    name: str = Field(..., description="指标名称")
    params: List[IndicatorParam] = Field(..., description="参数列表")


class IndicatorTypesResponse(BaseModel):
    """Response model for indicator types."""
    indicators: List[IndicatorType]


@router.post("/calculate", response_model=IndicatorCalculateResponse)
async def calculate_indicator(
    request: IndicatorCalculateRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate technical indicator for a stock.
    
    Args:
        request: Indicator calculation request containing stock code, indicator type, parameters, and date range
    
    Returns:
        IndicatorCalculateResponse: Calculated indicator data
    
    Requirements: 4.3
    """
    try:
        # Validate stock code format
        import re
        if not re.match(r'^\d{6}\.(SH|SZ)$', request.stock_code):
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_STOCK_CODE",
                    "message": "股票代码格式无效",
                    "details": f"股票代码必须是6位数字加.SH或.SZ，例如: 600000.SH"
                }
            )
        
        # Validate indicator type
        valid_indicators = ['MA', 'MACD', 'RSI', 'BOLL']
        if request.indicator_type not in valid_indicators:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_INDICATOR_TYPE",
                    "message": "指标类型无效",
                    "details": f"指标类型必须是 {', '.join(valid_indicators)} 之一"
                }
            )
        
        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(request.start_date, '%Y-%m-%d')
            datetime.strptime(request.end_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_DATE_FORMAT",
                    "message": "日期格式无效",
                    "details": "日期格式必须是 YYYY-MM-DD"
                }
            )
        
        logger.info(f"Calculating {request.indicator_type} for {request.stock_code}")
        
        # Try to get from cache first
        import json
        cache_key = f"indicator:{request.stock_code}:{request.indicator_type}:{json.dumps(request.params, sort_keys=True)}:{request.start_date}:{request.end_date}"
        if settings.cache_enabled:
            cached_data = cache_service.get(cache_key)
            if cached_data:
                logger.info(f"Indicator {request.indicator_type} for {request.stock_code} retrieved from cache")
                return IndicatorCalculateResponse(**cached_data)
        
        # Get K-line data
        repo = DataRepository(db)
        df = repo.get_kline_data(request.stock_code, request.start_date, request.end_date)
        
        # If not in database, fetch from data provider
        if df.empty:
            logger.info(f"No data in database, fetching from data provider")
            data_provider = DataProvider()
            df = data_provider.get_kline_data(
                request.stock_code,
                request.start_date,
                request.end_date,
                period='daily'
            )
            
            # Save to database for future use
            if not df.empty:
                repo.save_kline_data(request.stock_code, df)
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "NO_DATA",
                    "message": "未找到数据",
                    "details": f"未找到股票 {request.stock_code} 在指定日期范围内的数据"
                }
            )
        
        # Calculate indicator
        calculator = IndicatorCalculator()
        result_data = {}
        
        if request.indicator_type == 'MA':
            periods = request.params.get('periods', [5, 10, 20, 60])
            if not isinstance(periods, list):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "INVALID_PARAMS",
                        "message": "参数无效",
                        "details": "MA的periods参数必须是数组"
                    }
                )
            
            ma_results = calculator.calculate_ma(df, periods)
            
            # Convert to response format
            result_data['dates'] = df['trade_date'].dt.strftime('%Y-%m-%d').tolist()
            for key, series in ma_results.items():
                result_data[key] = series.tolist()
        
        elif request.indicator_type == 'MACD':
            fast_period = request.params.get('fast_period', 12)
            slow_period = request.params.get('slow_period', 26)
            signal_period = request.params.get('signal_period', 9)
            
            macd_results = calculator.calculate_macd(df, fast_period, slow_period, signal_period)
            
            # Convert to response format
            result_data['dates'] = df['trade_date'].dt.strftime('%Y-%m-%d').tolist()
            result_data['DIF'] = macd_results['DIF'].tolist()
            result_data['DEA'] = macd_results['DEA'].tolist()
            result_data['MACD'] = macd_results['MACD'].tolist()
        
        elif request.indicator_type == 'RSI':
            period = request.params.get('period', 14)
            
            rsi_result = calculator.calculate_rsi(df, period)
            
            # Convert to response format
            result_data['dates'] = df['trade_date'].dt.strftime('%Y-%m-%d').tolist()
            result_data[f'RSI{period}'] = rsi_result.tolist()
        
        elif request.indicator_type == 'BOLL':
            period = request.params.get('period', 20)
            std_dev = request.params.get('std_dev', 2.0)
            
            boll_results = calculator.calculate_boll(df, period, std_dev)
            
            # Convert to response format
            result_data['dates'] = df['trade_date'].dt.strftime('%Y-%m-%d').tolist()
            result_data['upper'] = boll_results['upper'].tolist()
            result_data['middle'] = boll_results['middle'].tolist()
            result_data['lower'] = boll_results['lower'].tolist()
        
        response = IndicatorCalculateResponse(
            indicator_type=request.indicator_type,
            data=result_data
        )
        
        # Store in cache
        if settings.cache_enabled:
            cache_service.set(cache_key, response.dict(), ttl=settings.cache_ttl_indicators)
        
        return response
        
    except HTTPException:
        raise
    except IndicatorCalculationError as e:
        logger.error(f"Indicator calculation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "code": "CALCULATION_ERROR",
                "message": "指标计算失败",
                "details": str(e)
            }
        )
    except DataSourceError as e:
        logger.error(f"Data source error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "code": "DATA_SOURCE_ERROR",
                "message": "无法从数据源获取数据",
                "details": str(e)
            }
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "数据验证失败",
                "details": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误",
                "details": str(e)
            }
        )


@router.get("/types", response_model=IndicatorTypesResponse)
async def get_indicator_types():
    """
    Get list of supported indicator types and their parameters.
    
    Returns:
        IndicatorTypesResponse: List of available indicators with parameter definitions
    
    Requirements: 4.3
    """
    try:
        indicators = [
            IndicatorType(
                type="MA",
                name="移动平均线",
                params=[
                    IndicatorParam(
                        name="periods",
                        type="array",
                        default=[5, 10, 20, 60],
                        description="计算周期数组，例如 [5, 10, 20]"
                    )
                ]
            ),
            IndicatorType(
                type="EMA",
                name="指数移动平均线",
                params=[
                    IndicatorParam(
                        name="periods",
                        type="array",
                        default=[12, 26, 50],
                        description="计算周期数组"
                    )
                ]
            ),
            IndicatorType(
                type="MACD",
                name="指数平滑异同移动平均线",
                params=[
                    IndicatorParam(
                        name="fast_period",
                        type="int",
                        default=12,
                        description="快速EMA周期"
                    ),
                    IndicatorParam(
                        name="slow_period",
                        type="int",
                        default=26,
                        description="慢速EMA周期"
                    ),
                    IndicatorParam(
                        name="signal_period",
                        type="int",
                        default=9,
                        description="信号线周期"
                    )
                ]
            ),
            IndicatorType(
                type="RSI",
                name="相对强弱指标",
                params=[
                    IndicatorParam(
                        name="period",
                        type="int",
                        default=14,
                        description="计算周期"
                    )
                ]
            ),
            IndicatorType(
                type="BOLL",
                name="布林带",
                params=[
                    IndicatorParam(
                        name="period",
                        type="int",
                        default=20,
                        description="移动平均周期"
                    ),
                    IndicatorParam(
                        name="std_dev",
                        type="float",
                        default=2.0,
                        description="标准差倍数"
                    )
                ]
            ),
            IndicatorType(
                type="KDJ",
                name="随机指标",
                params=[
                    IndicatorParam(
                        name="n",
                        type="int",
                        default=9,
                        description="RSV周期"
                    ),
                    IndicatorParam(
                        name="m1",
                        type="int",
                        default=3,
                        description="K值平滑周期"
                    ),
                    IndicatorParam(
                        name="m2",
                        type="int",
                        default=3,
                        description="D值平滑周期"
                    )
                ]
            ),
            IndicatorType(
                type="CCI",
                name="顺势指标",
                params=[
                    IndicatorParam(
                        name="period",
                        type="int",
                        default=14,
                        description="计算周期"
                    )
                ]
            ),
            IndicatorType(
                type="ATR",
                name="平均真实波幅",
                params=[
                    IndicatorParam(
                        name="period",
                        type="int",
                        default=14,
                        description="计算周期"
                    )
                ]
            ),
            IndicatorType(
                type="OBV",
                name="能量潮指标",
                params=[]
            ),
            IndicatorType(
                type="WR",
                name="威廉指标",
                params=[
                    IndicatorParam(
                        name="period",
                        type="int",
                        default=14,
                        description="计算周期"
                    )
                ]
            ),
            IndicatorType(
                type="DMI",
                name="趋向指标",
                params=[
                    IndicatorParam(
                        name="period",
                        type="int",
                        default=14,
                        description="计算周期"
                    )
                ]
            ),
            IndicatorType(
                type="VWAP",
                name="成交量加权平均价",
                params=[]
            )
        ]
        
        return IndicatorTypesResponse(indicators=indicators)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误",
                "details": str(e)
            }
        )
