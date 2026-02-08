"""
Rate limiting middleware using token bucket algorithm.

Requirements: 8.4
Implements request rate limiting to protect the system from overload.
"""

import time
from typing import Dict, Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import threading


class TokenBucket:
    """
    Token bucket implementation for rate limiting.
    
    The token bucket algorithm allows for burst traffic while maintaining
    an average rate limit over time.
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize the token bucket.
        
        Args:
            capacity: Maximum number of tokens in the bucket
            refill_rate: Number of tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if not enough tokens available
        """
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm.
    
    Limits the number of requests per client IP address to prevent
    system overload and abuse.
    
    Requirements: 8.4
    """
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_size: int = 10
    ):
        """
        Initialize the rate limiter middleware.
        
        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests per minute per IP
            burst_size: Maximum burst size (bucket capacity)
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.refill_rate = requests_per_minute / 60.0  # tokens per second
        
        # Store token buckets per client IP
        self.buckets: Dict[str, TokenBucket] = {}
        self.buckets_lock = threading.Lock()
        
        # Cleanup old buckets periodically
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client IP address
        """
        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _get_bucket(self, client_ip: str) -> TokenBucket:
        """
        Get or create a token bucket for a client IP.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            TokenBucket instance for the client
        """
        with self.buckets_lock:
            if client_ip not in self.buckets:
                self.buckets[client_ip] = TokenBucket(
                    capacity=self.burst_size,
                    refill_rate=self.refill_rate
                )
            return self.buckets[client_ip]
    
    def _cleanup_old_buckets(self):
        """Remove inactive buckets to prevent memory leaks."""
        now = time.time()
        
        # Only cleanup periodically
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        with self.buckets_lock:
            # Remove buckets that haven't been used recently
            inactive_threshold = now - 600  # 10 minutes
            to_remove = [
                ip for ip, bucket in self.buckets.items()
                if bucket.last_refill < inactive_threshold
            ]
            
            for ip in to_remove:
                del self.buckets[ip]
            
            self.last_cleanup = now
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request with rate limiting.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            Response object
        """
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/", "/health"]:
            return await call_next(request)
        
        # Get client IP and token bucket
        client_ip = self._get_client_ip(request)
        bucket = self._get_bucket(client_ip)
        
        # Try to consume a token
        if not bucket.consume(1):
            # Rate limit exceeded
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "请求过于频繁，请稍后再试",
                        "details": f"每分钟最多允许 {self.requests_per_minute} 个请求",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60"
                }
            )
        
        # Cleanup old buckets periodically
        self._cleanup_old_buckets()
        
        # Add rate limit headers to response
        response = await call_next(request)
        
        # Calculate remaining tokens
        remaining = int(bucket.tokens)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
