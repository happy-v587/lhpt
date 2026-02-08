"""
Strategy management API routes.
Provides endpoints for creating, retrieving, and deleting trading strategies.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
import uuid

from database import get_db
from repositories.data_repository import DataRepository

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/strategies", tags=["strategies"])


# Pydantic models for request/response
class IndicatorParams(BaseModel):
    """Indicator parameters model."""
    type: str = Field(..., description="指标类型")
    params: Dict[str, Any] = Field(..., description="指标参数")


class TradingCondition(BaseModel):
    """Trading condition model."""
    indicator: str = Field(..., description="指标名称")
    operator: str = Field(..., description="操作符 (>, <, =, cross_up, cross_down)")
    value: Any = Field(..., description="比较值")
    action: str = Field(default="buy", description="动作类型 (buy/sell)")


class StrategyCreateRequest(BaseModel):
    """Request model for creating a strategy."""
    name: str = Field(..., min_length=1, max_length=100, description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    indicators: List[IndicatorParams] = Field(..., description="指标列表")
    conditions: List[TradingCondition] = Field(..., description="交易条件列表")


class StrategyResponse(BaseModel):
    """Response model for a strategy."""
    id: str = Field(..., description="策略ID")
    name: str = Field(..., description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")


class StrategyDetailResponse(BaseModel):
    """Detailed response model for a strategy."""
    id: str = Field(..., description="策略ID")
    name: str = Field(..., description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    indicators: List[IndicatorParams] = Field(..., description="指标列表")
    conditions: List[TradingCondition] = Field(..., description="交易条件列表")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")


class StrategyListResponse(BaseModel):
    """Response model for strategy list."""
    strategies: List[StrategyResponse]


class StrategyDeleteResponse(BaseModel):
    """Response model for strategy deletion."""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")


@router.get("", response_model=StrategyListResponse)
async def get_strategies(db: Session = Depends(get_db)):
    """
    Get all saved trading strategies.
    
    Returns:
        StrategyListResponse: List of all strategies
    
    Requirements: 4.4
    """
    try:
        logger.info("Fetching all strategies")
        repo = DataRepository(db)
        strategies = repo.get_strategies()
        
        # Convert to response model (without full config details)
        strategy_responses = []
        for strategy in strategies:
            strategy_responses.append(StrategyResponse(
                id=strategy['id'],
                name=strategy['name'],
                description=strategy['description'],
                created_at=strategy['created_at'],
                updated_at=strategy['updated_at']
            ))
        
        return StrategyListResponse(strategies=strategy_responses)
        
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


@router.get("/{strategy_id}", response_model=StrategyDetailResponse)
async def get_strategy(strategy_id: str, db: Session = Depends(get_db)):
    """
    Get a specific strategy by ID.
    
    Args:
        strategy_id: Strategy UUID
    
    Returns:
        StrategyDetailResponse: Detailed strategy information
    
    Requirements: 4.4
    """
    try:
        logger.info(f"Fetching strategy {strategy_id}")
        repo = DataRepository(db)
        strategy = repo.get_strategy_by_id(strategy_id)
        
        if not strategy:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "STRATEGY_NOT_FOUND",
                    "message": "策略未找到",
                    "details": f"未找到ID为 {strategy_id} 的策略"
                }
            )
        
        # Parse config
        config = strategy['config']
        indicators = [IndicatorParams(**ind) for ind in config.get('indicators', [])]
        conditions = [TradingCondition(**cond) for cond in config.get('conditions', [])]
        
        return StrategyDetailResponse(
            id=strategy['id'],
            name=strategy['name'],
            description=strategy['description'],
            indicators=indicators,
            conditions=conditions,
            created_at=strategy['created_at'],
            updated_at=strategy['updated_at']
        )
        
    except HTTPException:
        raise
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


@router.post("", response_model=StrategyResponse)
async def create_strategy(
    request: StrategyCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new trading strategy.
    
    Args:
        request: Strategy creation request
    
    Returns:
        StrategyResponse: Created strategy information
    
    Requirements: 4.5
    """
    try:
        # Validate operator values
        valid_operators = ['>', '<', '=', 'cross_up', 'cross_down']
        for condition in request.conditions:
            if condition.operator not in valid_operators:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "INVALID_OPERATOR",
                        "message": "操作符无效",
                        "details": f"操作符必须是 {', '.join(valid_operators)} 之一"
                    }
                )
        
        logger.info(f"Creating strategy: {request.name}")
        
        # Generate UUID
        strategy_id = str(uuid.uuid4())
        
        # Prepare strategy data
        strategy_data = {
            'id': strategy_id,
            'name': request.name,
            'description': request.description,
            'config': {
                'indicators': [ind.dict() for ind in request.indicators],
                'conditions': [cond.dict() for cond in request.conditions]
            }
        }
        
        # Save to database
        repo = DataRepository(db)
        saved_id = repo.save_strategy(strategy_data)
        
        # Get the saved strategy to return
        saved_strategy = repo.get_strategy_by_id(saved_id)
        
        return StrategyResponse(
            id=saved_strategy['id'],
            name=saved_strategy['name'],
            description=saved_strategy['description'],
            created_at=saved_strategy['created_at'],
            updated_at=saved_strategy['updated_at']
        )
        
    except HTTPException:
        raise
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


@router.delete("/{strategy_id}", response_model=StrategyDeleteResponse)
async def delete_strategy(strategy_id: str, db: Session = Depends(get_db)):
    """
    Delete a trading strategy.
    
    Args:
        strategy_id: Strategy UUID
    
    Returns:
        StrategyDeleteResponse: Deletion result
    
    Requirements: 4.5
    """
    try:
        logger.info(f"Deleting strategy {strategy_id}")
        repo = DataRepository(db)
        success = repo.delete_strategy(strategy_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "STRATEGY_NOT_FOUND",
                    "message": "策略未找到",
                    "details": f"未找到ID为 {strategy_id} 的策略"
                }
            )
        
        return StrategyDeleteResponse(
            success=True,
            message="策略已删除"
        )
        
    except HTTPException:
        raise
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
