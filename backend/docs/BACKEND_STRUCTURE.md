# Backend 目录结构说明

## 目录概览

```
backend/
├── api/                    # API路由层
├── models/                 # 数据模型层
├── services/              # 业务逻辑层
├── repositories/          # 数据访问层
├── validators/            # 数据验证层
├── middleware/            # 中间件层
├── alembic/               # 数据库迁移
├── tests/                 # 测试文件
├── scripts/               # 工具脚本
├── docs/                  # 文档目录
├── data/                  # 数据文件
├── venv/                  # Python虚拟环境
├── main.py               # 应用入口
├── config.py             # 配置管理
├── database.py           # 数据库连接
├── exceptions.py         # 自定义异常
└── requirements.txt      # 依赖包列表
```

## 详细说明

### 1. API层 (`api/`)
**职责**: 定义HTTP端点，处理请求和响应

**文件**:
- `__init__.py` - 包初始化
- `stocks.py` - 股票相关API
- `indicators.py` - 技术指标API
- `strategies.py` - 策略管理API
- `backtests.py` - 回测功能API
- `custom_indicators.py` - 自定义指标API

**规范**:
- 使用FastAPI的APIRouter
- 定义Pydantic模型进行请求/响应验证
- 统一的错误处理
- 完整的API文档注释
- 路由前缀: `/api/{resource}`

**示例**:
```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/stocks", tags=["stocks"])

@router.get("")
async def get_stocks():
    """获取股票列表"""
    pass
```

### 2. 模型层 (`models/`)
**职责**: 定义数据库表结构和ORM模型

**文件**:
- `stock.py` - 股票模型
- `kline_data.py` - K线数据模型
- `strategy.py` - 策略模型
- `backtest.py` - 回测结果模型
- `custom_indicator.py` - 自定义指标模型

**规范**:
- 使用SQLAlchemy ORM
- 每个模型一个文件
- 包含字段注释和约束
- 定义索引和关系
- 使用类型提示

**示例**:
```python
from sqlalchemy import Column, String, Date
from database import Base

class Stock(Base):
    __tablename__ = 'stocks'
    
    code = Column(String(10), primary_key=True, comment='股票代码')
    name = Column(String(50), nullable=False, comment='股票名称')
```

### 3. 服务层 (`services/`)
**职责**: 实现核心业务逻辑

**文件**:
- `data_provider.py` - 数据获取服务
- `indicator_calculator.py` - 指标计算服务
- `backtest_engine.py` - 回测引擎
- `custom_indicator_engine.py` - 自定义指标引擎
- `cache_service.py` - 缓存服务

**规范**:
- 单一职责原则
- 不直接访问数据库（通过Repository）
- 包含完整的业务逻辑
- 异常处理和日志记录
- 可测试性

**示例**:
```python
class IndicatorCalculator:
    """技术指标计算服务"""
    
    def calculate_ma(self, data: pd.DataFrame, periods: List[int]) -> Dict:
        """计算移动平均线"""
        pass
```

### 4. 数据访问层 (`repositories/`)
**职责**: 封装数据库操作

**文件**:
- `data_repository.py` - 数据访问仓库

**规范**:
- 所有数据库操作集中管理
- 使用Session管理事务
- 提供CRUD操作
- 缓存失效处理
- 批量操作优化

**示例**:
```python
class DataRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_kline_data(self, stock_code: str, start_date: str, end_date: str):
        """获取K线数据"""
        pass
```

### 5. 验证层 (`validators/`)
**职责**: 数据验证和业务规则检查

**文件**:
- `kline_validator.py` - K线数据验证器

**规范**:
- 独立的验证逻辑
- 抛出明确的验证异常
- 可复用的验证规则
- 完整的错误信息

**示例**:
```python
class KLineDataValidator:
    @staticmethod
    def validate_dataframe(df: pd.DataFrame):
        """验证K线数据完整性"""
        pass
```

### 6. 中间件层 (`middleware/`)
**职责**: 请求/响应拦截和处理

**文件**:
- `rate_limiter.py` - 限流中间件

**规范**:
- 实现FastAPI中间件接口
- 不影响业务逻辑
- 性能优化
- 可配置

### 7. 数据库迁移 (`alembic/`)
**职责**: 管理数据库schema变更

**文件**:
- `env.py` - Alembic环境配置
- `versions/` - 迁移脚本目录
  - `001_initial_schema.py` - 初始schema
  - `002_add_backtest_and_custom_indicators.py` - 添加回测和自定义指标表

**规范**:
- 每次schema变更创建新的迁移文件
- 迁移文件命名: `{序号}_{描述}.py`
- 包含upgrade和downgrade方法
- 测试迁移脚本

**使用**:
```bash
# 创建迁移
alembic revision -m "description"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 8. 测试 (`tests/`)
**职责**: 单元测试和集成测试

**文件分类**:
- `test_api_*.py` - API测试
- `test_*_service.py` - 服务层测试
- `test_*_integration.py` - 集成测试
- `conftest.py` - pytest配置和fixtures

**规范**:
- 使用pytest框架
- 测试覆盖率 > 80%
- 独立的测试数据库
- Mock外部依赖
- 清晰的测试命名

**运行测试**:
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_api_endpoints.py

# 查看覆盖率
pytest --cov=. --cov-report=html
```

### 9. 工具脚本 (`scripts/`)
**职责**: 开发和维护工具

**文件**:
- `init_db.py` - 初始化数据库
- `test_api_manual.py` - 手动API测试
- `demo_*.py` - 功能演示脚本
- `verify_*.py` - 验证脚本

**规范**:
- 独立可执行
- 包含使用说明
- 错误处理
- 日志输出

### 10. 文档 (`docs/`)
**职责**: 技术文档和设计文档

**文件**:
- `BACKEND_STRUCTURE.md` - 目录结构说明（本文件）
- `API_IMPLEMENTATION_SUMMARY.md` - API实现总结
- `DIRECTORY_STRUCTURE.md` - 详细目录结构
- `PERFORMANCE_OPTIMIZATION.md` - 性能优化文档
- `TASK_*_IMPLEMENTATION_SUMMARY.md` - 任务实现总结

**规范**: 见《文档管理约束》

### 11. 核心文件

#### `main.py`
应用入口，配置FastAPI应用

**内容**:
- 创建FastAPI实例
- 配置CORS
- 注册路由
- 全局异常处理
- 启动配置

#### `config.py`
配置管理，从环境变量读取配置

**内容**:
- 数据库配置
- API配置
- 缓存配置
- 限流配置
- 日志配置

#### `database.py`
数据库连接和Session管理

**内容**:
- SQLAlchemy引擎配置
- Session工厂
- Base类定义
- 依赖注入函数

#### `exceptions.py`
自定义异常类

**内容**:
- QuantTradingError基类
- 各种业务异常
- 错误码定义

#### `requirements.txt`
Python依赖包列表

**主要依赖**:
- fastapi - Web框架
- sqlalchemy - ORM
- pandas - 数据处理
- numpy - 数值计算
- alembic - 数据库迁移
- pytest - 测试框架

## 代码组织原则

### 1. 分层架构
```
API层 → 服务层 → 数据访问层 → 数据库
  ↓       ↓          ↓
验证层   业务逻辑   ORM模型
```

### 2. 依赖方向
- 上层依赖下层
- 下层不依赖上层
- 同层之间尽量解耦

### 3. 单一职责
- 每个模块只负责一个功能
- 每个类只有一个变更原因
- 每个函数只做一件事

### 4. 开闭原则
- 对扩展开放
- 对修改关闭
- 使用接口和抽象

### 5. 依赖注入
- 使用FastAPI的Depends
- 便于测试和替换
- 降低耦合度

## 命名规范

### 文件命名
- 小写字母
- 下划线分隔
- 描述性名称
- 例: `indicator_calculator.py`

### 类命名
- 大驼峰命名
- 名词或名词短语
- 例: `IndicatorCalculator`

### 函数命名
- 小写字母
- 下划线分隔
- 动词开头
- 例: `calculate_ma()`

### 变量命名
- 小写字母
- 下划线分隔
- 描述性名称
- 例: `stock_code`

### 常量命名
- 全大写字母
- 下划线分隔
- 例: `MAX_RETRY_COUNT`

## 代码风格

### 1. 使用类型提示
```python
def calculate_ma(data: pd.DataFrame, periods: List[int]) -> Dict[str, pd.Series]:
    pass
```

### 2. 文档字符串
```python
def calculate_ma(data: pd.DataFrame, periods: List[int]) -> Dict[str, pd.Series]:
    """
    计算移动平均线。
    
    Args:
        data: K线数据
        periods: 周期列表
    
    Returns:
        包含各周期MA的字典
    
    Raises:
        ValueError: 数据不足时抛出
    """
    pass
```

### 3. 日志记录
```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.info("开始处理")
    try:
        # 业务逻辑
        pass
    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)
        raise
```

### 4. 异常处理
```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"操作失败: {e}")
    raise QuantTradingError("OPERATION_FAILED", "操作失败", str(e))
```

## 性能优化

### 1. 数据库优化
- 使用索引
- 批量操作
- 连接池
- 查询优化

### 2. 缓存策略
- Redis缓存
- 缓存失效
- 缓存预热
- 缓存穿透保护

### 3. 异步处理
- 使用async/await
- 并发请求
- 后台任务

### 4. 数据处理
- Pandas向量化
- NumPy优化
- 避免循环
- 内存管理

## 安全规范

### 1. 输入验证
- 使用Pydantic验证
- SQL注入防护
- XSS防护

### 2. 错误处理
- 不暴露敏感信息
- 统一错误格式
- 日志记录

### 3. 限流保护
- API限流
- 防止DDoS
- 资源保护

### 4. 数据安全
- 敏感数据加密
- 访问控制
- 审计日志

## 开发流程

### 1. 新功能开发
1. 在`models/`定义数据模型
2. 创建数据库迁移
3. 在`repositories/`实现数据访问
4. 在`services/`实现业务逻辑
5. 在`api/`创建API端点
6. 编写测试
7. 更新文档

### 2. Bug修复
1. 编写复现测试
2. 定位问题
3. 修复代码
4. 验证测试通过
5. 更新文档

### 3. 代码审查
- 检查代码规范
- 验证测试覆盖
- 评估性能影响
- 审查安全问题

## 部署说明

### 开发环境
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
python main.py
```

### 生产环境
```bash
# 使用Docker
docker build -t quant-trading-backend .
docker run -p 8000:8000 quant-trading-backend

# 或使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 维护指南

### 日常维护
- 监控日志
- 检查性能
- 备份数据库
- 更新依赖

### 问题排查
1. 查看日志文件
2. 检查数据库状态
3. 验证API响应
4. 分析性能指标

### 数据库维护
- 定期备份
- 清理过期数据
- 优化索引
- 监控大小

## 相关文档

- [文档管理约束](./DOCUMENTATION_GUIDELINES.md)
- [API实现总结](./API_IMPLEMENTATION_SUMMARY.md)
- [性能优化文档](./PERFORMANCE_OPTIMIZATION.md)
- [项目README](../README.md)
