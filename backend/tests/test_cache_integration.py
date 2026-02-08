"""
Integration tests for cache functionality with API endpoints.

Requirements: 10.3
Property 16: 缓存一致性
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import pandas as pd

from main import app
from database import Base, get_db
from services.cache_service import get_cache_service
from repositories.data_repository import DataRepository


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_cache.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override dependencies
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Setup test database before each test."""
    Base.metadata.create_all(bind=engine)
    
    # Clear cache before each test
    cache_service = get_cache_service()
    cache_service.clear()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


def test_kline_data_caching():
    """
    Test that K-line data is properly cached and retrieved from cache.
    
    Property 16: 缓存一致性
    """
    # First, add some test data to the database
    db = TestingSessionLocal()
    repo = DataRepository(db)
    
    # Create test K-line data
    test_data = pd.DataFrame({
        'trade_date': pd.date_range('2024-01-01', periods=5),
        'open': [10.0, 10.5, 11.0, 10.8, 11.2],
        'close': [10.5, 11.0, 10.8, 11.2, 11.5],
        'high': [10.8, 11.2, 11.3, 11.5, 11.8],
        'low': [9.8, 10.3, 10.5, 10.6, 11.0],
        'volume': [1000000, 1100000, 1200000, 1150000, 1300000]
    })
    
    repo.save_kline_data("600000.SH", test_data)
    db.close()
    
    # First request - should fetch from database and cache
    response1 = client.get(
        "/api/stocks/600000.SH/kline",
        params={
            "start_date": "2024-01-01",
            "end_date": "2024-01-05",
            "period": "daily"
        }
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert len(data1["data"]) == 5
    
    # Second request - should retrieve from cache (faster)
    response2 = client.get(
        "/api/stocks/600000.SH/kline",
        params={
            "start_date": "2024-01-01",
            "end_date": "2024-01-05",
            "period": "daily"
        }
    )
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Data should be identical
    assert data1 == data2


def test_cache_invalidation_on_data_update():
    """
    Test that cache is properly invalidated when data is updated.
    
    Property 16: 缓存一致性
    For any cached data, when the underlying database data is updated,
    subsequent reads should return the updated data, not stale cache values.
    """
    db = TestingSessionLocal()
    repo = DataRepository(db)
    
    # Create initial test data
    initial_data = pd.DataFrame({
        'trade_date': pd.date_range('2024-01-01', periods=3),
        'open': [10.0, 10.5, 11.0],
        'close': [10.5, 11.0, 10.8],
        'high': [10.8, 11.2, 11.3],
        'low': [9.8, 10.3, 10.5],
        'volume': [1000000, 1100000, 1200000]
    })
    
    repo.save_kline_data("600000.SH", initial_data)
    
    # First request - cache the data
    response1 = client.get(
        "/api/stocks/600000.SH/kline",
        params={
            "start_date": "2024-01-01",
            "end_date": "2024-01-03",
            "period": "daily"
        }
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["data"][0]["close"] == 10.5
    
    # Update the data
    updated_data = pd.DataFrame({
        'trade_date': pd.date_range('2024-01-01', periods=3),
        'open': [10.0, 10.5, 11.0],
        'close': [12.0, 12.5, 13.0],  # Updated close prices
        'high': [12.5, 13.0, 13.5],
        'low': [9.8, 10.3, 10.5],
        'volume': [1000000, 1100000, 1200000]
    })
    
    repo.save_kline_data("600000.SH", updated_data)
    db.close()
    
    # Second request - should get updated data (cache should be invalidated)
    response2 = client.get(
        "/api/stocks/600000.SH/kline",
        params={
            "start_date": "2024-01-01",
            "end_date": "2024-01-03",
            "period": "daily"
        }
    )
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Should get updated close price, not cached old value
    assert data2["data"][0]["close"] == 12.0


def test_indicator_caching():
    """
    Test that indicator calculations are properly cached.
    """
    db = TestingSessionLocal()
    repo = DataRepository(db)
    
    # Create test data with enough points for MA calculation
    test_data = pd.DataFrame({
        'trade_date': pd.to_datetime(pd.date_range('2024-01-01', periods=30)),
        'open': [10.0 + i * 0.1 for i in range(30)],
        'close': [10.5 + i * 0.1 for i in range(30)],
        'high': [10.8 + i * 0.1 for i in range(30)],
        'low': [9.8 + i * 0.1 for i in range(30)],
        'volume': [1000000 + i * 10000 for i in range(30)]
    })
    
    repo.save_kline_data("600000.SH", test_data)
    db.close()
    
    # First request - calculate and cache
    response1 = client.post(
        "/api/indicators/calculate",
        json={
            "stock_code": "600000.SH",
            "indicator_type": "MA",
            "params": {"periods": [5, 10]},
            "start_date": "2024-01-01",
            "end_date": "2024-01-30"
        }
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert "MA5" in data1["data"]
    assert "MA10" in data1["data"]
    
    # Second request - should retrieve from cache
    response2 = client.post(
        "/api/indicators/calculate",
        json={
            "stock_code": "600000.SH",
            "indicator_type": "MA",
            "params": {"periods": [5, 10]},
            "start_date": "2024-01-01",
            "end_date": "2024-01-30"
        }
    )
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Data should be identical
    assert data1 == data2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
