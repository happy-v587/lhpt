<template>
  <div class="chart-view">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>数据可视化</h2>
          <el-text type="info">查看K线图表和技术指标</el-text>
        </div>
      </template>

      <div class="chart-content">
        <!-- 控制面板 -->
        <el-card shadow="never" class="control-panel">
          <div class="controls">
            <!-- 股票选择 -->
            <div class="control-item">
              <label>选择股票:</label>
              <StockSelector
                v-model="selectedStock"
                @change="handleStockChange"
              />
            </div>

            <!-- 周期切换 -->
            <div class="control-item">
              <label>时间周期:</label>
              <el-radio-group v-model="period" @change="handlePeriodChange">
                <el-radio-button label="daily">日线</el-radio-button>
                <el-radio-button label="weekly">周线</el-radio-button>
                <el-radio-button label="monthly">月线</el-radio-button>
              </el-radio-group>
            </div>

            <!-- 指标管理 -->
            <div class="control-item">
              <label>技术指标:</label>
              <el-button
                type="primary"
                size="small"
                @click="showAddIndicator = true"
              >
                <el-icon><Plus /></el-icon>
                添加指标
              </el-button>
            </div>
          </div>

          <!-- 已添加的指标 -->
          <div v-if="indicators.length > 0" class="indicators-list">
            <el-tag
              v-for="(indicator, index) in indicators"
              :key="index"
              closable
              @close="removeIndicator(index)"
              size="large"
              type="success"
              class="indicator-tag"
            >
              <strong>{{ indicator.type }}</strong>: {{ formatParams(indicator.params) }}
            </el-tag>
          </div>
          <el-empty
            v-else
            description="暂未添加技术指标"
            :image-size="60"
          />
        </el-card>

        <!-- K线图表 -->
        <el-card shadow="never" class="chart-card">
          <div v-if="!selectedStock" class="empty-chart">
            <el-empty description="请先选择股票" :image-size="100" />
          </div>
          <KLineChart
            v-else
            :stock-code="selectedStock"
            :period="period"
            :indicators="indicators"
            @period-change="handlePeriodChange"
          />
        </el-card>
      </div>
    </el-card>

    <!-- 添加指标对话框 -->
    <el-dialog
      v-model="showAddIndicator"
      title="添加技术指标"
      width="500px"
    >
      <IndicatorConfig
        @save="handleIndicatorAdd"
        @cancel="showAddIndicator = false"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import StockSelector from '@/components/StockSelector.vue'
import KLineChart from '@/components/KLineChart.vue'
import IndicatorConfig from '@/components/IndicatorConfig.vue'
import { ElMessage } from 'element-plus'

const selectedStock = ref('')
const period = ref('daily')
const indicators = ref([])
const showAddIndicator = ref(false)

// 处理股票变化
const handleStockChange = (stock) => {
  ElMessage.success(`已选择股票: ${stock.name}`)
}

// 处理周期变化
const handlePeriodChange = (newPeriod) => {
  period.value = newPeriod
}

// 添加指标
const handleIndicatorAdd = (indicator) => {
  // 检查是否已存在相同配置的指标
  const exists = indicators.value.some(
    ind => ind.type === indicator.type && 
    JSON.stringify(ind.params) === JSON.stringify(indicator.params)
  )
  
  if (exists) {
    ElMessage.warning('该指标配置已存在')
    return
  }
  
  indicators.value.push(indicator)
  showAddIndicator.value = false
  ElMessage.success('指标添加成功')
}

// 移除指标
const removeIndicator = (index) => {
  indicators.value.splice(index, 1)
  ElMessage.success('指标已移除')
}

// 格式化参数显示
const formatParams = (params) => {
  return Object.entries(params)
    .map(([key, value]) => {
      if (Array.isArray(value)) {
        return `${key}=[${value.join(', ')}]`
      }
      return `${key}=${value}`
    })
    .join(', ')
}
</script>

<style scoped>
.chart-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-card {
  min-height: calc(100vh - 100px);
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.chart-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.control-panel {
  border: 1px solid #e4e7ed;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: flex-start;
}

.control-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 200px;
}

.control-item label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.indicators-list {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.indicator-tag {
  padding: 8px 12px;
  font-size: 14px;
}

.indicator-tag strong {
  margin-right: 4px;
}

.chart-card {
  border: 1px solid #e4e7ed;
  min-height: 600px;
}

.empty-chart {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 500px;
}
</style>
