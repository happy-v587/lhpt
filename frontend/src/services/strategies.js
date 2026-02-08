import apiClient from './api'

/**
 * 策略管理API服务
 */

/**
 * 获取所有策略列表
 * @returns {Promise<Object>} 策略列表
 */
export const getStrategies = async () => {
  return await apiClient.get('/strategies')
}

/**
 * 获取单个策略详情
 * @param {string} id - 策略ID
 * @returns {Promise<Object>} 策略详情
 */
export const getStrategy = async (id) => {
  return await apiClient.get(`/strategies/${id}`)
}

/**
 * 创建新策略
 * @param {Object} strategy - 策略配置
 * @param {string} strategy.name - 策略名称
 * @param {string} strategy.description - 策略描述
 * @param {Array} strategy.indicators - 指标列表
 * @param {Array} strategy.conditions - 交易条件列表
 * @returns {Promise<Object>} 创建的策略信息
 */
export const createStrategy = async (strategy) => {
  return await apiClient.post('/strategies', strategy)
}

/**
 * 删除策略
 * @param {string} id - 策略ID
 * @returns {Promise<Object>} 删除结果
 */
export const deleteStrategy = async (id) => {
  return await apiClient.delete(`/strategies/${id}`)
}
