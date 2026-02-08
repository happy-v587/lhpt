# 回测功能使用指南

## 问题修复

已修复回测API的两个问题：

1. **自动获取K线数据**: 如果数据库中没有数据，系统会自动从数据提供者获取
2. **策略配置访问**: 修复了字典访问方式的bug

## 使用方法

### 1. 快速测试

使用提供的测试脚本：

```bash
./test_backtest.sh
```

### 2. 手动测试

#### 2.1 运行回测

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

**参数说明：**
- `strategy_id`: 策略ID（必须先创建策略）
- `stock_code`: 股票代码（格式：000001.SZ 或 600000.SH）
- `start_date`: 开始日期（YYYY-MM-DD，不能是未来日期）
- `end_date`: 结束日期（YYYY-MM-DD，不能是未来日期）
- `initial_capital`: 初始资金（默认100000）
- `commission_rate`: 手续费率（默认0.0003，即0.03%）
- `slippage_rate`: 滑点率（默认0.0001，即0.01%）

**成功响应示例：**
```json
{
  "backtest_id": "uuid-string",
  "metrics": {
    "initial_capital": 100000.0,
    "final_capital": 105000.0,
    "total_return": 0.05,
    "annual_return": 0.05,
    "sharpe_ratio": 1.5,
    "max_drawdown": -0.08,
    "win_rate": 0.6,
    "total_trades": 20,
    "winning_trades": 12,
    "losing_trades": 8
  },
  "message": "回测完成"
}
```

#### 2.2 查看回测列表

```bash
# 查看所有回测
curl 'http://localhost:8000/api/backtests' | python3 -m json.tool

# 按策略ID筛选
curl 'http://localhost:8000/api/backtests?strategy_id=ad7994b8-217a-4db1-98eb-1dc77090cc32' | python3 -m json.tool
```

#### 2.3 查看回测详情

```bash
curl 'http://localhost:8000/api/backtests/{backtest_id}' | python3 -m json.tool
```

**详情响应包含：**
- 基本信息（策略ID、股票代码、日期范围等）
- 性能指标（收益率、夏普比率、最大回撤等）
- 交易记录（每笔交易的详细信息）
- 资金曲线（每日资金变化）

#### 2.4 删除回测

```bash
curl -X DELETE 'http://localhost:8000/api/backtests/{backtest_id}'
```

## 前端使用

在前端页面中：

1. **导航到回测页面**: 点击左侧菜单的"回测管理"
2. **运行回测**:
   - 选择策略
   - 选择股票
   - 设置日期范围
   - 配置资金和费率参数
   - 点击"运行回测"
3. **查看结果**:
   - 在"回测历史"标签页查看所有回测记录
   - 点击"查看详情"查看完整的回测报告
   - 查看交易记录和资金曲线图表

## 常见问题

### 1. "策略不存在"

**原因**: 提供的策略ID在数据库中不存在

**解决方法**:
```bash
# 查看所有策略
curl 'http://localhost:8000/api/strategies' | python3 -m json.tool

# 或在前端"策略管理"页面创建新策略
```

### 2. "没有找到K线数据"

**原因**: 
- 股票代码格式错误
- 日期范围是未来日期
- 数据源不可用

**解决方法**:
- 检查股票代码格式（必须是 6位数字.SH 或 6位数字.SZ）
- 使用历史日期（例如：2024-01-01 到 2024-12-31）
- 确保后端数据源配置正确

### 3. 日期范围选择

**注意事项**:
- 不能选择未来日期
- 建议使用至少3个月的数据进行回测
- 日期范围越长，回测结果越可靠
- 当前日期是 2026-02-08，所以可以使用 2024 年或 2025 年的数据

### 4. 性能指标说明

- **总收益率 (total_return)**: (最终资金 - 初始资金) / 初始资金
- **年化收益率 (annual_return)**: 按年计算的收益率
- **夏普比率 (sharpe_ratio)**: 风险调整后的收益率，越高越好（>1为良好）
- **最大回撤 (max_drawdown)**: 从峰值到谷底的最大跌幅（负值）
- **胜率 (win_rate)**: 盈利交易数 / 总交易数
- **交易次数 (total_trades)**: 总共执行的买卖次数

## 示例：完整的回测流程

```bash
# 1. 查看可用策略
curl 'http://localhost:8000/api/strategies' | python3 -m json.tool

# 2. 运行回测（使用2024年数据）
curl 'http://localhost:8000/api/backtests/run' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "strategy_id": "your-strategy-id",
    "stock_code": "000001.SZ",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 100000,
    "commission_rate": 0.0003,
    "slippage_rate": 0.0001
  }' | python3 -m json.tool

# 3. 查看回测详情（使用上一步返回的backtest_id）
curl 'http://localhost:8000/api/backtests/{backtest_id}' | python3 -m json.tool

# 4. 查看所有回测历史
curl 'http://localhost:8000/api/backtests' | python3 -m json.tool
```

## 技术细节

### 回测引擎特性

- ✅ 支持多种技术指标（MA、EMA、MACD、RSI、BOLL、KDJ等）
- ✅ 支持复杂的买卖条件组合
- ✅ 考虑手续费和滑点
- ✅ 计算夏普比率
- ✅ 记录完整的交易历史
- ✅ 生成资金曲线
- ✅ 自动从数据源获取K线数据

### 数据流程

1. 接收回测请求
2. 验证策略是否存在
3. 从数据库获取K线数据
4. 如果数据库没有，从数据提供者获取并保存
5. 运行回测引擎
6. 保存回测结果到数据库
7. 返回性能指标和回测ID
