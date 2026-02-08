<template>
  <div class="custom-indicator-view">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <div>
            <h2>自定义指标</h2>
            <el-text type="info">创建和管理自定义技术指标公式</el-text>
          </div>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建指标
          </el-button>
        </div>
      </template>

      <!-- 指标列表 -->
      <el-table
        :data="indicators"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="display_name" label="指标名称" width="150" />
        <el-table-column prop="name" label="标识符" width="120" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="公式" width="300">
          <template #default="{ row }">
            <el-text class="formula-text" truncated>{{ row.formula }}</el-text>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewIndicator(row)">
              查看
            </el-button>
            <el-button size="small" type="primary" @click="testIndicator(row)">
              测试
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建指标对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建自定义指标"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="indicatorFormRef"
        :model="indicatorForm"
        :rules="indicatorRules"
        label-width="120px"
      >
        <el-form-item label="指标名称" prop="name">
          <el-input
            v-model="indicatorForm.name"
            placeholder="英文标识符，如: zscore"
          />
        </el-form-item>

        <el-form-item label="显示名称" prop="display_name">
          <el-input
            v-model="indicatorForm.display_name"
            placeholder="中文名称，如: Z-Score"
          />
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="indicatorForm.description"
            type="textarea"
            :rows="2"
            placeholder="指标说明"
          />
        </el-form-item>

        <el-form-item label="公式" prop="formula">
          <el-input
            v-model="indicatorForm.formula"
            type="textarea"
            :rows="4"
            placeholder="例如: (CLOSE - SMA(CLOSE, 20)) / STD(CLOSE, 20)"
          />
          <div class="formula-help">
            <el-text type="info" size="small">
              支持函数: SMA, EMA, STD, MAX, MIN, SUM, AVG, REF, CROSS, CROSS_UP, CROSS_DOWN
            </el-text>
            <el-button
              type="primary"
              link
              size="small"
              @click="validateCurrentFormula"
            >
              验证公式
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="参数定义">
          <div class="params-section">
            <el-button
              size="small"
              @click="addParam"
            >
              <el-icon><Plus /></el-icon>
              添加参数
            </el-button>
            
            <div v-for="(param, index) in indicatorForm.params" :key="index" class="param-item">
              <el-input
                v-model="param.name"
                placeholder="参数名"
                style="width: 120px"
              />
              <el-select v-model="param.type" style="width: 100px">
                <el-option label="整数" value="int" />
                <el-option label="浮点" value="float" />
                <el-option label="字符串" value="string" />
              </el-select>
              <el-input
                v-model="param.default"
                placeholder="默认值"
                style="width: 100px"
              />
              <el-input
                v-model="param.description"
                placeholder="说明"
                style="flex: 1"
              />
              <el-button
                type="danger"
                size="small"
                @click="removeParam(index)"
              >
                删除
              </el-button>
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

    <!-- 查看指标对话框 -->
    <el-dialog
      v-model="showViewDialog"
      title="指标详情"
      width="600px"
    >
      <el-descriptions v-if="currentIndicator" :column="1" border>
        <el-descriptions-item label="指标名称">
          {{ currentIndicator.display_name }}
        </el-descriptions-item>
        <el-descriptions-item label="标识符">
          {{ currentIndicator.name }}
        </el-descriptions-item>
        <el-descriptions-item label="描述">
          {{ currentIndicator.description || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="公式">
          <el-text class="formula-display">{{ currentIndicator.formula }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="参数">
          <div v-if="currentIndicator.params.length > 0">
            <div v-for="param in currentIndicator.params" :key="param.name" class="param-display">
              <el-tag size="small">{{ param.name }}</el-tag>
              <span>类型: {{ param.type }}</span>
              <span>默认: {{ param.default }}</span>
              <span v-if="param.description">{{ param.description }}</span>
            </div>
          </div>
          <el-text v-else type="info">无参数</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentIndicator.is_active ? 'success' : 'info'">
            {{ currentIndicator.is_active ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ currentIndicator.created_at }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 测试指标对话框 -->
    <el-dialog
      v-model="showTestDialog"
      title="测试指标"
      width="600px"
    >
      <el-form
        ref="testFormRef"
        :model="testForm"
        label-width="100px"
      >
        <el-form-item label="股票代码">
          <StockSelector v-model="testForm.stock_code" />
        </el-form-item>

        <el-form-item label="时间范围">
          <el-date-picker
            v-model="testForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item
          v-for="param in currentIndicator?.params"
          :key="param.name"
          :label="param.name"
        >
          <el-input-number
            v-if="param.type === 'int'"
            v-model="testForm.params[param.name]"
            :placeholder="String(param.default)"
          />
          <el-input-number
            v-else-if="param.type === 'float'"
            v-model="testForm.params[param.name]"
            :precision="4"
            :placeholder="String(param.default)"
          />
          <el-input
            v-else
            v-model="testForm.params[param.name]"
            :placeholder="String(param.default)"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showTestDialog = false">取消</el-button>
        <el-button type="primary" @click="handleTest" :loading="testing">
          计算
        </el-button>
      </template>

      <!-- 测试结果 -->
      <div v-if="testResult" class="test-result">
        <el-divider content-position="left">计算结果</el-divider>
        <el-alert
          title="计算成功"
          type="success"
          :closable="false"
          show-icon
        />
        <el-text type="info">
          已成功计算指标值，共 {{ Object.keys(testResult.data).length }} 个数据点
        </el-text>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import StockSelector from '@/components/StockSelector.vue'
import {
  getCustomIndicators,
  createCustomIndicator,
  deleteCustomIndicator,
  validateFormula,
  calculateCustomIndicator
} from '@/services/customIndicators'

const indicators = ref([])
const loading = ref(false)
const creating = ref(false)
const testing = ref(false)
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const showTestDialog = ref(false)
const currentIndicator = ref(null)
const testResult = ref(null)

const indicatorFormRef = ref(null)
const indicatorForm = ref({
  name: '',
  display_name: '',
  description: '',
  indicator_type: 'formula',
  formula: '',
  params: []
})

const indicatorRules = {
  name: [
    { required: true, message: '请输入指标名称', trigger: 'blur' },
    { pattern: /^[a-z_][a-z0-9_]*$/i, message: '只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  display_name: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
  formula: [{ required: true, message: '请输入公式', trigger: 'blur' }]
}

const testForm = ref({
  stock_code: '',
  dateRange: [],
  params: {}
})

// 加载指标列表
const loadIndicators = async () => {
  loading.value = true
  try {
    const data = await getCustomIndicators()
    indicators.value = data.indicators
  } catch (error) {
    ElMessage.error('加载指标列表失败')
  } finally {
    loading.value = false
  }
}

// 添加参数
const addParam = () => {
  indicatorForm.value.params.push({
    name: '',
    type: 'int',
    default: 0,
    description: ''
  })
}

// 移除参数
const removeParam = (index) => {
  indicatorForm.value.params.splice(index, 1)
}

// 验证公式
const validateCurrentFormula = async () => {
  if (!indicatorForm.value.formula) {
    ElMessage.warning('请先输入公式')
    return
  }

  try {
    const result = await validateFormula(indicatorForm.value.formula)
    if (result.valid) {
      ElMessage.success('公式验证通过')
    } else {
      ElMessage.error(`公式验证失败: ${result.message}`)
    }
  } catch (error) {
    ElMessage.error('验证失败')
  }
}

// 创建指标
const handleCreate = async () => {
  if (!indicatorFormRef.value) return

  await indicatorFormRef.value.validate(async (valid) => {
    if (!valid) return

    creating.value = true
    try {
      await createCustomIndicator(indicatorForm.value)
      ElMessage.success('指标创建成功')
      showCreateDialog.value = false
      indicatorFormRef.value.resetFields()
      indicatorForm.value.params = []
      loadIndicators()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '创建失败')
    } finally {
      creating.value = false
    }
  })
}

// 查看指标
const viewIndicator = (indicator) => {
  currentIndicator.value = indicator
  showViewDialog.value = true
}

// 测试指标
const testIndicator = (indicator) => {
  currentIndicator.value = indicator
  testForm.value = {
    stock_code: '',
    dateRange: [],
    params: {}
  }
  testResult.value = null
  showTestDialog.value = true
}

// 执行测试
const handleTest = async () => {
  if (!testForm.value.stock_code || !testForm.value.dateRange.length) {
    ElMessage.warning('请填写完整的测试参数')
    return
  }

  testing.value = true
  try {
    const config = {
      indicator_id: currentIndicator.value.id,
      stock_code: testForm.value.stock_code,
      start_date: testForm.value.dateRange[0],
      end_date: testForm.value.dateRange[1],
      params: testForm.value.params
    }

    testResult.value = await calculateCustomIndicator(config)
    ElMessage.success('计算成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '计算失败')
  } finally {
    testing.value = false
  }
}

// 删除指标
const handleDelete = async (indicatorId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个指标吗？', '提示', {
      type: 'warning'
    })

    await deleteCustomIndicator(indicatorId)
    ElMessage.success('删除成功')
    loadIndicators()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadIndicators()
})
</script>

<style scoped>
.custom-indicator-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-card {
  min-height: calc(100vh - 100px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.formula-text {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.formula-help {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.params-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.param-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.formula-display {
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

.param-display {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.param-display:last-child {
  border-bottom: none;
}

.test-result {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}
</style>
