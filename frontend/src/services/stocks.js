import apiClient from './api'

/**
 * 股票数据API服务
 */

/**
 * 获取所有A股列表
 * @returns {Promise<Array>} 股票列表
 */
export const getStockList = async () => {
  return await apiClient.get('/stocks')
}

/**
 * 获取指定股票的K线数据
 * @param {string} code - 股票代码 (e.g., "600000.SH")
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期 (YYYY-MM-DD)
 * @param {string} params.end_date - 结束日期 (YYYY-MM-DD)
 * @param {string} params.period - 周期类型 (daily/weekly/monthly)
 * @returns {Promise<Object>} K线数据
 */
export const getKLineData = async (code, params) => {
  return await apiClient.get(`/stocks/${code}/kline`, { params })
}

/**
 * 获取股票基本信息
 * @param {string} code - 股票代码 (e.g., "600000.SH")
 * @returns {Promise<Object>} 股票信息
 */
export const getStockInfo = async (code) => {
  return await apiClient.get(`/stocks/${code}/info`)
}
