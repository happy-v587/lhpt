/**
 * Custom Indicators API service
 */
import api from './api'

/**
 * Create a custom indicator
 * @param {Object} indicator - Indicator configuration
 * @returns {Promise}
 */
export const createCustomIndicator = async (indicator) => {
  return await api.post('/custom-indicators', indicator)
}

/**
 * Get list of custom indicators
 * @param {boolean} activeOnly - Only return active indicators
 * @returns {Promise}
 */
export const getCustomIndicators = async (activeOnly = true) => {
  return await api.get('/custom-indicators', {
    params: { active_only: activeOnly }
  })
}

/**
 * Get custom indicator detail
 * @param {string} indicatorId - Indicator ID
 * @returns {Promise}
 */
export const getCustomIndicator = async (indicatorId) => {
  return await api.get(`/custom-indicators/${indicatorId}`)
}

/**
 * Delete a custom indicator
 * @param {string} indicatorId - Indicator ID
 * @returns {Promise}
 */
export const deleteCustomIndicator = async (indicatorId) => {
  return await api.delete(`/custom-indicators/${indicatorId}`)
}

/**
 * Validate a formula
 * @param {string} formula - Formula to validate
 * @returns {Promise}
 */
export const validateFormula = async (formula) => {
  return await api.post('/custom-indicators/validate-formula', { formula })
}

/**
 * Calculate a custom indicator
 * @param {Object} config - Calculation configuration
 * @returns {Promise}
 */
export const calculateCustomIndicator = async (config) => {
  return await api.post('/custom-indicators/calculate', config)
}

export default {
  createCustomIndicator,
  getCustomIndicators,
  getCustomIndicator,
  deleteCustomIndicator,
  validateFormula,
  calculateCustomIndicator
}
