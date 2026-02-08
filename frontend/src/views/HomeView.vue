<template>
  <div class="home">
    <el-card class="welcome-card">
      <div class="welcome-content">
        <h1>中国A股量化交易系统</h1>
        <p class="subtitle">欢迎使用量化交易平台</p>
        <p class="description">
          本系统提供A股市场数据获取、技术指标计算、策略配置和数据可视化功能，
          帮助您进行量化交易分析和策略开发。
        </p>
      </div>
    </el-card>

    <div class="feature-cards">
      <el-card
        v-for="feature in features"
        :key="feature.path"
        shadow="hover"
        class="feature-card"
        @click="navigateTo(feature.path)"
      >
        <div class="feature-content">
          <el-icon :size="48" :color="feature.color">
            <component :is="feature.icon" />
          </el-icon>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
          <el-button type="primary" link>
            进入 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </el-card>
    </div>

    <el-card class="info-card">
      <template #header>
        <h3>系统功能</h3>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="info-item">
            <el-icon :size="24" color="#409eff"><DataLine /></el-icon>
            <h4>数据获取</h4>
            <p>实时获取A股市场数据，支持日线、周线、月线等多种周期</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <el-icon :size="24" color="#67c23a"><TrendCharts /></el-icon>
            <h4>技术指标</h4>
            <p>支持MA、MACD、RSI、BOLL等常用技术指标计算</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <el-icon :size="24" color="#e6a23c"><Document /></el-icon>
            <h4>策略管理</h4>
            <p>创建和管理交易策略，支持多指标组合配置</p>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { 
  Setting, 
  DataLine, 
  Document, 
  ArrowRight,
  TrendCharts
} from '@element-plus/icons-vue'

const router = useRouter()

const features = [
  {
    path: '/indicator-config',
    icon: Setting,
    color: '#409eff',
    title: '指标配置',
    description: '选择股票并配置技术指标参数，支持自定义周期和阈值'
  },
  {
    path: '/chart',
    icon: DataLine,
    color: '#67c23a',
    title: '数据可视化',
    description: '查看K线图表和技术指标曲线，支持多周期切换和指标叠加'
  },
  {
    path: '/strategy',
    icon: Document,
    color: '#e6a23c',
    title: '策略管理',
    description: '创建、查看和管理交易策略，支持多指标组合条件配置'
  }
]

const navigateTo = (path) => {
  router.push(path)
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 30px;
}

.welcome-content {
  text-align: center;
  padding: 40px 20px;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 16px;
  color: #409eff;
  font-weight: 600;
}

.subtitle {
  font-size: 1.3rem;
  color: #606266;
  margin-bottom: 20px;
}

.description {
  font-size: 1rem;
  color: #909399;
  line-height: 1.6;
  max-width: 800px;
  margin: 0 auto;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.feature-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-content {
  text-align: center;
  padding: 20px;
}

.feature-content h3 {
  margin: 16px 0 12px;
  font-size: 1.3rem;
  color: #303133;
}

.feature-content p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
  min-height: 48px;
}

.info-card {
  margin-bottom: 20px;
}

.info-card h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #303133;
}

.info-item {
  text-align: center;
  padding: 20px;
}

.info-item h4 {
  margin: 12px 0 8px;
  font-size: 1.1rem;
  color: #303133;
}

.info-item p {
  color: #606266;
  line-height: 1.6;
  font-size: 0.9rem;
}
</style>
