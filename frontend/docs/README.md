# Frontend 文档

## 文档索引

- [前端更新日志](./FRONTEND_UPDATES.md) - 前端功能更新和变更记录
- [策略条件指南](./STRATEGY_CONDITION_GUIDE.md) - 策略条件配置使用指南
- [组件说明](./COMPONENTS.md) - 前端组件使用说明

## 项目结构

```
frontend/
├── src/
│   ├── assets/          # 静态资源
│   ├── components/      # 可复用组件
│   ├── router/          # 路由配置
│   ├── services/        # API 服务层
│   ├── stores/          # 状态管理
│   ├── utils/           # 工具函数
│   ├── views/           # 页面视图
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── docs/                # 文档目录
├── dist/                # 构建输出
├── index.html           # HTML 模板
├── package.json         # 依赖配置
└── vite.config.js       # Vite 配置

```

## 主要组件

- **IndicatorConfig.vue** - 指标配置组件
- **KLineChart.vue** - K线图表组件
- **StockSelector.vue** - 股票选择器
- **StrategyManager.vue** - 策略管理器

## 主要视图

- **HomeView.vue** - 首页
- **ChartView.vue** - 图表视图
- **BacktestView.vue** - 回测视图
- **StrategyView.vue** - 策略视图
- **CustomIndicatorView.vue** - 自定义指标视图
- **IndicatorConfigView.vue** - 指标配置视图

## 服务层

- **api.js** - API 基础配置
- **stocks.js** - 股票相关 API
- **strategies.js** - 策略相关 API
- **backtests.js** - 回测相关 API
- **indicators.js** - 指标相关 API
- **customIndicators.js** - 自定义指标相关 API
