"""add backtest and custom indicators tables

Revision ID: 002
Revises: 001
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create custom_indicators table
    op.create_table(
        'custom_indicators',
        sa.Column('id', sa.String(36), primary_key=True, comment='UUID'),
        sa.Column('name', sa.String(100), nullable=False, unique=True, comment='指标名称'),
        sa.Column('display_name', sa.String(100), nullable=False, comment='显示名称'),
        sa.Column('description', sa.Text, nullable=True, comment='指标描述'),
        sa.Column('indicator_type', sa.String(20), nullable=False, default='formula', comment='指标类型'),
        sa.Column('formula', sa.Text, nullable=True, comment='计算公式'),
        sa.Column('params', sa.JSON, nullable=False, comment='参数定义'),
        sa.Column('plugin_module', sa.String(200), nullable=True, comment='插件模块路径'),
        sa.Column('plugin_class', sa.String(100), nullable=True, comment='插件类名'),
        sa.Column('is_active', sa.Boolean, default=True, comment='是否启用'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), comment='更新时间'),
    )
    
    op.create_index('idx_custom_indicators_type', 'custom_indicators', ['indicator_type'])
    op.create_index('idx_custom_indicators_active', 'custom_indicators', ['is_active'])
    
    # Create backtests table
    op.create_table(
        'backtests',
        sa.Column('id', sa.String(36), primary_key=True, comment='UUID'),
        sa.Column('strategy_id', sa.String(36), sa.ForeignKey('strategies.id'), nullable=False, comment='策略ID'),
        sa.Column('stock_code', sa.String(10), nullable=False, comment='股票代码'),
        sa.Column('start_date', sa.DateTime, nullable=False, comment='回测开始日期'),
        sa.Column('end_date', sa.DateTime, nullable=False, comment='回测结束日期'),
        sa.Column('initial_capital', sa.Numeric(20, 2), nullable=False, comment='初始资金'),
        sa.Column('commission_rate', sa.Numeric(10, 6), default=0.0003, comment='手续费率'),
        sa.Column('slippage_rate', sa.Numeric(10, 6), default=0.0001, comment='滑点率'),
        sa.Column('final_capital', sa.Numeric(20, 2), comment='最终资金'),
        sa.Column('total_return', sa.Numeric(10, 4), comment='总收益率'),
        sa.Column('annual_return', sa.Numeric(10, 4), comment='年化收益率'),
        sa.Column('sharpe_ratio', sa.Numeric(10, 4), comment='夏普比率'),
        sa.Column('max_drawdown', sa.Numeric(10, 4), comment='最大回撤'),
        sa.Column('win_rate', sa.Numeric(10, 4), comment='胜率'),
        sa.Column('total_trades', sa.Integer, comment='总交易次数'),
        sa.Column('trades', sa.JSON, comment='交易记录'),
        sa.Column('equity_curve', sa.JSON, comment='资金曲线'),
        sa.Column('metrics', sa.JSON, comment='其他指标'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), comment='创建时间'),
    )
    
    op.create_index('idx_backtests_strategy', 'backtests', ['strategy_id'])
    op.create_index('idx_backtests_stock', 'backtests', ['stock_code'])
    op.create_index('idx_backtests_created', 'backtests', ['created_at'])


def downgrade():
    op.drop_index('idx_backtests_created', 'backtests')
    op.drop_index('idx_backtests_stock', 'backtests')
    op.drop_index('idx_backtests_strategy', 'backtests')
    op.drop_table('backtests')
    
    op.drop_index('idx_custom_indicators_active', 'custom_indicators')
    op.drop_index('idx_custom_indicators_type', 'custom_indicators')
    op.drop_table('custom_indicators')
