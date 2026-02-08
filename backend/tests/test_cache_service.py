"""
Tests for cache service functionality.

Requirements: 10.3
Property 16: 缓存一致性
"""

import pytest
from services.cache_service import CacheService


def test_memory_cache_basic_operations():
    """Test basic cache operations with in-memory cache."""
    cache = CacheService(redis_url=None)  # Use memory cache
    
    # Test set and get
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"
    
    # Test get non-existent key
    assert cache.get("non_existent") is None
    
    # Test delete
    cache.delete("test_key")
    assert cache.get("test_key") is None


def test_memory_cache_complex_values():
    """Test caching complex data structures."""
    cache = CacheService(redis_url=None)
    
    # Test dict
    test_dict = {"name": "Test", "value": 123, "nested": {"key": "value"}}
    cache.set("dict_key", test_dict)
    assert cache.get("dict_key") == test_dict
    
    # Test list
    test_list = [1, 2, 3, "four", {"five": 5}]
    cache.set("list_key", test_list)
    assert cache.get("list_key") == test_list


def test_cache_invalidate_pattern():
    """Test pattern-based cache invalidation."""
    cache = CacheService(redis_url=None)
    
    # Set multiple keys
    cache.set("stock:600000:data", "data1")
    cache.set("stock:600000:info", "info1")
    cache.set("stock:000001:data", "data2")
    cache.set("other:key", "other")
    
    # Invalidate pattern
    count = cache.invalidate_pattern("stock:600000:*")
    assert count == 2
    
    # Check keys are deleted
    assert cache.get("stock:600000:data") is None
    assert cache.get("stock:600000:info") is None
    
    # Check other keys still exist
    assert cache.get("stock:000001:data") == "data2"
    assert cache.get("other:key") == "other"


def test_cache_clear():
    """Test clearing all cache entries."""
    cache = CacheService(redis_url=None)
    
    # Set multiple keys
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    
    # Clear cache
    cache.clear()
    
    # Check all keys are deleted
    assert cache.get("key1") is None
    assert cache.get("key2") is None
    assert cache.get("key3") is None


def test_cache_key_generation():
    """Test cache key generation from function arguments."""
    cache = CacheService(redis_url=None)
    
    # Test with simple arguments
    key1 = cache._generate_cache_key("prefix", "arg1", "arg2", param1="value1")
    key2 = cache._generate_cache_key("prefix", "arg1", "arg2", param1="value1")
    assert key1 == key2  # Same arguments should generate same key
    
    # Test with different arguments
    key3 = cache._generate_cache_key("prefix", "arg1", "arg3", param1="value1")
    assert key1 != key3  # Different arguments should generate different keys


def test_cache_consistency_on_update():
    """
    Test cache consistency when data is updated.
    
    Property 16: 缓存一致性
    For any cached data, when the underlying database data is updated,
    subsequent reads should return the updated data, not stale cache values.
    """
    cache = CacheService(redis_url=None)
    
    # Simulate initial cache
    stock_code = "600000.SH"
    cache_key = f"kline:{stock_code}:2024-01-01:2024-01-31:daily"
    initial_data = {"code": stock_code, "data": [{"date": "2024-01-01", "close": 10.0}]}
    cache.set(cache_key, initial_data)
    
    # Verify cached data
    assert cache.get(cache_key) == initial_data
    
    # Simulate data update - invalidate cache
    cache.invalidate_pattern(f"kline:{stock_code}:*")
    
    # Verify cache is cleared
    assert cache.get(cache_key) is None
    
    # Simulate new data being cached
    updated_data = {"code": stock_code, "data": [{"date": "2024-01-01", "close": 11.0}]}
    cache.set(cache_key, updated_data)
    
    # Verify updated data is returned
    assert cache.get(cache_key) == updated_data
    assert cache.get(cache_key)["data"][0]["close"] == 11.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
