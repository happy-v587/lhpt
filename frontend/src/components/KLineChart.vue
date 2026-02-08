<template>
  <div class="kline-chart">
    <div class="chart-controls">
      <el-radio-group v-model="currentPeriod" @change="handlePeriodChange">
        <el-radio-button label="daily">日线</el-radio-button>
        <el-radio-button label="weekly">周线</el-radio-button>
        <el-radio-button label="monthly">月线</el-radio-button>
      </el-radio-group>
    </div>
    
    <div ref="chartRef" class="chart-container" v-loading="loading"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getKLineData } from '@/services/stocks'
import { calculateIndicator } from '@/services/indicators'
import { ElMessage } from 'element-plus'

const props = defineProps({
  stockCode: {
    type: String,
    required: true
  },
  period: {
    type: String,
    default: 'daily',
    validator: (value) => ['daily', 'weekly', 'monthly'].includes(value)
  },
  indicators: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['period-change'])

const chartRef = ref(null)
const chart = ref(null)
const loading = ref(false)
const currentPeriod = ref(props.period)
const chartData = ref({
  dates: [],
  klines: [],
  indicators: {}
})

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  
  chart.value = echarts.init(chartRef.value)
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
}

// 处理窗口大小变化
const handleResize = () => {
  chart.value?.resize()
}

// 加载K线数据
const loadKLineData = async () => {
  if (!props.stockCode) return
  
  loading.value = true
  try {
    // 计算日期范围（最近一年）
    const endDate = new Date()
    const startDate = new Date()
    startDate.setFullYear(startDate.getFullYear() - 1)
    
    const response = await getKLineData(props.stockCode, {
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0],
      period: currentPeriod.value
    })
    
    if (response.data && response.data.length > 0) {
      chartData.value.dates = response.data.map(item => item.date)
      chartData.value.klines = response.data.map(item => [
        item.open,
        item.close,
        item.low,
        item.high,
        item.volume
      ])
      
      // 加载指标数据
      await loadIndicators()
      
      // 渲染图表
      renderChart()
    } else {
      ElMessage.warning('暂无数据')
    }
  } catch (error) {
    console.error('加载K线数据失败:', error)
    ElMessage.error('加载K线数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 加载指标数据
const loadIndicators = async () => {
  if (!props.indicators || props.indicators.length === 0) {
    chartData.value.indicators = {}
    return
  }
  
  const endDate = new Date()
  const startDate = new Date()
  startDate.setFullYear(startDate.getFullYear() - 1)
  
  try {
    const indicatorPromises = props.indicators.map(indicator =>
      calculateIndicator({
        stock_code: props.stockCode,
        indicator_type: indicator.type,
        params: indicator.params,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
      })
    )
    
    const results = await Promise.all(indicatorPromises)
    
    // 合并指标数据
    chartData.value.indicators = {}
    results.forEach(result => {
      if (result.data) {
        Object.keys(result.data).forEach(key => {
          if (key !== 'dates') {
            chartData.value.indicators[key] = result.data[key]
          }
        })
      }
    })
  } catch (error) {
    console.error('加载指标数据失败:', error)
    ElMessage.error('加载指标数据失败')
  }
}

// 渲染图表
const renderChart = () => {
  if (!chart.value || chartData.value.dates.length === 0) return
  
  const option = {
    animation: false,
    legend: {
      bottom: 10,
      left: 'center',
      data: ['K线', ...Object.keys(chartData.value.indicators)]
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      borderWidth: 1,
      borderColor: '#ccc',
      padding: 10,
      textStyle: {
        color: '#000'
      },
      formatter: function (params) {
        let result = `<div style="font-weight: bold;">${params[0].axisValue}</div>`
        
        params.forEach(param => {
          if (param.seriesName === 'K线') {
            const data = param.data
            result += `<div style="margin-top: 5px;">
              开盘: ${data[1]}<br/>
              收盘: ${data[2]}<br/>
              最低: ${data[3]}<br/>
              最高: ${data[4]}<br/>
              成交量: ${data[5] || 0}
            </div>`
          } else {
            result += `<div>${param.marker}${param.seriesName}: ${param.value}</div>`
          }
        })
        
        return result
      }
    },
    axisPointer: {
      link: [{ xAxisIndex: 'all' }],
      label: {
        backgroundColor: '#777'
      }
    },
    grid: [
      {
        left: '10%',
        right: '8%',
        height: '50%'
      },
      {
        left: '10%',
        right: '8%',
        top: '63%',
        height: '16%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: chartData.value.dates,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      },
      {
        type: 'category',
        gridIndex: 1,
        data: chartData.value.dates,
        boundaryGap: false,
        axisLine: { onZero: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: {
          show: true
        }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 50,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '85%',
        start: 50,
        end: 100
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: chartData.value.klines,
        itemStyle: {
          color: '#ef232a',
          color0: '#14b143',
          borderColor: '#ef232a',
          borderColor0: '#14b143'
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: chartData.value.klines.map(item => item[4])
      }
    ]
  }
  
  // 添加指标线
  Object.keys(chartData.value.indicators).forEach(key => {
    option.series.push({
      name: key,
      type: 'line',
      data: chartData.value.indicators[key],
      smooth: true,
      lineStyle: {
        width: 1
      },
      showSymbol: false
    })
  })
  
  chart.value.setOption(option, true)
}

// 处理周期变化
const handlePeriodChange = (period) => {
  emit('period-change', period)
  loadKLineData()
}

// 监听股票代码变化
watch(() => props.stockCode, () => {
  loadKLineData()
})

// 监听周期变化
watch(() => props.period, (newPeriod) => {
  currentPeriod.value = newPeriod
  loadKLineData()
})

// 监听指标变化
watch(() => props.indicators, async () => {
  await loadIndicators()
  renderChart()
}, { deep: true })

onMounted(async () => {
  await nextTick()
  initChart()
  if (props.stockCode) {
    loadKLineData()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart.value?.dispose()
})
</script>

<style scoped>
.kline-chart {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-controls {
  padding: 10px;
  display: flex;
  justify-content: center;
  border-bottom: 1px solid #e4e7ed;
}

.chart-container {
  flex: 1;
  min-height: 500px;
  width: 100%;
}
</style>
