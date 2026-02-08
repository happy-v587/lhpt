"""
Backtest model for storing backtest results and configurations.
"""

from sqlalchemy import Column, String, Text, DateTime, JSON, Numeric, Integer, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Backtest(Base):
    """Backtest result model."""
    
    __tablename__ = "backtests"
    
    id = Column(String(36), primary_key=True, comment="UUID")
    strategy_id = Column(String(36), ForeignKey('strategies.id'), nullable=False, comment="策略ID")
    stock_code = Column(String(10), nullable=False, comment="股票代码")
    start_date = Column(DateTime, nullable=False, comment="回测开始日期")
    end_date = Column(DateTime, nullable=False, comment="回测结束日期")
    
    # 回测配置
    initial_capital = Column(Numeric(20, 2), nullable=False, comment="初始资金")
    commission_rate = Column(Numeric(10, 6), default=0.0003, comment="手续费率")
    slippage_rate = Column(Numeric(10, 6), default=0.0001, comment="滑点率")
    
    # 回测结果
    final_capital = Column(Numeric(20, 2), comment="最终资金")
    total_return = Column(Numeric(10, 4), comment="总收益率")
    annual_return = Column(Numeric(10, 4), comment="年化收益率")
    sharpe_ratio = Column(Numeric(10, 4), comment="夏普比率")
    max_drawdown = Column(Numeric(10, 4), comment="最大回撤")
    win_rate = Column(Numeric(10, 4), comment="胜率")
    total_trades = Column(Integer, comment="总交易次数")
    
    # 详细数据
    trades = Column(JSON, comment="交易记录")
    equity_curve = Column(JSON, comment="资金曲线")
    metrics = Column(JSON, comment="其他指标")
    
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    def __repr__(self):
        return f"<Backtest(id={self.id}, strategy_id={self.strategy_id}, sharpe_ratio={self.sharpe_ratio})>"
