# 量化交易系统升级总结

## 新增功能概览

本次升级为系统添加了 4 大核心功能模块，解决了您提出的所有问题。

---

## ✅ 1. 夏普比率计算

**位置**: `backend/services/backtest_engine.py`

**功能**: 在回测结果中自动计算夏普比率，评估策略的风险调整后收益。

**计算公式**:
```
Sharpe Ratio = (策略收益率 - 无风险收益率) / 策略收益率标准差 * √252
```

**使用方式**: 运行回测后自动返回在 `metrics.sharpe_ratio` 字段中。

---

## ✅ 2. 完整回测功能

**新增文件**:
- `backend/models/backtest.py` - 回测结果数据模型
- `backend/services/backtest_engine.py` - 回测引擎核心逻辑
- `backend/api/backtests.py` - 回测 API 端点

**功能特性**:
- ✅ 完整的交易模拟（买入/卖出）
- ✅ 手续费和滑点计算
- ✅ 资金曲线跟踪
- ✅ 多维度性能指标（夏普比率、最大回撤、胜率等）
- ✅ 详细交易记录

**API 端点**:
```
POST   /api/backtests/run          # 运行回测
GET    /api/backtests              # 获取回测列表
GET    /api/backtests/{id}         # 获取回测详情
DELETE /api/backtests/{id}         # 删除回测
```

**使用示例**:
```json
POST /api/backtests/run
{
  "strategy_id": "xxx",
  "stock_code": "600000.SH",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 100000
}
```

---

## ✅ 3. 策略与指标关联

**改进**: 策略配置现在完整包含指标定义和交易条件。

**策略配置结构**:
```json
{
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
```

**支持的操作符**: `>`, `<`, `>=`, `<=`, `==`

**条件逻辑**: 同一 action 的多个条件使用 AND 逻辑（全部满足才触发）

---

## ✅ 4. 扩展指标系统

### 4.1 内置指标扩展（4 → 12 个）

**原有指标**:
1. MA - 移动平均线
2. MACD - 指数平滑异同移动平均线
3. RSI - 相对强弱指标
4. BOLL - 布林带

**新增指标**:
5. EMA - 指数移动平均线
6. KDJ - 随机指标
7. CCI - 顺势指标
8. ATR - 平均真实波幅
9. OBV - 能量潮指标
10. WR - 威廉指标
11. DMI - 趋向指标
12. VWAP - 成交量加权平均价

**实现位置**: `backend/services/indicator_calculator.py`

### 4.2 自定义公式机制

**新增文件**:
- `backend/models/custom_indicator.py` - 自定义指标数据模型
- `backend/services/custom_indicator_engine.py` - 公式引擎
- `backend/api/custom_indicators.py` - 自定义指标 API

**功能特性**:
- ✅ 安全的公式评估（防止代码注入）
- ✅ 支持数学运算和技术分析函数
- ✅ 公式验证和语法检查
- ✅ 参数化配置

**支持的函数**:
- 数学: `abs()`, `sqrt()`, `log()`, `exp()`, `pow()`
- 聚合: `sum()`, `avg()`, `max()`, `min()`, `std()`
- 技术: `ema()`, `sma()`, `ref()`, `cross()`, `cross_up()`, `cross_down()`
- 数据: `OPEN`, `CLOSE`, `HIGH`, `LOW`, `VOLUME`

**公式示例**:
```python
# Z-Score
"(CLOSE - SMA(CLOSE, 20)) / STD(CLOSE, 20)"

# 价格动量
"CLOSE / REF(CLOSE, 10) - 1"

# 成交量比率
"VOLUME / AVG(VOLUME, 20)"

# 金叉信号
"CROSS_UP(SMA(CLOSE, 5), SMA(CLOSE, 20))"
```

**API 端点**:
```
POST   /api/custom-indicators                # 创建自定义指标
GET    /api/custom-indicators                # 获取指标列表
GET    /api/custom-indicators/{id}           # 获取指标详情
DELETE /api/custom-indicators/{id}           # 删除指标
POST   /api/custom-indicators/validate-formula  # 验证公式
POST   /api/custom-indicators/calculate      # 计算指标
```

---

## 📦 新增文件清单

### 数据模型
- `backend/models/backtest.py`
- `backend/models/custom_indicator.py`

### 服务层
- `backend/services/backtest_engine.py`
- `backend/services/custom_indicator_engine.py`
- `backend/services/indicator_calculator.py` (扩展)

### API 层
- `backend/api/backtests.py`
- `backend/api/custom_indicators.py`
- `backend/api/indicators.py` (更新)

### 数据库迁移
- `backend/alembic/versions/002_add_backtest_and_custom_indicators.py`

### 文档和测试
- `backend/README_FEATURES.md` (详细功能文档)
- `backend/scripts/test_new_features.py` (测试脚本)

---

## 🔧 部署步骤

### 1. 更新依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 运行数据库迁移
```bash
alembic upgrade head
```

### 3. 更新主应用
`backend/main.py` 已自动更新，包含新的路由。

### 4. 重启服务
```bash
# 开发环境
python main.py

# 或使用 Docker
docker-compose up --build
```

---

## 📊 数据库变更

### 新增表

**custom_indicators** - 自定义指标定义
```sql
- id (主键)
- name (唯一)
- display_name
- formula
- params (JSON)
- indicator_type
- is_active
```

**backtests** - 回测结果
```sql
- id (主键)
- strategy_id (外键)
- stock_code
- start_date, end_date
- initial_capital
- sharpe_ratio
- total_return
- max_drawdown
- trades (JSON)
- equity_curve (JSON)
```

---

## 🎯 完整使用流程

### 步骤 1: 创建策略（关联指标）
```bash
POST /api/strategies
{
  "name": "MA交叉策略",
  "indicators": [
    {"type": "MA", "params": {"periods": [5, 20]}}
  ],
  "conditions": [
    {"indicator": "MA5", "operator": ">", "value": "MA20", "action": "buy"},
    {"indicator": "MA5", "operator": "<", "value": "MA20", "action": "sell"}
  ]
}
```

### 步骤 2: 运行回测（自动计算夏普比率）
```bash
POST /api/backtests/run
{
  "strategy_id": "{从步骤1获取}",
  "stock_code": "600000.SH",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 100000
}
```

### 步骤 3: 查看结果
```bash
GET /api/backtests/{backtest_id}

# 响应包含
{
  "metrics": {
    "sharpe_ratio": 1.85,      # 夏普比率
    "annual_return": 0.25,     # 年化收益
    "max_drawdown": -0.15,     # 最大回撤
    "win_rate": 0.65,          # 胜率
    "total_trades": 24         # 交易次数
  },
  "trades": [...],             # 详细交易记录
  "equity_curve": [...]        # 资金曲线
}
```

### 步骤 4: 创建自定义指标（可选）
```bash
POST /api/custom-indicators
{
  "name": "zscore",
  "display_name": "Z-Score",
  "formula": "(CLOSE - SMA(CLOSE, period)) / STD(CLOSE, period)",
  "params": [
    {"name": "period", "type": "int", "default": 20}
  ]
}
```

---

## 🔒 安全性

### 自定义公式安全措施
1. ✅ 禁止代码注入（不允许 `import`, `exec`, `eval`）
2. ✅ 沙箱执行环境
3. ✅ 函数白名单机制
4. ✅ 语法验证

### 回测安全
1. ✅ 数据隔离（使用历史数据）
2. ✅ 参数验证
3. ✅ 资源限制

---

## 📈 性能优化

1. ✅ 指标计算结果缓存
2. ✅ 数据库索引优化
3. ✅ 批量操作支持
4. ✅ 异步处理能力

---

## 🎓 夏普比率解读

| 夏普比率 | 评级 | 说明 |
|---------|------|------|
| > 3.0   | 卓越 | 风险调整后收益非常优秀 |
| 2.0-3.0 | 优秀 | 风险调整后收益良好 |
| 1.0-2.0 | 良好 | 风险调整后收益可接受 |
| 0-1.0   | 一般 | 风险调整后收益较低 |
| < 0     | 较差 | 策略表现不如无风险资产 |

---

## ❓ 常见问题

**Q: 如何提高回测速度？**
A: 使用较短的时间范围，减少指标数量，或启用缓存。

**Q: 自定义公式有长度限制吗？**
A: 建议不超过 1000 字符，过长可能影响性能。

**Q: 回测结果能代表实盘表现吗？**
A: 回测是历史模拟，实盘会受滑点、流动性等因素影响，结果仅供参考。

**Q: 如何添加更多内置指标？**
A: 在 `indicator_calculator.py` 中添加新方法，并在 `indicators.py` 的 `/types` 端点中注册。

---

## 🚀 后续扩展方向

### 短期
- [ ] 实时交易执行
- [ ] 风险管理模块（止损/止盈）
- [ ] 多股票组合回测

### 中期
- [ ] 机器学习指标
- [ ] 因子分析
- [ ] 事件驱动策略

### 长期
- [ ] 分布式回测
- [ ] 高频交易支持
- [ ] 期货/期权支持

---

## 📝 总结

本次升级完全解决了您提出的问题：

✅ **夏普比率** - 已集成到回测引擎中  
✅ **回测功能** - 完整实现，包含多维度指标  
✅ **策略与指标关联** - 策略配置包含指标定义  
✅ **指标扩展** - 从 4 个扩展到 12 个  
✅ **自定义公式机制** - 安全的公式引擎  
✅ **插件机制** - 预留插件接口（custom_indicator 表中的 plugin_module/plugin_class 字段）

系统现在具备了完整的量化交易能力，可以进行策略开发、回测验证和性能评估。
