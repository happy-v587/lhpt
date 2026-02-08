import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/indicator-config',
      name: 'indicator-config',
      component: () => import('../views/IndicatorConfigView.vue')
    },
    {
      path: '/custom-indicator',
      name: 'custom-indicator',
      component: () => import('../views/CustomIndicatorView.vue')
    },
    {
      path: '/chart',
      name: 'chart',
      component: () => import('../views/ChartView.vue')
    },
    {
      path: '/strategy',
      name: 'strategy',
      component: () => import('../views/StrategyView.vue')
    },
    {
      path: '/backtest',
      name: 'backtest',
      component: () => import('../views/BacktestView.vue')
    }
  ]
})

export default router
