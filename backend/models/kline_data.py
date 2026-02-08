"""
K-line data model for storing historical trading data.
"""

from sqlalchemy import Column, Integer, String, Date, Numeric, BigInteger, DateTime, Index, UniqueConstraint
from sqlalchemy.sql import func
from database import Base


class KLineData(Base):
    """K-line data model."""
    
    __tablename__ = "kline_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    stock_code = Column(String(10), nullable=False, comment="股票代码")
    trade_date = Column(Date, nullable=False, comment="交易日期")
    open = Column(Numeric(10, 2), nullable=False, comment="开盘价")
    close = Column(Numeric(10, 2), nullable=False, comment="收盘价")
    high = Column(Numeric(10, 2), nullable=False, comment="最高价")
    low = Column(Numeric(10, 2), nullable=False, comment="最低价")
    volume = Column(BigInteger, nullable=False, comment="成交量")
    amount = Column(Numeric(20, 2), nullable=True, comment="成交额")
    period = Column(String(10), default='daily', nullable=False, comment="周期类型")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    # Unique constraint to prevent duplicate records
    __table_args__ = (
        UniqueConstraint('stock_code', 'trade_date', 'period', name='uix_stock_date_period'),
        Index('idx_kline_stock_date', 'stock_code', 'trade_date'),
        Index('idx_kline_date', 'trade_date'),
    )
    
    def __repr__(self):
        return f"<KLineData(stock_code={self.stock_code}, trade_date={self.trade_date}, close={self.close})>"
