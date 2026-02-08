"""
API endpoint tests for backend API validation.
Tests all API endpoints to ensure they work correctly.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from database import Base, get_db
from models.stock import Stock
from models.kline_data import KLineData
from models.strategy import Strategy
import uuid
from datetime import datetime, date


# Create test database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def test_db():
    """Create test database tables."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session and add test data
    db = TestingSessionLocal()
    
    try:
        # Add some test data
        test_stock = Stock(
            code="600000.SH",
            name="浦发银行",
            exchange="SH",
            industry="银行"
        )
        db.add(test_stock)
        
        # Add test K-line data
        for i in range(30):
            kline = KLineData(
                stock_code="600000.SH",
                trade_date=date(2024, 1, i + 1),
                open=10.0 + i * 0.1,
                close=10.1 + i * 0.1,
                high=10.2 + i * 0.1,
                low=9.9 + i * 0.1,
                volume=1000000 + i * 10000,
                amount=10000000.0 + i * 100000,
                period="daily"
            )
            db.add(kline)
        
        db.commit()
        
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct response."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_check_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestStockEndpoints:
    """Test stock-related API endpoints."""
    
    def test_get_stocks_endpoint(self, test_db):
        """
        Test GET /api/stocks endpoint.
        Requirements: 4.1
        """
        response = client.get("/api/stocks")
        
        # Should return 200 or 503 (if data source unavailable)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "stocks" in data
            assert isinstance(data["stocks"], list)
    
    def test_get_kline_data_endpoint(self, test_db):
        """
        Test GET /api/stocks/{code}/kline endpoint.
        Requirements: 4.2, 9.4
        """
        response = client.get(
            "/api/stocks/600000.SH/kline",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "period": "daily"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert data["code"] == "600000.SH"
        assert "data" in data
        assert isinstance(data["data"], list)
        
        # Verify data structure
        if len(data["data"]) > 0:
            point = data["data"][0]
            assert "date" in point
            assert "open" in point
            assert "close" in point
            assert "high" in point
            assert "low" in point
            assert "volume" in point
    
    def test_get_kline_data_invalid_stock_code(self, test_db):
        """
        Test K-line endpoint with invalid stock code.
        Requirements: 9.3, 9.4
        """
        response = client.get(
            "/api/stocks/INVALID/kline",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "period": "daily"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "INVALID_STOCK_CODE"
    
    def test_get_kline_data_invalid_period(self, test_db):
        """
        Test K-line endpoint with invalid period.
        Requirements: 9.4
        """
        response = client.get(
            "/api/stocks/600000.SH/kline",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "period": "invalid"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "INVALID_PERIOD"
    
    def test_get_kline_data_invalid_date_format(self, test_db):
        """
        Test K-line endpoint with invalid date format.
        Requirements: 9.4
        """
        response = client.get(
            "/api/stocks/600000.SH/kline",
            params={
                "start_date": "2024/01/01",
                "end_date": "2024-01-31",
                "period": "daily"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "INVALID_DATE_FORMAT"
    
    def test_get_stock_info_endpoint(self, test_db):
        """
        Test GET /api/stocks/{code}/info endpoint.
        Requirements: 4.2
        """
        response = client.get("/api/stocks/600000.SH/info")
        
        # Should return 200 or 503 (if data source unavailable)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "code" in data
            assert "name" in data
            assert "exchange" in data
    
    def test_get_stock_info_invalid_code(self, test_db):
        """
        Test stock info endpoint with invalid code.
        Requirements: 9.3
        """
        response = client.get("/api/stocks/INVALID/info")
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "INVALID_STOCK_CODE"


class TestIndicatorEndpoints:
    """Test indicator-related API endpoints."""
    
    def test_get_indicator_types_endpoint(self, test_db):
        """
        Test GET /api/indicators/types endpoint.
        Requirements: 4.3
        """
        response = client.get("/api/indicators/types")
        
        assert response.status_code == 200
        data = response.json()
        assert "indicators" in data
        assert isinstance(data["indicators"], list)
        assert len(data["indicators"]) > 0
        
        # Verify structure
        indicator = data["indicators"][0]
        assert "type" in indicator
        assert "name" in indicator
        assert "params" in indicator
    
    def test_calculate_ma_indicator(self, test_db):
        """
        Test POST /api/indicators/calculate for MA.
        Requirements: 4.3
        """
        response = client.post(
            "/api/indicators/calculate",
            json={
                "stock_code": "600000.SH",
                "indicator_type": "MA",
                "params": {"periods": [5, 10, 20]},
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["indicator_type"] == "MA"
        assert "data" in data
        assert "dates" in data["data"]
        assert "MA5" in data["data"]
        assert "MA10" in data["data"]
        assert "MA20" in data["data"]
    
    def test_calculate_macd_indicator(self, test_db):
        """
        Test POST /api/indicators/calculate for MACD.
        Requirements: 4.3
        """
        response = client.post(
            "/api/indicators/calculate",
            json={
                "stock_code": "600000.SH",
                "indicator_type": "MACD",
                "params": {
                    "fast_period": 12,
                    "slow_period": 26,
                    "signal_period": 9
                },
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["indicator_type"] == "MACD"
        assert "data" in data
        assert "DIF" in data["data"]
        assert "DEA" in data["data"]
        assert "MACD" in data["data"]
    
    def test_calculate_rsi_indicator(self, test_db):
        """
        Test POST /api/indicators/calculate for RSI.
        Requirements: 4.3
        """
        response = client.post(
            "/api/indicators/calculate",
            json={
                "stock_code": "600000.SH",
                "indicator_type": "RSI",
                "params": {"period": 14},
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["indicator_type"] == "RSI"
        assert "data" in data
        assert "RSI14" in data["data"]
    
    def test_calculate_boll_indicator(self, test_db):
        """
        Test POST /api/indicators/calculate for BOLL.
        Requirements: 4.3
        """
        response = client.post(
            "/api/indicators/calculate",
            json={
                "stock_code": "600000.SH",
                "indicator_type": "BOLL",
                "params": {"period": 20, "std_dev": 2.0},
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["indicator_type"] == "BOLL"
        assert "data" in data
        assert "upper" in data["data"]
        assert "middle" in data["data"]
        assert "lower" in data["data"]
    
    def test_calculate_indicator_invalid_stock_code(self, test_db):
        """
        Test indicator calculation with invalid stock code.
        Requirements: 9.3
        """
        response = client.post(
            "/api/indicators/calculate",
            json={
                "stock_code": "INVALID",
                "indicator_type": "MA",
                "params": {"periods": [5]},
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "INVALID_STOCK_CODE"
    
    def test_calculate_indicator_invalid_type(self, test_db):
        """
        Test indicator calculation with invalid indicator type.
        Requirements: 9.4
        """
        response = client.post(
            "/api/indicators/calculate",
            json={
                "stock_code": "600000.SH",
                "indicator_type": "INVALID",
                "params": {},
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "INVALID_INDICATOR_TYPE"


class TestStrategyEndpoints:
    """Test strategy-related API endpoints."""
    
    def test_get_strategies_empty(self, test_db):
        """
        Test GET /api/strategies with no strategies.
        Requirements: 4.4
        """
        response = client.get("/api/strategies")
        
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data
        assert isinstance(data["strategies"], list)
    
    def test_create_strategy(self, test_db):
        """
        Test POST /api/strategies to create a strategy.
        Requirements: 4.5
        """
        response = client.post(
            "/api/strategies",
            json={
                "name": "双均线策略",
                "description": "MA5上穿MA20买入",
                "indicators": [
                    {"type": "MA", "params": {"periods": [5, 20]}}
                ],
                "conditions": [
                    {
                        "indicator": "MA5",
                        "operator": "cross_up",
                        "value": "MA20"
                    }
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "双均线策略"
        assert "created_at" in data
        
        return data["id"]
    
    def test_get_strategies_with_data(self, test_db):
        """
        Test GET /api/strategies with existing strategies.
        Requirements: 4.4
        """
        # First create a strategy
        create_response = client.post(
            "/api/strategies",
            json={
                "name": "测试策略",
                "description": "测试描述",
                "indicators": [{"type": "MA", "params": {"periods": [5]}}],
                "conditions": [{"indicator": "MA5", "operator": ">", "value": 10}]
            }
        )
        assert create_response.status_code == 200
        
        # Then get all strategies
        response = client.get("/api/strategies")
        
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data
        assert len(data["strategies"]) > 0
    
    def test_get_strategy_by_id(self, test_db):
        """
        Test GET /api/strategies/{id} to get specific strategy.
        Requirements: 4.4
        """
        # First create a strategy
        create_response = client.post(
            "/api/strategies",
            json={
                "name": "详细策略",
                "description": "详细描述",
                "indicators": [{"type": "RSI", "params": {"period": 14}}],
                "conditions": [{"indicator": "RSI14", "operator": "<", "value": 30}]
            }
        )
        assert create_response.status_code == 200
        strategy_id = create_response.json()["id"]
        
        # Get the strategy by ID
        response = client.get(f"/api/strategies/{strategy_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == strategy_id
        assert data["name"] == "详细策略"
        assert "indicators" in data
        assert "conditions" in data
    
    def test_get_strategy_not_found(self, test_db):
        """
        Test GET /api/strategies/{id} with non-existent ID.
        Requirements: 4.4
        """
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/strategies/{fake_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "STRATEGY_NOT_FOUND"
    
    def test_delete_strategy(self, test_db):
        """
        Test DELETE /api/strategies/{id}.
        Requirements: 4.5
        """
        # First create a strategy
        create_response = client.post(
            "/api/strategies",
            json={
                "name": "待删除策略",
                "description": "将被删除",
                "indicators": [{"type": "MA", "params": {"periods": [5]}}],
                "conditions": [{"indicator": "MA5", "operator": ">", "value": 10}]
            }
        )
        assert create_response.status_code == 200
        strategy_id = create_response.json()["id"]
        
        # Delete the strategy
        response = client.delete(f"/api/strategies/{strategy_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        
        # Verify it's deleted
        get_response = client.get(f"/api/strategies/{strategy_id}")
        assert get_response.status_code == 404
    
    def test_delete_strategy_not_found(self, test_db):
        """
        Test DELETE /api/strategies/{id} with non-existent ID.
        Requirements: 4.5
        """
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/api/strategies/{fake_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "STRATEGY_NOT_FOUND"
    
    def test_create_strategy_invalid_operator(self, test_db):
        """
        Test creating strategy with invalid operator.
        Requirements: 9.4
        """
        response = client.post(
            "/api/strategies",
            json={
                "name": "无效策略",
                "description": "无效操作符",
                "indicators": [{"type": "MA", "params": {"periods": [5]}}],
                "conditions": [{"indicator": "MA5", "operator": "invalid_op", "value": 10}]
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "INVALID_OPERATOR"


class TestErrorResponseFormat:
    """
    Test error response format consistency.
    Property 13: Error response format consistency
    Requirements: 4.6, 8.3
    """
    
    def test_error_response_has_standard_format(self, test_db):
        """Test that all error responses follow standard format."""
        # Trigger an error
        response = client.get("/api/stocks/INVALID/info")
        
        assert response.status_code == 400
        data = response.json()
        
        # Verify standard error format
        assert "detail" in data
        error = data["detail"]
        assert "code" in error
        assert "message" in error
        assert "details" in error
        
        # Verify error code is a string
        assert isinstance(error["code"], str)
        assert isinstance(error["message"], str)
    
    def test_validation_error_format(self, test_db):
        """Test validation error response format."""
        # Send invalid request (missing required fields)
        response = client.post(
            "/api/indicators/calculate",
            json={
                "stock_code": "600000.SH"
                # Missing required fields
            }
        )
        
        # Our custom error handler converts 422 to 400
        assert response.status_code == 400
        data = response.json()
        
        # Verify error format
        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert error["code"] == "VALIDATION_ERROR"
        assert "message" in error
        assert "timestamp" in error
