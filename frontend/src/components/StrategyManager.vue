<template>
  <div class="strategy-manager">
    <!-- 策略列表 -->
    <div class="strategy-list">
      <div class="list-header">
        <h3>策略列表</h3>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          创建策略
        </el-button>
      </div>

      <el-table
        :data="strategies"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="策略名称" width="200" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="指标数量" width="100">
          <template #default="{ row }">
            {{ row.indicators?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="条件数量" width="100">
          <template #default="{ row }">
            {{ row.conditions?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleView(row)"
              link
            >
              查看
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
              link
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 创建策略对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建新策略"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="策略名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入策略名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="策略描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入策略描述"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="技术指标">
          <div class="indicators-list">
            <div
              v-for="(indicator, index) in formData.indicators"
              :key="index"
              class="indicator-item"
            >
              <el-tag closable @close="removeIndicator(index)">
                {{ indicator.type }} - {{ JSON.stringify(indicator.params) }}
              </el-tag>
            </div>
            <el-button size="small" @click="showAddIndicator = true">
              添加指标
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="交易条件">
          <div class="conditions-list">
            <div
              v-for="(condition, index) in formData.conditions"
              :key="index"
              class="condition-item"
            >
              <el-select
                v-model="condition.action"
                placeholder="动作"
                style="width: 100px"
              >
                <el-option label="买入" value="buy">
                  <span style="color: #67c23a">📈 买入</span>
                </el-option>
                <el-option label="卖出" value="sell">
                  <span style="color: #f56c6c">📉 卖出</span>
                </el-option>
              </el-select>
              <span style="margin: 0 8px; color: #909399">当</span>
              <el-input
                v-model="condition.indicator"
                placeholder="指标名称 (如: MA5)"
                style="width: 140px"
              />
              <el-select
                v-model="condition.operator"
                placeholder="运算符"
                style="width: 100px; margin: 0 8px"
              >
                <el-option label=">" value=">" />
                <el-option label="<" value="<" />
                <el-option label=">=" value=">=" />
                <el-option label="<=" value="<=" />
                <el-option label="==" value="==" />
              </el-select>
              <el-input
                v-model="condition.value"
                placeholder="值 (如: MA20 或 30)"
                style="width: 140px"
              />
              <el-button
                type="danger"
                size="small"
                @click="removeCondition(index)"
                style="margin-left: 8px"
              >
                删除
              </el-button>
            </div>
            
            <div class="add-condition-buttons">
              <el-button size="small" type="success" @click="addCondition('buy')">
                <el-icon><Plus /></el-icon>
                添加买入条件
              </el-button>
              <el-button size="small" type="danger" @click="addCondition('sell')">
                <el-icon><Plus /></el-icon>
                添加卖出条件
              </el-button>
            </div>
            
            <el-alert
              v-if="formData.conditions.length === 0"
              title="提示：请至少添加一个买入条件和一个卖出条件"
              type="info"
              :closable="false"
              show-icon
              style="margin-top: 10px"
            />
            
            <div v-if="formData.conditions.length > 0" class="conditions-summary">
              <el-divider content-position="left">条件预览</el-divider>
              <div class="summary-section">
                <h5>📈 买入条件 ({{ buyConditions.length }})</h5>
                <div v-if="buyConditions.length > 0" class="condition-preview">
                  <div v-for="(cond, idx) in buyConditions" :key="idx" class="preview-item buy">
                    {{ cond.indicator }} {{ cond.operator }} {{ cond.value }}
                  </div>
                  <el-text type="info" size="small">
                    (所有条件需同时满足)
                  </el-text>
                </div>
                <el-text v-else type="info">暂无买入条件</el-text>
              </div>
              
              <div class="summary-section">
                <h5>📉 卖出条件 ({{ sellConditions.length }})</h5>
                <div v-if="sellConditions.length > 0" class="condition-preview">
                  <div v-for="(cond, idx) in sellConditions" :key="idx" class="preview-item sell">
                    {{ cond.indicator }} {{ cond.operator }} {{ cond.value }}
                  </div>
                  <el-text type="info" size="small">
                    (所有条件需同时满足)
                  </el-text>
                </div>
                <el-text v-else type="info">暂无卖出条件</el-text>
              </div>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加指标对话框 -->
    <el-dialog
      v-model="showAddIndicator"
      title="添加技术指标"
      width="500px"
    >
      <IndicatorConfig
        @save="handleIndicatorSave"
        @cancel="showAddIndicator = false"
      />
    </el-dialog>

    <!-- 查看策略详情对话框 -->
    <el-dialog
      v-model="showViewDialog"
      title="策略详情"
      width="600px"
    >
      <div v-if="currentStrategy" class="strategy-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="策略名称">
            {{ currentStrategy.name }}
          </el-descriptions-item>
          <el-descriptions-item label="描述">
            {{ currentStrategy.description || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(currentStrategy.created_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <h4 style="margin-top: 20px">技术指标</h4>
        <el-tag
          v-for="(indicator, index) in (currentStrategy.indicators || [])"
          :key="index"
          style="margin-right: 10px; margin-bottom: 10px"
        >
          {{ indicator.type }}: {{ JSON.stringify(indicator.params) }}
        </el-tag>

        <h4 style="margin-top: 20px">交易条件</h4>
        
        <div class="detail-conditions">
          <div class="detail-section">
            <h5>📈 买入条件</h5>
            <div
              v-for="(condition, index) in (currentStrategy.conditions || []).filter(c => c.action === 'buy')"
              :key="'buy-' + index"
              class="detail-condition-item buy"
            >
              <el-tag type="success" size="small">买入</el-tag>
              <span>{{ condition.indicator }} {{ condition.operator }} {{ condition.value }}</span>
            </div>
            <el-text v-if="!(currentStrategy.conditions || []).some(c => c.action === 'buy')" type="info">
              暂无买入条件
            </el-text>
          </div>
          
          <div class="detail-section">
            <h5>📉 卖出条件</h5>
            <div
              v-for="(condition, index) in (currentStrategy.conditions || []).filter(c => c.action === 'sell')"
              :key="'sell-' + index"
              class="detail-condition-item sell"
            >
              <el-tag type="danger" size="small">卖出</el-tag>
              <span>{{ condition.indicator }} {{ condition.operator }} {{ condition.value }}</span>
            </div>
            <el-text v-if="!(currentStrategy.conditions || []).some(c => c.action === 'sell')" type="info">
              暂无卖出条件
            </el-text>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { getStrategies, getStrategy, createStrategy, deleteStrategy } from '@/services/strategies'
import { ElMessage, ElMessageBox } from 'element-plus'
import IndicatorConfig from './IndicatorConfig.vue'

const strategies = ref([])
const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)
const showAddIndicator = ref(false)
const showViewDialog = ref(false)
const currentStrategy = ref(null)
const formRef = ref(null)

const formData = ref({
  name: '',
  description: '',
  indicators: [],
  conditions: []
})

const formRules = {
  name: [
    { required: true, message: '请输入策略名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ]
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 加载策略列表
const loadStrategies = async () => {
  loading.value = true
  try {
    const response = await getStrategies()
    strategies.value = response.strategies || []
  } catch (error) {
    console.error('加载策略列表失败:', error)
    ElMessage.error('加载策略列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 计算买入和卖出条件
const buyConditions = computed(() => {
  return formData.value.conditions.filter(c => c.action === 'buy')
})

const sellConditions = computed(() => {
  return formData.value.conditions.filter(c => c.action === 'sell')
})

// 添加条件
const addCondition = (action = 'buy') => {
  formData.value.conditions.push({
    indicator: '',
    operator: '>',
    value: '',
    action: action
  })
}

// 移除条件
const removeCondition = (index) => {
  formData.value.conditions.splice(index, 1)
}

// 移除指标
const removeIndicator = (index) => {
  formData.value.indicators.splice(index, 1)
}

// 处理指标保存
const handleIndicatorSave = (indicator) => {
  formData.value.indicators.push(indicator)
  showAddIndicator.value = false
  ElMessage.success('指标添加成功')
}

// 处理创建策略
const handleCreate = async () => {
  try {
    await formRef.value?.validate()
    
    if (formData.value.indicators.length === 0) {
      ElMessage.warning('请至少添加一个技术指标')
      return
    }
    
    if (formData.value.conditions.length === 0) {
      ElMessage.warning('请至少添加一个交易条件')
      return
    }
    
    // 检查是否有买入和卖出条件
    const hasBuyCondition = formData.value.conditions.some(c => c.action === 'buy')
    const hasSellCondition = formData.value.conditions.some(c => c.action === 'sell')
    
    if (!hasBuyCondition) {
      ElMessage.warning('请至少添加一个买入条件')
      return
    }
    
    if (!hasSellCondition) {
      ElMessage.warning('请至少添加一个卖出条件')
      return
    }
    
    creating.value = true
    await createStrategy(formData.value)
    
    ElMessage.success('策略创建成功')
    showCreateDialog.value = false
    resetForm()
    loadStrategies()
  } catch (error) {
    console.error('创建策略失败:', error)
    ElMessage.error('创建策略失败，请稍后重试')
  } finally {
    creating.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.value = {
    name: '',
    description: '',
    indicators: [],
    conditions: []
  }
  formRef.value?.resetFields()
}

// 查看策略详情
const handleView = async (strategy) => {
  try {
    // 获取完整的策略详情（包含indicators和conditions）
    const detailResponse = await getStrategy(strategy.id)
    currentStrategy.value = detailResponse
    showViewDialog.value = true
  } catch (error) {
    console.error('获取策略详情失败:', error)
    ElMessage.error('获取策略详情失败，请稍后重试')
  }
}

// 删除策略
const handleDelete = async (strategy) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除策略"${strategy.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteStrategy(strategy.id)
    ElMessage.success('策略删除成功')
    loadStrategies()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除策略失败:', error)
      ElMessage.error('删除策略失败，请稍后重试')
    }
  }
}

onMounted(() => {
  loadStrategies()
})
</script>

<style scoped>
.strategy-manager {
  padding: 20px;
}

.strategy-list {
  background: white;
  padding: 20px;
  border-radius: 4px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.indicators-list,
.conditions-list {
  width: 100%;
}

.indicator-item,
.condition-item {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.strategy-detail {
  padding: 10px 0;
}

.strategy-detail h4 {
  margin: 20px 0 10px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.add-condition-buttons {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.conditions-summary {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.summary-section {
  margin-bottom: 15px;
}

.summary-section:last-child {
  margin-bottom: 0;
}

.summary-section h5 {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.condition-preview {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-item {
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'Courier New', monospace;
}

.preview-item.buy {
  background: #f0f9ff;
  border-left: 3px solid #67c23a;
  color: #529b2e;
}

.preview-item.sell {
  background: #fef0f0;
  border-left: 3px solid #f56c6c;
  color: #c45656;
}

.detail-conditions {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section h5 {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.detail-condition-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  margin-bottom: 8px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.detail-condition-item.buy {
  background: #f0f9ff;
  border-left: 3px solid #67c23a;
}

.detail-condition-item.sell {
  background: #fef0f0;
  border-left: 3px solid #f56c6c;
}
</style>
