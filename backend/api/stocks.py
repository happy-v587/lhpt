"""
Stock data API routes.
Provides endpoints for fetching stock lists, K-line data, and stock information.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field
import logging

from database import get_db
from services.data_provider import DataProvider, DataSourceError
from repositories.data_repository import DataRepository
from services.cache_service import get_cache_service
from config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Get cache service
cache_service = get_cache_service()

# Create router
router = APIRouter(prefix="/api/stocks", tags=["stocks"])


# Pydantic models for request/response
class StockInfo(BaseModel):
    """Stock information model."""
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    exchange: str = Field(..., description="交易所 (SH/SZ)")
    industry: Optional[str] = Field(None, description="所属行业")
    list_date: Optional[str] = Field(None, description="上市日期")
    market_cap: Optional[float] = Field(None, description="市值")


class StockListResponse(BaseModel):
    """Response model for stock list."""
    stocks: List[StockInfo]


class KLineDataPoint(BaseModel):
    """Single K-line data point."""
    date: str = Field(..., description="交易日期")
    open: float = Field(..., description="开盘价")
    close: float = Field(..., description="收盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    volume: int = Field(..., description="成交量")
    amount: Optional[float] = Field(None, description="成交额")


class KLineDataResponse(BaseModel):
    """Response model for K-line data."""
    code: str = Field(..., description="股票代码")
    name: Optional[str] = Field(None, description="股票名称")
    data: List[KLineDataPoint]


@router.get("", response_model=StockListResponse)
async def get_stocks(db: Session = Depends(get_db)):
    """
    Get list of all A-share stocks.
    
    Returns:
        StockListResponse: List of all available stocks
    
    Requirements: 4.1, 10.3
    Property 16: 缓存一致性
    """
    try:
        logger.info("Fetching stock list")
        
        # Try to get from cache first
        cache_key = "stock_list"
        if settings.cache_enabled:
            cached_data = cache_service.get(cache_key)
            if cached_data:
                logger.info("Stock list retrieved from cache")
                return StockListResponse(stocks=[StockInfo(**s) for s in cached_data])
        
        # Cache miss - fetch from data provider
        data_provider = DataProvider()
        stocks = data_provider.get_stock_list()
        
        # Store in cache
        if settings.cache_enabled:
            cache_service.set(cache_key, stocks, ttl=settings.cache_ttl_stock_list)
        
        # Convert to response model
        stock_infos = [StockInfo(**stock) for stock in stocks]
        
        return StockListResponse(stocks=stock_infos)
        
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


@router.get("/{code}/kline", response_model=KLineDataResponse)
async def get_kline_data(
    code: str,
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    period: str = Query("daily", description="周期类型 (daily/weekly/monthly)"),
    db: Session = Depends(get_db)
):
    """
    Get K-line data for a specific stock.
    
    Args:
        code: Stock code (e.g., "600000.SH")
        start_date: Start date in format YYYY-MM-DD
        end_date: End date in format YYYY-MM-DD
        period: Period type (daily, weekly, monthly)
    
    Returns:
        KLineDataResponse: K-line data for the specified stock and date range
    
    Requirements: 4.2, 9.4
    """
    try:
        # Validate stock code format
        import re
        if not re.match(r'^\d{6}\.(SH|SZ)$', code):
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_STOCK_CODE",
                    "message": "股票代码格式无效",
                    "details": f"股票代码必须是6位数字加.SH或.SZ，例如: 600000.SH"
                }
            )
        
        # Validate period
        if period not in ['daily', 'weekly', 'monthly']:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_PERIOD",
                    "message": "周期类型无效",
                    "details": f"周期类型必须是 daily, weekly 或 monthly"
                }
            )
        
        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_DATE_FORMAT",
                    "message": "日期格式无效",
                    "details": "日期格式必须是 YYYY-MM-DD"
                }
            )
        
        logger.info(f"Fetching K-line data for {code} from {start_date} to {end_date}, period={period}")
        
        # Try to get from cache first
        cache_key = f"kline:{code}:{start_date}:{end_date}:{period}"
        if settings.cache_enabled:
            cached_data = cache_service.get(cache_key)
            if cached_data:
                logger.info(f"K-line data for {code} retrieved from cache")
                return KLineDataResponse(**cached_data)
        
        # Try to get from database first
        repo = DataRepository(db)
        df = repo.get_kline_data(code, start_date, end_date, period)
        
        # If not in database or insufficient data, fetch from data provider
        if df.empty:
            logger.info(f"No data in database, fetching from data provider")
            data_provider = DataProvider()
            df = data_provider.get_kline_data(code, start_date, end_date, period)
            
            # Save to database for future use
            if not df.empty:
                repo.save_kline_data(code, df)
        
        if df.empty:
            return KLineDataResponse(code=code, name=None, data=[])
        
        # Convert DataFrame to response model
        data_points = []
        for _, row in df.iterrows():
            data_points.append(KLineDataPoint(
                date=row['trade_date'].strftime('%Y-%m-%d') if hasattr(row['trade_date'], 'strftime') else str(row['trade_date']),
                open=float(row['open']),
                close=float(row['close']),
                high=float(row['high']),
                low=float(row['low']),
                volume=int(row['volume']),
                amount=float(row['amount']) if row.get('amount') is not None else None
            ))
        
        response = KLineDataResponse(code=code, name=None, data=data_points)
        
        # Store in cache
        if settings.cache_enabled:
            cache_service.set(cache_key, response.dict(), ttl=settings.cache_ttl_kline_data)
        
        return response
        
    except HTTPException:
        raise
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


@router.get("/{code}/info", response_model=StockInfo)
async def get_stock_info(
    code: str,
    db: Session = Depends(get_db)
):
    """
    Get basic information for a specific stock.
    
    Args:
        code: Stock code (e.g., "600000.SH")
    
    Returns:
        StockInfo: Basic information about the stock
    
    Requirements: 4.2
    """
    try:
        # Validate stock code format
        import re
        if not re.match(r'^\d{6}\.(SH|SZ)$', code):
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_STOCK_CODE",
                    "message": "股票代码格式无效",
                    "details": f"股票代码必须是6位数字加.SH或.SZ，例如: 600000.SH"
                }
            )
        
        logger.info(f"Fetching stock info for {code}")
        data_provider = DataProvider()
        stock_info = data_provider.get_stock_info(code)
        
        return StockInfo(**stock_info)
        
    except HTTPException:
        raise
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
