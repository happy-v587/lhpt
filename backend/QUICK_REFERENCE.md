# Backend 快速参考

## 常用命令

### 环境管理
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 更新依赖
pip freeze > requirements.txt
```

### 数据库操作
```bash
# 初始化数据库
python scripts/init_db.py

# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history

# 验证索引
python scripts/verify_indexes.py
```

### 启动服务
```bash
# 开发模式（自动重载）
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api_endpoints.py

# 运行特定测试函数
pytest tests/test_api_endpoints.py::test_get_stocks

# 显示详细输出
pytest -v

# 显示打印输出
pytest -s

# 生成覆盖率报告
pytest --cov=. --cov-report=html

# 运行并停在第一个失败
pytest -x
```

### 工具脚本
```bash
# 演示指标计算
python scripts/demo_indicator_calculator.py

# 演示验证和限流
python scripts/demo_validation_and_rate_limiting.py

# 手动测试 API
python scripts/test_api_manual.py

# 测试新功能
python scripts/test_new_features.py
```

### Docker
```bash
# 构建镜像
docker build -t quant-trading-backend .

# 运行容器
docker run -p 8000:8000 quant-trading-backend

# 使用 docker-compose
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

## 项目结构速查

```
backend/
├── api/              # API 端点
├── models/           # 数据模型
├── services/         # 业务逻辑
├── repositories/     # 数据访问
├── middleware/       # 中间件
├── validators/       # 验证器
├── alembic/          # 数据库迁移
├── tests/            # 测试
├── scripts/          # 工具脚本
├── docs/             # 文档
├── data/             # 数据文件
└── main.py           # 入口文件
```

## API 端点速查

### 股票数据
```
GET    /api/stocks                    # 获取股票列表
GET    /api/stocks/{symbol}/klines    # 获取K线数据
```

### 技术指标
```
GET    /api/indicators/calculate      # 计算指标
GET    /api/indicators/list           # 指标列表
```

### 自定义指标
```
POST   /api/custom-indicators         # 创建
GET    /api/custom-indicators         # 列表
GET    /api/custom-indicators/{id}    # 详情
PUT    /api/custom-indicators/{id}    # 更新
DELETE /api/custom-indicators/{id}    # 删除
POST   /api/custom-indicators/{id}/execute  # 执行
```

### 策略
```
POST   /api/strategies                # 创建
GET    /api/strategies                # 列表
GET    /api/strategies/{id}           # 详情
PUT    /api/strategies/{id}           # 更新
DELETE /api/strategies/{id}           # 删除
```

### 回测
```
POST   /api/backtests                 # 创建
GET    /api/backtests                 # 列表
GET    /api/backtests/{id}            # 详情
DELETE /api/backtests/{id}            # 删除
```

## 环境变量

```env
# 数据库
DATABASE_URL=sqlite:///./data/quant_trading.db

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# 调试模式
DEBUG=True

# 日志级别
LOG_LEVEL=INFO

# API 限流
RATE_LIMIT_PER_MINUTE=60
```

## 常见问题

### 1. 数据库锁定
```bash
# 关闭所有连接后重试
rm data/quant_trading.db
python scripts/init_db.py
```

### 2. 依赖安装失败
```bash
# 升级 pip
pip install --upgrade pip

# 清除缓存
pip cache purge

# 重新安装
pip install -r requirements.txt
```

### 3. 测试失败
```bash
# 清除缓存
pytest --cache-clear

# 重新运行
pytest -v
```

### 4. 端口被占用
```bash
# 查找占用端口的进程
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# 杀死进程
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

## 开发流程

### 新增 API 端点
1. 在 `models/` 定义数据模型
2. 在 `repositories/` 添加数据访问方法
3. 在 `services/` 实现业务逻辑
4. 在 `api/` 添加路由端点
5. 在 `tests/` 编写测试
6. 更新文档

### 修改现有功能
1. 修改相应模块代码
2. 更新测试用例
3. 运行测试确保通过
4. 更新文档

### 数据库变更
1. 修改 `models/` 中的模型
2. 创建迁移: `alembic revision --autogenerate -m "描述"`
3. 检查生成的迁移文件
4. 应用迁移: `alembic upgrade head`
5. 测试验证

## 代码规范

### Python 风格
```python
# 导入顺序
import os  # 标准库
import sys

from fastapi import FastAPI  # 第三方库

from models import Stock  # 本地模块

# 类型注解
def get_stock(symbol: str) -> Stock:
    pass

# 文档字符串
def calculate_ma(data: list, period: int) -> list:
    """
    计算移动平均线
    
    Args:
        data: 价格数据列表
        period: 周期
        
    Returns:
        移动平均值列表
    """
    pass
```

### 命名规范
```python
# 变量和函数: snake_case
stock_data = get_stock_data()

# 类名: PascalCase
class DataProvider:
    pass

# 常量: UPPER_CASE
MAX_RETRY_COUNT = 3

# 私有方法: _前缀
def _internal_method():
    pass
```

## 性能优化技巧

### 1. 数据库查询
```python
# 使用索引
# 批量查询
# 避免 N+1 查询
# 使用 select_related/joinedload
```

### 2. 缓存
```python
# 使用 cache_service
# 设置合理的过期时间
# 缓存热点数据
```

### 3. 异步操作
```python
# 使用 async/await
# 并发处理独立任务
# 使用连接池
```

## 调试技巧

### 1. 日志
```python
import logging

logger = logging.getLogger(__name__)
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
```

### 2. 断点调试
```python
# 使用 pdb
import pdb; pdb.set_trace()

# 或使用 IDE 断点
```

### 3. API 测试
```bash
# 使用 curl
curl -X GET "http://localhost:8000/api/stocks"

# 使用 httpie
http GET localhost:8000/api/stocks

# 访问 Swagger UI
open http://localhost:8000/docs
```

## 有用的链接

- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 文档导航

- [完整 README](./README.md)
- [项目结构详解](./docs/PROJECT_STRUCTURE.md)
- [后端架构](./docs/BACKEND_STRUCTURE.md)
- [性能优化](./docs/PERFORMANCE_OPTIMIZATION.md)
- [文档索引](./docs/README.md)
