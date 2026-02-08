# 量化交易系统 - 后端

基于 FastAPI + SQLAlchemy 的量化交易系统后端服务。

## 技术栈

- **FastAPI** - 现代高性能 Web 框架
- **SQLAlchemy** - Python SQL 工具包和 ORM
- **Alembic** - 数据库迁移工具
- **Pandas** - 数据分析库
- **TA-Lib** - 技术分析库
- **Pytest** - 测试框架
- **Uvicorn** - ASGI 服务器

## 项目结构

```
backend/
├── api/                    # API 路由和端点
│   ├── __init__.py
│   ├── backtests.py        # 回测 API
│   ├── custom_indicators.py # 自定义指标 API
│   ├── indicators.py       # 指标 API
│   ├── stocks.py           # 股票数据 API
│   └── strategies.py       # 策略 API
├── models/                 # SQLAlchemy 数据库模型
│   ├── __init__.py
│   ├── backtest.py         # 回测模型
│   ├── custom_indicator.py # 自定义指标模型
│   ├── kline_data.py       # K线数据模型
│   ├── stock.py            # 股票模型
│   └── strategy.py         # 策略模型
├── services/               # 业务逻辑服务层
│   ├── __init__.py
│   ├── backtest_engine.py  # 回测引擎
│   ├── cache_service.py    # 缓存服务
│   ├── custom_indicator_engine.py # 自定义指标引擎
│   ├── data_provider.py    # 数据提供服务
│   └── indicator_calculator.py # 指标计算器
├── repositories/           # 数据访问层
│   ├── __init__.py
│   └── data_repository.py  # 数据仓库
├── middleware/             # 中间件
│   ├── __init__.py
│   └── rate_limiter.py     # 限流中间件
├── validators/             # 数据验证器
│   ├── __init__.py
│   └── kline_validator.py  # K线数据验证器
├── alembic/                # 数据库迁移
│   ├── versions/           # 迁移版本
│   ├── env.py              # Alembic 环境配置
│   └── script.py.mako      # 迁移脚本模板
├── tests/                  # 测试套件
│   ├── __init__.py
│   ├── conftest.py         # Pytest 配置
│   ├── test_api_*.py       # API 测试
│   ├── test_cache_*.py     # 缓存测试
│   ├── test_data_*.py      # 数据层测试
│   └── test_*.py           # 其他测试
├── scripts/                # 工具脚本
│   ├── init_db.py          # 数据库初始化
│   ├── verify_indexes.py   # 索引验证
│   ├── demo_*.py           # 功能演示
│   └── test_*.py           # 手动测试脚本
├── docs/                   # 项目文档
│   ├── README.md           # 文档索引
│   ├── API_*.md            # API 文档
│   ├── BACKEND_STRUCTURE.md # 后端架构文档
│   ├── DIRECTORY_STRUCTURE.md # 目录结构说明
│   ├── PERFORMANCE_OPTIMIZATION.md # 性能优化文档
│   ├── README_FEATURES.md  # 功能说明
│   ├── UPGRADE_SUMMARY.md  # 升级总结
│   └── TASK_*.md           # 任务实现文档
├── data/                   # 数据文件（不提交到 Git）
│   ├── .gitignore
│   └── *.db                # SQLite 数据库文件
├── venv/                   # Python 虚拟环境（不提交到 Git）
├── __init__.py             # 包初始化
├── main.py                 # FastAPI 应用入口
├── config.py               # 配置管理
├── database.py             # 数据库连接和会话
├── exceptions.py           # 自定义异常
├── requirements.txt        # Python 依赖
├── pytest.ini              # Pytest 配置
├── alembic.ini             # Alembic 配置
├── Dockerfile              # Docker 镜像配置
├── .dockerignore           # Docker 忽略文件
├── .env                    # 环境变量（不提交到 Git）
├── .env.example            # 环境变量示例
└── .gitignore              # Git 忽略文件
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并配置：

```env
DATABASE_URL=sqlite:///./data/quant_trading.db
CORS_ORIGINS=http://localhost:5173
DEBUG=True
```

### 3. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head

# 或使用初始化脚本
python scripts/init_db.py
```

### 4. 启动服务

```bash
# 开发模式
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

## 核心模块说明

### API 层 (api/)
处理 HTTP 请求和响应，定义 RESTful API 端点。

### 模型层 (models/)
定义数据库表结构和 ORM 模型。

### 服务层 (services/)
实现核心业务逻辑：
- **backtest_engine.py** - 策略回测引擎
- **indicator_calculator.py** - 技术指标计算
- **custom_indicator_engine.py** - 自定义指标执行
- **data_provider.py** - 数据获取和处理
- **cache_service.py** - 缓存管理

### 仓库层 (repositories/)
封装数据库操作，提供数据访问接口。

### 中间件 (middleware/)
请求处理中间件，如限流、日志等。

### 验证器 (validators/)
数据验证和清洗逻辑。

## 开发工具

### 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api_endpoints.py

# 运行并显示覆盖率
pytest --cov=. --cov-report=html
```

### 工具脚本

```bash
# 初始化数据库
python scripts/init_db.py

# 验证数据库索引
python scripts/verify_indexes.py

# 演示指标计算器
python scripts/demo_indicator_calculator.py

# 演示数据验证和限流
python scripts/demo_validation_and_rate_limiting.py

# 手动测试 API
python scripts/test_api_manual.py

# 测试新功能
python scripts/test_new_features.py
```

## API 端点

### 股票数据
- `GET /api/stocks` - 获取股票列表
- `GET /api/stocks/{symbol}/klines` - 获取 K 线数据

### 技术指标
- `GET /api/indicators/calculate` - 计算技术指标
- `GET /api/indicators/list` - 获取可用指标列表

### 自定义指标
- `POST /api/custom-indicators` - 创建自定义指标
- `GET /api/custom-indicators` - 获取自定义指标列表
- `POST /api/custom-indicators/{id}/execute` - 执行自定义指标

### 策略管理
- `POST /api/strategies` - 创建策略
- `GET /api/strategies` - 获取策略列表
- `PUT /api/strategies/{id}` - 更新策略
- `DELETE /api/strategies/{id}` - 删除策略

### 回测
- `POST /api/backtests` - 创建回测
- `GET /api/backtests` - 获取回测列表
- `GET /api/backtests/{id}` - 获取回测详情

## Docker 部署

### 构建镜像

```bash
docker build -t quant-trading-backend .
```

### 运行容器

```bash
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e DATABASE_URL=sqlite:///./data/quant_trading.db \
  quant-trading-backend
```

## 文档

详细文档请查看 [docs](./docs/) 目录：

- [文档索引](./docs/README.md)
- [后端架构](./docs/BACKEND_STRUCTURE.md)
- [目录结构](./docs/DIRECTORY_STRUCTURE.md)
- [性能优化](./docs/PERFORMANCE_OPTIMIZATION.md)
- [功能说明](./docs/README_FEATURES.md)
- [升级总结](./docs/UPGRADE_SUMMARY.md)

## 开发规范

- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写单元测试
- 添加必要的文档字符串
- 提交前运行测试和代码检查

## 性能优化

- 数据库查询优化和索引
- Redis 缓存（可选）
- 异步 I/O 操作
- 批量数据处理
- API 限流保护

## 许可证

MIT
