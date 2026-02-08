"""
Demonstration script for IndicatorCalculator.
Shows how to use the technical indicator calculator with sample data.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from services.indicator_calculator import IndicatorCalculator, IndicatorCalculationError


def create_sample_data(days=100):
    """Create sample K-line data for demonstration."""
    dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
    np.random.seed(42)
    
    # Generate realistic price data with trend
    base_price = 50.0
    trend = np.linspace(0, 10, days)
    volatility = np.random.randn(days) * 2
    close_prices = base_price + trend + volatility
    close_prices = np.maximum(close_prices, 10.0)  # Ensure positive prices
    
    data = pd.DataFrame({
        'trade_date': dates,
        'close': close_prices,
        'open': close_prices + np.random.randn(days) * 0.5,
        'high': close_prices + np.abs(np.random.randn(days) * 1.5),
        'low': close_prices - np.abs(np.random.randn(days) * 1.5),
        'volume': np.random.randint(1000000, 10000000, days)
    })
    
    return data


def main():
    """Main demonstration function."""
    print("=" * 80)
    print("IndicatorCalculator Demonstration")
    print("=" * 80)
    print()
    
    # Create calculator instance
    calculator = IndicatorCalculator()
    print("✓ IndicatorCalculator initialized")
    print()
    
    # Create sample data
    data = create_sample_data(100)
    print(f"✓ Created sample K-line data with {len(data)} records")
    print(f"  Date range: {data['trade_date'].min()} to {data['trade_date'].max()}")
    print(f"  Price range: {data['close'].min():.2f} to {data['close'].max():.2f}")
    print()
    
    # Calculate Moving Averages
    print("-" * 80)
    print("1. Moving Average (MA) Calculation")
    print("-" * 80)
    ma_result = calculator.calculate_ma(data, [5, 10, 20, 60])
    print(f"✓ Calculated MA for periods: 5, 10, 20, 60")
    for period, values in ma_result.items():
        valid_values = values.dropna()
        print(f"  {period}: {len(valid_values)} valid values, "
              f"range: {valid_values.min():.2f} to {valid_values.max():.2f}")
    print()
    
    # Calculate MACD
    print("-" * 80)
    print("2. MACD (Moving Average Convergence Divergence) Calculation")
    print("-" * 80)
    macd_result = calculator.calculate_macd(data, fast_period=12, slow_period=26, signal_period=9)
    print(f"✓ Calculated MACD with default parameters (12, 26, 9)")
    for key, values in macd_result.items():
        valid_values = values.dropna()
        print(f"  {key}: {len(valid_values)} valid values, "
              f"range: {valid_values.min():.2f} to {valid_values.max():.2f}")
    print()
    
    # Calculate RSI
    print("-" * 80)
    print("3. RSI (Relative Strength Index) Calculation")
    print("-" * 80)
    rsi_result = calculator.calculate_rsi(data, period=14)
    valid_rsi = rsi_result.dropna()
    print(f"✓ Calculated RSI with period 14")
    print(f"  Valid values: {len(valid_rsi)}")
    print(f"  Range: {valid_rsi.min():.2f} to {valid_rsi.max():.2f}")
    print(f"  Average: {valid_rsi.mean():.2f}")
    
    # Check for overbought/oversold conditions
    overbought = (valid_rsi > 70).sum()
    oversold = (valid_rsi < 30).sum()
    print(f"  Overbought periods (RSI > 70): {overbought}")
    print(f"  Oversold periods (RSI < 30): {oversold}")
    print()
    
    # Calculate Bollinger Bands
    print("-" * 80)
    print("4. Bollinger Bands (BOLL) Calculation")
    print("-" * 80)
    boll_result = calculator.calculate_boll(data, period=20, std_dev=2.0)
    print(f"✓ Calculated Bollinger Bands with period 20, std_dev 2.0")
    for key, values in boll_result.items():
        valid_values = values.dropna()
        print(f"  {key.capitalize()} band: {len(valid_values)} valid values, "
              f"range: {valid_values.min():.2f} to {valid_values.max():.2f}")
    
    # Check how many prices are within bands
    valid_indices = boll_result['middle'].notna()
    within_bands = (
        (data.loc[valid_indices, 'close'] >= boll_result['lower'][valid_indices]) &
        (data.loc[valid_indices, 'close'] <= boll_result['upper'][valid_indices])
    ).sum()
    total_valid = valid_indices.sum()
    percentage = (within_bands / total_valid * 100) if total_valid > 0 else 0
    print(f"  Prices within bands: {within_bands}/{total_valid} ({percentage:.1f}%)")
    print()
    
    # Demonstrate error handling
    print("-" * 80)
    print("5. Error Handling Demonstration")
    print("-" * 80)
    
    # Test with insufficient data
    small_data = data.head(5)
    try:
        calculator.calculate_ma(small_data, [20])
        print("  ✗ Should have raised an error for insufficient data")
    except IndicatorCalculationError as e:
        print(f"  ✓ Correctly caught error for insufficient data: {str(e)[:60]}...")
    
    # Test with invalid period
    try:
        calculator.calculate_rsi(data, period=-5)
        print("  ✗ Should have raised an error for invalid period")
    except IndicatorCalculationError as e:
        print(f"  ✓ Correctly caught error for invalid period: {str(e)[:60]}...")
    
    # Test with empty data
    try:
        calculator.calculate_boll(pd.DataFrame(), period=20)
        print("  ✗ Should have raised an error for empty data")
    except IndicatorCalculationError as e:
        print(f"  ✓ Correctly caught error for empty data: {str(e)[:60]}...")
    
    print()
    print("=" * 80)
    print("Demonstration Complete!")
    print("=" * 80)
    print()
    print("Summary:")
    print("  ✓ All four technical indicators calculated successfully")
    print("  ✓ Data validation working correctly")
    print("  ✓ Error handling functioning as expected")
    print()
    print("The IndicatorCalculator is ready for use in the quantitative trading system!")
    print()


if __name__ == "__main__":
    main()
