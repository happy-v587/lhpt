"""
Backtest API routes.
Provides endpoints for running backtests and retrieving results.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime
import logging
import uuid

from database import get_db
from services.backtest_engine import BacktestEngine
from services.data_provider import DataProvider
from repositories.data_repository import DataRepository
from models.backtest import Backtest
from exceptions import QuantTradingError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/backtests", tags=["backtests"])


# Pydantic models
class BacktestRunRequest(BaseModel):
    """Request model for running a backtest."""
    strategy_id: str = Field(..., description="策略ID")
    stock_code: str = Field(..., description="股票代码")
    start_date: str = Field(..., description="开始日期 (YYYY-MM-DD)")
    end_date: str = Field(..., description="结束日期 (YYYY-MM-DD)")
    initial_capital: float = Field(100000.0, description="初始资金")
    commission_rate: float = Field(0.0003, description="手续费率")
    slippage_rate: float = Field(0.0001, description="滑点率")


class BacktestMetrics(BaseModel):
    """Backtest metrics model."""
    initial_capital: float
    final_capital: float
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int


class BacktestRunResponse(BaseModel):
    """Response model for backtest run."""
    backtest_id: str
    metrics: BacktestMetrics
    message: str


class BacktestDetailResponse(BaseModel):
    """Detailed backtest response."""
    id: str
    strategy_id: str
    stock_code: str
    start_date: str
    end_date: str
    initial_capital: float
    commission_rate: float
    slippage_rate: float
    metrics: BacktestMetrics
    trades: List[Dict[str, Any]]
    equity_curve: List[Dict[str, Any]]
    created_at: str


class BacktestListItem(BaseModel):
    """Backtest list item."""
    id: str
    strategy_id: str
    stock_code: str
    start_date: str
    end_date: str
    sharpe_ratio: Optional[float]
    total_return: Optional[float]
    created_at: str


class BacktestListResponse(BaseModel):
    """Response model for backtest list."""
    backtests: List[BacktestListItem]


@router.post("/run", response_model=BacktestRunResponse)
async def run_backtest(
    request: BacktestRunRequest,
    db: Session = Depends(get_db)
):
    """
    Run a backtest for a strategy.
    
    Args:
        request: Backtest configuration
    
    Returns:
        Backtest results with metrics
    """
    try:
        logger.info(f"Running backtest for strategy {request.strategy_id} on {request.stock_code}")
        
        # Get strategy
        repo = DataRepository(db)
        strategy = repo.get_strategy_by_id(request.strategy_id)
        
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")
        
        # Get K-line data
        start = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end = datetime.strptime(request.end_date, "%Y-%m-%d").date()
        
        kline_data = repo.get_kline_data(
            stock_code=request.stock_code,
            start_date=start,
            end_date=end,
            period='daily'
        )
        
        # If not in database, fetch from data provider
        if kline_data.empty:
            logger.info(f"No data in database, fetching from data provider")
            data_provider = DataProvider()
            kline_data = data_provider.get_kline_data(
                request.stock_code,
                request.start_date,
                request.end_date,
                period='daily'
            )
            
            # Save to database for future use
            if not kline_data.empty:
                repo.save_kline_data(request.stock_code, kline_data)
        
        if kline_data.empty:
            raise HTTPException(status_code=404, detail="没有找到K线数据")
        
        # Prepare data
        kline_data['date'] = kline_data['trade_date']
        
        # Initialize backtest engine
        engine = BacktestEngine(
            initial_capital=request.initial_capital,
            commission_rate=request.commission_rate,
            slippage_rate=request.slippage_rate
        )
        
        # Run backtest
        results = engine.run_backtest(kline_data, strategy['config'])
        
        # Save backtest results
        backtest_id = str(uuid.uuid4())
        backtest = Backtest(
            id=backtest_id,
            strategy_id=request.strategy_id,
            stock_code=request.stock_code,
            start_date=start,
            end_date=end,
            initial_capital=request.initial_capital,
            commission_rate=request.commission_rate,
            slippage_rate=request.slippage_rate,
            final_capital=results['metrics']['final_capital'],
            total_return=results['metrics']['total_return'],
            annual_return=results['metrics']['annual_return'],
            sharpe_ratio=results['metrics']['sharpe_ratio'],
            max_drawdown=results['metrics']['max_drawdown'],
            win_rate=results['metrics']['win_rate'],
            total_trades=results['metrics']['total_trades'],
            trades=results['trades'],
            equity_curve=results['equity_curve'],
            metrics=results['metrics']
        )
        
        db.add(backtest)
        db.commit()
        
        logger.info(f"Backtest completed: {backtest_id}, Sharpe: {results['metrics']['sharpe_ratio']:.2f}")
        
        return BacktestRunResponse(
            backtest_id=backtest_id,
            metrics=BacktestMetrics(**results['metrics']),
            message="回测完成"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"回测失败: {str(e)}")


@router.get("", response_model=BacktestListResponse)
async def get_backtests(
    strategy_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of backtests.
    
    Args:
        strategy_id: Optional filter by strategy ID
    
    Returns:
        List of backtests
    """
    try:
        query = db.query(Backtest)
        
        if strategy_id:
            query = query.filter(Backtest.strategy_id == strategy_id)
        
        backtests = query.order_by(Backtest.created_at.desc()).all()
        
        return BacktestListResponse(
            backtests=[
                BacktestListItem(
                    id=bt.id,
                    strategy_id=bt.strategy_id,
                    stock_code=bt.stock_code,
                    start_date=bt.start_date.isoformat(),
                    end_date=bt.end_date.isoformat(),
                    sharpe_ratio=float(bt.sharpe_ratio) if bt.sharpe_ratio else None,
                    total_return=float(bt.total_return) if bt.total_return else None,
                    created_at=bt.created_at.isoformat()
                )
                for bt in backtests
            ]
        )
        
    except Exception as e:
        logger.error(f"Failed to get backtests: {e}")
        raise HTTPException(status_code=500, detail=f"获取回测列表失败: {str(e)}")


@router.get("/{backtest_id}", response_model=BacktestDetailResponse)
async def get_backtest_detail(
    backtest_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed backtest results.
    
    Args:
        backtest_id: Backtest ID
    
    Returns:
        Detailed backtest results
    """
    try:
        backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
        
        if not backtest:
            raise HTTPException(status_code=404, detail="回测不存在")
        
        return BacktestDetailResponse(
            id=backtest.id,
            strategy_id=backtest.strategy_id,
            stock_code=backtest.stock_code,
            start_date=backtest.start_date.isoformat(),
            end_date=backtest.end_date.isoformat(),
            initial_capital=float(backtest.initial_capital),
            commission_rate=float(backtest.commission_rate),
            slippage_rate=float(backtest.slippage_rate),
            metrics=BacktestMetrics(
                initial_capital=float(backtest.initial_capital),
                final_capital=float(backtest.final_capital),
                total_return=float(backtest.total_return),
                annual_return=float(backtest.annual_return),
                sharpe_ratio=float(backtest.sharpe_ratio),
                max_drawdown=float(backtest.max_drawdown),
                win_rate=float(backtest.win_rate),
                total_trades=backtest.total_trades,
                winning_trades=backtest.metrics.get('winning_trades', 0),
                losing_trades=backtest.metrics.get('losing_trades', 0)
            ),
            trades=backtest.trades,
            equity_curve=backtest.equity_curve,
            created_at=backtest.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get backtest detail: {e}")
        raise HTTPException(status_code=500, detail=f"获取回测详情失败: {str(e)}")


@router.delete("/{backtest_id}")
async def delete_backtest(
    backtest_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a backtest.
    
    Args:
        backtest_id: Backtest ID
    
    Returns:
        Success message
    """
    try:
        backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
        
        if not backtest:
            raise HTTPException(status_code=404, detail="回测不存在")
        
        db.delete(backtest)
        db.commit()
        
        return {"success": True, "message": "回测已删除"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete backtest: {e}")
        raise HTTPException(status_code=500, detail=f"删除回测失败: {str(e)}")
