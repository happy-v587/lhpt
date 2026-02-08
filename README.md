# 中国A股量化交易系统

基于Vue 3和Python FastAPI的量化交易平台，支持技术指标计算、策略配置、回测分析和数据可视化。

## 核心功能

- 📊 **技术指标**: 支持12种常用技术指标（MA、EMA、MACD、RSI、BOLL、KDJ、CCI、ATR、OBV、WR、DMI、VWAP）
- 🎯 **策略管理**: 灵活的策略配置，支持多指标组合和买卖条件设置
- 🔄 **回测功能**: 完整的回测引擎，计算夏普比率、最大回撤、胜率等性能指标
- 🎨 **自定义指标**: 支持自定义指标公式和参数配置
- 📈 **数据可视化**: K线图表、指标曲线、资金曲线等多维度展示
- 💾 **数据管理**: 自动获取和更新A股市场数据，历史数据持久化存储
- 🚀 **高性能**: Redis缓存、数据库索引优化、批量操作等性能优化

## 快速开始

详细的安装和使用说明请参考：[快速开始指南](./QUICK_START.md)

### 环境要求

- Python 3.9+
- Node.js 16+
- SQLite 3（开发环境）或 PostgreSQL 12+（生产环境）

### 快速启动

```bash
# 后端
cd backend
source venv/bin/activate
pip install -r requirements.txt
python main.py

# 前端
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173 开始使用

## 项目结构

```
.
├── backend/              # Python后端
│   ├── api/             # API路由和端点
│   ├── models/          # 数据库模型
│   ├── services/        # 业务逻辑服务
│   ├── repositories/    # 数据访问层
│   ├── middleware/      # 中间件（限流、CORS等）
│   ├── validators/      # 数据验证器
│   ├── alembic/         # 数据库迁移
│   ├── tests/           # 单元测试和集成测试
│   ├── scripts/         # 工具脚本
│   └── docs/            # Backend文档
│
├── frontend/            # Vue前端
│   ├── src/
│   │   ├── components/  # Vue组件
│   │   ├── views/       # 页面视图
│   │   ├── services/    # API服务
│   │   ├── utils/       # 工具函数
│   │   └── router/      # 路由配置
│   └── docs/            # Frontend文档
│
├── docs/                # 项目文档
│   ├── guides/          # 使用指南
│   ├── fixes/           # 问题修复记录
│   ├── features/        # 功能实现文档
│   └── archive/         # 归档文档
│
├── README.md            # 项目说明（本文件）
├── QUICK_START.md       # 快速开始指南
└── DOCUMENTATION_GUIDELINES.md  # 文档管理规范
```

详细的目录结构说明：
- [Backend目录结构](./backend/docs/BACKEND_STRUCTURE.md)
- [Frontend目录结构](./frontend/docs/FRONTEND_STRUCTURE.md)（待创建）

## 技术栈

**后端**:
- FastAPI - 现代化的Web框架
- SQLAlchemy - ORM框架
- Pandas & NumPy - 数据处理
- AkShare - A股数据获取
- Redis - 缓存服务
- Alembic - 数据库迁移
- Pytest - 测试框架

**前端**:
- Vue 3 - 渐进式框架
- Vite - 构建工具
- Element Plus - UI组件库
- ECharts - 图表库
- Pinia - 状态管理
- Vue Router - 路由管理

## 文档导航

### 使用指南
- [快速开始指南](./QUICK_START.md) - 安装和基本使用
- [技术指标使用指南](./docs/guides/INDICATOR_GUIDE.md) - 12种技术指标详解
- [回测功能指南](./docs/guides/BACKTEST_GUIDE.md) - 回测功能使用说明
- [API测试指南](./docs/guides/API_TEST_GUIDE.md) - API接口测试方法
- [环境变量配置](./ENVIRONMENT_VARIABLES.md) - 环境变量说明

### 开发文档
- [Backend目录结构](./backend/docs/BACKEND_STRUCTURE.md) - Backend代码组织
- [API实现总结](./backend/docs/API_IMPLEMENTATION_SUMMARY.md) - API设计和实现
- [性能优化文档](./backend/docs/PERFORMANCE_OPTIMIZATION.md) - 性能优化策略
- [文档管理规范](./DOCUMENTATION_GUIDELINES.md) - 文档编写和维护规范

### 功能实现
- [指标提示功能](./docs/features/INDICATOR_TOOLTIP_SUMMARY.md) - Hover提示实现
- [功能更新总结](./docs/features/UPDATE_SUMMARY.md) - 主要功能更新记录

### 问题修复
- [API响应修复](./docs/fixes/API_RESPONSE_FIX.md) - API响应处理问题修复
- [回测功能修复](./docs/fixes/BACKTEST_FIX_SUMMARY.md) - 回测功能问题修复
- [策略视图修复](./docs/fixes/STRATEGY_VIEW_FIX.md) - 策略查看功能修复

## API 文档

启动后端服务后，访问以下地址查看完整的 API 文档：

- **Swagger UI**: http://localhost:8000/docs - 交互式API文档
- **ReDoc**: http://localhost:8000/redoc - 美观的API文档

主要API端点：
- `/api/stocks` - 股票数据管理
- `/api/indicators` - 技术指标计算
- `/api/strategies` - 策略管理
- `/api/backtests` - 回测功能
- `/api/custom-indicators` - 自定义指标

## 开发指南

### 运行测试

```bash
# 后端测试
cd backend
pytest

# 查看测试覆盖率
pytest --cov=. --cov-report=html

# 前端测试
cd frontend
npm run test
```

### 数据库迁移

```bash
cd backend

# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 工具脚本

后端提供了多个实用脚本（在 backend 目录下运行）：

```bash
# 初始化数据库
python scripts/init_db.py

# 验证数据库索引
python scripts/verify_indexes.py

# 演示指标计算器
python scripts/demo_indicator_calculator.py

# 手动测试 API
python scripts/test_api_manual.py

# 测试新功能
python scripts/test_new_features.py
```

### 代码规范

- **Python**: 遵循PEP 8规范，使用类型提示
- **JavaScript**: 遵循ESLint规范
- **提交信息**: 使用语义化提交信息
- **文档**: 遵循[文档管理规范](./DOCUMENTATION_GUIDELINES.md)

## 部署

### Docker 部署（推荐）

```bash
# 开发环境
docker-compose up -d

# 生产环境
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose ps

# 停止服务
docker-compose down
```

### 生产环境部署

#### 后端部署

使用 Gunicorn + Uvicorn：

```bash
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 前端部署

```bash
cd frontend
npm run build
# 将 dist/ 目录部署到 Nginx 或其他静态文件服务器
```

#### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/frontend/dist;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

请确保：
- 代码通过所有测试
- 添加必要的测试用例
- 更新相关文档
- 遵循代码规范

## 常见问题

### Q: 如何获取股票数据？
A: 系统使用AkShare自动获取A股数据，首次使用时会自动下载。

### Q: 回测没有交易记录？
A: 检查策略条件是否合理，可能条件过于严格导致未触发。参考[回测功能指南](./docs/guides/BACKTEST_GUIDE.md)。

### Q: 如何添加自定义指标？
A: 在"自定义指标"页面创建，支持自定义公式。参考[技术指标使用指南](./docs/guides/INDICATOR_GUIDE.md)。

### Q: 前端显示"No data"？
A: 检查后端服务是否启动，API地址是否正确配置。参考[API响应修复](./docs/fixes/API_RESPONSE_FIX.md)。

更多问题请查看各个指南文档或提交Issue。

## 许可证

MIT License

## 联系方式

- 项目地址: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 文档网站: [Documentation Site]

---

**版本**: 1.0.0
**最后更新**: 2024-02-08
