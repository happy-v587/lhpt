<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 顶部导航栏 -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <el-icon :size="24" color="#409eff">
              <TrendCharts />
            </el-icon>
            <span class="logo-text">中国A股量化交易系统</span>
          </div>
          <div class="header-actions">
            <el-text type="info">欢迎使用量化交易平台</el-text>
          </div>
        </div>
      </el-header>

      <el-container class="main-container">
        <!-- 侧边栏菜单 -->
        <el-aside width="200px" class="app-aside">
          <el-menu
            :default-active="activeMenu"
            router
            class="sidebar-menu"
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/indicator-config">
              <el-icon><Setting /></el-icon>
              <span>指标配置</span>
            </el-menu-item>
            <el-menu-item index="/custom-indicator">
              <el-icon><Tools /></el-icon>
              <span>自定义指标</span>
            </el-menu-item>
            <el-menu-item index="/chart">
              <el-icon><DataLine /></el-icon>
              <span>数据可视化</span>
            </el-menu-item>
            <el-menu-item index="/strategy">
              <el-icon><Document /></el-icon>
              <span>策略管理</span>
            </el-menu-item>
            <el-menu-item index="/backtest">
              <el-icon><VideoPlay /></el-icon>
              <span>策略回测</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- 主内容区域 -->
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { 
  TrendCharts, 
  HomeFilled, 
  Setting, 
  DataLine, 
  Document,
  VideoPlay,
  Tools
} from '@element-plus/icons-vue'

const route = useRoute()

// 计算当前激活的菜单项
const activeMenu = computed(() => route.path)
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  overflow: hidden;
}

.app-container {
  height: 100vh;
}

.app-header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.main-container {
  height: calc(100vh - 60px);
}

.app-aside {
  background-color: #fff;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.sidebar-menu {
  border-right: none;
  height: 100%;
}

.app-main {
  background-color: #f5f7fa;
  overflow-y: auto;
  padding: 20px;
}
</style>
