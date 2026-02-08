import { describe, it, expect } from 'vitest'
import { getStockList, getKLineData, getStockInfo } from './stocks'
import { getIndicatorTypes, calculateIndicator } from './indicators'
import { getStrategies, createStrategy, deleteStrategy } from './strategies'

describe('API Services', () => {

  describe('Stocks API', () => {
    it('should export getStockList function', () => {
      expect(typeof getStockList).toBe('function')
    })

    it('should export getKLineData function', () => {
      expect(typeof getKLineData).toBe('function')
    })

    it('should export getStockInfo function', () => {
      expect(typeof getStockInfo).toBe('function')
    })
  })

  describe('Indicators API', () => {
    it('should export getIndicatorTypes function', () => {
      expect(typeof getIndicatorTypes).toBe('function')
    })

    it('should export calculateIndicator function', () => {
      expect(typeof calculateIndicator).toBe('function')
    })
  })

  describe('Strategies API', () => {
    it('should export getStrategies function', () => {
      expect(typeof getStrategies).toBe('function')
    })

    it('should export createStrategy function', () => {
      expect(typeof createStrategy).toBe('function')
    })

    it('should export deleteStrategy function', () => {
      expect(typeof deleteStrategy).toBe('function')
    })
  })
})
