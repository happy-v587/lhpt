# Performance Optimization Implementation

This document describes the performance optimizations implemented in the A-share quantitative trading system.

## Overview

The system implements two main performance optimization strategies:
1. **Data Caching** - Reduces database queries and external API calls
2. **Database Query Optimization** - Improves database performance through indexing and batch operations

## 1. Data Caching Mechanism

### Implementation

The caching system is implemented in `services/cache_service.py` and supports two modes:

#### In-Memory Cache (Default)
- Uses Python dictionaries for fast in-process caching
- No external dependencies required
- Suitable for single-server deployments
- Cache is lost on server restart

#### Redis Cache (Optional)
- Distributed caching using Redis
- Suitable for multi-server deployments
- Persistent cache across server restarts
- Requires Redis server installation

### Configuration

Configure caching in `.env` file:

```bash
# Enable/disable caching
CACHE_ENABLED=True

# Redis URL (leave empty for in-memory cache)
REDIS_URL=
# For Redis: REDIS_URL=redis://localhost:6379/0

# Cache TTL settings (in seconds)
CACHE_TTL_STOCK_LIST=600      # 10 minutes
CACHE_TTL_KLINE_DATA=300      # 5 minutes
CACHE_TTL_INDICATORS=300      # 5 minutes
```

### Cached Endpoints

The following API endpoints implement caching:

1. **GET /api/stocks** - Stock list
   - Cache key: `stock_list`
   - TTL: 10 minutes (configurable)

2. **GET /api/stocks/{code}/kline** - K-line data
   - Cache key: `kline:{code}:{start_date}:{end_date}:{period}`
   - TTL: 5 minutes (configurable)

3. **POST /api/indicators/calculate** - Technical indicators
   - Cache key: `indicator:{code}:{type}:{params}:{start_date}:{end_date}`
   - TTL: 5 minutes (configurable)

### Cache Invalidation

The system implements automatic cache invalidation to ensure data consistency (Property 16):

- When K-line data is updated via `save_kline_data()`, the cache is automatically invalidated for:
  - All K-line data for that stock: `kline:{stock_code}:*`
  - All indicators for that stock: `indicator:{stock_code}:*`

This ensures that subsequent requests always receive fresh data after updates.

### Usage Example

```python
from services.cache_service import get_cache_service

# Get cache service instance
cache = get_cache_service()

# Manual cache operations
cache.set("my_key", {"data": "value"}, ttl=300)
value = cache.get("my_key")
cache.delete("my_key")

# Pattern-based invalidation
cache.invalidate_pattern("stock:600000:*")
```

## 2. Database Query Optimization

### Indexes

The system creates the following indexes for optimal query performance:

#### KLineData Table
- `idx_kline_stock_date` - Composite index on (stock_code, trade_date)
  - Optimizes queries filtering by stock and date range
- `idx_kline_date` - Index on trade_date
  - Optimizes queries filtering by date only
- `uix_stock_date_period` - Unique constraint on (stock_code, trade_date, period)
  - Prevents duplicate records and speeds up upsert operations

#### Strategy Table
- `idx_strategies_created` - Index on created_at
  - Optimizes queries ordering by creation time

### Batch Operations

The data repository implements batch operations for better performance:

#### Batch Insert with Commit Batching
```python
# save_kline_data() commits in batches of 100 records
repo.save_kline_data(stock_code, large_dataframe)
```

#### Bulk Save for Multiple Stocks
```python
# More efficient than calling save_kline_data multiple times
data_by_stock = {
    "600000.SH": df1,
    "000001.SZ": df2,
    # ... more stocks
}
repo.bulk_save_kline_data(data_by_stock)
```

### Verification

Run the index verification script to ensure all indexes are properly created:

```bash
cd backend
python verify_indexes.py
```

Expected output:
```
✓ Index idx_kline_stock_date exists
✓ Index idx_kline_date exists
✓ Unique constraint uix_stock_date_period exists
✓ Index idx_strategies_created exists
```

## Performance Metrics

### Expected Improvements

With caching enabled:
- **Stock list queries**: ~90% reduction in response time (cached responses)
- **K-line data queries**: ~80% reduction for repeated queries
- **Indicator calculations**: ~85% reduction for repeated calculations

With database optimization:
- **K-line data queries**: 3-5x faster with proper indexes
- **Batch inserts**: 10-20x faster than individual inserts

## Testing

The implementation includes comprehensive tests:

### Unit Tests
- `tests/test_cache_service.py` - Cache service functionality
  - Basic operations (get, set, delete)
  - Complex data structures
  - Pattern-based invalidation
  - Cache consistency (Property 16)

### Integration Tests
- `tests/test_cache_integration.py` - Cache integration with API
  - K-line data caching
  - Cache invalidation on data update
  - Indicator caching

Run tests:
```bash
cd backend
python -m pytest tests/test_cache_service.py tests/test_cache_integration.py -v
```

## Requirements Satisfied

This implementation satisfies the following requirements:

- **Requirement 10.3**: Cache mechanism for frequently queried data
- **Requirement 10.5**: Database query optimization with indexes and batch operations
- **Property 16**: Cache consistency - ensures cached data is invalidated when underlying data changes

## Future Enhancements

Potential improvements for future versions:

1. **Cache warming** - Pre-populate cache with frequently accessed data
2. **Cache statistics** - Track hit/miss rates for monitoring
3. **Adaptive TTL** - Adjust TTL based on data update frequency
4. **Query result caching** - Cache complex query results at the database level
5. **Connection pooling** - Implement database connection pooling for better concurrency
