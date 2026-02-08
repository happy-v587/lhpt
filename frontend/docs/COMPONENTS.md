# 前端核心组件

本目录包含中国A股量化交易系统的核心Vue组件。

## 组件列表

### 1. StockSelector（股票选择器）

股票选择下拉框组件，支持搜索过滤功能。

**使用示例：**
```vue
<template>
  <StockSelector
    v-model="selectedStock"
    @change="handleStockChange"
  />
</template>

<script setup>
import { ref } from 'vue'
import { StockSelector } from '@/components'

const selectedStock = ref('')

const handleStockChange = (stock) => {
  console.log('选中的股票:', stock)
}
</script>
```

**Props:**
- `modelValue`: String - 当前选中的股票代码

**Events:**
- `update:modelValue`: 股票代码变化时触发
- `change`: 股票选择变化时触发，参数为完整的股票信息对象

### 2. IndicatorConfig（指标配置器）

技术指标配置组件，支持实时参数验证。

**使用示例：**
```vue
<template>
  <IndicatorConfig
    indicator-type="MA"
    @save="handleSave"
    @cancel="handleCancel"
  />
</template>

<script setup>
import { IndicatorConfig } from '@/components'

const handleSave = (config) => {
  console.log('保存的配置:', config)
  // config: { type: 'MA', params: { periods: [5, 10, 20] } }
}

const handleCancel = () => {
  console.log('取消配置')
}
</script>
```

**Props:**
- `indicatorType`: String - 预设的指标类型（可选）

**Events:**
- `save`: 保存配置时触发，参数为配置对象
- `cancel`: 取消配置时触发

### 3. KLineChart（K线图表）

K线图表组件，集成ECharts，支持指标叠加和周期切换。

**使用示例：**
```vue
<template>
  <KLineChart
    :stock-code="stockCode"
    :period="period"
    :indicators="indicators"
    @period-change="handlePeriodChange"
  />
</template>

<script setup>
import { ref } from 'vue'
import { KLineChart } from '@/components'

const stockCode = ref('600000.SH')
const period = ref('daily')
const indicators = ref([
  { type: 'MA', params: { periods: [5, 10, 20] } },
  { type: 'MACD', params: { fast_period: 12, slow_period: 26, signal_period: 9 } }
])

const handlePeriodChange = (newPeriod) => {
  console.log('周期变化:', newPeriod)
}
</script>
```

**Props:**
- `stockCode`: String (必需) - 股票代码
- `period`: String - 时间周期（daily/weekly/monthly），默认为 'daily'
- `indicators`: Array - 要显示的技术指标数组

**Events:**
- `period-change`: 周期变化时触发

### 4. StrategyManager（策略管理器）

策略管理组件，支持创建、查看和删除策略。

**使用示例：**
```vue
<template>
  <StrategyManager />
</template>

<script setup>
import { StrategyManager } from '@/components'
</script>
```

**功能：**
- 显示策略列表
- 创建新策略（包含指标和交易条件）
- 查看策略详情
- 删除策略（带确认）

## 依赖

所有组件依赖以下库：
- Vue 3
- Element Plus
- ECharts（仅KLineChart）
- Axios（通过services层）

## 注意事项

1. 所有组件都使用 Composition API 编写
2. 组件使用 Element Plus 的 UI 组件库
3. API 调用通过 `@/services` 层进行
4. 组件包含实时验证和错误处理
5. 支持响应式设计
