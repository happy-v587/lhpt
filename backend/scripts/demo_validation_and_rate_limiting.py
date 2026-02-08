"""
Demonstration of K-line data validation and rate limiting features.

This script demonstrates:
1. K-line data validator rejecting invalid data
2. Rate limiting middleware protecting the API
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from validators.kline_validator import KLineDataValidator
from exceptions import DataValidationError


def demo_validator():
    """Demonstrate K-line data validator."""
    print("=" * 60)
    print("K-LINE DATA VALIDATOR DEMONSTRATION")
    print("=" * 60)
    
    # Example 1: Valid data
    print("\n1. Testing VALID K-line data:")
    valid_data = pd.DataFrame({
        'open': [10.0, 11.0, 12.0],
        'close': [10.5, 11.5, 12.5],
        'high': [11.0, 12.0, 13.0],
        'low': [9.5, 10.5, 11.5],
        'volume': [1000000, 1100000, 1200000]
    })
    print(valid_data)
    try:
        KLineDataValidator.validate_dataframe(valid_data)
        print("✅ Validation PASSED - Data is valid!")
    except DataValidationError as e:
        print(f"❌ Validation FAILED: {e.message}")
    
    # Example 2: Invalid data - negative price
    print("\n2. Testing INVALID K-line data (negative price):")
    invalid_data_1 = pd.DataFrame({
        'open': [10.0, -11.0, 12.0],  # Negative price!
        'close': [10.5, 11.5, 12.5],
        'high': [11.0, 12.0, 13.0],
        'low': [9.5, 10.5, 11.5],
        'volume': [1000000, 1100000, 1200000]
    })
    print(invalid_data_1)
    try:
        KLineDataValidator.validate_dataframe(invalid_data_1)
        print("✅ Validation PASSED")
    except DataValidationError as e:
        print(f"❌ Validation FAILED: {e.message}")
        print(f"   Details: {e.details}")
    
    # Example 3: Invalid data - high < low
    print("\n3. Testing INVALID K-line data (high < low):")
    invalid_data_2 = pd.DataFrame({
        'open': [10.0, 11.0, 12.0],
        'close': [10.5, 11.5, 12.5],
        'high': [11.0, 10.0, 13.0],  # high < low!
        'low': [9.5, 10.5, 11.5],
        'volume': [1000000, 1100000, 1200000]
    })
    print(invalid_data_2)
    try:
        KLineDataValidator.validate_dataframe(invalid_data_2)
        print("✅ Validation PASSED")
    except DataValidationError as e:
        print(f"❌ Validation FAILED: {e.message}")
        print(f"   Details: {e.details}")
    
    # Example 4: Stock code validation
    print("\n4. Testing stock code validation:")
    valid_codes = ['600000.SH', '000001.SZ']
    invalid_codes = ['60000.SH', '600000.XX', '600000']
    
    print("Valid codes:")
    for code in valid_codes:
        try:
            KLineDataValidator.validate_stock_code(code)
            print(f"  ✅ {code} - Valid")
        except DataValidationError as e:
            print(f"  ❌ {code} - Invalid: {e.message}")
    
    print("\nInvalid codes:")
    for code in invalid_codes:
        try:
            KLineDataValidator.validate_stock_code(code)
            print(f"  ✅ {code} - Valid")
        except DataValidationError as e:
            print(f"  ❌ {code} - Invalid: {e.message}")
    
    # Example 5: Date range validation
    print("\n5. Testing date range validation:")
    test_cases = [
        ('2023-01-01', '2023-12-31', 'Valid range'),
        ('2023-12-31', '2023-01-01', 'Start after end'),
        ('2023/01/01', '2023-12-31', 'Invalid format'),
    ]
    
    for start, end, description in test_cases:
        try:
            KLineDataValidator.validate_date_range(start, end)
            print(f"  ✅ {description}: {start} to {end} - Valid")
        except DataValidationError as e:
            print(f"  ❌ {description}: {start} to {end} - Invalid")
            print(f"     {e.message}")


def demo_rate_limiter_concept():
    """Demonstrate rate limiting concept."""
    print("\n" + "=" * 60)
    print("RATE LIMITING MIDDLEWARE DEMONSTRATION")
    print("=" * 60)
    
    print("\nRate Limiting Configuration:")
    print("  - Requests per minute: 60")
    print("  - Burst size: 10")
    print("  - Algorithm: Token Bucket")
    
    print("\nHow it works:")
    print("  1. Each client IP gets a token bucket")
    print("  2. Bucket starts with 10 tokens (burst size)")
    print("  3. Each request consumes 1 token")
    print("  4. Tokens refill at 1 token/second (60/minute)")
    print("  5. If no tokens available, request is rejected with HTTP 429")
    
    print("\nExample scenario:")
    print("  - Client makes 10 requests rapidly → All succeed (burst)")
    print("  - Client makes 11th request immediately → Rejected (no tokens)")
    print("  - Client waits 1 second → 1 token refilled")
    print("  - Client makes request → Succeeds")
    
    print("\nError response format (HTTP 429):")
    print("""  {
    "error": {
      "code": "RATE_LIMIT_EXCEEDED",
      "message": "请求过于频繁，请稍后再试",
      "details": "每分钟最多允许 60 个请求",
      "timestamp": "2024-01-01T10:00:00Z"
    }
  }""")
    
    print("\nResponse headers:")
    print("  - X-RateLimit-Limit: 60")
    print("  - X-RateLimit-Remaining: 0")
    print("  - Retry-After: 60")
    
    print("\nExempt endpoints (no rate limiting):")
    print("  - / (root)")
    print("  - /health (health check)")


if __name__ == "__main__":
    demo_validator()
    demo_rate_limiter_concept()
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nTo test rate limiting in action:")
    print("  1. Start the API server: uvicorn main:app --reload")
    print("  2. Make rapid requests to any endpoint")
    print("  3. Observe HTTP 429 responses after burst limit")
