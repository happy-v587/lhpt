# 快速修复指南

## 🚨 当前问题

从截图看到：
- Request URL: `http://localhost:8000/stocks` ❌
- 应该是: `http://localhost:8000/api/stocks` ✅
- Status: 404 Not Found

## 🔧 立即修复步骤

### 步骤 1: 停止前端服务
```bash
# 在前端终端按 Ctrl+C
```

### 步骤 2: 删除缓存
```bash
cd frontend
rm -rf node_modules/.vite
rm -rf node_modules/.cache
```

### 步骤 3: 检查文件是否更新
```bash
# 查看 api.js 文件内容
cat src/services/api.js | grep baseURL
```

**应该看到**:
```javascript
baseURL: 'http://localhost:8000/api',
```

**如果看到的是**:
```javascript
baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
```

**手动修改为**:
```javascript
baseURL: 'http://localhost:8000/api',
```

### 步骤 4: 重新启动
```bash
npm run dev
```

### 步骤 5: 完全刷新浏览器
1. 打开开发者工具 (F12)
2. 右键点击刷新按钮
3. 选择"清空缓存并硬性重新加载"

或者：
- Windows/Linux: `Ctrl + Shift + Delete` → 清除缓存
- Mac: `Cmd + Shift + Delete` → 清除缓存

### 步骤 6: 验证
1. 打开 http://localhost:5173/strategy
2. 打开开发者工具 (F12)
3. 切换到 Console 标签
4. 应该看到：
```
API Request: GET http://localhost:8000/api/stocks
API Response: /stocks 200
```

5. 切换到 Network 标签
6. 应该看到：
```
GET /api/stocks - 200 OK
```

---

## 🔍 如果还是不行

### 方案 A: 手动修改所有文件

#### 1. 修改 `frontend/src/services/api.js`
```javascript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',  // 确保这里是 /api
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use(
  config => {
    console.log('Request:', config.baseURL + config.url)
    return config
  },
  error => Promise.reject(error)
)

apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('Error:', error.config?.url, error.response?.data)
    return Promise.reject(error)
  }
)

export default apiClient
```

#### 2. 确认 `frontend/src/services/stocks.js`
```javascript
export const getStockList = async () => {
  return await apiClient.get('/stocks')  // 不要 /api 前缀
}
```

#### 3. 确认 `frontend/src/services/strategies.js`
```javascript
export const getStrategies = async () => {
  return await apiClient.get('/strategies')  // 不要 /api 前缀
}
```

### 方案 B: 使用完整 URL

如果 baseURL 始终不生效，可以使用完整 URL：

#### 修改 `frontend/src/services/stocks.js`
```javascript
export const getStockList = async () => {
  return await apiClient.get('http://localhost:8000/api/stocks')
}
```

---

## 🧪 测试后端 API

在修复前端之前，先确认后端 API 是否正常：

```bash
# 测试 1: 健康检查
curl http://localhost:8000/health

# 测试 2: 股票列表
curl http://localhost:8000/api/stocks

# 测试 3: 策略列表
curl http://localhost:8000/api/strategies

# 测试 4: 指标类型
curl http://localhost:8000/api/indicators/types
```

如果这些都返回 404，说明后端路由有问题。

---

## 📝 检查清单

- [ ] 后端服务正在运行 (http://localhost:8000)
- [ ] 后端 API 可以访问 (`curl http://localhost:8000/api/stocks`)
- [ ] 前端服务已重启
- [ ] 浏览器缓存已清除
- [ ] `api.js` 中 baseURL 是 `http://localhost:8000/api`
- [ ] 其他服务文件中的路径不包含 `/api` 前缀
- [ ] 开发者工具中看到正确的请求 URL

---

## 🎯 预期结果

### 浏览器控制台 (Console)
```
API Request: GET http://localhost:8000/api/stocks
API Response: /stocks 200
Stock list response: {data: {stocks: Array(4000)}}
Loaded stocks: 4000
```

### 浏览器网络 (Network)
```
Name: stocks
Status: 200
Type: xhr
Size: ~500KB
Time: ~2s
```

### 股票选择器
```
┌─────────────────────────────────┐
│ 请选择股票                  ▼  │
└─────────────────────────────────┘
  ↓ 点击后
┌─────────────────────────────────┐
│ 000001.SZ - 平安银行        SZ  │
│ 000002.SZ - 万科A           SZ  │
│ 600000.SH - 浦发银行        SH  │
│ ...                             │
└─────────────────────────────────┘
```

---

## 💡 终极解决方案

如果以上都不行，使用这个临时方案：

### 创建 `frontend/.env.local`
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### 修改 `frontend/src/services/api.js`
```javascript
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})
```

### 重启前端
```bash
npm run dev
```

---

## 🆘 还是不行？

提供以下信息：

1. **后端测试结果**:
```bash
curl http://localhost:8000/api/stocks
```

2. **前端 api.js 内容**:
```bash
cat frontend/src/services/api.js
```

3. **浏览器控制台日志** (Console 标签的所有输出)

4. **浏览器网络请求** (Network 标签中失败请求的详细信息)

---

现在按照步骤操作，应该可以解决问题！🚀
