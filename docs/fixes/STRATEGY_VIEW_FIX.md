# 策略查看功能修复总结

## 问题描述

前端在查看策略详情时出现错误：
```
TypeError: Cannot read properties of undefined (reading 'filter')
at StrategyManager.vue:266:71
```

## 根本原因

1. **策略列表API不返回完整数据**: `GET /api/strategies` 返回的是简化的策略列表（`StrategyResponse`），不包含 `indicators` 和 `conditions` 字段

2. **前端直接使用列表数据**: `handleView` 函数直接使用列表中的策略对象，导致访问 `currentStrategy.conditions.filter()` 时出错

3. **缺少action字段**: 后端的 `TradingCondition` 模型缺少 `action` 字段，无法区分买入和卖出条件

## 修复内容

### 1. 添加获取单个策略详情的服务方法

**文件**: `frontend/src/services/strategies.js`

```javascript
/**
 * 获取单个策略详情
 * @param {string} id - 策略ID
 * @returns {Promise<Object>} 策略详情
 */
export const getStrategy = async (id) => {
  return await apiClient.get(`/strategies/${id}`)
}
```

### 2. 修改handleView函数异步获取详情

**文件**: `frontend/src/components/StrategyManager.vue`

```javascript
// 修复前
const handleView = (strategy) => {
  currentStrategy.value = strategy
  showViewDialog.value = true
}

// 修复后
const handleView = async (strategy) => {
  try {
    // 获取完整的策略详情（包含indicators和conditions）
    const detailResponse = await getStrategy(strategy.id)
    currentStrategy.value = detailResponse
    showViewDialog.value = true
  } catch (error) {
    console.error('获取策略详情失败:', error)
    ElMessage.error('获取策略详情失败，请稍后重试')
  }
}
```

### 3. 添加安全检查防止undefined错误

**文件**: `frontend/src/components/StrategyManager.vue`

```vue
<!-- 修复前 -->
<el-tag v-for="(indicator, index) in currentStrategy.indicators">

<!-- 修复后 -->
<el-tag v-for="(indicator, index) in (currentStrategy.indicators || [])">

<!-- 修复前 -->
<div v-for="(condition, index) in currentStrategy.conditions.filter(c => c.action === 'buy')">

<!-- 修复后 -->
<div v-for="(condition, index) in (currentStrategy.conditions || []).filter(c => c.action === 'buy')">
```

### 4. 添加action字段到TradingCondition模型

**文件**: `backend/api/strategies.py`

```python
class TradingCondition(BaseModel):
    """Trading condition model."""
    indicator: str = Field(..., description="指标名称")
    operator: str = Field(..., description="操作符 (>, <, =, cross_up, cross_down)")
    value: Any = Field(..., description="比较值")
    action: str = Field(default="buy", description="动作类型 (buy/sell)")  # 新增
```

## API端点说明

### 策略列表 (简化版)
```
GET /api/strategies
```

**响应**:
```json
{
  "strategies": [
    {
      "id": "uuid",
      "name": "策略名称",
      "description": "描述",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### 策略详情 (完整版)
```
GET /api/strategies/{strategy_id}
```

**响应**:
```json
{
  "id": "uuid",
  "name": "策略名称",
  "description": "描述",
  "indicators": [
    {
      "type": "MA",
      "params": {"periods": [5, 10, 20]}
    }
  ],
  "conditions": [
    {
      "indicator": "MA5",
      "operator": ">",
      "value": "MA10",
      "action": "buy"
    },
    {
      "indicator": "MA5",
      "operator": "<",
      "value": "MA10",
      "action": "sell"
    }
  ],
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

## 测试步骤

1. **重启前端服务** (如果需要):
   ```bash
   cd frontend
   npm run dev
   ```

2. **清除浏览器缓存**: 硬刷新 (Cmd+Shift+R 或 Ctrl+Shift+R)

3. **测试查看策略详情**:
   - 打开"策略管理"页面
   - 点击任意策略的"查看"按钮
   - 应该能看到完整的策略详情，包括：
     - 技术指标列表
     - 买入条件（绿色标签）
     - 卖出条件（红色标签）

4. **验证API响应**:
   ```bash
   # 获取策略列表
   curl 'http://localhost:8000/api/strategies' | python3 -m json.tool
   
   # 获取策略详情
   curl 'http://localhost:8000/api/strategies/{strategy_id}' | python3 -m json.tool
   ```

## 相关文件

- `frontend/src/services/strategies.js` - 策略服务
- `frontend/src/components/StrategyManager.vue` - 策略管理组件
- `backend/api/strategies.py` - 策略API端点

## 注意事项

1. **数据结构一致性**: 确保前端创建策略时，conditions 中包含 `action` 字段
2. **向后兼容**: 旧的策略数据可能没有 `action` 字段，使用默认值 "buy"
3. **错误处理**: 添加了适当的错误处理和用户提示
4. **性能优化**: 只在需要时获取完整的策略详情，列表页面仍使用简化数据
