# 量化交易系统 - 新增功能说明

## 概述

本次更新为量化交易系统添加了以下核心功能：

1. **夏普比率计算** - 评估策略风险调整后收益
2. **回测引擎** - 完整的策略回测功能
3. **策略与指标关联** - 策略配置中包含指标定义
4. **扩展指标系统** - 从 4 个指标扩展到 12 个，并支持自定义公式

---

## 1. 夏普比率计算

### 功能说明
夏普比率（Sharpe Ratio）是衡量投资组合风险调整后收益的重要指标。

### 计算公式
```
Sharpe Ratio = (策略收益率 - 无风险收益率) / 策略收益率标准差 * √252
```

### 使用方式
夏普比率会在回测结果中自动计算并返回。

### API 示例
```bash
POST /api/backtests/run
{
  "strategy_id": "xxx",
  "stock_code": "600000.SH",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 100000
}

# 响应包含
{
  "metrics": {
    "sharpe_ratio": 1.85,
    "annual_return": 0.25,
    "max_drawdown": -0.15,
    ...
  }
}
```

---

## 2. 回测引擎

### 功能特性
- ✅ 完整的交易模拟（买入/卖出）
- ✅ 手续费和滑点计算
- ✅ 资金曲线跟踪
- ✅ 多维度性能指标
- ✅ 交易记录详情

### 性能指标
- **总收益率** - 策略总体收益
- **年化收益率** - 按年计算的收益率
- **夏普比率** - 风险调整后收益
- **最大回撤** - 最大资金回撤幅度
- **胜率** - 盈利交易占比
- **交易次数** - 总交易次数统计

### API 端点

#### 运行回测
```bash
POST /api/backtests/run
Content-Type: application/json

{
  "strategy_id": "strategy-uuid",
  "stock_code": "600000.SH",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 100000.0,
  "commission_rate": 0.0003,
  "slippage_rate": 0.0001
}
```

#### 获取回测列表
```bash
GET /api/backtests?strategy_id=xxx
```

#### 获取回测详情
```bash
GET /api/backtests/{backtest_id}
```

#### 删除回测
```bash
DELETE /api/backtests/{backtest_id}
```

### 使用示例

```python
# 1. 创建策略
strategy = {
    "name": "MA交叉策略",
    "indicators": [
        {
            "type": "MA",
            "params": {"periods": [5, 20]}
        }
    ],
    "conditions": [
        {
            "indicator": "MA5",
            "operator": ">",
            "value": "MA20",
            "action": "buy"
        },
        {
            "indicator": "MA5",
            "operator": "<",
            "value": "MA20",
            "action": "sell"
        }
    ]
}

# 2. 运行回测
backtest_result = run_backtest(
    strategy_id=strategy_id,
    stock_code="600000.SH",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# 3. 查看结果
print(f"夏普比率: {backtest_result['metrics']['sharpe_ratio']}")
print(f"年化收益: {backtest_result['metrics']['annual_return']}")
print(f"最大回撤: {backtest_result['metrics']['max_drawdown']}")
```

---

## 3. 策略与指标关联

### 功能说明
策略配置现在完整包含指标定义和交易条件，实现了策略与指标的紧密关联。

### 策略配置结构

```json
{
  "name": "MACD金叉策略",
  "description": "基于MACD金叉死叉的交易策略",
  "indicators": [
    {
      "type": "MACD",
      "params": {
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9
      }
    },
    {
      "type": "RSI",
      "params": {
        "period": 14
      }
    }
  ],
  "conditions": [
    {
      "indicator": "DIF",
      "operator": ">",
      "value": "DEA",
      "action": "buy"
    },
    {
      "indicator": "RSI",
      "operator": "<",
      "value": 30,
      "action": "buy"
    },
    {
      "indicator": "DIF",
      "operator": "<",
      "value": "DEA",
      "action": "sell"
    }
  ]
}
```

### 支持的操作符
- `>` - 大于
- `<` - 小于
- `>=` - 大于等于
- `<=` - 小于等于
- `==` - 等于

### 条件逻辑
- 同一 action 的多个条件使用 **AND** 逻辑（全部满足才触发）
- 买入和卖出条件独立评估

---

## 4. 扩展指标系统

### 4.1 内置指标（从 4 个扩展到 12 个）

#### 原有指标
1. **MA** - 移动平均线
2. **MACD** - 指数平滑异同移动平均线
3. **RSI** - 相对强弱指标
4. **BOLL** - 布林带

#### 新增指标
5. **EMA** - 指数移动平均线
6. **KDJ** - 随机指标
7. **CCI** - 顺势指标
8. **ATR** - 平均真实波幅
9. **OBV** - 能量潮指标
10. **WR** - 威廉指标
11. **DMI** - 趋向指标
12. **VWAP** - 成交量加权平均价

### 4.2 自定义公式机制

#### 功能特性
- ✅ 安全的公式评估（无代码注入风险）
- ✅ 支持数学运算和技术分析函数
- ✅ 公式验证和语法检查
- ✅ 参数化配置

#### 支持的函数

**数学函数**
- `abs()` - 绝对值
- `sqrt()` - 平方根
- `log()` - 对数
- `exp()` - 指数
- `pow()` - 幂运算

**聚合函数**
- `sum(x, n)` - n 期求和
- `avg(x, n)` - n 期平均
- `max(x, n)` - n 期最大值
- `min(x, n)` - n 期最小值
- `std(x, n)` - n 期标准差

**技术函数**
- `ema(x, n)` - 指数移动平均
- `sma(x, n)` - 简单移动平均
- `ref(x, n)` - 引用 n 期前的值
- `cross(a, b)` - 交叉判断
- `cross_up(a, b)` - 上穿判断
- `cross_down(a, b)` - 下穿判断

**数据变量**
- `OPEN` / `open` - 开盘价
- `CLOSE` / `close` - 收盘价
- `HIGH` / `high` - 最高价
- `LOW` / `low` - 最低价
- `VOLUME` / `volume` - 成交量

#### 公式示例

```python
# 1. Z-Score 指标
formula = "(CLOSE - SMA(CLOSE, 20)) / STD(CLOSE, 20)"

# 2. 价格动量
formula = "CLOSE / REF(CLOSE, 10) - 1"

# 3. 成交量比率
formula = "VOLUME / AVG(VOLUME, 20)"

# 4. 自定义布林带
formula = "SMA(CLOSE, 20) + 2.5 * STD(CLOSE, 20)"

# 5. 金叉信号
formula = "CROSS_UP(SMA(CLOSE, 5), SMA(CLOSE, 20))"
```

### 4.3 自定义指标 API

#### 创建自定义指标
```bash
POST /api/custom-indicators
Content-Type: application/json

{
  "name": "zscore",
  "display_name": "Z-Score",
  "description": "价格标准化指标",
  "indicator_type": "formula",
  "formula": "(CLOSE - SMA(CLOSE, period)) / STD(CLOSE, period)",
  "params": [
    {
      "name": "period",
      "type": "int",
      "default": 20,
      "description": "计算周期"
    }
  ]
}
```

#### 验证公式
```bash
POST /api/custom-indicators/validate-formula
Content-Type: application/json

{
  "formula": "(CLOSE - SMA(CLOSE, 20)) / STD(CLOSE, 20)"
}

# 响应
{
  "valid": true,
  "message": "公式语法正确"
}
```

#### 获取自定义指标列表
```bash
GET /api/custom-indicators?active_only=true
```

#### 计算自定义指标
```bash
POST /api/custom-indicators/calculate
Content-Type: application/json

{
  "indicator_id": "indicator-uuid",
  "stock_code": "600000.SH",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "params": {
    "period": 20
  }
}
```

#### 删除自定义指标
```bash
DELETE /api/custom-indicators/{indicator_id}
```

---

## 5. 数据库变更

### 新增表

#### custom_indicators 表
```sql
CREATE TABLE custom_indicators (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    indicator_type VARCHAR(20) DEFAULT 'formula',
    formula TEXT,
    params JSON NOT NULL,
    plugin_module VARCHAR(200),
    plugin_class VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### backtests 表
```sql
CREATE TABLE backtests (
    id VARCHAR(36) PRIMARY KEY,
    strategy_id VARCHAR(36) NOT NULL,
    stock_code VARCHAR(10) NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    initial_capital DECIMAL(20, 2) NOT NULL,
    commission_rate DECIMAL(10, 6) DEFAULT 0.0003,
    slippage_rate DECIMAL(10, 6) DEFAULT 0.0001,
    final_capital DECIMAL(20, 2),
    total_return DECIMAL(10, 4),
    annual_return DECIMAL(10, 4),
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    win_rate DECIMAL(10, 4),
    total_trades INTEGER,
    trades JSON,
    equity_curve JSON,
    metrics JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (strategy_id) REFERENCES strategies(id)
);
```

### 迁移命令
```bash
cd backend
alembic upgrade head
```

---

## 6. 完整使用流程示例

### 步骤 1: 创建自定义指标
```python
# 创建 Z-Score 指标
custom_indicator = {
    "name": "zscore",
    "display_name": "Z-Score",
    "formula": "(CLOSE - SMA(CLOSE, period)) / STD(CLOSE, period)",
    "params": [{"name": "period", "type": "int", "default": 20}]
}
```

### 步骤 2: 创建策略
```python
strategy = {
    "name": "均值回归策略",
    "indicators": [
        {"type": "MA", "params": {"periods": [20]}},
        # 可以引用自定义指标
    ],
    "conditions": [
        {"indicator": "MA20", "operator": ">", "value": "close", "action": "buy"},
        {"indicator": "MA20", "operator": "<", "value": "close", "action": "sell"}
    ]
}
```

### 步骤 3: 运行回测
```python
backtest = {
    "strategy_id": strategy_id,
    "stock_code": "600000.SH",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 100000
}
```

### 步骤 4: 分析结果
```python
# 查看关键指标
print(f"夏普比率: {result['sharpe_ratio']:.2f}")
print(f"年化收益: {result['annual_return']:.2%}")
print(f"最大回撤: {result['max_drawdown']:.2%}")
print(f"胜率: {result['win_rate']:.2%}")

# 查看交易记录
for trade in result['trades']:
    print(f"{trade['date']}: {trade['action']} {trade['shares']} @ {trade['price']}")

# 绘制资金曲线
import matplotlib.pyplot as plt
dates = [e['date'] for e in result['equity_curve']]
equity = [e['equity'] for e in result['equity_curve']]
plt.plot(dates, equity)
plt.show()
```

---

## 7. 安全性说明

### 自定义公式安全措施
1. **禁止代码注入** - 不允许 `import`, `exec`, `eval` 等危险操作
2. **沙箱执行** - 公式在受限环境中执行
3. **函数白名单** - 只允许预定义的安全函数
4. **语法验证** - 创建前验证公式语法

### 回测安全
1. **数据隔离** - 回测使用历史数据，不影响实盘
2. **资源限制** - 防止过长时间的回测占用资源
3. **参数验证** - 严格验证所有输入参数

---

## 8. 性能优化建议

1. **缓存策略** - 指标计算结果会被缓存
2. **批量回测** - 可以并行运行多个回测
3. **数据预加载** - 提前加载常用股票数据
4. **索引优化** - 数据库表已添加必要索引

---

## 9. 后续扩展方向

### 短期计划
- [ ] 实时交易执行
- [ ] 风险管理模块（止损/止盈）
- [ ] 多股票组合回测
- [ ] 策略优化器（参数寻优）

### 中期计划
- [ ] 机器学习指标
- [ ] 因子分析
- [ ] 事件驱动策略
- [ ] WebSocket 实时数据

### 长期计划
- [ ] 分布式回测
- [ ] 高频交易支持
- [ ] 期货/期权支持
- [ ] 社区策略市场

---

## 10. 常见问题

### Q: 如何提高回测速度？
A: 使用较短的时间范围，减少指标数量，或使用缓存。

### Q: 自定义公式有长度限制吗？
A: 建议公式长度不超过 1000 字符，过长的公式可能影响性能。

### Q: 夏普比率多少算好？
A: 一般认为 > 1 为良好，> 2 为优秀，> 3 为卓越。

### Q: 回测结果能代表实盘表现吗？
A: 回测是历史模拟，实盘会受到滑点、流动性等因素影响，结果仅供参考。

---

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
