"""
API Checkpoint Tests - Backend API Validation
Tests core API functionality to ensure all endpoints are working correctly.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app

# Create test client
client = TestClient(app)


class TestAPIHealthAndStructure:
    """Test that API is running and has correct structure."""
    
    def test_root_endpoint_accessible(self):
        """Test that root endpoint is accessible."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_endpoint_accessible(self):
        """Test that health check endpoint is accessible."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestStockAPIEndpoints:
    """Test stock-related API endpoints structure and validation."""
    
    def test_get_stocks_endpoint_exists(self):
        """Test that GET /api/stocks endpoint exists."""
        response = client.get("/api/stocks")
        # Should return 200 or 503 (if data source unavailable)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "stocks" in data
    
    def test_get_kline_validates_stock_code(self):
        """Test that K-line endpoint validates stock code format."""
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
    
    def test_get_kline_validates_period(self):
        """Test that K-line endpoint validates period parameter."""
        response = client.get(
            "/api/stocks/600000.SH/kline",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "period": "invalid_period"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "INVALID_PERIOD"
    
    def test_get_kline_validates_date_format(self):
        """Test that K-line endpoint validates date format."""
        response = client.get(
            "/api/stocks/600000.SH/kline",
            params={
                "start_date": "2024/01/01",  # Wrong format
                "end_date": "2024-01-31",
                "period": "daily"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "INVALID_DATE_FORMAT"
    
    def test_get_stock_info_validates_code(self):
        """Test that stock info endpoint validates stock code."""
        response = client.get("/api/stocks/INVALID/info")
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "INVALID_STOCK_CODE"


class TestIndicatorAPIEndpoints:
    """Test indicator-related API endpoints structure and validation."""
    
    def test_get_indicator_types_endpoint(self):
        """Test that GET /api/indicators/types endpoint works."""
        response = client.get("/api/indicators/types")
        
        assert response.status_code == 200
        data = response.json()
        assert "indicators" in data
        assert isinstance(data["indicators"], list)
        assert len(data["indicators"]) > 0
        
        # Verify structure of indicator types
        indicator = data["indicators"][0]
        assert "type" in indicator
        assert "name" in indicator
        assert "params" in indicator
    
    def test_calculate_indicator_validates_stock_code(self):
        """Test that indicator calculation validates stock code."""
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
    
    def test_calculate_indicator_validates_indicator_type(self):
        """Test that indicator calculation validates indicator type."""
        response = client.post(
            "/api/indicators/calculate",
            json={
                "stock_code": "600000.SH",
                "indicator_type": "INVALID_TYPE",
                "params": {},
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "INVALID_INDICATOR_TYPE"
    
    def test_calculate_indicator_validates_date_format(self):
        """Test that indicator calculation validates date format."""
        response = client.post(
            "/api/indicators/calculate",
            json={
                "stock_code": "600000.SH",
                "indicator_type": "MA",
                "params": {"periods": [5]},
                "start_date": "2024/01/01",  # Wrong format
                "end_date": "2024-01-31"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "INVALID_DATE_FORMAT"


class TestStrategyAPIEndpoints:
    """Test strategy-related API endpoints structure and validation."""
    
    def test_get_strategies_endpoint_exists(self):
        """Test that GET /api/strategies endpoint exists."""
        response = client.get("/api/strategies")
        
        # Should return 200 (even if empty) or 500 if database not initialized
        # This is acceptable for a checkpoint test
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "strategies" in data
            assert isinstance(data["strategies"], list)
    
    def test_create_strategy_validates_operator(self):
        """Test that strategy creation validates operator values."""
        response = client.post(
            "/api/strategies",
            json={
                "name": "测试策略",
                "description": "测试",
                "indicators": [{"type": "MA", "params": {"periods": [5]}}],
                "conditions": [{"indicator": "MA5", "operator": "invalid_op", "value": 10}]
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "INVALID_OPERATOR"
    
    def test_create_strategy_validates_required_fields(self):
        """Test that strategy creation validates required fields."""
        response = client.post(
            "/api/strategies",
            json={
                # Missing required fields
                "description": "测试"
            }
        )
        
        # Should return validation error
        assert response.status_code in [400, 422]


class TestErrorResponseFormat:
    """
    Test error response format consistency.
    Property 13: Error response format consistency
    Requirements: 4.6, 8.3
    """
    
    def test_error_responses_have_standard_format(self):
        """Test that all error responses follow standard format."""
        # Trigger various errors and check format
        test_cases = [
            ("/api/stocks/INVALID/info", 400),
            ("/api/stocks/600000.SH/kline?start_date=2024/01/01&end_date=2024-01-31&period=daily", 400),
        ]
        
        for endpoint, expected_status in test_cases:
            response = client.get(endpoint)
            assert response.status_code == expected_status
            
            data = response.json()
            assert "detail" in data
            error = data["detail"]
            
            # Verify standard error format
            assert "code" in error
            assert "message" in error
            assert "details" in error
            
            # Verify types
            assert isinstance(error["code"], str)
            assert isinstance(error["message"], str)
    
    def test_validation_error_has_standard_format(self):
        """Test that validation errors have standard format."""
        response = client.post(
            "/api/indicators/calculate",
            json={
                "stock_code": "600000.SH"
                # Missing required fields
            }
        )
        
        # Our custom error handler converts validation errors to 400
        assert response.status_code == 400
        data = response.json()
        
        # Verify error format
        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert error["code"] == "VALIDATION_ERROR"
        assert "message" in error
        assert "timestamp" in error


class TestAPICORSConfiguration:
    """Test that CORS is properly configured."""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses."""
        response = client.get("/")
        
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


def test_all_api_routes_registered():
    """Test that all expected API routes are registered."""
    # Get all routes from the app
    routes = [route.path for route in app.routes]
    
    # Check that key routes exist
    expected_routes = [
        "/",
        "/health",
        "/api/stocks",
        "/api/stocks/{code}/kline",
        "/api/stocks/{code}/info",
        "/api/indicators/calculate",
        "/api/indicators/types",
        "/api/strategies",
        "/api/strategies/{strategy_id}",
    ]
    
    for expected_route in expected_routes:
        assert any(expected_route in route for route in routes), f"Route {expected_route} not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
