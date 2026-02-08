# API响应处理修复说明

## 问题根源

响应拦截器在 `frontend/src/services/api.js` 中已经返回了 `response.data`：

```javascript
apiClient.interceptors.response.use(
  response => {
    console.log('API Response:', response.config.url, response.status)
    // 返回 response.data 而不是整个 response
    return response.data
  },
  // ...
)
```

这意味着当后端返回：
```json
{
  "indicators": [...]
}
```

拦截器提取的 `response.data` 就是 `{ indicators: [...] }`。

但是组件中的代码还在尝试访问 `response.data.indicators`，这会导致 `undefined`。

## 修复内容

### 1. IndicatorConfig.vue
**修复前：**
```javascript
if (response && response.data) {
  indicatorTypes.value = response.data.indicators || []
} else if (response && response.indicators) {
  indicatorTypes.value = response.indicators || []
}
```

**修复后：**
```javascript
// 响应拦截器已经返回了 response.data，所以这里直接使用 response.indicators
if (response && response.indicators) {
  indicatorTypes.value = response.indicators
} else if (Array.isArray(response)) {
  indicatorTypes.value = response
}
```

### 2. StockSelector.vue
**修复前：**
```javascript
if (response && response.data) {
  stocks.value = response.data.stocks || []
} else if (response && response.stocks) {
  stocks.value = response.stocks || []
}
```

**修复后：**
```javascript
// 响应拦截器已经返回了 response.data，所以这里直接使用 response.stocks
if (response && response.stocks) {
  stocks.value = response.stocks
} else if (Array.isArray(response)) {
  stocks.value = response
}
```

## 如何测试

1. **清除Vite缓存并重启前端服务：**
   ```bash
   cd frontend
   rm -rf node_modules/.vite
   npm run dev
   ```

2. **硬刷新浏览器：**
   - Mac: `Cmd + Shift + R`
   - Windows/Linux: `Ctrl + Shift + R`

3. **检查浏览器控制台：**
   - 应该看到 `Loaded indicator types: 12`
   - 应该看到 `Loaded stocks: X`（X是股票数量）
   - 指标类型下拉框应该显示12个指标
   - 股票选择器应该显示股票列表

## 一致性说明

现在所有组件都遵循相同的模式：
- 响应拦截器统一返回 `response.data`
- 所有组件直接访问响应对象的属性（如 `response.indicators`、`response.stocks`）
- 不再需要访问 `response.data.xxx`
