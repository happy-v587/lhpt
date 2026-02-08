"""
Stock model for storing stock information.
"""

from sqlalchemy import Column, String, Date, DateTime
from sqlalchemy.sql import func
from database import Base


class Stock(Base):
    """Stock information model."""
    
    __tablename__ = "stocks"
    
    code = Column(String(10), primary_key=True, comment="股票代码")
    name = Column(String(50), nullable=False, comment="股票名称")
    exchange = Column(String(2), nullable=False, comment="交易所 (SH/SZ)")
    industry = Column(String(50), nullable=True, comment="所属行业")
    list_date = Column(Date, nullable=True, comment="上市日期")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<Stock(code={self.code}, name={self.name}, exchange={self.exchange})>"
