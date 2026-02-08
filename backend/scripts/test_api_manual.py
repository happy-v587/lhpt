"""
Manual API testing script to verify endpoints work correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    print("\n=== Testing Root Endpoint ===")
    response = client.get("/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 200


def test_health():
    """Test health check endpoint."""
    print("\n=== Testing Health Check Endpoint ===")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 200


def test_indicator_types():
    """Test indicator types endpoint."""
    print("\n=== Testing Indicator Types Endpoint ===")
    response = client.get("/api/indicators/types")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Number of indicators: {len(data['indicators'])}")
    for indicator in data['indicators']:
        print(f"  - {indicator['type']}: {indicator['name']}")
    assert response.status_code == 200
    assert len(data['indicators']) == 4


def test_strategies_empty():
    """Test strategies endpoint (should be empty initially)."""
    print("\n=== Testing Strategies Endpoint (Empty) ===")
    response = client.get("/api/strategies")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 200


def test_create_strategy():
    """Test creating a strategy."""
    print("\n=== Testing Create Strategy Endpoint ===")
    strategy_data = {
        "name": "测试策略",
        "description": "这是一个测试策略",
        "indicators": [
            {
                "type": "MA",
                "params": {"periods": [5, 20]}
            }
        ],
        "conditions": [
            {
                "indicator": "MA5",
                "operator": "cross_up",
                "value": "MA20"
            }
        ]
    }
    response = client.post("/api/strategies", json=strategy_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    return response.json()['id']


def test_get_strategy(strategy_id):
    """Test getting a specific strategy."""
    print(f"\n=== Testing Get Strategy Endpoint (ID: {strategy_id}) ===")
    response = client.get(f"/api/strategies/{strategy_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 200


def test_delete_strategy(strategy_id):
    """Test deleting a strategy."""
    print(f"\n=== Testing Delete Strategy Endpoint (ID: {strategy_id}) ===")
    response = client.delete(f"/api/strategies/{strategy_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 200


def test_invalid_stock_code():
    """Test invalid stock code validation."""
    print("\n=== Testing Invalid Stock Code Validation ===")
    response = client.get("/api/stocks/INVALID/kline?start_date=2024-01-01&end_date=2024-01-31")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 400
    assert "INVALID_STOCK_CODE" in response.json()['detail']['code']


def test_invalid_date_format():
    """Test invalid date format validation."""
    print("\n=== Testing Invalid Date Format Validation ===")
    response = client.get("/api/stocks/600000.SH/kline?start_date=2024/01/01&end_date=2024-01-31")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 400
    assert "INVALID_DATE_FORMAT" in response.json()['detail']['code']


if __name__ == "__main__":
    print("=" * 60)
    print("API Manual Testing")
    print("=" * 60)
    
    try:
        # Basic endpoints
        test_root()
        test_health()
        test_indicator_types()
        
        # Strategy management
        test_strategies_empty()
        strategy_id = test_create_strategy()
        test_get_strategy(strategy_id)
        test_delete_strategy(strategy_id)
        
        # Validation tests
        test_invalid_stock_code()
        test_invalid_date_format()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
