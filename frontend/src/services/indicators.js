import apiClient from './api'

/**
 * 技术指标API服务
 */

/**
 * 获取支持的指标类型列表
 * @returns {Promise<Object>} 指标类型列表及其参数配置
 */
export const getIndicatorTypes = async () => {
  return await apiClient.get('/indicators/types')
}

/**
 * 计算技术指标
 * @param {Object} config - 指标计算配置
 * @param {string} config.stock_code - 股票代码
 * @param {string} config.indicator_type - 指标类型 (MA/MACD/RSI/BOLL)
 * @param {Object} config.params - 指标参数
 * @param {string} config.start_date - 开始日期
 * @param {string} config.end_date - 结束日期
 * @returns {Promise<Object>} 计算结果
 */
export const calculateIndicator = async (config) => {
  return await apiClient.post('/indicators/calculate', config)
}
