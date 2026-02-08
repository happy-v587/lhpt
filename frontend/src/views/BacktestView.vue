<template>
  <div class="backtest-view">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>策略回测</h2>
          <el-text type="info">运行策略回测并查看性能指标</el-text>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="backtest-tabs">
        <!-- 运行回测 -->
        <el-tab-pane label="运行回测" name="run">
          <el-card shadow="never" class="run-card">
            <el-form
              ref="backtestFormRef"
              :model="backtestForm"
              :rules="backtestRules"
              label-width="120px"
              class="backtest-form"
            >
              <el-form-item label="选择策略" prop="strategy_id">
                <el-select
                  v-model="backtestForm.strategy_id"
                  placeholder="请选择策略"
                  style="width: 100%"
                  @change="handleStrategyChange"
                >
                  <el-option
                    v-for="strategy in strategies"
                    :key="strategy.id"
                    :label="strategy.name"
                    :value="strategy.id"
                  >
                    <span>{{ strategy.name }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">
                      {{ strategy.description }}
                    </span>
                  </el-option>
                </el-select>
              </el-form-item>

              <el-form-item label="股票代码" prop="stock_code">
                <StockSelector v-model="backtestForm.stock_code" />
              </el-form-item>

              <el-form-item label="回测时间" prop="dateRange">
                <el-date-picker
                  v-model="backtestForm.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item label="初始资金">
                <el-input-number
                  v-model="backtestForm.initial_capital"
                  :min="10000"
                  :max="10000000"
                  :step="10000"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item label="手续费率">
                <el-input-number
                  v-model="backtestForm.commission_rate"
                  :min="0"
                  :max="0.01"
                  :step="0.0001"
                  :precision="4"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item label="滑点率">
                <el-input-number
                  v-model="backtestForm.slippage_rate"
                  :min="0"
                  :max="0.01"
                  :step="0.0001"
                  :precision="4"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  :loading="running"
                  @click="handleRunBacktest"
                >
                  <el-icon v-if="!running"><VideoPlay /></el-icon>
                  {{ running ? '回测运行中...' : '开始回测' }}
                </el-button>
                <el-button @click="resetForm">重置</el-button>
              </el-form-item>
            </el-form>

            <!-- 回测结果 -->
            <div v-if="currentResult" class="result-section">
              <el-divider content-position="left">
                <h3>回测结果</h3>
              </el-divider>

              <el-row :gutter="20" class="metrics-row">
                <el-col :span="6">
                  <el-tooltip
                    :content="getMetricTooltip('sharpe_ratio')"
                    placement="top"
                    effect="light"
                  >
                    <el-statistic title="夏普比率" :value="currentResult.metrics.sharpe_ratio" :precision="4">
                      <template #suffix>
                        <el-tag :type="getSharpeRatingType(currentResult.metrics.sharpe_ratio)">
                          {{ getSharpeRating(currentResult.metrics.sharpe_ratio) }}
                        </el-tag>
                      </template>
                    </el-statistic>
                  </el-tooltip>
                </el-col>
                <el-col :span="6">
                  <el-tooltip
                    :content="getMetricTooltip('annual_return')"
                    placement="top"
                    effect="light"
                  >
                    <el-statistic title="年化收益率" :value="currentResult.metrics.annual_return * 100" :precision="2" suffix="%" />
                  </el-tooltip>
                </el-col>
                <el-col :span="6">
                  <el-tooltip
                    :content="getMetricTooltip('max_drawdown')"
                    placement="top"
                    effect="light"
                  >
                    <el-statistic title="最大回撤" :value="currentResult.metrics.max_drawdown * 100" :precision="2" suffix="%" />
                  </el-tooltip>
                </el-col>
                <el-col :span="6">
                  <el-tooltip
                    :content="getMetricTooltip('win_rate')"
                    placement="top"
                    effect="light"
                  >
                    <el-statistic title="胜率" :value="currentResult.metrics.win_rate * 100" :precision="2" suffix="%" />
                  </el-tooltip>
                </el-col>
              </el-row>

              <el-row :gutter="20" class="metrics-row">
                <el-col :span="6">
                  <el-statistic title="初始资金" :value="currentResult.metrics.initial_capital" :precision="2" prefix="¥" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="最终资金" :value="currentResult.metrics.final_capital" :precision="2" prefix="¥" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="总收益率" :value="currentResult.metrics.total_return * 100" :precision="2" suffix="%" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="交易次数" :value="currentResult.metrics.total_trades" />
                </el-col>
              </el-row>

              <el-button type="success" @click="viewBacktestDetail(currentResult.backtest_id)">
                查看详细报告
              </el-button>
            </div>
          </el-card>
        </el-tab-pane>

        <!-- 回测历史 -->
        <el-tab-pane label="回测历史" name="history">
          <el-card shadow="never">
            <el-table
              :data="backtestHistory"
              v-loading="loadingHistory"
              stripe
              style="width: 100%"
            >
              <el-table-column prop="stock_code" label="股票代码" width="120" />
              <el-table-column label="回测时间" width="220">
                <template #default="{ row }">
                  {{ row.start_date }} ~ {{ row.end_date }}
                </template>
              </el-table-column>
              <el-table-column label="夏普比率" width="150">
                <template #default="{ row }">
                  <el-tag :type="getSharpeRatingType(row.sharpe_ratio)">
                    {{ row.sharpe_ratio?.toFixed(4) || 'N/A' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="总收益率" width="120">
                <template #default="{ row }">
                  <span :style="{ color: row.total_return >= 0 ? '#67c23a' : '#f56c6c' }">
                    {{ (row.total_return * 100).toFixed(2) }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="180" />
              <el-table-column label="操作" fixed="right" width="180">
                <template #default="{ row }">
                  <el-button size="small" @click="viewBacktestDetail(row.id)">
                    详情
                  </el-button>
                  <el-button
                    size="small"
                    type="danger"
                    @click="handleDeleteBacktest(row.id)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 回测详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="回测详细报告"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-if="detailData" class="detail-content">
        <!-- 性能指标 -->
        <el-descriptions title="性能指标" :column="3" border>
          <el-descriptions-item label="夏普比率">
            {{ detailData.metrics.sharpe_ratio.toFixed(4) }}
            <el-tag :type="getSharpeRatingType(detailData.metrics.sharpe_ratio)" size="small" style="margin-left: 8px">
              {{ getSharpeRating(detailData.metrics.sharpe_ratio) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="年化收益率">
            {{ (detailData.metrics.annual_return * 100).toFixed(2) }}%
          </el-descriptions-item>
          <el-descriptions-item label="总收益率">
            {{ (detailData.metrics.total_return * 100).toFixed(2) }}%
          </el-descriptions-item>
          <el-descriptions-item label="最大回撤">
            {{ (detailData.metrics.max_drawdown * 100).toFixed(2) }}%
          </el-descriptions-item>
          <el-descriptions-item label="胜率">
            {{ (detailData.metrics.win_rate * 100).toFixed(2) }}%
          </el-descriptions-item>
          <el-descriptions-item label="交易次数">
            {{ detailData.metrics.total_trades }}
          </el-descriptions-item>
          <el-descriptions-item label="盈利交易">
            {{ detailData.metrics.winning_trades }}
          </el-descriptions-item>
          <el-descriptions-item label="亏损交易">
            {{ detailData.metrics.losing_trades }}
          </el-descriptions-item>
          <el-descriptions-item label="初始资金">
            ¥{{ detailData.initial_capital.toLocaleString() }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 交易记录 -->
        <el-divider content-position="left">
          <h3>交易记录</h3>
        </el-divider>
        <el-table :data="detailData.trades" stripe max-height="400">
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-tag :type="row.action === 'buy' ? 'success' : 'danger'">
                {{ row.action === 'buy' ? '买入' : '卖出' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="shares" label="股数" width="100" />
          <el-table-column label="价格" width="120">
            <template #default="{ row }">
              ¥{{ row.price.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="金额" width="150">
            <template #default="{ row }">
              ¥{{ row.amount.toLocaleString() }}
            </template>
          </el-table-column>
          <el-table-column label="手续费" width="120">
            <template #default="{ row }">
              ¥{{ row.commission.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="原因" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay } from '@element-plus/icons-vue'
import StockSelector from '@/components/StockSelector.vue'
import { getStrategies } from '@/services/strategies'
import { runBacktest, getBacktests, getBacktestDetail, deleteBacktest } from '@/services/backtests'
import { backtestMetrics } from '@/utils/indicatorDescriptions'

const activeTab = ref('run')
const strategies = ref([])
const running = ref(false)
const currentResult = ref(null)
const backtestHistory = ref([])
const loadingHistory = ref(false)
const showDetailDialog = ref(false)
const detailData = ref(null)

const backtestFormRef = ref(null)
const backtestForm = ref({
  strategy_id: '',
  stock_code: '',
  dateRange: [],
  initial_capital: 100000,
  commission_rate: 0.0003,
  slippage_rate: 0.0001
})

const backtestRules = {
  strategy_id: [{ required: true, message: '请选择策略', trigger: 'change' }],
  stock_code: [{ required: true, message: '请选择股票', trigger: 'change' }],
  dateRange: [{ required: true, message: '请选择回测时间', trigger: 'change' }]
}

// 加载策略列表
const loadStrategies = async () => {
  try {
    const data = await getStrategies()
    strategies.value = data.strategies
  } catch (error) {
    ElMessage.error('加载策略列表失败')
  }
}

// 加载回测历史
const loadBacktestHistory = async () => {
  loadingHistory.value = true
  try {
    const data = await getBacktests()
    backtestHistory.value = data.backtests
  } catch (error) {
    ElMessage.error('加载回测历史失败')
  } finally {
    loadingHistory.value = false
  }
}

// 运行回测
const handleRunBacktest = async () => {
  if (!backtestFormRef.value) return
  
  await backtestFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    running.value = true
    currentResult.value = null
    
    try {
      const config = {
        strategy_id: backtestForm.value.strategy_id,
        stock_code: backtestForm.value.stock_code,
        start_date: backtestForm.value.dateRange[0],
        end_date: backtestForm.value.dateRange[1],
        initial_capital: backtestForm.value.initial_capital,
        commission_rate: backtestForm.value.commission_rate,
        slippage_rate: backtestForm.value.slippage_rate
      }
      
      const result = await runBacktest(config)
      currentResult.value = result
      
      ElMessage.success('回测完成！')
      
      // 刷新历史列表
      if (activeTab.value === 'history') {
        loadBacktestHistory()
      }
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '回测失败')
    } finally {
      running.value = false
    }
  })
}

// 查看回测详情
const viewBacktestDetail = async (backtestId) => {
  try {
    detailData.value = await getBacktestDetail(backtestId)
    showDetailDialog.value = true
  } catch (error) {
    ElMessage.error('加载回测详情失败')
  }
}

// 删除回测
const handleDeleteBacktest = async (backtestId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条回测记录吗？', '提示', {
      type: 'warning'
    })
    
    await deleteBacktest(backtestId)
    ElMessage.success('删除成功')
    loadBacktestHistory()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 重置表单
const resetForm = () => {
  backtestFormRef.value?.resetFields()
  currentResult.value = null
}

// 策略变化
const handleStrategyChange = () => {
  currentResult.value = null
}

// 获取夏普比率评级
const getSharpeRating = (sharpe) => {
  if (sharpe > 3) return '卓越'
  if (sharpe > 2) return '优秀'
  if (sharpe > 1) return '良好'
  if (sharpe > 0) return '一般'
  return '较差'
}

const getSharpeRatingType = (sharpe) => {
  if (sharpe > 3) return 'success'
  if (sharpe > 2) return 'success'
  if (sharpe > 1) return 'warning'
  if (sharpe > 0) return 'info'
  return 'danger'
}

// 获取指标tooltip
const getMetricTooltip = (metricKey) => {
  const metric = backtestMetrics[metricKey]
  if (!metric) return ''
  
  let tooltip = `${metric.name}\n${metric.description}`
  
  if (metric.interpretation) {
    tooltip += `\n评价标准: ${metric.interpretation}`
  }
  
  if (metric.example) {
    tooltip += `\n示例: ${metric.example}`
  }
  
  return tooltip
}

onMounted(() => {
  loadStrategies()
  loadBacktestHistory()
})
</script>

<style scoped>
.backtest-view {
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

.backtest-tabs {
  margin-top: 20px;
}

.run-card {
  border: 1px solid #e4e7ed;
}

.backtest-form {
  max-width: 600px;
}

.result-section {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 1px solid #e4e7ed;
}

.metrics-row {
  margin-bottom: 20px;
}

.detail-content {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
