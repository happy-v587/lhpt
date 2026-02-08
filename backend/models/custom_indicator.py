"""
Custom indicator model for user-defined technical indicators.
"""

from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean, Index
from sqlalchemy.sql import func
from database import Base


class CustomIndicator(Base):
    """Custom indicator definition model."""
    
    __tablename__ = "custom_indicators"
    
    id = Column(String(36), primary_key=True, comment="UUID")
    name = Column(String(100), nullable=False, unique=True, comment="指标名称")
    display_name = Column(String(100), nullable=False, comment="显示名称")
    description = Column(Text, nullable=True, comment="指标描述")
    
    # 指标类型：formula（公式）或 plugin（插件）
    indicator_type = Column(String(20), nullable=False, default='formula', comment="指标类型")
    
    # 公式定义（用于 formula 类型）
    formula = Column(Text, nullable=True, comment="计算公式")
    
    # 参数定义
    params = Column(JSON, nullable=False, comment="参数定义")
    
    # 插件信息（用于 plugin 类型）
    plugin_module = Column(String(200), nullable=True, comment="插件模块路径")
    plugin_class = Column(String(100), nullable=True, comment="插件类名")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index('idx_custom_indicators_type', 'indicator_type'),
        Index('idx_custom_indicators_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<CustomIndicator(id={self.id}, name={self.name}, type={self.indicator_type})>"
