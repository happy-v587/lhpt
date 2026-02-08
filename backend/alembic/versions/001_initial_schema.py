"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create stocks table
    op.create_table(
        'stocks',
        sa.Column('code', sa.String(10), primary_key=True, comment='股票代码'),
        sa.Column('name', sa.String(50), nullable=False, comment='股票名称'),
        sa.Column('exchange', sa.String(2), nullable=False, comment='交易所 (SH/SZ)'),
        sa.Column('industry', sa.String(50), nullable=True, comment='所属行业'),
        sa.Column('list_date', sa.Date, nullable=True, comment='上市日期'),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), comment='更新时间'),
    )
    
    # Create indexes for stocks table
    op.create_index('idx_stocks_exchange', 'stocks', ['exchange'])
    op.create_index('idx_stocks_industry', 'stocks', ['industry'])
    
    # Create kline_data table
    op.create_table(
        'kline_data',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, comment='主键ID'),
        sa.Column('stock_code', sa.String(10), nullable=False, comment='股票代码'),
        sa.Column('trade_date', sa.Date, nullable=False, comment='交易日期'),
        sa.Column('open', sa.Numeric(10, 2), nullable=False, comment='开盘价'),
        sa.Column('close', sa.Numeric(10, 2), nullable=False, comment='收盘价'),
        sa.Column('high', sa.Numeric(10, 2), nullable=False, comment='最高价'),
        sa.Column('low', sa.Numeric(10, 2), nullable=False, comment='最低价'),
        sa.Column('volume', sa.BigInteger, nullable=False, comment='成交量'),
        sa.Column('amount', sa.Numeric(20, 2), nullable=True, comment='成交额'),
        sa.Column('period', sa.String(10), server_default='daily', nullable=False, comment='周期类型'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), comment='创建时间'),
    )
    
    # Create unique constraint and indexes for kline_data table
    op.create_index('uix_stock_date_period', 'kline_data', ['stock_code', 'trade_date', 'period'], unique=True)
    op.create_index('idx_kline_stock_date', 'kline_data', ['stock_code', 'trade_date'])
    op.create_index('idx_kline_date', 'kline_data', ['trade_date'])
    
    # Create strategies table
    op.create_table(
        'strategies',
        sa.Column('id', sa.String(36), primary_key=True, comment='UUID'),
        sa.Column('name', sa.String(100), nullable=False, comment='策略名称'),
        sa.Column('description', sa.Text, nullable=True, comment='策略描述'),
        sa.Column('config', sa.JSON, nullable=False, comment='策略配置（JSON格式）'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), comment='更新时间'),
    )
    
    # Create index for strategies table
    op.create_index('idx_strategies_created', 'strategies', ['created_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('strategies')
    op.drop_table('kline_data')
    op.drop_table('stocks')
