# 环境变量配置文档

本文档详细说明了中国A股量化交易系统的所有环境变量配置。

## 目录

- [快速开始](#快速开始)
- [后端环境变量](#后端环境变量)
- [前端环境变量](#前端环境变量)
- [Docker Compose环境变量](#docker-compose环境变量)
- [环境配置示例](#环境配置示例)

## 快速开始

### 开发环境设置

1. **后端配置：**
```bash
cd backend
cp .env.example .env
# 编辑 .env 文件（开发环境通常使用默认值即可）
```

2. **前端配置：**
```bash
cd frontend
cp .env.example .env
# 编辑 .env 文件（开发环境通常使用默认值即可）
```

3. **Docker Compose配置：**
```bash
cp .env.example .env
# 编辑 .env 文件（开发环境通常使用默认值即可）
```

### 生产环境设置

生产环境需要修改以下关键配置：
- 数据库密码（强密码）
- Redis密码
- CORS来源（实际域名）
- 日志级别（WARNING或ERROR）
- 关闭调试模式

## 后端环境变量

### 数据库配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `DATABASE_URL` | string | `sqlite:///./quant_trading.db` | 数据库连接字符串 | 是 |
| `DB_POOL_SIZE` | int | `5` | 数据库连接池大小 | 否 |
| `DB_MAX_OVERFLOW` | int | `10` | 连接池最大溢出数 | 否 |
| `DB_ECHO` | bool | `False` | 是否输出SQL日志 | 否 |

**DATABASE_URL格式：**
- SQLite: `sqlite:///./database.db`
- PostgreSQL: `postgresql://user:password@host:port/database`
- MySQL: `mysql://user:password@host:port/database`

### API服务配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `API_HOST` | string | `0.0.0.0` | API监听地址 | 否 |
| `API_PORT` | int | `8000` | API监听端口 | 否 |
| `API_RELOAD` | bool | `True` | 开发模式自动重载 | 否 |
| `ENVIRONMENT` | string | `development` | 运行环境 | 否 |

### CORS配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `CORS_ORIGINS` | string | `http://localhost:5173` | 允许的跨域来源（逗号分隔） | 是 |

**示例：**
```env
# 单个来源
CORS_ORIGINS=http://localhost:5173

# 多个来源
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://yourdomain.com
```

### Redis缓存配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `REDIS_URL` | string | `` | Redis连接URL（空则使用内存缓存） | 否 |
| `CACHE_ENABLED` | bool | `True` | 是否启用缓存 | 否 |
| `CACHE_TTL_STOCK_LIST` | int | `600` | 股票列表缓存时间（秒） | 否 |
| `CACHE_TTL_KLINE_DATA` | int | `300` | K线数据缓存时间（秒） | 否 |
| `CACHE_TTL_INDICATORS` | int | `300` | 技术指标缓存时间（秒） | 否 |
| `CACHE_TTL_STOCK_INFO` | int | `3600` | 股票信息缓存时间（秒） | 否 |

**REDIS_URL格式：**
```env
# 无密码
REDIS_URL=redis://localhost:6379/0

# 有密码
REDIS_URL=redis://:password@localhost:6379/0
```

### 日志配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `LOG_LEVEL` | string | `INFO` | 日志级别 | 否 |
| `LOG_FILE` | string | `` | 日志文件路径（空则只输出到控制台） | 否 |

**日志级别：**
- `DEBUG`: 详细的调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

### 安全配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `RATE_LIMIT_PER_MINUTE` | int | `60` | 每分钟最大请求数 | 否 |
| `SECRET_KEY` | string | `` | JWT密钥（如启用认证） | 否 |

### 数据源配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `TUSHARE_TOKEN` | string | `` | Tushare API Token | 否 |
| `DATA_FETCH_RETRY_TIMES` | int | `3` | 数据获取重试次数 | 否 |
| `DATA_FETCH_TIMEOUT` | int | `30` | 数据获取超时时间（秒） | 否 |

### 其他配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `TIMEZONE` | string | `Asia/Shanghai` | 时区设置 | 否 |
| `DEBUG` | bool | `True` | 调试模式 | 否 |

## 前端环境变量

### API配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `VITE_API_BASE_URL` | string | `http://localhost:8000` | 后端API基础URL | 是 |

### 应用配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `VITE_APP_TITLE` | string | `中国A股量化交易系统` | 应用标题 | 否 |
| `VITE_APP_VERSION` | string | `1.0.0` | 应用版本 | 否 |

### 功能开关

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `VITE_DEBUG` | bool | `true` | 调试模式 | 否 |
| `VITE_ENABLE_MOCK` | bool | `false` | 启用Mock数据 | 否 |

### 图表配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `VITE_CHART_THEME` | string | `light` | ECharts主题 | 否 |
| `VITE_DEFAULT_KLINE_COUNT` | int | `100` | 默认显示K线数量 | 否 |

### 其他配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `VITE_CACHE_EXPIRE_TIME` | int | `300000` | 缓存过期时间（毫秒） | 否 |
| `VITE_REQUEST_TIMEOUT` | int | `30000` | 请求超时时间（毫秒） | 否 |
| `VITE_ENABLE_REQUEST_LOG` | bool | `true` | 启用请求日志 | 否 |

## Docker Compose环境变量

### PostgreSQL配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `POSTGRES_DB` | string | `quant_trading` | 数据库名称 | 是 |
| `POSTGRES_USER` | string | `postgres` | 数据库用户名 | 是 |
| `POSTGRES_PASSWORD` | string | `postgres` | 数据库密码 | 是 |
| `POSTGRES_PORT` | int | `5432` | 宿主机映射端口 | 否 |

### Redis配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `REDIS_PORT` | int | `6379` | 宿主机映射端口 | 否 |
| `REDIS_PASSWORD` | string | `` | Redis密码 | 否 |

### 服务端口配置

| 变量名 | 类型 | 默认值 | 说明 | 必需 |
|--------|------|--------|------|------|
| `BACKEND_PORT` | int | `8000` | 后端服务端口 | 否 |
| `FRONTEND_PORT` | int | `80` | 前端服务端口 | 否 |

## 环境配置示例

### 开发环境

**backend/.env:**
```env
DATABASE_URL=sqlite:///./quant_trading.db
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True
CORS_ORIGINS=http://localhost:5173
REDIS_URL=
CACHE_ENABLED=True
LOG_LEVEL=INFO
DEBUG=True
```

**frontend/.env:**
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_DEBUG=true
```

**根目录 .env:**
```env
POSTGRES_DB=quant_trading
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
BACKEND_PORT=8000
FRONTEND_PORT=80
```

### 生产环境

**backend/.env:**
```env
DATABASE_URL=postgresql://quant_user:strong_password@db:5432/quant_trading_prod
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=False
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
REDIS_URL=redis://:redis_password@redis:6379/0
CACHE_ENABLED=True
CACHE_TTL_STOCK_LIST=600
CACHE_TTL_KLINE_DATA=300
LOG_LEVEL=WARNING
LOG_FILE=/var/log/quant-trading/app.log
RATE_LIMIT_PER_MINUTE=100
DEBUG=False
```

**frontend/.env.production:**
```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_DEBUG=false
VITE_ENABLE_MOCK=false
```

**根目录 .env:**
```env
POSTGRES_DB=quant_trading_prod
POSTGRES_USER=quant_user
POSTGRES_PASSWORD=your_strong_password_here
POSTGRES_PORT=5432

REDIS_PASSWORD=your_redis_password_here
REDIS_PORT=6379

BACKEND_PORT=8000
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
RATE_LIMIT_PER_MINUTE=100
LOG_LEVEL=WARNING

FRONTEND_PORT=80
VITE_API_BASE_URL=https://api.yourdomain.com

DOMAIN=yourdomain.com
```

## 安全建议

1. **永远不要提交 .env 文件到版本控制系统**
   - 将 `.env` 添加到 `.gitignore`
   - 只提交 `.env.example` 作为模板

2. **使用强密码**
   - 数据库密码至少16位，包含大小写字母、数字和特殊字符
   - Redis密码至少12位
   - 定期更换密码

3. **生产环境配置**
   - 关闭调试模式（`DEBUG=False`）
   - 设置合适的日志级别（`WARNING`或`ERROR`）
   - 启用HTTPS
   - 配置防火墙规则

4. **敏感信息管理**
   - 使用环境变量管理敏感信息
   - 考虑使用密钥管理服务（如AWS Secrets Manager、HashiCorp Vault）
   - 定期审计配置

## 故障排查

### 常见问题

1. **数据库连接失败**
   - 检查 `DATABASE_URL` 格式是否正确
   - 确认数据库服务已启动
   - 验证用户名和密码

2. **CORS错误**
   - 检查 `CORS_ORIGINS` 是否包含前端域名
   - 确认格式正确（逗号分隔，无空格）

3. **Redis连接失败**
   - 检查 `REDIS_URL` 格式
   - 确认Redis服务已启动
   - 验证密码（如有）

4. **前端无法访问API**
   - 检查 `VITE_API_BASE_URL` 是否正确
   - 确认后端服务已启动
   - 检查网络连接和防火墙规则

## 更多信息

- [项目README](./README.md)
- [部署文档](./README.md#部署)
- [API文档](http://localhost:8000/docs)
