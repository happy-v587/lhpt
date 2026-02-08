# 快速开始指南

## 🚀 5分钟上手新功能

### 前提条件
- 后端服务已启动（http://localhost:8000）
- 前端服务已启动（http://localhost:5173）
- 数据库迁移已完成

---

## 步骤 1: 运行数据库迁移（仅首次）

```bash
cd backend
alembic upgrade head
```

预期输出:
```
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, add backtest and custom indicators tables
```

---

## 步骤 2: 重启服务

### 后端
```bash
cd backend
python main.py
```

### 前端
```bash
cd frontend
npm run dev
```

---

## 步骤 3: 体验新功能

### 🎯 功能 1: 运行策略回测（含夏普比率）

1. **访问回测页面**: http://localhost:5173/backtest

2. **创建测试策略**（如果还没有）:
   - 访问 http://localhost:5173/strategy
   - 点击"创建策略"
   - 输入以下配置:
     ```
     名称: MA交叉测试
     描述: 5日均线上穿20日均线买入
     ```
   - 添加指标: MA，周期 [5, 20]
   - 添加买入条件: MA5 > MA20
   - 添加卖出条件: MA5 < MA20
   - 保存

3. **运行回测**:
   - 选择刚创建的策略
   - 选择股票: 600000.SH（浦发银行）
   - 选择时间: 2023-01-01 至 2023-12-31
   - 初始资金: 100000
   - 点击"开始回测"

4. **查看结果**:
   - 夏普比率（带评级）
   - 年化收益率
   - 最大回撤
   - 胜率
   - 交易次数

**预期结果**: 
- 回测在几秒内完成
- 显示夏普比率及评级（如 1.85 - 良好）
- 显示完整的性能指标

---

### 🛠️ 功能 2: 创建自定义指标

1. **访问自定义指标页面**: http://localhost:5173/custom-indicator

2. **创建简单指标**:
   - 点击"创建指标"
   - 填写表单:
     ```
     指标名称: price_change
     显示名称: 价格变化率
     描述: 当日价格变化百分比
     公式: (CLOSE - OPEN) / OPEN
     ```
   - 点击"验证公式"（应该显示"公式验证通过"）
   - 点击"创建"

3. **测试指标**:
   - 在列表中找到刚创建的指标
   - 点击"测试"
   - 选择股票: 600000.SH
   - 选择时间: 2023-01-01 至 2023-12-31
   - 点击"计算"

**预期结果**:
- 指标创建成功
- 公式验证通过
- 计算成功并显示数据点数量

---

### 📊 功能 3: 使用新增的技术指标

1. **访问数据可视化页面**: http://localhost:5173/chart

2. **添加新指标**:
   - 选择股票: 600000.SH
   - 点击"添加指标"
   - 选择新指标类型（如 KDJ、ATR、OBV 等）
   - 配置参数
   - 保存

3. **查看图表**:
   - K线图会显示新添加的指标
   - 可以同时添加多个指标

**预期结果**:
- 新指标正确显示在图表上
- 指标数值合理

---

## 🧪 快速测试脚本

### 测试回测 API

```bash
# 1. 创建策略
curl -X POST http://localhost:8000/api/strategies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试策略",
    "description": "MA交叉",
    "indicators": [{"type": "MA", "params": {"periods": [5, 20]}}],
    "conditions": [
      {"indicator": "MA5", "operator": ">", "value": "MA20", "action": "buy"},
      {"indicator": "MA5", "operator": "<", "value": "MA20", "action": "sell"}
    ]
  }'

# 记录返回的 strategy_id

# 2. 运行回测
curl -X POST http://localhost:8000/api/backtests/run \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "YOUR_STRATEGY_ID",
    "stock_code": "600000.SH",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 100000
  }'

# 3. 查看回测列表
curl http://localhost:8000/api/backtests
```

### 测试自定义指标 API

```bash
# 1. 创建自定义指标
curl -X POST http://localhost:8000/api/custom-indicators \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_indicator",
    "display_name": "测试指标",
    "indicator_type": "formula",
    "formula": "(CLOSE - OPEN) / OPEN",
    "params": []
  }'

# 2. 验证公式
curl -X POST http://localhost:8000/api/custom-indicators/validate-formula \
  -H "Content-Type: application/json" \
  -d '{
    "formula": "(CLOSE - SMA(CLOSE, 20)) / STD(CLOSE, 20)"
  }'

# 3. 获取指标列表
curl http://localhost:8000/api/custom-indicators
```

### 测试新增指标

```bash
# 获取所有指标类型（应该有 12 个）
curl http://localhost:8000/api/indicators/types

# 计算 KDJ 指标
curl -X POST http://localhost:8000/api/indicators/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600000.SH",
    "indicator_type": "KDJ",
    "params": {"n": 9, "m1": 3, "m2": 3},
    "start_date": "2023-01-01",
    "end_date": "2023-12-31"
  }'
```

---

## ✅ 验证清单

完成以下检查确认功能正常：

### 后端
- [ ] 数据库迁移成功
- [ ] 后端服务启动无错误
- [ ] `/api/backtests` 端点可访问
- [ ] `/api/custom-indicators` 端点可访问
- [ ] `/api/indicators/types` 返回 12 个指标

### 前端
- [ ] 前端服务启动无错误
- [ ] 导航菜单显示"策略回测"和"自定义指标"
- [ ] 回测页面可以正常访问
- [ ] 自定义指标页面可以正常访问
- [ ] 所有页面无控制台错误

### 功能
- [ ] 可以创建策略
- [ ] 可以运行回测
- [ ] 回测结果显示夏普比率
- [ ] 可以创建自定义指标
- [ ] 可以验证公式
- [ ] 可以计算自定义指标
- [ ] 可以使用新增的技术指标

---

## 🐛 常见问题

### Q1: 数据库迁移失败
```bash
# 检查当前版本
alembic current

# 如果显示 001，运行升级
alembic upgrade head

# 如果报错"表已存在"
alembic stamp head
```

### Q2: 后端启动报错 "Module not found"
```bash
# 确保在虚拟环境中
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 重新安装依赖
pip install -r requirements.txt
```

### Q3: 前端页面空白
```bash
# 检查浏览器控制台
# 常见原因: 后端未启动或端口不对

# 检查 API 配置
cat frontend/src/services/api.js
# 确保 baseURL 正确（默认 http://localhost:8000/api）
```

### Q4: 回测返回"没有找到K线数据"
```bash
# 需要先获取股票数据
# 访问 http://localhost:5173/chart
# 选择股票并加载数据
# 或使用 API 获取数据
curl http://localhost:8000/api/stocks/600000.SH/kline?start_date=2023-01-01&end_date=2023-12-31
```

---

## 📖 下一步

完成快速开始后，您可以：

1. **深入学习**: 阅读 [完整更新指南](COMPLETE_UPDATE_GUIDE.md)
2. **查看示例**: 查看 [后端功能详细说明](backend/README_FEATURES.md)
3. **前端开发**: 查看 [前端更新说明](frontend/FRONTEND_UPDATES.md)
4. **运行测试**: 执行 `python backend/scripts/test_new_features.py`

---

## 💡 提示

- **夏普比率**: > 1 为良好，> 2 为优秀，> 3 为卓越
- **回测时间**: 建议至少使用 1 年的数据
- **自定义公式**: 支持的函数见文档，使用大写变量名（CLOSE, OPEN 等）
- **指标组合**: 可以在策略中组合多个指标提高准确性

---

## 🎉 恭喜！

您已经成功完成了新功能的快速上手！

现在您可以：
- ✅ 运行策略回测并查看夏普比率
- ✅ 创建和使用自定义指标
- ✅ 使用 12 种技术指标进行分析
- ✅ 管理回测历史记录

开始您的量化交易之旅吧！🚀
