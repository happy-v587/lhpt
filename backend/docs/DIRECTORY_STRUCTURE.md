# Backend 目录结构整理说明

## 整理日期
2026-02-08

## 整理内容

### 1. 新增目录

- **scripts/** - 工具脚本和演示代码
- **docs/** - 项目文档
- **data/** - 本地数据库文件（不提交到 git）

### 2. 文件迁移

#### scripts/ 目录
- `init_db.py` - 数据库初始化脚本
- `verify_indexes.py` - 数据库索引验证脚本
- `demo_indicator_calculator.py` - 指标计算器演示
- `demo_validation_and_rate_limiting.py` - 数据验证和限流演示
- `test_api_manual.py` - 手动 API 测试脚本

#### docs/ 目录
- `API_CHECKPOINT_SUMMARY.md`
- `API_IMPLEMENTATION_SUMMARY.md`
- `PERFORMANCE_OPTIMIZATION.md`
- `TASK_9_IMPLEMENTATION_SUMMARY.md`

#### data/ 目录
- `quant_trading.db` - 主数据库
- `test_cache.db` - 测试缓存数据库
- `.gitignore` - 忽略数据库文件

### 3. 代码修改

所有 scripts 目录下的脚本都已更新导入路径：

```python
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

这样可以从 backend 根目录正常运行脚本。

### 4. 依赖更新

更新 `requirements.txt` 中的 SQLAlchemy 版本：
- 从 `sqlalchemy==2.0.25` 改为 `sqlalchemy>=2.0.46`
- 原因：Python 3.14 兼容性要求

## 使用方法

### 运行脚本

所有脚本都需要在 backend 目录下运行：

```bash
cd backend
source venv/bin/activate

# 初始化数据库
python scripts/init_db.py

# 验证索引
python scripts/verify_indexes.py

# 演示功能
python scripts/demo_indicator_calculator.py
python scripts/demo_validation_and_rate_limiting.py

# 测试 API
python scripts/test_api_manual.py
```

## 目录结构

```
backend/
├── api/              # API 路由
├── models/           # 数据模型
├── services/         # 业务服务
├── repositories/     # 数据访问
├── middleware/       # 中间件
├── validators/       # 验证器
├── alembic/          # 数据库迁移
├── tests/            # 测试
├── scripts/          # 工具脚本 ✨ 新增
├── docs/             # 文档 ✨ 新增
├── data/             # 数据库文件 ✨ 新增
├── main.py           # 应用入口
├── config.py         # 配置
├── database.py       # 数据库连接
└── exceptions.py     # 异常定义
```

## 优势

1. **清晰的目录结构** - 核心代码和辅助文件分离
2. **易于维护** - 文档和脚本集中管理
3. **版本控制友好** - 数据库文件自动忽略
4. **开发体验提升** - 更容易找到需要的文件
