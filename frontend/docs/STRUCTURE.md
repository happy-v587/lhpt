# Frontend 项目结构说明

## 整理日期
2026-02-08

## 目录结构

### 根目录文件
```
frontend/
├── .dockerignore        # Docker 忽略文件配置
├── .env                 # 环境变量（不提交到 Git）
├── .env.example         # 环境变量示例
├── .gitignore           # Git 忽略文件配置
├── Dockerfile           # Docker 镜像构建配置
├── index.html           # HTML 入口模板
├── nginx.conf           # Nginx 服务器配置
├── package.json         # NPM 依赖和脚本配置
├── package-lock.json    # NPM 依赖锁定文件
├── README.md            # 项目主文档
└── vite.config.js       # Vite 构建工具配置
```

### 源代码目录 (src/)
```
src/
├── assets/              # 静态资源（图片、字体等）
├── components/          # 可复用 Vue 组件
│   ├── index.js                 # 组件导出索引
│   ├── IndicatorConfig.vue      # 指标配置组件
│   ├── KLineChart.vue           # K线图表组件
│   ├── StockSelector.vue        # 股票选择器组件
│   └── StrategyManager.vue      # 策略管理器组件
├── router/              # Vue Router 路由配置
│   └── index.js                 # 路由定义
├── services/            # API 服务层
│   ├── api.js                   # Axios 基础配置
│   ├── api.test.js              # API 测试
│   ├── backtests.js             # 回测相关 API
│   ├── customIndicators.js      # 自定义指标 API
│   ├── index.js                 # 服务导出索引
│   ├── indicators.js            # 指标 API
│   ├── stocks.js                # 股票数据 API
│   └── strategies.js            # 策略 API
├── stores/              # Pinia 状态管理（待实现）
├── utils/               # 工具函数
│   └── indicatorDescriptions.js # 指标描述信息
├── views/               # 页面视图组件
│   ├── BacktestView.vue         # 回测页面
│   ├── ChartView.vue            # 图表页面
│   ├── CustomIndicatorView.vue  # 自定义指标页面
│   ├── HomeView.vue             # 首页
│   ├── IndicatorConfigView.vue  # 指标配置页面
│   └── StrategyView.vue         # 策略页面
├── App.vue              # 根组件
└── main.js              # 应用入口文件
```

### 文档目录 (docs/)
```
docs/
├── README.md                    # 文档索引
├── COMPONENTS.md                # 组件使用说明
├── FRONTEND_UPDATES.md          # 前端更新日志
├── STRATEGY_CONDITION_GUIDE.md  # 策略条件配置指南
└── STRUCTURE.md                 # 项目结构说明（本文件）
```

### 构建输出目录 (dist/)
```
dist/                    # Vite 构建输出（不提交到 Git）
├── assets/              # 打包后的静态资源
└── index.html           # 打包后的 HTML 文件
```

### 依赖目录 (node_modules/)
```
node_modules/            # NPM 依赖包（不提交到 Git）
```

## 文件命名规范

### Vue 组件
- **组件文件**: PascalCase（如 `KLineChart.vue`）
- **视图文件**: PascalCase + View 后缀（如 `HomeView.vue`）

### JavaScript 文件
- **服务文件**: camelCase（如 `customIndicators.js`）
- **工具文件**: camelCase（如 `indicatorDescriptions.js`）
- **配置文件**: kebab-case 或 camelCase（如 `vite.config.js`）

### 文档文件
- **说明文档**: UPPERCASE + 下划线（如 `FRONTEND_UPDATES.md`）
- **主文档**: README.md

## 代码组织原则

### 1. 关注点分离
- **components/**: 纯展示组件，可复用
- **views/**: 页面级组件，包含业务逻辑
- **services/**: API 调用封装
- **stores/**: 全局状态管理
- **utils/**: 纯函数工具

### 2. 模块化
- 每个功能模块独立
- 通过 index.js 统一导出
- 避免循环依赖

### 3. 可维护性
- 单一职责原则
- 代码注释清晰
- 文档及时更新

## 开发工作流

### 1. 新增功能
```
1. 在 views/ 创建页面组件
2. 在 router/ 添加路由
3. 在 services/ 添加 API 调用
4. 在 components/ 创建可复用组件
5. 更新相关文档
```

### 2. 修改组件
```
1. 修改组件代码
2. 更新组件文档
3. 运行测试确保无破坏性变更
```

### 3. API 集成
```
1. 在 services/ 对应文件添加 API 方法
2. 使用统一的错误处理
3. 添加必要的类型注释
```

## 待优化项

- [ ] 添加 TypeScript 支持
- [ ] 完善 Pinia 状态管理
- [ ] 增加单元测试覆盖率
- [ ] 添加 E2E 测试
- [ ] 优化构建性能
- [ ] 添加代码分割
- [ ] 实现国际化（i18n）
- [ ] 添加主题切换功能

## 相关链接

- [Vue 3 文档](https://vuejs.org/)
- [Vite 文档](https://vitejs.dev/)
- [Element Plus 文档](https://element-plus.org/)
- [Vue Router 文档](https://router.vuejs.org/)
- [Pinia 文档](https://pinia.vuejs.org/)
