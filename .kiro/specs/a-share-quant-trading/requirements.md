# 需求文档

## 简介

中国A股量化交易系统是一个基于Vue前端和Python后端的量化交易平台。该系统允许用户通过Web界面配置技术指标和交易策略，后端负责从数据源获取A股市场数据、存储历史数据、计算技术指标，并提供RESTful API接口供前端调用。

## 术语表

- **System**: 中国A股量化交易系统
- **Frontend**: 基于Vue.js的Web用户界面
- **Backend**: 基于Python的API服务器
- **Data_Provider**: 外部A股数据源接口（推荐使用AkShare或Tushare Python库）
- **Database**: 数据存储层（推荐使用SQLite或PostgreSQL）
- **Indicator**: 技术指标（如MA、MACD、RSI等）
- **Strategy**: 基于指标的交易策略配置
- **Stock_Code**: A股股票代码（如600000.SH表示浦发银行上交所，000001.SZ表示平安银行深交所）
- **AkShare**: 开源的Python金融数据接口库，提供免费的A股数据
- **Tushare**: Python金融数据接口，提供A股、基金、期货等数据（需注册token）

## 需求

### 需求 1: 股票数据获取

**用户故事:** 作为系统管理员，我希望系统能够自动获取A股市场数据，以便为量化分析提供数据基础。

#### 验收标准

1. WHEN 系统启动时，THE System SHALL 初始化Data_Provider连接（使用AkShare或Tushare库）
2. WHEN 用户请求股票数据时，THE System SHALL 通过Data_Provider获取指定Stock_Code的实时行情数据
3. WHEN 获取历史数据时，THE System SHALL 支持按日期范围查询K线数据（日线、周线、月线）
4. THE System SHALL 支持获取股票基本信息（股票名称、所属行业、上市日期等）
5. IF Data_Provider调用失败或超时，THEN THE System SHALL 记录错误日志并返回明确的错误信息
6. WHEN 数据获取成功时，THE System SHALL 在2秒内返回响应
7. THE System SHALL 遵守数据源的访问频率限制，避免被封禁

### 需求 2: 数据存储管理

**用户故事:** 作为系统，我需要持久化存储股票数据，以便支持历史数据查询和回测分析。

#### 验收标准

1. WHEN 接收到新的股票数据时，THE Database SHALL 存储包含日期、开盘价、收盘价、最高价、最低价、成交量的完整记录
2. WHEN 存储重复日期的数据时，THE System SHALL 更新现有记录而不是创建重复条目
3. WHEN 查询历史数据时，THE Database SHALL 在500毫秒内返回最近3年的数据
4. THE System SHALL 每日自动更新所有已关注股票的最新数据
5. WHEN 数据库空间不足时，THE System SHALL 记录警告并通知管理员

### 需求 3: 技术指标计算

**用户故事:** 作为量化交易者，我希望系统能够计算常用技术指标，以便进行技术分析和策略开发。

#### 验收标准

1. WHEN 用户请求计算移动平均线（MA）时，THE System SHALL 支持5日、10日、20日、60日等自定义周期
2. WHEN 用户请求MACD指标时，THE System SHALL 计算DIF、DEA和MACD柱状图值
3. WHEN 用户请求RSI指标时，THE System SHALL 支持6日、12日、24日等自定义周期
4. WHEN 用户请求布林带（BOLL）时，THE System SHALL 计算上轨、中轨、下轨三条线
5. WHEN 计算指标时，THE System SHALL 使用标准的技术分析公式确保计算准确性
6. IF 数据不足以计算指标，THEN THE System SHALL 返回明确的错误提示

### 需求 4: 后端API接口

**用户故事:** 作为前端开发者，我需要清晰的RESTful API接口，以便前端能够获取数据和配置策略。

#### 验收标准

1. THE Backend SHALL 提供GET /api/stocks端点返回所有可用股票列表
2. THE Backend SHALL 提供GET /api/stocks/{code}/kline端点返回指定股票的K线数据
3. THE Backend SHALL 提供POST /api/indicators/calculate端点接收指标配置并返回计算结果
4. THE Backend SHALL 提供GET /api/strategies端点返回用户保存的策略列表
5. THE Backend SHALL 提供POST /api/strategies端点创建新的策略配置
6. WHEN API请求失败时，THE Backend SHALL 返回标准的HTTP状态码和JSON格式的错误信息
7. THE Backend SHALL 支持CORS跨域请求以允许前端访问

### 需求 5: 前端指标配置界面

**用户故事:** 作为量化交易者，我希望通过可视化界面配置技术指标参数，以便快速测试不同的策略组合。

#### 验收标准

1. WHEN 用户访问配置页面时，THE Frontend SHALL 显示可用的技术指标列表
2. WHEN 用户选择一个指标时，THE Frontend SHALL 显示该指标的可配置参数（如周期、阈值等）
3. WHEN 用户修改参数时，THE Frontend SHALL 实时验证输入的有效性
4. WHEN 用户保存配置时，THE Frontend SHALL 发送POST请求到Backend并显示保存结果
5. WHEN 配置保存成功时，THE Frontend SHALL 清空表单并显示成功提示

### 需求 6: 数据可视化展示

**用户故事:** 作为量化交易者，我希望看到K线图和指标曲线的可视化展示，以便直观分析市场走势。

#### 验收标准

1. WHEN 用户选择一只股票时，THE Frontend SHALL 显示该股票的K线图
2. WHEN 用户添加技术指标时，THE Frontend SHALL 在图表上叠加显示指标曲线
3. WHEN 用户缩放或拖动图表时，THE Frontend SHALL 保持流畅的交互体验
4. THE Frontend SHALL 支持切换日线、周线、月线等不同时间周期
5. WHEN 鼠标悬停在K线上时，THE Frontend SHALL 显示该日期的详细数据

### 需求 7: 策略配置与管理

**用户故事:** 作为量化交易者，我希望能够创建、保存和管理多个交易策略，以便进行策略对比和优化。

#### 验收标准

1. WHEN 用户创建新策略时，THE System SHALL 允许命名策略并添加描述
2. WHEN 用户配置策略时，THE System SHALL 支持组合多个技术指标作为买卖条件
3. WHEN 用户保存策略时，THE System SHALL 将策略配置持久化到Database
4. WHEN 用户查看策略列表时，THE System SHALL 显示所有已保存的策略及其基本信息
5. WHEN 用户删除策略时，THE System SHALL 请求确认并从Database中移除该策略

### 需求 8: 系统错误处理

**用户故事:** 作为系统架构师，我希望系统具有完善的错误处理机制，以便提高系统稳定性和用户体验。

#### 验收标准

1. WHEN Backend发生异常时，THE System SHALL 捕获异常并记录到日志文件
2. WHEN 数据源不可用时，THE System SHALL 尝试使用缓存数据并通知用户
3. WHEN 用户输入无效参数时，THE System SHALL 返回清晰的验证错误信息
4. WHEN 系统负载过高时，THE System SHALL 实施请求限流保护
5. IF 数据库连接失败，THEN THE System SHALL 自动重试最多3次

### 需求 9: 数据安全与验证

**用户故事:** 作为系统管理员，我希望系统能够验证和清洗数据，以便确保数据质量和系统安全。

#### 验收标准

1. WHEN 接收外部数据时，THE System SHALL 验证数据格式和完整性
2. WHEN 检测到异常数据（如价格为负数）时，THE System SHALL 拒绝存储并记录警告
3. WHEN 用户输入Stock_Code时，THE System SHALL 验证代码格式符合A股规范（6位数字+交易所后缀）
4. THE System SHALL 对所有API输入参数进行类型和范围验证
5. WHEN SQL查询构建时，THE System SHALL 使用参数化查询防止SQL注入

### 需求 10: 性能与可扩展性

**用户故事:** 作为系统架构师，我希望系统具有良好的性能和可扩展性，以便支持更多用户和数据量。

#### 验收标准

1. WHEN 计算技术指标时，THE System SHALL 使用向量化计算提高性能
2. WHEN 多个用户同时请求时，THE System SHALL 支持并发处理至少100个请求
3. THE System SHALL 对频繁查询的数据实施缓存机制
4. WHEN 添加新的技术指标时，THE System SHALL 通过插件化架构支持扩展
5. THE Database SHALL 对常用查询字段（如股票代码、日期）建立索引
