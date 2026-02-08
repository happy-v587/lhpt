"""
Tests for IndicatorCalculator class.
Validates technical indicator calculations.
"""

import pytest
import pandas as pd
import numpy as np
from services.indicator_calculator import IndicatorCalculator, IndicatorCalculationError


@pytest.fixture
def calculator():
    """Fixture to create an IndicatorCalculator instance."""
    return IndicatorCalculator()


@pytest.fixture
def sample_kline_data():
    """Fixture to create sample K-line data for testing."""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # Generate realistic price data
    close_prices = 100 + np.cumsum(np.random.randn(100) * 2)
    
    data = pd.DataFrame({
        'trade_date': dates,
        'close': close_prices,
        'open': close_prices + np.random.randn(100) * 0.5,
        'high': close_prices + np.abs(np.random.randn(100) * 1.5),
        'low': close_prices - np.abs(np.random.randn(100) * 1.5),
        'volume': np.random.randint(1000000, 10000000, 100)
    })
    
    return data


class TestIndicatorCalculator:
    """Test suite for IndicatorCalculator."""
    
    def test_calculator_initialization(self, calculator):
        """Test that calculator initializes correctly."""
        assert calculator is not None
    
    def test_validate_data_with_valid_data(self, calculator, sample_kline_data):
        """Test data validation with valid data."""
        # Should not raise an exception
        calculator._validate_data(sample_kline_data, ['close'])
    
    def test_validate_data_with_empty_data(self, calculator):
        """Test data validation with empty DataFrame."""
        empty_df = pd.DataFrame()
        with pytest.raises(IndicatorCalculationError, match="Input data is empty"):
            calculator._validate_data(empty_df, ['close'])
    
    def test_validate_data_with_missing_columns(self, calculator, sample_kline_data):
        """Test data validation with missing required columns."""
        with pytest.raises(IndicatorCalculationError, match="Missing required columns"):
            calculator._validate_data(sample_kline_data, ['close', 'nonexistent'])
    
    def test_validate_data_length_sufficient(self, calculator, sample_kline_data):
        """Test data length validation with sufficient data."""
        # Should not raise an exception
        calculator._validate_data_length(sample_kline_data, 50, "TestIndicator")
    
    def test_validate_data_length_insufficient(self, calculator, sample_kline_data):
        """Test data length validation with insufficient data."""
        with pytest.raises(IndicatorCalculationError, match="Insufficient data"):
            calculator._validate_data_length(sample_kline_data, 200, "TestIndicator")
    
    def test_validate_period_valid(self, calculator):
        """Test period validation with valid period."""
        # Should not raise an exception
        calculator._validate_period(10, "TestIndicator")
    
    def test_validate_period_invalid(self, calculator):
        """Test period validation with invalid periods."""
        with pytest.raises(IndicatorCalculationError, match="Invalid period"):
            calculator._validate_period(0, "TestIndicator")
        
        with pytest.raises(IndicatorCalculationError, match="Invalid period"):
            calculator._validate_period(-5, "TestIndicator")
    
    def test_calculate_ma_single_period(self, calculator, sample_kline_data):
        """Test MA calculation with a single period."""
        result = calculator.calculate_ma(sample_kline_data, [5])
        
        assert 'MA5' in result
        assert isinstance(result['MA5'], pd.Series)
        assert len(result['MA5']) == len(sample_kline_data)
        
        # First 4 values should be NaN (not enough data)
        assert result['MA5'].iloc[:4].isna().all()
        
        # 5th value should be the mean of first 5 closing prices
        expected_ma5 = sample_kline_data['close'].iloc[:5].mean()
        assert abs(result['MA5'].iloc[4] - expected_ma5) < 0.01
    
    def test_calculate_ma_multiple_periods(self, calculator, sample_kline_data):
        """Test MA calculation with multiple periods."""
        result = calculator.calculate_ma(sample_kline_data, [5, 10, 20])
        
        assert 'MA5' in result
        assert 'MA10' in result
        assert 'MA20' in result
        
        # All should be Series of same length
        assert len(result['MA5']) == len(sample_kline_data)
        assert len(result['MA10']) == len(sample_kline_data)
        assert len(result['MA20']) == len(sample_kline_data)
    
    def test_calculate_ma_insufficient_data(self, calculator):
        """Test MA calculation with insufficient data."""
        small_data = pd.DataFrame({'close': [100, 101, 102]})
        
        with pytest.raises(IndicatorCalculationError, match="Insufficient data"):
            calculator.calculate_ma(small_data, [10])
    
    def test_calculate_macd_default_params(self, calculator, sample_kline_data):
        """Test MACD calculation with default parameters."""
        result = calculator.calculate_macd(sample_kline_data)
        
        assert 'DIF' in result
        assert 'DEA' in result
        assert 'MACD' in result
        
        # All should be Series of same length
        assert len(result['DIF']) == len(sample_kline_data)
        assert len(result['DEA']) == len(sample_kline_data)
        assert len(result['MACD']) == len(sample_kline_data)
        
        # MACD should equal DIF - DEA
        macd_calculated = result['DIF'] - result['DEA']
        assert np.allclose(result['MACD'], macd_calculated, rtol=1e-10)
    
    def test_calculate_macd_custom_params(self, calculator, sample_kline_data):
        """Test MACD calculation with custom parameters."""
        result = calculator.calculate_macd(
            sample_kline_data,
            fast_period=6,
            slow_period=13,
            signal_period=5
        )
        
        assert 'DIF' in result
        assert 'DEA' in result
        assert 'MACD' in result
    
    def test_calculate_macd_insufficient_data(self, calculator):
        """Test MACD calculation with insufficient data."""
        small_data = pd.DataFrame({'close': [100, 101, 102]})
        
        with pytest.raises(IndicatorCalculationError, match="Insufficient data"):
            calculator.calculate_macd(small_data)
    
    def test_calculate_macd_invalid_periods(self, calculator, sample_kline_data):
        """Test MACD calculation with invalid period configuration."""
        with pytest.raises(IndicatorCalculationError, match="Fast period.*must be less than slow period"):
            calculator.calculate_macd(sample_kline_data, fast_period=26, slow_period=12)
    
    def test_calculate_rsi_default_period(self, calculator, sample_kline_data):
        """Test RSI calculation with default period."""
        result = calculator.calculate_rsi(sample_kline_data)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_kline_data)
        
        # RSI values should be between 0 and 100 (excluding NaN)
        valid_rsi = result.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()
    
    def test_calculate_rsi_custom_period(self, calculator, sample_kline_data):
        """Test RSI calculation with custom period."""
        result = calculator.calculate_rsi(sample_kline_data, period=6)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_kline_data)
        
        # RSI values should be between 0 and 100
        valid_rsi = result.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()
    
    def test_calculate_rsi_insufficient_data(self, calculator):
        """Test RSI calculation with insufficient data."""
        small_data = pd.DataFrame({'close': [100, 101, 102]})
        
        with pytest.raises(IndicatorCalculationError, match="Insufficient data"):
            calculator.calculate_rsi(small_data, period=14)
    
    def test_calculate_boll_default_params(self, calculator, sample_kline_data):
        """Test Bollinger Bands calculation with default parameters."""
        result = calculator.calculate_boll(sample_kline_data)
        
        assert 'upper' in result
        assert 'middle' in result
        assert 'lower' in result
        
        # All should be Series of same length
        assert len(result['upper']) == len(sample_kline_data)
        assert len(result['middle']) == len(sample_kline_data)
        assert len(result['lower']) == len(sample_kline_data)
        
        # Upper band should be >= middle band >= lower band (excluding NaN)
        valid_indices = result['middle'].notna()
        assert (result['upper'][valid_indices] >= result['middle'][valid_indices]).all()
        assert (result['middle'][valid_indices] >= result['lower'][valid_indices]).all()
    
    def test_calculate_boll_custom_params(self, calculator, sample_kline_data):
        """Test Bollinger Bands calculation with custom parameters."""
        result = calculator.calculate_boll(sample_kline_data, period=10, std_dev=1.5)
        
        assert 'upper' in result
        assert 'middle' in result
        assert 'lower' in result
    
    def test_calculate_boll_insufficient_data(self, calculator):
        """Test Bollinger Bands calculation with insufficient data."""
        small_data = pd.DataFrame({'close': [100, 101, 102]})
        
        with pytest.raises(IndicatorCalculationError, match="Insufficient data"):
            calculator.calculate_boll(small_data, period=20)
    
    def test_calculate_boll_invalid_std_dev(self, calculator, sample_kline_data):
        """Test Bollinger Bands calculation with invalid std_dev."""
        with pytest.raises(IndicatorCalculationError, match="Invalid std_dev"):
            calculator.calculate_boll(sample_kline_data, std_dev=-1)
        
        with pytest.raises(IndicatorCalculationError, match="Invalid std_dev"):
            calculator.calculate_boll(sample_kline_data, std_dev=0)
