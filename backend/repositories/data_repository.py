"""
Data repository for database operations.
Handles CRUD operations for stocks, K-line data, and strategies.
"""

from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
import pandas as pd
import logging

from models.stock import Stock
from models.kline_data import KLineData
from models.strategy import Strategy
from validators.kline_validator import KLineDataValidator

logger = logging.getLogger(__name__)


class DataRepository:
    """Repository for data access operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        
        # Get cache service for invalidation
        try:
            from services.cache_service import get_cache_service
            self.cache_service = get_cache_service()
        except Exception as e:
            logger.warning(f"Failed to initialize cache service: {e}")
            self.cache_service = None
    
    def save_kline_data(self, stock_code: str, data: pd.DataFrame) -> None:
        """
        Save K-line data to the database with upsert support.
        If a record with the same stock_code, trade_date, and period exists,
        it will be updated; otherwise, a new record will be created.
        
        Uses batch operations for better performance.
        
        Args:
            stock_code: Stock code (e.g., "600000.SH")
            data: DataFrame containing K-line data with columns:
                  trade_date, open, close, high, low, volume, amount (optional), period (optional)
        
        Raises:
            ValueError: If required columns are missing from the DataFrame
            DataValidationError: If data validation fails
        
        Requirements: 9.1, 9.2, 10.5
        Property 1: K线数据完整性约束
        Property 11: 异常数据拒绝
        """
        required_columns = ['trade_date', 'open', 'close', 'high', 'low', 'volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Validate K-line data before saving
        KLineDataValidator.validate_dataframe(data)
        
        # Add stock_code to the data
        data = data.copy()
        data['stock_code'] = stock_code
        
        # Set default period if not provided
        if 'period' not in data.columns:
            data['period'] = 'daily'
        
        # Convert DataFrame to list of dictionaries
        records = data.to_dict('records')
        
        # Use batch upsert for better performance
        # For SQLite, we need to do this record by record due to limitations
        # For PostgreSQL, we could use bulk_insert_mappings with on_conflict
        
        # Batch size for commits
        batch_size = 100
        batch_count = 0
        
        for record in records:
            # Check if record exists
            existing = self.db.query(KLineData).filter(
                and_(
                    KLineData.stock_code == record['stock_code'],
                    KLineData.trade_date == record['trade_date'],
                    KLineData.period == record.get('period', 'daily')
                )
            ).first()
            
            if existing:
                # Update existing record
                for key, value in record.items():
                    if key != 'stock_code' and key != 'trade_date' and key != 'period':
                        setattr(existing, key, value)
            else:
                # Create new record
                kline = KLineData(**record)
                self.db.add(kline)
            
            batch_count += 1
            
            # Commit in batches for better performance
            if batch_count >= batch_size:
                self.db.commit()
                batch_count = 0
                logger.debug(f"Committed batch of {batch_size} records")
        
        # Commit remaining records
        if batch_count > 0:
            self.db.commit()
            logger.debug(f"Committed final batch of {batch_count} records")
        
        # Invalidate cache for this stock
        # Property 16: 缓存一致性 - when data is updated, cache must be invalidated
        if self.cache_service:
            try:
                # Invalidate K-line data cache
                self.cache_service.invalidate_pattern(f"kline:{stock_code}:*")
                # Invalidate indicator cache for this stock
                self.cache_service.invalidate_pattern(f"indicator:{stock_code}:*")
                logger.info(f"Cache invalidated for stock {stock_code}")
            except Exception as e:
                logger.warning(f"Failed to invalidate cache: {e}")
    
    def bulk_save_kline_data(self, data_by_stock: dict) -> None:
        """
        Bulk save K-line data for multiple stocks.
        More efficient than calling save_kline_data multiple times.
        
        Args:
            data_by_stock: Dictionary mapping stock codes to DataFrames
                          e.g., {"600000.SH": df1, "000001.SZ": df2}
        
        Requirements: 10.5
        """
        for stock_code, df in data_by_stock.items():
            self.save_kline_data(stock_code, df)
        
        logger.info(f"Bulk saved K-line data for {len(data_by_stock)} stocks")
    
    def get_kline_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        period: str = 'daily'
    ) -> pd.DataFrame:
        """
        Retrieve K-line data from the database for a given date range.
        
        Args:
            stock_code: Stock code (e.g., "600000.SH")
            start_date: Start date in format "YYYY-MM-DD"
            end_date: End date in format "YYYY-MM-DD"
            period: Period type ('daily', 'weekly', 'monthly'), default is 'daily'
        
        Returns:
            DataFrame containing K-line data with columns:
            trade_date, open, close, high, low, volume, amount
        """
        query = self.db.query(KLineData).filter(
            and_(
                KLineData.stock_code == stock_code,
                KLineData.trade_date >= start_date,
                KLineData.trade_date <= end_date,
                KLineData.period == period
            )
        ).order_by(KLineData.trade_date)
        
        results = query.all()
        
        if not results:
            return pd.DataFrame()
        
        # Convert to DataFrame
        data = []
        for record in results:
            data.append({
                'trade_date': record.trade_date,
                'open': float(record.open),
                'close': float(record.close),
                'high': float(record.high),
                'low': float(record.low),
                'volume': record.volume,
                'amount': float(record.amount) if record.amount else None
            })
        
        df = pd.DataFrame(data)
        
        # Ensure trade_date is datetime type
        if not df.empty:
            df['trade_date'] = pd.to_datetime(df['trade_date'])
        
        return df
    
    def save_strategy(self, strategy_data: dict) -> str:
        """
        Save a trading strategy configuration to the database.
        
        Args:
            strategy_data: Dictionary containing strategy information:
                - id: Strategy UUID (optional, will be generated if not provided)
                - name: Strategy name
                - description: Strategy description (optional)
                - config: Strategy configuration as dict (will be stored as JSON)
        
        Returns:
            Strategy ID (UUID)
        
        Raises:
            ValueError: If required fields are missing
        """
        if 'name' not in strategy_data:
            raise ValueError("Strategy name is required")
        
        if 'config' not in strategy_data:
            raise ValueError("Strategy config is required")
        
        # Generate UUID if not provided
        if 'id' not in strategy_data or not strategy_data['id']:
            import uuid
            strategy_data['id'] = str(uuid.uuid4())
        
        strategy = Strategy(
            id=strategy_data['id'],
            name=strategy_data['name'],
            description=strategy_data.get('description'),
            config=strategy_data['config']
        )
        
        self.db.add(strategy)
        self.db.commit()
        self.db.refresh(strategy)
        
        return strategy.id
    
    def get_strategies(self) -> List[dict]:
        """
        Retrieve all trading strategies from the database.
        
        Returns:
            List of dictionaries containing strategy information:
            - id: Strategy UUID
            - name: Strategy name
            - description: Strategy description
            - config: Strategy configuration
            - created_at: Creation timestamp
            - updated_at: Last update timestamp
        """
        strategies = self.db.query(Strategy).order_by(Strategy.created_at.desc()).all()
        
        result = []
        for strategy in strategies:
            result.append({
                'id': strategy.id,
                'name': strategy.name,
                'description': strategy.description,
                'config': strategy.config,
                'created_at': strategy.created_at.isoformat() if strategy.created_at else None,
                'updated_at': strategy.updated_at.isoformat() if strategy.updated_at else None
            })
        
        return result
    
    def get_strategy_by_id(self, strategy_id: str) -> Optional[dict]:
        """
        Retrieve a specific strategy by ID.
        
        Args:
            strategy_id: Strategy UUID
        
        Returns:
            Dictionary containing strategy information, or None if not found
        """
        strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            return None
        
        return {
            'id': strategy.id,
            'name': strategy.name,
            'description': strategy.description,
            'config': strategy.config,
            'created_at': strategy.created_at.isoformat() if strategy.created_at else None,
            'updated_at': strategy.updated_at.isoformat() if strategy.updated_at else None
        }
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """
        Delete a strategy from the database.
        
        Args:
            strategy_id: Strategy UUID
        
        Returns:
            True if the strategy was deleted, False if not found
        """
        strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            return False
        
        self.db.delete(strategy)
        self.db.commit()
        
        return True
