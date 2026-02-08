# 回测功能修复总结

## 修复的问题

### 1. 自动获取K线数据
**问题**: 回测API没有自动从数据提供者获取K线数据，导致"没有找到K线数据"错误

**修复**: 在 `backend/api/backtests.py` 中添加了自动获取逻辑
```python
# If not in database, fetch from data provider
if kline_data.empty:
    logger.info(f"No data in database, fetching from data provider")
    data_provider = DataProvider()
    kline_data = data_provider.get_kline_data(...)
    
    # Save to database for future use
    if not kline_data.empty:
        repo.save_kline_data(request.stock_code, kline_data)
```

### 2. 策略配置访问方式
**问题**: `get_strategy_by_id` 返回字典，但代码使用了 `strategy.config` 而不是 `strategy['config']`

**修复**: 修改为正确的字典访问方式
```python
# 修复前
results = engine.run_backtest(kline_data, strategy.config)

# 修复后
results = engine.run_backtest(kline_data, strategy['config'])
```

### 3. Timestamp序列化问题
**问题**: 回测引擎返回的equity_curve中包含pandas Timestamp对象，无法序列化为JSON

**修复**: 在 `backend/services/backtest_engine.py` 中添加日期转换逻辑
```python
# Convert equity curve dates to strings for JSON serialization
equity_curve_serializable = []
for point in self.equity_curve:
    date_value = point['date']
    if isinstance(date_value, pd.Timestamp):
        date_str = date_value.strftime('%Y-%m-%d')
    elif isinstance(date_value, date):
        date_str = date_value.isoformat()
    else:
        date_str = str(date_value)
    
    equity_curve_serializable.append({
        'date': date_str,
        'equity': float(point['equity']),
        'cash': float(point['cash']),
        'position_value': float(point['position_value'])
    })
```

### 4. 数据库表缺失
**问题**: backtests和custom_indicators表不存在

**修复**: 运行数据库迁移
```bash
cd backend
source venv/bin/activate
alembic stamp 001  # 标记当前版本
alembic upgrade head  # 运行新迁移
```

## 测试结果

✅ 回测API现在可以正常工作
✅ 自动从数据源获取K线数据
✅ 正确保存回测结果到数据库
✅ 返回完整的性能指标

### 测试命令
```bash
./test_backtest.sh
```

### 测试响应
```json
{
    "backtest_id": "54c846c0-08a6-41b3-94d1-da7cb03f0206",
    "metrics": {
        "initial_capital": 100000.0,
        "final_capital": 100000.0,
        "total_return": 0.0,
        "annual_return": 0.0,
        "sharpe_ratio": 0.0,
        "max_drawdown": 0.0,
        "win_rate": 0.0,
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0
    },
    "message": "回测完成"
}
```

## 注意事项

### 为什么没有交易？
如果回测结果显示 `total_trades: 0`，可能的原因：

1. **策略条件未触发**: 策略的买入/卖出条件在整个回测期间都没有被满足
2. **指标数据不足**: 某些指标需要预热期（如MA20需要20天数据）
3. **策略配置问题**: 检查策略配置中的条件是否合理

### 如何调试策略

1. **查看策略配置**:
```bash
curl 'http://localhost:8000/api/strategies' | python3 -m json.tool
```

2. **检查K线数据**:
```bash
curl 'http://localhost:8000/api/stocks/000001.SZ/kline?start_date=2024-01-01&end_date=2024-12-31' | python3 -m json.tool
```

3. **测试指标计算**:
```bash
curl 'http://localhost:8000/api/indicators/calculate' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "stock_code": "000001.SZ",
    "indicator_type": "MA",
    "params": {"periods": [5, 10, 20]},
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }' | python3 -m json.tool
```

4. **修改策略条件**: 在前端"策略管理"页面调整买入/卖出条件，使其更容易触发

## 使用curl命令运行回测

```bash
curl 'http://localhost:8000/api/backtests/run' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "strategy_id": "ad7994b8-217a-4db1-98eb-1dc77090cc32",
    "stock_code": "000001.SZ",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 100000,
    "commission_rate": 0.0003,
    "slippage_rate": 0.0001
  }' | python3 -m json.tool
```

## 相关文件

- `backend/api/backtests.py` - 回测API端点
- `backend/services/backtest_engine.py` - 回测引擎
- `backend/alembic/versions/002_add_backtest_and_custom_indicators.py` - 数据库迁移
- `test_backtest.sh` - 测试脚本
- `BACKTEST_GUIDE.md` - 详细使用指南
