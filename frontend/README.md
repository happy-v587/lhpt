# 量化交易系统 - 前端

基于 Vue 3 + Vite + Element Plus 的量化交易系统前端应用。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Element Plus** - Vue 3 组件库
- **Vue Router** - 官方路由管理器
- **Pinia** - Vue 状态管理
- **Axios** - HTTP 客户端
- **ECharts** - 数据可视化图表库
- **Sass** - CSS 预处理器

## 项目结构

```
frontend/
├── src/
│   ├── assets/          # 静态资源（图片、字体等）
│   ├── components/      # 可复用组件
│   │   ├── IndicatorConfig.vue      # 指标配置组件
│   │   ├── KLineChart.vue           # K线图表组件
│   │   ├── StockSelector.vue        # 股票选择器
│   │   └── StrategyManager.vue      # 策略管理器
│   ├── router/          # 路由配置
│   ├── services/        # API 服务层
│   │   ├── api.js                   # API 基础配置
│   │   ├── stocks.js                # 股票 API
│   │   ├── strategies.js            # 策略 API
│   │   ├── backtests.js             # 回测 API
│   │   ├── indicators.js            # 指标 API
│   │   └── customIndicators.js      # 自定义指标 API
│   ├── stores/          # Pinia 状态管理
│   ├── utils/           # 工具函数
│   │   └── indicatorDescriptions.js # 指标描述
│   ├── views/           # 页面视图
│   │   ├── HomeView.vue             # 首页
│   │   ├── ChartView.vue            # 图表视图
│   │   ├── BacktestView.vue         # 回测视图
│   │   ├── StrategyView.vue         # 策略视图
│   │   ├── CustomIndicatorView.vue  # 自定义指标视图
│   │   └── IndicatorConfigView.vue  # 指标配置视图
│   ├── App.vue          # 根组件
│   └── main.js          # 应用入口
├── docs/                # 文档目录
│   ├── README.md                    # 文档索引
│   ├── FRONTEND_UPDATES.md          # 更新日志
│   ├── STRATEGY_CONDITION_GUIDE.md  # 策略条件指南
│   └── COMPONENTS.md                # 组件说明
├── dist/                # 构建输出目录
├── index.html           # HTML 入口模板
├── vite.config.js       # Vite 配置文件
├── package.json         # 项目依赖配置
├── Dockerfile           # Docker 镜像配置
├── nginx.conf           # Nginx 配置
├── .env                 # 环境变量
└── .env.example         # 环境变量示例

```

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:5173

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 环境变量

复制 `.env.example` 到 `.env` 并配置：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 主要功能

### 1. 股票数据查看
- 实时 K 线图表展示
- 多种技术指标叠加
- 支持多时间周期切换

### 2. 策略管理
- 创建和编辑交易策略
- 可视化策略条件配置
- 策略参数调整

### 3. 回测系统
- 历史数据回测
- 回测结果可视化
- 性能指标分析

### 4. 自定义指标
- 创建自定义技术指标
- Python 代码编辑器
- 指标测试和验证

## 文档

详细文档请查看 [docs](./docs/) 目录：

- [前端更新日志](./docs/FRONTEND_UPDATES.md)
- [策略条件指南](./docs/STRATEGY_CONDITION_GUIDE.md)
- [组件使用说明](./docs/COMPONENTS.md)

## Docker 部署

### 构建镜像

```bash
docker build -t quant-trading-frontend .
```

### 运行容器

```bash
docker run -p 80:80 quant-trading-frontend
```

## 开发规范

- 使用 Vue 3 Composition API
- 组件命名采用 PascalCase
- 文件命名采用 camelCase
- 遵循 ESLint 代码规范
- 提交前确保代码通过测试

## 测试

```bash
npm run test
```

## 许可证

MIT
