"""
Cache service for improving performance.
Supports both in-memory caching and Redis (optional).

Requirements: 10.3
Property 16: 缓存一致性
"""

import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """
    Cache service that supports both in-memory and Redis caching.
    Falls back to in-memory cache if Redis is not available.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize cache service.
        
        Args:
            redis_url: Redis connection URL (optional)
        """
        self.redis_client = None
        self.memory_cache = {}
        
        # Try to initialize Redis if URL is provided
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis, falling back to memory cache: {e}")
                self.redis_client = None
        else:
            logger.info("Using in-memory cache (Redis not configured)")
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate a cache key from function arguments.
        
        Args:
            prefix: Cache key prefix
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Cache key string
        """
        # Create a string representation of arguments
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                # For complex objects, use hash
                key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
        
        # Add keyword arguments (sorted for consistency)
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}={v}")
            else:
                key_parts.append(f"{k}={hashlib.md5(str(v).encode()).hexdigest()[:8]}")
        
        return ":".join(key_parts)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with optional TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.redis_client:
                serialized = json.dumps(value, default=str)
                if ttl:
                    self.redis_client.setex(key, ttl, serialized)
                else:
                    self.redis_client.set(key, serialized)
            else:
                # In-memory cache doesn't support TTL expiration
                # In production, consider using cachetools for TTL support
                self.memory_cache[key] = value
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache keys matching a pattern.
        
        Args:
            pattern: Pattern to match (e.g., "stock:600000*")
        
        Returns:
            Number of keys deleted
        """
        count = 0
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    count = self.redis_client.delete(*keys)
            else:
                # For memory cache, match keys manually
                keys_to_delete = [
                    k for k in self.memory_cache.keys()
                    if self._match_pattern(k, pattern)
                ]
                for key in keys_to_delete:
                    self.memory_cache.pop(key, None)
                count = len(keys_to_delete)
        except Exception as e:
            logger.error(f"Error invalidating pattern {pattern}: {e}")
        
        return count
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """
        Simple pattern matching for memory cache.
        
        Args:
            key: Cache key
            pattern: Pattern with * wildcard
        
        Returns:
            True if key matches pattern
        """
        if '*' not in pattern:
            return key == pattern
        
        # Simple wildcard matching
        parts = pattern.split('*')
        if len(parts) == 2:
            prefix, suffix = parts
            return key.startswith(prefix) and key.endswith(suffix)
        
        return False


def cached(
    prefix: str,
    ttl: int = 300,
    cache_service: Optional[CacheService] = None
):
    """
    Decorator for caching function results.
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (default: 300 = 5 minutes)
        cache_service: CacheService instance (optional)
    
    Example:
        @cached(prefix="stock_list", ttl=600)
        def get_stock_list():
            # Expensive operation
            return fetch_stocks()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Skip caching if no cache service provided
            if cache_service is None:
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key = cache_service._generate_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_value
            
            # Cache miss - call function
            logger.debug(f"Cache miss for key: {cache_key}")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_service.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


# Global cache service instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """
    Get the global cache service instance.
    
    Returns:
        CacheService instance
    """
    global _cache_service
    if _cache_service is None:
        from config import settings
        _cache_service = CacheService(redis_url=settings.redis_url)
    return _cache_service
