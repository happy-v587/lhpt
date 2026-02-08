# Backend 项目结构详解

## 整理日期
2026-02-08

## 架构概览

本项目采用分层架构设计，遵循关注点分离原则：

```
API 层 → 服务层 → 仓库层 → 模型层
  ↓        ↓         ↓         ↓
路由    业务逻辑   数据访问   数据库
```

## 目录结构

### 1. API 层 (api/)

**职责**: 处理 HTTP 请求和响应，定义 RESTful API 端点

```
api/
├── __init__.py              # API 模块初始化
├── backtests.py             # 回测相关端点
├── custom_indicators.py     # 自定义指标端点
├── indicators.py            # 技术指标端点
├── stocks.py                # 股票数据端点
└── strategies.py            # 策略管理端点
```

**特点**:
- 使用 FastAPI 路由装饰器
- 请求参数验证
- 响应模型定义
- 错误处理

### 2. 模型层 (models/)

**职责**: 定义数据库表结构和 ORM 映射

```
models/
├── __init__.py              # 模型导出
├── backtest.py              # 回测结果模型
├── custom_indicator.py      # 自定义指标模型
├── kline_data.py            # K线数据模型
├── stock.py                 # 股票信息模型
└── strategy.py              # 策略配置模型
```

**特点**:
- SQLAlchemy ORM 模型
- 表关系定义
- 索引优化
- 数据约束

### 3. 服务层 (services/)

**职责**: 实现核心业务逻辑

```
services/
├── __init__.py                    # 服务导出
├── backtest_engine.py             # 回测引擎
├── cache_service.py               # 缓存服务
├── custom_indicator_engine.py     # 自定义指标执行引擎
├── data_provider.py               # 数据提供服务
└── indicator_calculator.py        # 技术指标计算器
```

**核心服务说明**:

#### backtest_engine.py
- 策略回测执行
- 交易信号生成
- 收益计算
- 性能指标统计

#### indicator_calculator.py
- 技术指标计算（MA, EMA, MACD, RSI, BOLL 等）
- 支持多种时间周期
- 批量计算优化

#### custom_indicator_engine.py
- 执行用户自定义 Python 代码
- 安全沙箱环境
- 指标结果验证

#### data_provider.py
- 股票数据获取
- K线数据处理
- 数据缓存管理

#### cache_service.py
- 内存缓存
- 缓存失效策略
- 性能优化

### 4. 仓库层 (repositories/)

**职责**: 封装数据库操作

```
repositories/
├── __init__.py              # 仓库导出
└── data_repository.py       # 数据访问仓库
```

**特点**:
- 数据库查询封装
- 事务管理
- 批量操作优化
- 查询结果缓存

### 5. 中间件 (middleware/)

**职责**: 请求处理中间件

```
middleware/
├── __init__.py              # 中间件导出
└── rate_limiter.py          # API 限流中间件
```

**功能**:
- API 请求限流
- 请求日志记录
- 错误处理
- CORS 配置

### 6. 验证器 (validators/)

**职责**: 数据验证和清洗

```
validators/
├── __init__.py              # 验证器导出
└── kline_validator.py       # K线数据验证器
```

**功能**:
- 数据格式验证
- 数据完整性检查
- 异常数据处理
- 数据标准化

### 7. 数据库迁移 (alembic/)

**职责**: 数据库版本控制和迁移

```
alembic/
├── versions/                # 迁移版本文件
│   ├── 001_initial_schema.py
│   └── 002_add_backtest_and_custom_indicators.py
├── env.py                   # Alembic 环境配置
└── script.py.mako           # 迁移脚本模板
```

**使用**:
```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 8. 测试 (tests/)

**职责**: 单元测试和集成测试

```
tests/
├── __init__.py                      # 测试包初始化
├── conftest.py                      # Pytest 配置和 fixtures
├── test_api_checkpoint.py           # API 检查点测试
├── test_api_endpoints.py            # API 端点测试
├── test_backtest.sh                 # 回测脚本测试
├── test_cache_integration.py        # 缓存集成测试
├── test_cache_service.py            # 缓存服务测试
├── test_data_layer_checkpoint.py    # 数据层检查点测试
├── test_data_provider_checkpoint.py # 数据提供者测试
├── test_indicator_calculator.py     # 指标计算器测试
├── test_indicator_integration.py    # 指标集成测试
├── test_kline_validator.py          # K线验证器测试
└── test_rate_limiter.py             # 限流器测试
```

**测试类型**:
- 单元测试: 测试单个函数/类
- 集成测试: 测试模块间交互
- API 测试: 测试 HTTP 端点
- 性能测试: 测试响应时间和吞吐量

### 9. 工具脚本 (scripts/)

**职责**: 开发和维护工具

```
scripts/
├── init_db.py                              # 数据库初始化
├── verify_indexes.py                       # 索引验证
├── demo_indicator_calculator.py            # 指标计算演示
├── demo_validation_and_rate_limiting.py    # 验证和限流演示
├── test_api_manual.py                      # 手动 API 测试
└── test_new_features.py                    # 新功能测试
```

**使用场景**:
- 数据库初始化和迁移
- 功能演示和验证
- 手动测试
- 数据维护

### 10. 文档 (docs/)

**职责**: 项目文档和说明

```
docs/
├── README.md                        # 文档索引
├── API_CHECKPOINT_SUMMARY.md        # API 检查点总结
├── API_IMPLEMENTATION_SUMMARY.md    # API 实现总结
├── BACKEND_STRUCTURE.md             # 后端架构说明
├── DIRECTORY_STRUCTURE.md           # 目录结构说明
├── PERFORMANCE_OPTIMIZATION.md      # 性能优化指南
├── PROJECT_STRUCTURE.md             # 项目结构详解（本文件）
├── README_FEATURES.md               # 功能特性说明
├── UPGRADE_SUMMARY.md               # 升级总结
└── TASK_9_IMPLEMENTATION_SUMMARY.md # 任务实现文档
```

### 11. 数据目录 (data/)

**职责**: 存储本地数据文件

```
data/
├── .gitignore               # 忽略数据库文件
├── quant_trading.db         # 主数据库（不提交）
└── test_cache.db            # 测试缓存数据库（不提交）
```

**注意**: 数据库文件不应提交到版本控制

## 核心文件说明

### main.py
FastAPI 应用入口文件

```python
# 主要功能
- 创建 FastAPI 应用实例
- 配置 CORS 中间件
- 注册 API 路由
- 配置异常处理
- 启动 Uvicorn 服务器
```

### config.py
配置管理

```python
# 主要功能
- 环境变量加载
- 配置参数定义
- 数据库连接配置
- CORS 配置
```

### database.py
数据库连接和会话管理

```python
# 主要功能
- SQLAlchemy 引擎创建
- 会话工厂配置
- 数据库依赖注入
- 连接池管理
```

### exceptions.py
自定义异常定义

```python
# 主要异常类型
- ValidationError: 数据验证错误
- NotFoundError: 资源不存在
- BusinessError: 业务逻辑错误
- DatabaseError: 数据库操作错误
```

## 配置文件

### requirements.txt
Python 依赖包列表

**主要依赖**:
- fastapi: Web 框架
- uvicorn: ASGI 服务器
- sqlalchemy: ORM
- alembic: 数据库迁移
- pandas: 数据分析
- ta-lib: 技术分析
- pytest: 测试框架

### pytest.ini
Pytest 测试配置

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### alembic.ini
Alembic 迁移配置

```ini
[alembic]
script_location = alembic
sqlalchemy.url = sqlite:///./data/quant_trading.db
```

### Dockerfile
Docker 镜像构建配置

```dockerfile
# 基于 Python 3.11
# 安装依赖
# 复制代码
# 暴露端口 8000
# 启动命令
```

### .dockerignore
Docker 构建忽略文件

```
venv/
__pycache__/
*.pyc
.env
data/*.db
```

### .gitignore
Git 版本控制忽略文件

```
__pycache__/
*.pyc
venv/
.env
*.db
.pytest_cache/
```

### .env.example
环境变量示例

```env
DATABASE_URL=sqlite:///./data/quant_trading.db
CORS_ORIGINS=http://localhost:5173
DEBUG=True
```

## 数据流

### 1. API 请求流程

```
客户端请求
    ↓
API 层 (api/)
    ↓
服务层 (services/)
    ↓
仓库层 (repositories/)
    ↓
模型层 (models/)
    ↓
数据库
```

### 2. 数据处理流程

```
原始数据
    ↓
验证器 (validators/)
    ↓
数据提供者 (data_provider.py)
    ↓
缓存服务 (cache_service.py)
    ↓
业务服务 (services/)
    ↓
API 响应
```

## 设计模式

### 1. 分层架构
- API 层、服务层、仓库层、模型层分离
- 单向依赖，避免循环依赖

### 2. 依赖注入
- 使用 FastAPI 的依赖注入系统
- 数据库会话注入
- 服务实例注入

### 3. 仓库模式
- 封装数据访问逻辑
- 统一数据操作接口
- 便于测试和维护

### 4. 服务模式
- 封装业务逻辑
- 可复用的服务组件
- 单一职责原则

## 命名规范

### Python 文件
- 模块文件: snake_case (如 `data_provider.py`)
- 类名: PascalCase (如 `DataProvider`)
- 函数名: snake_case (如 `get_stock_data`)
- 常量: UPPER_CASE (如 `MAX_RETRY_COUNT`)

### 数据库
- 表名: snake_case (如 `kline_data`)
- 字段名: snake_case (如 `created_at`)
- 索引名: `idx_表名_字段名` (如 `idx_kline_data_symbol`)

### API 端点
- RESTful 风格
- 使用复数名词 (如 `/api/stocks`)
- 使用连字符 (如 `/api/custom-indicators`)

## 开发工作流

### 1. 新增功能
```
1. 在 models/ 定义数据模型
2. 创建数据库迁移
3. 在 repositories/ 添加数据访问方法
4. 在 services/ 实现业务逻辑
5. 在 api/ 添加 API 端点
6. 编写测试
7. 更新文档
```

### 2. 修改现有功能
```
1. 修改相应层的代码
2. 更新数据库迁移（如需要）
3. 更新测试
4. 运行测试确保无破坏性变更
5. 更新文档
```

### 3. 性能优化
```
1. 识别性能瓶颈
2. 添加数据库索引
3. 实施缓存策略
4. 优化查询语句
5. 批量处理优化
6. 性能测试验证
```

## 最佳实践

### 1. 代码质量
- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写文档字符串
- 代码审查

### 2. 测试
- 单元测试覆盖率 > 80%
- 集成测试关键流程
- 测试边界条件
- 使用 fixtures 复用测试数据

### 3. 安全
- 输入验证
- SQL 注入防护
- API 限流
- 错误信息脱敏

### 4. 性能
- 数据库查询优化
- 使用缓存
- 异步 I/O
- 批量操作

### 5. 可维护性
- 模块化设计
- 清晰的代码结构
- 完善的文档
- 版本控制

## 待优化项

- [ ] 添加 Redis 缓存支持
- [ ] 实现异步任务队列
- [ ] 添加日志系统
- [ ] 实现用户认证和授权
- [ ] 添加 API 版本控制
- [ ] 实现数据备份策略
- [ ] 添加监控和告警
- [ ] 优化大数据量查询
- [ ] 实现分布式部署
- [ ] 添加 GraphQL 支持

## 相关文档

- [后端架构说明](./BACKEND_STRUCTURE.md)
- [目录结构说明](./DIRECTORY_STRUCTURE.md)
- [性能优化指南](./PERFORMANCE_OPTIMIZATION.md)
- [API 文档](http://localhost:8000/docs)
