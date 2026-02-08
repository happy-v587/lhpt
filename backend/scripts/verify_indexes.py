"""
Script to verify database indexes are properly created.

Requirements: 10.5
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect
from database import engine
from models.kline_data import KLineData
from models.stock import Stock
from models.strategy import Strategy
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_indexes():
    """
    Verify that all required indexes are created in the database.
    """
    inspector = inspect(engine)
    
    # Check KLineData indexes
    logger.info("Checking KLineData table indexes...")
    kline_indexes = inspector.get_indexes('kline_data')
    kline_index_names = [idx['name'] for idx in kline_indexes]
    
    required_kline_indexes = [
        'idx_kline_stock_date',
        'idx_kline_date'
    ]
    
    for idx_name in required_kline_indexes:
        if idx_name in kline_index_names:
            logger.info(f"✓ Index {idx_name} exists")
        else:
            logger.warning(f"✗ Index {idx_name} is missing!")
    
    # Check unique constraint
    kline_constraints = inspector.get_unique_constraints('kline_data')
    constraint_names = [c['name'] for c in kline_constraints]
    
    if 'uix_stock_date_period' in constraint_names:
        logger.info("✓ Unique constraint uix_stock_date_period exists")
    else:
        logger.warning("✗ Unique constraint uix_stock_date_period is missing!")
    
    # Check Strategy indexes
    logger.info("\nChecking Strategy table indexes...")
    strategy_indexes = inspector.get_indexes('strategies')
    strategy_index_names = [idx['name'] for idx in strategy_indexes]
    
    if 'idx_strategies_created' in strategy_index_names:
        logger.info("✓ Index idx_strategies_created exists")
    else:
        logger.warning("✗ Index idx_strategies_created is missing!")
    
    # Print all indexes for reference
    logger.info("\n=== All KLineData Indexes ===")
    for idx in kline_indexes:
        logger.info(f"  {idx['name']}: {idx['column_names']}")
    
    logger.info("\n=== All Strategy Indexes ===")
    for idx in strategy_indexes:
        logger.info(f"  {idx['name']}: {idx['column_names']}")
    
    logger.info("\nIndex verification complete!")


if __name__ == "__main__":
    verify_indexes()
