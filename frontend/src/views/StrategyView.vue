<template>
  <div class="strategy-view">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>策略管理</h2>
          <el-text type="info">创建、查看和管理交易策略</el-text>
        </div>
      </template>

      <div class="strategy-content">
        <!-- 策略管理组件 -->
        <StrategyManager />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import StrategyManager from '@/components/StrategyManager.vue'
</script>

<style scoped>
.strategy-view {
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

.strategy-content {
  padding: 0;
}
</style>
