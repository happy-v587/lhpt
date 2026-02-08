"""
Custom indicators API routes.
Provides endpoints for managing custom indicators.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
import uuid

from database import get_db
from models.custom_indicator import CustomIndicator
from services.custom_indicator_engine import CustomIndicatorEngine
from services.data_provider import DataProvider
from repositories.data_repository import DataRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/custom-indicators", tags=["custom-indicators"])


# Pydantic models
class IndicatorParamDef(BaseModel):
    """Indicator parameter definition."""
    name: str = Field(..., description="参数名称")
    type: str = Field(..., description="参数类型 (int/float/string)")
    default: Any = Field(..., description="默认值")
    description: Optional[str] = Field(None, description="参数描述")


class CustomIndicatorCreateRequest(BaseModel):
    """Request model for creating custom indicator."""
    name: str = Field(..., min_length=1, max_length=100, description="指标名称（唯一标识）")
    display_name: str = Field(..., min_length=1, max_length=100, description="显示名称")
    description: Optional[str] = Field(None, description="指标描述")
    indicator_type: str = Field("formula", description="指标类型 (formula/plugin)")
    formula: Optional[str] = Field(None, description="计算公式")
    params: List[IndicatorParamDef] = Field([], description="参数定义")
    plugin_module: Optional[str] = Field(None, description="插件模块路径")
    plugin_class: Optional[str] = Field(None, description="插件类名")


class CustomIndicatorResponse(BaseModel):
    """Response model for custom indicator."""
    id: str
    name: str
    display_name: str
    description: Optional[str]
    indicator_type: str
    formula: Optional[str]
    params: List[Dict[str, Any]]
    is_active: bool
    created_at: str
    updated_at: str


class CustomIndicatorListResponse(BaseModel):
    """Response model for custom indicator list."""
    indicators: List[CustomIndicatorResponse]


class FormulaValidateRequest(BaseModel):
    """Request model for formula validation."""
    formula: str = Field(..., description="公式")


class FormulaValidateResponse(BaseModel):
    """Response model for formula validation."""
    valid: bool
    message: str


class IndicatorCalculateRequest(BaseModel):
    """Request model for calculating custom indicator."""
    indicator_id: str = Field(..., description="指标ID")
    stock_code: str = Field(..., description="股票代码")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    params: Dict[str, Any] = Field({}, description="参数值")


@router.post("", response_model=CustomIndicatorResponse)
async def create_custom_indicator(
    request: CustomIndicatorCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a custom indicator.
    
    Args:
        request: Custom indicator configuration
    
    Returns:
        Created custom indicator
    """
    try:
        # Check if name already exists
        existing = db.query(CustomIndicator).filter(
            CustomIndicator.name == request.name
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="指标名称已存在")
        
        # Validate formula if type is formula
        if request.indicator_type == 'formula':
            if not request.formula:
                raise HTTPException(status_code=400, detail="公式类型指标必须提供公式")
            
            engine = CustomIndicatorEngine()
            validation = engine.validate_formula(request.formula)
            
            if not validation['valid']:
                raise HTTPException(status_code=400, detail=f"公式验证失败: {validation['message']}")
        
        # Create indicator
        indicator_id = str(uuid.uuid4())
        indicator = CustomIndicator(
            id=indicator_id,
            name=request.name,
            display_name=request.display_name,
            description=request.description,
            indicator_type=request.indicator_type,
            formula=request.formula,
            params=[p.dict() for p in request.params],
            plugin_module=request.plugin_module,
            plugin_class=request.plugin_class,
            is_active=True
        )
        
        db.add(indicator)
        db.commit()
        db.refresh(indicator)
        
        logger.info(f"Created custom indicator: {indicator.name}")
        
        return CustomIndicatorResponse(
            id=indicator.id,
            name=indicator.name,
            display_name=indicator.display_name,
            description=indicator.description,
            indicator_type=indicator.indicator_type,
            formula=indicator.formula,
            params=indicator.params,
            is_active=indicator.is_active,
            created_at=indicator.created_at.isoformat(),
            updated_at=indicator.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create custom indicator: {e}")
        raise HTTPException(status_code=500, detail=f"创建自定义指标失败: {str(e)}")


@router.get("", response_model=CustomIndicatorListResponse)
async def get_custom_indicators(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get list of custom indicators.
    
    Args:
        active_only: Only return active indicators
    
    Returns:
        List of custom indicators
    """
    try:
        query = db.query(CustomIndicator)
        
        if active_only:
            query = query.filter(CustomIndicator.is_active == True)
        
        indicators = query.order_by(CustomIndicator.created_at.desc()).all()
        
        return CustomIndicatorListResponse(
            indicators=[
                CustomIndicatorResponse(
                    id=ind.id,
                    name=ind.name,
                    display_name=ind.display_name,
                    description=ind.description,
                    indicator_type=ind.indicator_type,
                    formula=ind.formula,
                    params=ind.params,
                    is_active=ind.is_active,
                    created_at=ind.created_at.isoformat(),
                    updated_at=ind.updated_at.isoformat()
                )
                for ind in indicators
            ]
        )
        
    except Exception as e:
        logger.error(f"Failed to get custom indicators: {e}")
        raise HTTPException(status_code=500, detail=f"获取自定义指标列表失败: {str(e)}")


@router.get("/{indicator_id}", response_model=CustomIndicatorResponse)
async def get_custom_indicator(
    indicator_id: str,
    db: Session = Depends(get_db)
):
    """Get custom indicator by ID."""
    indicator = db.query(CustomIndicator).filter(
        CustomIndicator.id == indicator_id
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    return CustomIndicatorResponse(
        id=indicator.id,
        name=indicator.name,
        display_name=indicator.display_name,
        description=indicator.description,
        indicator_type=indicator.indicator_type,
        formula=indicator.formula,
        params=indicator.params,
        is_active=indicator.is_active,
        created_at=indicator.created_at.isoformat(),
        updated_at=indicator.updated_at.isoformat()
    )


@router.delete("/{indicator_id}")
async def delete_custom_indicator(
    indicator_id: str,
    db: Session = Depends(get_db)
):
    """Delete a custom indicator."""
    indicator = db.query(CustomIndicator).filter(
        CustomIndicator.id == indicator_id
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    db.delete(indicator)
    db.commit()
    
    return {"success": True, "message": "指标已删除"}


@router.post("/validate-formula", response_model=FormulaValidateResponse)
async def validate_formula(request: FormulaValidateRequest):
    """
    Validate a formula.
    
    Args:
        request: Formula to validate
    
    Returns:
        Validation result
    """
    try:
        engine = CustomIndicatorEngine()
        result = engine.validate_formula(request.formula)
        
        return FormulaValidateResponse(**result)
        
    except Exception as e:
        logger.error(f"Formula validation error: {e}")
        return FormulaValidateResponse(
            valid=False,
            message=f"验证失败: {str(e)}"
        )


@router.post("/calculate")
async def calculate_custom_indicator(
    request: IndicatorCalculateRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate a custom indicator.
    
    Args:
        request: Calculation request
    
    Returns:
        Calculated indicator data
    """
    try:
        # Get indicator definition
        indicator = db.query(CustomIndicator).filter(
            CustomIndicator.id == request.indicator_id
        ).first()
        
        if not indicator:
            raise HTTPException(status_code=404, detail="指标不存在")
        
        if not indicator.is_active:
            raise HTTPException(status_code=400, detail="指标未启用")
        
        # Get K-line data
        from datetime import datetime
        start = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end = datetime.strptime(request.end_date, "%Y-%m-%d").date()
        
        repo = DataRepository(db)
        data = repo.get_kline_data(
            stock_code=request.stock_code,
            start_date=start,
            end_date=end,
            period='daily'
        )
        
        if data.empty:
            raise HTTPException(status_code=404, detail="没有找到K线数据")
        
        # Calculate indicator
        if indicator.indicator_type == 'formula':
            engine = CustomIndicatorEngine()
            result = engine.evaluate_formula(
                indicator.formula,
                data,
                request.params
            )
            
            return {
                "indicator_name": indicator.name,
                "data": result.to_dict()
            }
        else:
            raise HTTPException(status_code=400, detail="插件类型指标暂不支持")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate custom indicator: {e}")
        raise HTTPException(status_code=500, detail=f"计算指标失败: {str(e)}")
