"""
Tests for rate limiting middleware.

Requirements: 8.4
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import time
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from middleware.rate_limiter import RateLimiterMiddleware, TokenBucket


class TestTokenBucket:
    """Test suite for TokenBucket."""
    
    def test_token_bucket_initialization(self):
        """Test token bucket is initialized with full capacity."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        assert bucket.tokens == 10
        assert bucket.capacity == 10
        assert bucket.refill_rate == 1.0
    
    def test_token_bucket_consume_success(self):
        """Test consuming tokens when available."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        # Should succeed
        assert bucket.consume(5) is True
        assert bucket.tokens == 5
    
    def test_token_bucket_consume_failure(self):
        """Test consuming tokens when not enough available."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        # Consume all tokens
        bucket.consume(10)
        
        # Should fail (tokens might be slightly above 0 due to refill)
        assert bucket.consume(1) is False
        assert bucket.tokens < 1
    
    def test_token_bucket_refill(self):
        """Test tokens are refilled over time."""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)  # 10 tokens per second
        
        # Consume all tokens
        bucket.consume(10)
        assert bucket.tokens == 0
        
        # Wait for refill
        time.sleep(0.5)  # Should add ~5 tokens
        
        # Should be able to consume some tokens
        assert bucket.consume(4) is True
    
    def test_token_bucket_max_capacity(self):
        """Test tokens don't exceed capacity."""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)
        
        # Wait for potential refill
        time.sleep(1.0)
        
        # Should still be at capacity
        assert bucket.tokens <= 10


class TestRateLimiterMiddleware:
    """Test suite for RateLimiterMiddleware."""
    
    def test_rate_limiter_allows_requests_within_limit(self):
        """Test requests within rate limit are allowed."""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        # Add rate limiter with high limit
        app.add_middleware(
            RateLimiterMiddleware,
            requests_per_minute=60,
            burst_size=10
        )
        
        client = TestClient(app)
        
        # Make requests within limit
        for _ in range(5):
            response = client.get("/test")
            assert response.status_code == 200
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
    
    def test_rate_limiter_blocks_requests_exceeding_limit(self):
        """Test requests exceeding rate limit are blocked."""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        # Add rate limiter with very low limit
        app.add_middleware(
            RateLimiterMiddleware,
            requests_per_minute=5,
            burst_size=3
        )
        
        client = TestClient(app)
        
        # Make requests up to burst size
        for i in range(3):
            response = client.get("/test")
            assert response.status_code == 200, f"Request {i+1} should succeed"
        
        # Next request should be rate limited
        response = client.get("/test")
        assert response.status_code == 429
        assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert "Retry-After" in response.headers
    
    def test_rate_limiter_skips_health_check(self):
        """Test rate limiter skips health check endpoints."""
        app = FastAPI()
        
        @app.get("/")
        async def root():
            return {"message": "root"}
        
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        # Add rate limiter with very low limit
        app.add_middleware(
            RateLimiterMiddleware,
            requests_per_minute=5,
            burst_size=2
        )
        
        client = TestClient(app)
        
        # Exhaust rate limit on /test
        client.get("/test")
        client.get("/test")
        
        # Health check should still work
        response = client.get("/health")
        assert response.status_code == 200
        
        # Root should still work
        response = client.get("/")
        assert response.status_code == 200
    
    def test_rate_limiter_error_response_format(self):
        """Test rate limiter returns properly formatted error response."""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        app.add_middleware(
            RateLimiterMiddleware,
            requests_per_minute=5,
            burst_size=1
        )
        
        client = TestClient(app)
        
        # Exhaust rate limit
        client.get("/test")
        
        # Get rate limited response
        response = client.get("/test")
        assert response.status_code == 429
        
        # Check error format
        error_data = response.json()
        assert "error" in error_data
        assert "code" in error_data["error"]
        assert "message" in error_data["error"]
        assert "details" in error_data["error"]
        assert "timestamp" in error_data["error"]
        
        # Check headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert response.headers["X-RateLimit-Remaining"] == "0"
