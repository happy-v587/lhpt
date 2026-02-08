/**
 * Backtest API service
 */
import api from './api'

/**
 * Run a backtest
 * @param {Object} config - Backtest configuration
 * @returns {Promise}
 */
export const runBacktest = async (config) => {
  return await api.post('/backtests/run', config)
}

/**
 * Get list of backtests
 * @param {string} strategyId - Optional strategy ID filter
 * @returns {Promise}
 */
export const getBacktests = async (strategyId = null) => {
  const params = strategyId ? { strategy_id: strategyId } : {}
  return await api.get('/backtests', { params })
}

/**
 * Get backtest detail
 * @param {string} backtestId - Backtest ID
 * @returns {Promise}
 */
export const getBacktestDetail = async (backtestId) => {
  return await api.get(`/backtests/${backtestId}`)
}

/**
 * Delete a backtest
 * @param {string} backtestId - Backtest ID
 * @returns {Promise}
 */
export const deleteBacktest = async (backtestId) => {
  return await api.delete(`/backtests/${backtestId}`)
}

export default {
  runBacktest,
  getBacktests,
  getBacktestDetail,
  deleteBacktest
}
