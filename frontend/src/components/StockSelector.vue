<template>
  <div class="stock-selector">
    <el-select
      v-model="selectedStock"
      filterable
      placeholder="请选择股票"
      :loading="loading"
      @change="handleChange"
      class="stock-select"
    >
      <el-option
        v-for="stock in filteredStocks"
        :key="stock.code"
        :label="`${stock.code} - ${stock.name}`"
        :value="stock.code"
      >
        <span class="stock-code">{{ stock.code }}</span>
        <span class="stock-name">{{ stock.name }}</span>
        <span class="stock-exchange">{{ stock.exchange }}</span>
      </el-option>
    </el-select>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getStockList } from '@/services/stocks'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const stocks = ref([])
const loading = ref(false)
const selectedStock = ref(props.modelValue)

// 计算过滤后的股票列表（Element Plus的filterable会自动处理搜索）
const filteredStocks = computed(() => stocks.value)

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  selectedStock.value = newVal
})

// 监听内部值变化
watch(selectedStock, (newVal) => {
  emit('update:modelValue', newVal)
})

// 处理选择变化
const handleChange = (code) => {
  const stock = stocks.value.find(s => s.code === code)
  if (stock) {
    emit('change', stock)
  }
}

// 加载股票列表
const loadStocks = async () => {
  loading.value = true
  try {
    const response = await getStockList()
    console.log('Stock list response:', response) // 调试日志
    // 响应拦截器已经返回了 response.data，所以这里直接使用 response.stocks
    if (response && response.stocks) {
      stocks.value = response.stocks
    } else if (Array.isArray(response)) {
      stocks.value = response
    } else {
      console.warn('Unexpected response format:', response)
      stocks.value = []
    }
    console.log('Loaded stocks:', stocks.value.length) // 调试日志
  } catch (error) {
    console.error('加载股票列表失败:', error)
    ElMessage.error('加载股票列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStocks()
})
</script>

<style scoped>
.stock-selector {
  width: 100%;
}

.stock-select {
  width: 100%;
}

.el-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-code {
  font-weight: 600;
  color: #303133;
  margin-right: 8px;
}

.stock-name {
  flex: 1;
  color: #606266;
}

.stock-exchange {
  font-size: 12px;
  color: #909399;
  padding: 2px 6px;
  background-color: #f4f4f5;
  border-radius: 3px;
}
</style>
