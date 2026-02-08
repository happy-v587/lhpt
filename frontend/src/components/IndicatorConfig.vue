<template>
  <div class="indicator-config">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="120px"
      @submit.prevent="handleSave"
    >
      <el-form-item label="指标类型" prop="type">
        <el-select
          v-model="formData.type"
          placeholder="请选择指标类型"
          @change="handleTypeChange"
          :disabled="!!indicatorType"
        >
          <el-option
            v-for="indicator in indicatorTypes"
            :key="indicator.type"
            :label="indicator.name"
            :value="indicator.type"
          >
            <div class="indicator-option">
              <span class="indicator-name">{{ indicator.type }} - {{ indicator.name }}</span>
              <el-tooltip
                :content="getIndicatorTooltip(indicator.type)"
                placement="right"
                effect="light"
                :show-after="300"
              >
                <el-icon class="info-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </el-option>
        </el-select>
      </el-form-item>

      <!-- 指标说明卡片 -->
      <el-alert
        v-if="currentIndicator && getIndicatorDesc(formData.type)"
        :title="getIndicatorDesc(formData.type).name"
        type="info"
        :closable="false"
        class="indicator-info"
      >
        <template #default>
          <div class="indicator-detail">
            <p><strong>说明：</strong>{{ getIndicatorDesc(formData.type).description }}</p>
            <p><strong>用法：</strong>{{ getIndicatorDesc(formData.type).usage }}</p>
            <p v-if="getIndicatorDesc(formData.type).example">
              <strong>示例：</strong>{{ getIndicatorDesc(formData.type).example }}
            </p>
          </div>
        </template>
      </el-alert>

      <!-- 动态参数配置 -->
      <template v-if="currentIndicator">
        <el-form-item
          v-for="param in currentIndicator.params"
          :key="param.name"
          :prop="`params.${param.name}`"
        >
          <template #label>
            <span>{{ getParamLabel(param) }}</span>
            <el-tooltip
              v-if="getParamTooltip(formData.type, param.name)"
              :content="getParamTooltip(formData.type, param.name)"
              placement="top"
              effect="light"
            >
              <el-icon class="param-info-icon"><QuestionFilled /></el-icon>
            </el-tooltip>
          </template>
          
          <!-- 数组类型参数 -->
          <el-input
            v-if="param.type === 'array'"
            v-model="formData.params[param.name]"
            placeholder="请输入数值，用逗号分隔"
            @input="validateParam(param.name)"
          >
            <template #append>
              <span class="param-hint">例: {{ formatArrayDefault(param.default) }}</span>
            </template>
          </el-input>

          <!-- 整数类型参数 -->
          <el-input-number
            v-else-if="param.type === 'int'"
            v-model="formData.params[param.name]"
            :min="1"
            :max="500"
            :step="1"
            @change="validateParam(param.name)"
          />

          <!-- 浮点数类型参数 -->
          <el-input-number
            v-else-if="param.type === 'float'"
            v-model="formData.params[param.name]"
            :min="0.1"
            :max="10"
            :step="0.1"
            :precision="1"
            @change="validateParam(param.name)"
          />
        </el-form-item>
      </template>

      <!-- 参数验证错误提示 -->
      <el-alert
        v-if="validationError"
        :title="validationError"
        type="error"
        :closable="false"
        show-icon
        class="validation-alert"
      />

      <el-form-item>
        <el-button type="primary" @click="handleSave" :disabled="!!validationError">
          保存配置
        </el-button>
        <el-button @click="handleCancel">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { InfoFilled, QuestionFilled } from '@element-plus/icons-vue'
import { getIndicatorTypes } from '@/services/indicators'
import { ElMessage } from 'element-plus'
import { indicatorDescriptions } from '@/utils/indicatorDescriptions'

const props = defineProps({
  indicatorType: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['save', 'cancel'])

const formRef = ref(null)
const indicatorTypes = ref([])
const formData = ref({
  type: props.indicatorType || '',
  params: {}
})
const validationError = ref('')

// 表单验证规则
const rules = {
  type: [
    { required: true, message: '请选择指标类型', trigger: 'change' }
  ]
}

// 当前选中的指标配置
const currentIndicator = computed(() => {
  return indicatorTypes.value.find(ind => ind.type === formData.value.type)
})

// 获取参数标签
const getParamLabel = (param) => {
  const labels = {
    periods: '周期',
    fast_period: '快线周期',
    slow_period: '慢线周期',
    signal_period: '信号线周期',
    period: '周期',
    std_dev: '标准差倍数',
    n: 'RSV周期',
    m1: 'K值平滑周期',
    m2: 'D值平滑周期'
  }
  return labels[param.name] || param.name
}

// 获取指标描述
const getIndicatorDesc = (type) => {
  return indicatorDescriptions[type] || null
}

// 获取指标tooltip
const getIndicatorTooltip = (type) => {
  const desc = indicatorDescriptions[type]
  if (!desc) return ''
  return `${desc.fullName}\n${desc.description}`
}

// 获取参数tooltip
const getParamTooltip = (indicatorType, paramName) => {
  const desc = indicatorDescriptions[indicatorType]
  if (!desc || !desc.params) return ''
  return desc.params[paramName] || ''
}

// 格式化数组默认值
const formatArrayDefault = (defaultValue) => {
  if (Array.isArray(defaultValue)) {
    return defaultValue.join(', ')
  }
  return String(defaultValue)
}

// 处理指标类型变化
const handleTypeChange = (type) => {
  const indicator = indicatorTypes.value.find(ind => ind.type === type)
  if (indicator) {
    // 初始化参数为默认值
    formData.value.params = {}
    indicator.params.forEach(param => {
      if (param.type === 'array') {
        formData.value.params[param.name] = formatArrayDefault(param.default)
      } else {
        formData.value.params[param.name] = param.default
      }
    })
    validationError.value = ''
  }
}

// 实时验证参数
const validateParam = (paramName) => {
  const param = currentIndicator.value?.params.find(p => p.name === paramName)
  if (!param) return

  const value = formData.value.params[paramName]

  // 验证数组类型
  if (param.type === 'array') {
    if (typeof value === 'string') {
      const parts = value.split(',').map(v => v.trim()).filter(v => v !== '')
      const numbers = parts.map(v => Number(v))
      
      if (parts.length === 0) {
        validationError.value = `${getParamLabel(param)}不能为空`
        return
      }
      
      if (numbers.some(n => isNaN(n))) {
        validationError.value = `${getParamLabel(param)}必须是数字，用逗号分隔`
        return
      }
      
      if (numbers.some(n => n <= 0)) {
        validationError.value = `${getParamLabel(param)}必须为正整数`
        return
      }
    }
  }

  // 验证整数类型
  if (param.type === 'int') {
    if (!Number.isInteger(value) || value <= 0) {
      validationError.value = `${getParamLabel(param)}必须为正整数`
      return
    }
  }

  // 验证浮点数类型
  if (param.type === 'float') {
    if (typeof value !== 'number' || value <= 0) {
      validationError.value = `${getParamLabel(param)}必须为正数`
      return
    }
  }

  validationError.value = ''
}

// 处理保存
const handleSave = async () => {
  try {
    await formRef.value?.validate()
    
    // 验证所有参数
    if (currentIndicator.value) {
      for (const param of currentIndicator.value.params) {
        validateParam(param.name)
        if (validationError.value) {
          return
        }
      }
    }

    // 转换参数格式
    const params = { ...formData.value.params }
    if (currentIndicator.value) {
      currentIndicator.value.params.forEach(param => {
        if (param.type === 'array' && typeof params[param.name] === 'string') {
          params[param.name] = params[param.name]
            .split(',')
            .map(v => Number(v.trim()))
            .filter(v => !isNaN(v))
        }
      })
    }

    emit('save', {
      type: formData.value.type,
      params
    })

    ElMessage.success('配置保存成功')
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

// 处理取消
const handleCancel = () => {
  emit('cancel')
}

// 加载指标类型
const loadIndicatorTypes = async () => {
  try {
    console.log('Loading indicator types...')
    const response = await getIndicatorTypes()
    console.log('Indicator types response:', response)
    
    // 响应拦截器已经返回了 response.data，所以这里直接使用 response.indicators
    if (response && response.indicators) {
      indicatorTypes.value = response.indicators
    } else if (Array.isArray(response)) {
      indicatorTypes.value = response
    } else {
      console.warn('Unexpected response format:', response)
      indicatorTypes.value = []
    }
    
    console.log('Loaded indicator types:', indicatorTypes.value.length)
    
    // 如果有预设的指标类型，初始化参数
    if (props.indicatorType) {
      handleTypeChange(props.indicatorType)
    }
  } catch (error) {
    console.error('加载指标类型失败:', error)
    ElMessage.error('加载指标类型失败，请稍后重试')
  }
}

// 监听外部指标类型变化
watch(() => props.indicatorType, (newType) => {
  if (newType && newType !== formData.value.type) {
    formData.value.type = newType
    handleTypeChange(newType)
  }
})

onMounted(() => {
  loadIndicatorTypes()
})
</script>

<style scoped>
.indicator-config {
  padding: 20px;
}

.indicator-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.indicator-name {
  flex: 1;
}

.info-icon {
  color: #409eff;
  font-size: 14px;
  margin-left: 8px;
  cursor: help;
}

.param-info-icon {
  color: #909399;
  font-size: 14px;
  margin-left: 4px;
  cursor: help;
}

.indicator-info {
  margin-bottom: 20px;
}

.indicator-detail {
  font-size: 13px;
  line-height: 1.8;
}

.indicator-detail p {
  margin: 8px 0;
}

.indicator-detail strong {
  color: #303133;
  margin-right: 4px;
}

.param-hint {
  font-size: 12px;
  color: #909399;
}

.validation-alert {
  margin-bottom: 20px;
}

.el-form-item {
  margin-bottom: 22px;
}
</style>
