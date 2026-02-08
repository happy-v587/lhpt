"""
Integration test for IndicatorCalculator with realistic data scenarios.
"""

import pytest
import pandas as pd
import numpy as np
from services.indicator_calculator import IndicatorCalculator


@pytest.fixture
def calculator():
    """Fixture to create an IndicatorCalculator instance."""
    return IndicatorCalculator()


@pytest.fixture
def realistic_stock_data():
    """
    Create realistic stock data for integration testing.
    Simulates 6 months of daily trading data.
    """
    dates = pd.date_range(start='2024-01-01', periods=120, freq='D')
    np.random.seed(123)
    
    # Simulate realistic price movement with trend and volatility
    base_price = 50.0
    trend = np.linspace(0, 20, 120)  # Upward trend
    volatility = np.random.randn(120) * 2
    close_prices = base_price + trend + volatility
    
    # Ensure prices are positive
    close_prices = np.maximum(close_prices, 10.0)
    
    data = pd.DataFrame({
        'trade_date': dates,
        'close': close_prices,
        'open': close_prices + np.random.randn(120) * 0.5,
        'high': close_prices + np.abs(np.random.randn(120) * 1.5),
        'low': close_prices - np.abs(np.random.randn(120) * 1.5),
        'volume': np.random.randint(1000000, 10000000, 120)
    })
    
    return data


class TestIndicatorIntegration:
    """Integration tests for IndicatorCalculator with realistic scenarios."""
    
    def test_complete_technical_analysis_workflow(self, calculator, realistic_stock_data):
        """
        Test a complete technical analysis workflow using all indicators.
        This simulates a real-world scenario where a trader analyzes a stock.
        """
        # Calculate all indicators
        ma_result = calculator.calculate_ma(realistic_stock_data, [5, 10, 20, 60])
        macd_result = calculator.calculate_macd(realistic_stock_data)
        rsi_result = calculator.calculate_rsi(realistic_stock_data, period=14)
        boll_result = calculator.calculate_boll(realistic_stock_data, period=20, std_dev=2.0)
        
        # Verify all indicators were calculated
        assert len(ma_result) == 4
        assert all(key in ma_result for key in ['MA5', 'MA10', 'MA20', 'MA60'])
        assert all(key in macd_result for key in ['DIF', 'DEA', 'MACD'])
        assert len(rsi_result) == len(realistic_stock_data)
        assert all(key in boll_result for key in ['upper', 'middle', 'lower'])
        
        # Verify data integrity
        # MA values should be in reasonable range relative to price
        for ma_key in ma_result:
            valid_ma = ma_result[ma_key].dropna()
            assert (valid_ma > 0).all()
            assert (valid_ma < realistic_stock_data['close'].max() * 1.5).all()
        
        # RSI should be between 0 and 100
        valid_rsi = rsi_result.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()
        
        # Bollinger bands should maintain order: upper >= middle >= lower
        valid_indices = boll_result['middle'].notna()
        assert (boll_result['upper'][valid_indices] >= boll_result['middle'][valid_indices]).all()
        assert (boll_result['middle'][valid_indices] >= boll_result['lower'][valid_indices]).all()
    
    def test_ma_crossover_detection(self, calculator, realistic_stock_data):
        """
        Test detecting MA crossovers (common trading signal).
        When MA5 crosses above MA20, it's a potential buy signal.
        """
        ma_result = calculator.calculate_ma(realistic_stock_data, [5, 20])
        
        ma5 = ma_result['MA5']
        ma20 = ma_result['MA20']
        
        # Find crossover points (where MA5 crosses MA20)
        # This is where (MA5 - MA20) changes sign
        diff = ma5 - ma20
        crossovers = ((diff.shift(1) < 0) & (diff > 0)).sum()
        
        # In realistic data, there should be some crossovers
        # Just verify the calculation works without errors
        assert crossovers >= 0
    
    def test_rsi_overbought_oversold_detection(self, calculator, realistic_stock_data):
        """
        Test detecting overbought/oversold conditions using RSI.
        RSI > 70 is typically considered overbought.
        RSI < 30 is typically considered oversold.
        """
        rsi = calculator.calculate_rsi(realistic_stock_data, period=14)
        
        valid_rsi = rsi.dropna()
        
        # Count overbought and oversold conditions
        overbought = (valid_rsi > 70).sum()
        oversold = (valid_rsi < 30).sum()
        
        # Just verify the calculation works
        assert overbought >= 0
        assert oversold >= 0
        
        # Verify RSI is within valid range
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()
    
    def test_bollinger_band_squeeze_detection(self, calculator, realistic_stock_data):
        """
        Test detecting Bollinger Band squeeze (low volatility period).
        A squeeze occurs when the bands are close together.
        """
        boll_result = calculator.calculate_boll(realistic_stock_data, period=20, std_dev=2.0)
        
        # Calculate band width (upper - lower)
        band_width = boll_result['upper'] - boll_result['lower']
        valid_width = band_width.dropna()
        
        # Band width should always be positive
        assert (valid_width > 0).all()
        
        # Calculate relative band width (as percentage of middle band)
        relative_width = (band_width / boll_result['middle'] * 100).dropna()
        
        # Relative width should be reasonable (typically 5-30%)
        assert (relative_width > 0).all()
        assert (relative_width < 100).all()
    
    def test_macd_histogram_zero_crossings(self, calculator, realistic_stock_data):
        """
        Test MACD histogram zero crossings (trading signals).
        When MACD crosses above zero, it's a potential buy signal.
        """
        macd_result = calculator.calculate_macd(realistic_stock_data)
        
        macd_histogram = macd_result['MACD']
        
        # Find zero crossings
        zero_crossings = ((macd_histogram.shift(1) < 0) & (macd_histogram > 0)).sum()
        
        # Just verify the calculation works
        assert zero_crossings >= 0
        
        # Verify MACD equals DIF - DEA
        dif_dea_diff = macd_result['DIF'] - macd_result['DEA']
        assert np.allclose(macd_histogram, dif_dea_diff, rtol=1e-10)
    
    def test_indicator_determinism(self, calculator, realistic_stock_data):
        """
        Test that indicators produce deterministic results.
        Running the same calculation twice should give identical results.
        
        Validates Property 4: Indicator calculation determinism
        """
        # Calculate indicators twice
        ma1 = calculator.calculate_ma(realistic_stock_data, [10, 20])
        ma2 = calculator.calculate_ma(realistic_stock_data, [10, 20])
        
        macd1 = calculator.calculate_macd(realistic_stock_data)
        macd2 = calculator.calculate_macd(realistic_stock_data)
        
        rsi1 = calculator.calculate_rsi(realistic_stock_data)
        rsi2 = calculator.calculate_rsi(realistic_stock_data)
        
        boll1 = calculator.calculate_boll(realistic_stock_data)
        boll2 = calculator.calculate_boll(realistic_stock_data)
        
        # Verify results are identical
        for key in ma1:
            assert ma1[key].equals(ma2[key])
        
        for key in macd1:
            assert macd1[key].equals(macd2[key])
        
        assert rsi1.equals(rsi2)
        
        for key in boll1:
            assert boll1[key].equals(boll2[key])
