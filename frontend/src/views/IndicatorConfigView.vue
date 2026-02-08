<template>
  <div class="indicator-config-view">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>技术指标配置</h2>
          <el-text type="info">选择股票并配置技术指标参数</el-text>
        </div>
      </template>

      <div class="config-content">
        <!-- 股票选择器 -->
        <el-card shadow="never" class="section-card">
          <template #header>
            <h3>选择股票</h3>
          </template>
          <StockSelector
            v-model="selectedStock"
            @change="handleStockChange"
          />
          <div v-if="currentStockInfo" class="stock-info">
            <el-descriptions :column="2" size="small" border>
              <el-descriptions-item label="股票代码">
                {{ currentStockInfo.code }}
              </el-descriptions-item>
              <el-descriptions-item label="股票名称">
                {{ currentStockInfo.name }}
              </el-descriptions-item>
              <el-descriptions-item label="交易所">
                {{ currentStockInfo.exchange }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>

        <!-- 指标配置器 -->
        <el-card shadow="never" class="section-card">
          <template #header>
            <h3>配置技术指标</h3>
          </template>
          <IndicatorConfig
            @save="handleSave"
            @cancel="handleCancel"
          />
        </el-card>

        <!-- 已保存的配置列表 -->
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="saved-header">
              <h3>已保存的配置</h3>
              <el-button
                v-if="savedConfigs.length > 0"
                type="danger"
                size="small"
                @click="clearAllConfigs"
              >
                清空所有
              </el-button>
            </div>
          </template>
          <div v-if="savedConfigs.length === 0" class="empty-state">
            <el-empty description="暂无保存的配置" />
          </div>
          <div v-else class="saved-configs">
            <el-tag
              v-for="(config, index) in savedConfigs"
              :key="index"
              closable
              @close="removeConfig(index)"
              size="large"
              class="config-tag"
            >
              <strong>{{ config.type }}</strong>: {{ formatParams(config.params) }}
            </el-tag>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import StockSelector from '@/components/StockSelector.vue'
import IndicatorConfig from '@/components/IndicatorConfig.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const selectedStock = ref('')
const currentStockInfo = ref(null)
const savedConfigs = ref([])

// 处理股票变化
const handleStockChange = (stock) => {
  currentStockInfo.value = stock
  ElMessage.success(`已选择股票: ${stock.name}`)
}

// 处理保存配置
const handleSave = (config) => {
  savedConfigs.value.push({
    ...config,
    stockCode: selectedStock.value,
    timestamp: new Date().toISOString()
  })
  ElMessage.success('配置已保存')
}

// 处理取消
const handleCancel = () => {
  ElMessage.info('已取消配置')
}

// 移除配置
const removeConfig = (index) => {
  savedConfigs.value.splice(index, 1)
  ElMessage.success('配置已删除')
}

// 清空所有配置
const clearAllConfigs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有已保存的配置吗？',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    savedConfigs.value = []
    ElMessage.success('已清空所有配置')
  } catch (error) {
    // 用户取消
  }
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
.indicator-config-view {
  max-width: 1200px;
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

.config-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-card {
  border: 1px solid #e4e7ed;
}

.section-card h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.stock-info {
  margin-top: 16px;
}

.saved-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-state {
  padding: 40px 0;
}

.saved-configs {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.config-tag {
  padding: 8px 12px;
  font-size: 14px;
}

.config-tag strong {
  color: #409eff;
  margin-right: 4px;
}
</style>
