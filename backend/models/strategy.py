"""
Strategy model for storing trading strategy configurations.
"""

from sqlalchemy import Column, String, Text, DateTime, Index, JSON
from sqlalchemy.sql import func
from database import Base


class Strategy(Base):
    """Strategy configuration model."""
    
    __tablename__ = "strategies"
    
    id = Column(String(36), primary_key=True, comment="UUID")
    name = Column(String(100), nullable=False, comment="策略名称")
    description = Column(Text, nullable=True, comment="策略描述")
    config = Column(JSON, nullable=False, comment="策略配置（JSON格式）")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index('idx_strategies_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Strategy(id={self.id}, name={self.name})>"
