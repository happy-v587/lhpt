"""
Checkpoint test to verify data layer implementation.
This test validates that the core data layer components are working correctly.
"""

import pytest
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import uuid

from database import Base
from models.stock import Stock
from models.kline_data import KLineData
from models.strategy import Strategy
from repositories.data_repository import DataRepository


@pytest.fixture
def test_db():
    """Create a test database in memory."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def repository(test_db):
    """Create a DataRepository instance with test database."""
    return DataRepository(test_db)


class TestDataLayerCheckpoint:
    """Checkpoint tests for data layer validation."""
    
    def test_database_models_creation(self, test_db):
        """Test that all database models can be created."""
        # Create a stock
        stock = Stock(
            code="600000.SH",
            name="浦发银行",
            exchange="SH",
            industry="银行",
            list_date=date(1999, 11, 10)
        )
        test_db.add(stock)
        test_db.commit()
        
        # Verify stock was created
        retrieved_stock = test_db.query(Stock).filter(Stock.code == "600000.SH").first()
        assert retrieved_stock is not None
        assert retrieved_stock.name == "浦发银行"
        assert retrieved_stock.exchange == "SH"
    
    def test_kline_data_creation(self, test_db):
        """Test that K-line data can be created."""
        kline = KLineData(
            stock_code="600000.SH",
            trade_date=date(2024, 1, 1),
            open=10.5,
            close=10.8,
            high=11.0,
            low=10.3,
            volume=1000000,
            amount=10800000.0,
            period="daily"
        )
        test_db.add(kline)
        test_db.commit()
        
        # Verify K-line data was created
        retrieved_kline = test_db.query(KLineData).filter(
            KLineData.stock_code == "600000.SH"
        ).first()
        assert retrieved_kline is not None
        assert float(retrieved_kline.close) == 10.8
        assert retrieved_kline.volume == 1000000
    
    def test_strategy_creation(self, test_db):
        """Test that strategy can be created."""
        strategy_id = str(uuid.uuid4())
        strategy = Strategy(
            id=strategy_id,
            name="测试策略",
            description="这是一个测试策略",
            config={"indicators": ["MA5", "MA10"], "conditions": []}
        )
        test_db.add(strategy)
        test_db.commit()
        
        # Verify strategy was created
        retrieved_strategy = test_db.query(Strategy).filter(
            Strategy.id == strategy_id
        ).first()
        assert retrieved_strategy is not None
        assert retrieved_strategy.name == "测试策略"
        assert "MA5" in retrieved_strategy.config["indicators"]
    
    def test_repository_save_kline_data(self, repository):
        """Test DataRepository save_kline_data method."""
        # Create test data
        data = pd.DataFrame({
            'trade_date': [date(2024, 1, 1), date(2024, 1, 2)],
            'open': [10.5, 10.8],
            'close': [10.8, 11.0],
            'high': [11.0, 11.2],
            'low': [10.3, 10.7],
            'volume': [1000000, 1100000],
            'amount': [10800000.0, 12100000.0]
        })
        
        # Save data
        repository.save_kline_data("600000.SH", data)
        
        # Verify data was saved
        retrieved_data = repository.get_kline_data(
            "600000.SH",
            "2024-01-01",
            "2024-01-02"
        )
        
        assert len(retrieved_data) == 2
        assert retrieved_data.iloc[0]['close'] == 10.8
        assert retrieved_data.iloc[1]['close'] == 11.0
    
    def test_repository_upsert_kline_data(self, repository):
        """Test that save_kline_data performs upsert correctly."""
        # Create initial data
        data1 = pd.DataFrame({
            'trade_date': [date(2024, 1, 1)],
            'open': [10.5],
            'close': [10.8],
            'high': [11.0],
            'low': [10.3],
            'volume': [1000000]
        })
        
        repository.save_kline_data("600000.SH", data1)
        
        # Update with new data for same date
        data2 = pd.DataFrame({
            'trade_date': [date(2024, 1, 1)],
            'open': [10.6],
            'close': [10.9],
            'high': [11.1],
            'low': [10.4],
            'volume': [1100000]
        })
        
        repository.save_kline_data("600000.SH", data2)
        
        # Verify only one record exists with updated values
        retrieved_data = repository.get_kline_data(
            "600000.SH",
            "2024-01-01",
            "2024-01-01"
        )
        
        assert len(retrieved_data) == 1
        assert retrieved_data.iloc[0]['close'] == 10.9
        assert retrieved_data.iloc[0]['volume'] == 1100000
    
    def test_repository_save_and_get_strategy(self, repository):
        """Test strategy save and retrieval."""
        strategy_data = {
            'name': '双均线策略',
            'description': 'MA5上穿MA20买入',
            'config': {
                'indicators': [
                    {'type': 'MA', 'params': {'periods': [5, 20]}}
                ],
                'conditions': [
                    {'indicator': 'MA5', 'operator': 'cross_up', 'value': 'MA20'}
                ]
            }
        }
        
        # Save strategy
        strategy_id = repository.save_strategy(strategy_data)
        assert strategy_id is not None
        
        # Retrieve strategies
        strategies = repository.get_strategies()
        assert len(strategies) == 1
        assert strategies[0]['name'] == '双均线策略'
        assert strategies[0]['id'] == strategy_id
    
    def test_repository_delete_strategy(self, repository):
        """Test strategy deletion."""
        strategy_data = {
            'name': '测试策略',
            'config': {'indicators': []}
        }
        
        # Save strategy
        strategy_id = repository.save_strategy(strategy_data)
        
        # Delete strategy
        result = repository.delete_strategy(strategy_id)
        assert result is True
        
        # Verify strategy was deleted
        strategies = repository.get_strategies()
        assert len(strategies) == 0
        
        # Try to delete non-existent strategy
        result = repository.delete_strategy("non-existent-id")
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
