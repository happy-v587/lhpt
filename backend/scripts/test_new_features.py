"""
Test script for new features: backtest, custom indicators, and extended indicators.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from services.indicator_calculator import IndicatorCalculator
from services.custom_indicator_engine import CustomIndicatorEngine
from services.backtest_engine import BacktestEngine


def test_extended_indicators():
    """Test newly added indicators."""
    print("=" * 60)
    print("测试扩展指标")
    print("=" * 60)
    
    # Generate sample data
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    
    data = pd.DataFrame({
        'date': dates,
        'open': 100 + np.random.randn(len(dates)).cumsum(),
        'close': 100 + np.random.randn(len(dates)).cumsum(),
        'high': 102 + np.random.randn(len(dates)).cumsum(),
        'low': 98 + np.random.randn(len(dates)).cumsum(),
        'volume': np.random.randint(1000000, 10000000, len(dates))
    })
    
    # Ensure price relationships
    data['high'] = data[['open', 'close', 'high']].max(axis=1)
    data['low'] = data[['open', 'close', 'low']].min(axis=1)
    
    calculator = IndicatorCalculator()
    
    # Test KDJ
    print("\n1. 测试 KDJ 指标")
    try:
        kdj = calculator.calculate_kdj(data)
        print(f"   ✓ KDJ 计算成功")
        print(f"   K 最新值: {kdj['K'].iloc[-1]:.2f}")
        print(f"   D 最新值: {kdj['D'].iloc[-1]:.2f}")
        print(f"   J 最新值: {kdj['J'].iloc[-1]:.2f}")
    except Exception as e:
        print(f"   ✗ KDJ 计算失败: {e}")
    
    # Test CCI
    print("\n2. 测试 CCI 指标")
    try:
        cci = calculator.calculate_cci(data)
        print(f"   ✓ CCI 计算成功")
        print(f"   CCI 最新值: {cci.iloc[-1]:.2f}")
    except Exception as e:
        print(f"   ✗ CCI 计算失败: {e}")
    
    # Test ATR
    print("\n3. 测试 ATR 指标")
    try:
        atr = calculator.calculate_atr(data)
        print(f"   ✓ ATR 计算成功")
        print(f"   ATR 最新值: {atr.iloc[-1]:.2f}")
    except Exception as e:
        print(f"   ✗ ATR 计算失败: {e}")
    
    # Test OBV
    print("\n4. 测试 OBV 指标")
    try:
        obv = calculator.calculate_obv(data)
        print(f"   ✓ OBV 计算成功")
        print(f"   OBV 最新值: {obv.iloc[-1]:.0f}")
    except Exception as e:
        print(f"   ✗ OBV 计算失败: {e}")
    
    # Test WR
    print("\n5. 测试 WR 指标")
    try:
        wr = calculator.calculate_wr(data)
        print(f"   ✓ WR 计算成功")
        print(f"   WR 最新值: {wr.iloc[-1]:.2f}")
    except Exception as e:
        print(f"   ✗ WR 计算失败: {e}")
    
    # Test DMI
    print("\n6. 测试 DMI 指标")
    try:
        dmi = calculator.calculate_dmi(data)
        print(f"   ✓ DMI 计算成功")
        print(f"   PDI 最新值: {dmi['PDI'].iloc[-1]:.2f}")
        print(f"   MDI 最新值: {dmi['MDI'].iloc[-1]:.2f}")
        print(f"   ADX 最新值: {dmi['ADX'].iloc[-1]:.2f}")
    except Exception as e:
        print(f"   ✗ DMI 计算失败: {e}")
    
    # Test EMA
    print("\n7. 测试 EMA 指标")
    try:
        ema = calculator.calculate_ema(data, [12, 26, 50])
        print(f"   ✓ EMA 计算成功")
        print(f"   EMA12 最新值: {ema['EMA12'].iloc[-1]:.2f}")
        print(f"   EMA26 最新值: {ema['EMA26'].iloc[-1]:.2f}")
    except Exception as e:
        print(f"   ✗ EMA 计算失败: {e}")
    
    # Test VWAP
    print("\n8. 测试 VWAP 指标")
    try:
        vwap = calculator.calculate_vwap(data)
        print(f"   ✓ VWAP 计算成功")
        print(f"   VWAP 最新值: {vwap.iloc[-1]:.2f}")
    except Exception as e:
        print(f"   ✗ VWAP 计算失败: {e}")


def test_custom_indicator_engine():
    """Test custom indicator formula engine."""
    print("\n" + "=" * 60)
    print("测试自定义指标引擎")
    print("=" * 60)
    
    # Generate sample data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    data = pd.DataFrame({
        'date': dates,
        'open': 100 + np.random.randn(100).cumsum(),
        'close': 100 + np.random.randn(100).cumsum(),
        'high': 102 + np.random.randn(100).cumsum(),
        'low': 98 + np.random.randn(100).cumsum(),
        'volume': np.random.randint(1000000, 10000000, 100)
    })
    
    data['high'] = data[['open', 'close', 'high']].max(axis=1)
    data['low'] = data[['open', 'close', 'low']].min(axis=1)
    
    engine = CustomIndicatorEngine()
    
    # Test 1: Simple formula
    print("\n1. 测试简单公式: (CLOSE - OPEN) / OPEN")
    try:
        result = engine.evaluate_formula(
            "(CLOSE - OPEN) / OPEN",
            data,
            {}
        )
        print(f"   ✓ 公式计算成功")
        print(f"   最新值: {result.iloc[-1]:.4f}")
    except Exception as e:
        print(f"   ✗ 公式计算失败: {e}")
    
    # Test 2: Z-Score
    print("\n2. 测试 Z-Score: (CLOSE - SMA(CLOSE, 20)) / STD(CLOSE, 20)")
    try:
        result = engine.evaluate_formula(
            "(close - sma(close, 20)) / std(close, 20)",
            data,
            {}
        )
        print(f"   ✓ Z-Score 计算成功")
        print(f"   最新值: {result.iloc[-1]:.4f}")
    except Exception as e:
        print(f"   ✗ Z-Score 计算失败: {e}")
    
    # Test 3: Volume ratio
    print("\n3. 测试成交量比率: VOLUME / AVG(VOLUME, 10)")
    try:
        result = engine.evaluate_formula(
            "volume / avg(volume, 10)",
            data,
            {}
        )
        print(f"   ✓ 成交量比率计算成功")
        print(f"   最新值: {result.iloc[-1]:.4f}")
    except Exception as e:
        print(f"   ✗ 成交量比率计算失败: {e}")
    
    # Test 4: Formula validation
    print("\n4. 测试公式验证")
    
    valid_formula = "SMA(CLOSE, 20)"
    validation = engine.validate_formula(valid_formula)
    print(f"   公式: {valid_formula}")
    print(f"   验证结果: {'✓ 通过' if validation['valid'] else '✗ 失败'}")
    print(f"   消息: {validation['message']}")
    
    invalid_formula = "import os; os.system('ls')"
    validation = engine.validate_formula(invalid_formula)
    print(f"\n   公式: {invalid_formula}")
    print(f"   验证结果: {'✓ 通过' if validation['valid'] else '✗ 失败'}")
    print(f"   消息: {validation['message']}")


def test_backtest_engine():
    """Test backtest engine with Sharpe ratio calculation."""
    print("\n" + "=" * 60)
    print("测试回测引擎（包含夏普比率）")
    print("=" * 60)
    
    # Generate sample data
    dates = pd.date_range(start='2023-01-01', periods=252, freq='D')
    np.random.seed(42)
    
    # Generate trending data
    trend = np.linspace(100, 120, 252)
    noise = np.random.randn(252) * 2
    
    data = pd.DataFrame({
        'date': dates,
        'open': trend + noise,
        'close': trend + noise + np.random.randn(252) * 0.5,
        'high': trend + noise + 2,
        'low': trend + noise - 2,
        'volume': np.random.randint(1000000, 10000000, 252)
    })
    
    data['high'] = data[['open', 'close', 'high']].max(axis=1)
    data['low'] = data[['open', 'close', 'low']].min(axis=1)
    
    # Define a simple MA crossover strategy
    strategy_config = {
        'indicators': [
            {
                'type': 'MA',
                'params': {'periods': [5, 20]}
            }
        ],
        'conditions': [
            {
                'indicator': 'MA5',
                'operator': '>',
                'value': 'MA20',
                'action': 'buy'
            },
            {
                'indicator': 'MA5',
                'operator': '<',
                'value': 'MA20',
                'action': 'sell'
            }
        ]
    }
    
    print("\n策略配置:")
    print(f"  指标: MA5, MA20")
    print(f"  买入条件: MA5 > MA20")
    print(f"  卖出条件: MA5 < MA20")
    
    # Run backtest
    print("\n运行回测...")
    engine = BacktestEngine(
        initial_capital=100000.0,
        commission_rate=0.0003,
        slippage_rate=0.0001
    )
    
    try:
        results = engine.run_backtest(data, strategy_config)
        
        print("\n回测结果:")
        print("-" * 60)
        metrics = results['metrics']
        
        print(f"初始资金: ¥{metrics['initial_capital']:,.2f}")
        print(f"最终资金: ¥{metrics['final_capital']:,.2f}")
        print(f"总收益率: {metrics['total_return']:.2%}")
        print(f"年化收益率: {metrics['annual_return']:.2%}")
        print(f"夏普比率: {metrics['sharpe_ratio']:.4f}")
        print(f"最大回撤: {metrics['max_drawdown']:.2%}")
        print(f"胜率: {metrics['win_rate']:.2%}")
        print(f"总交易次数: {metrics['total_trades']}")
        print(f"盈利交易: {metrics['winning_trades']}")
        print(f"亏损交易: {metrics['losing_trades']}")
        
        # Show some trades
        if results['trades']:
            print("\n交易记录（前5笔）:")
            print("-" * 60)
            for i, trade in enumerate(results['trades'][:5]):
                print(f"{i+1}. {trade['date']} - {trade['action'].upper()}: "
                      f"{trade['shares']} 股 @ ¥{trade['price']:.2f}, "
                      f"金额: ¥{trade['amount']:,.2f}")
        
        # Sharpe ratio interpretation
        print("\n夏普比率解读:")
        sharpe = metrics['sharpe_ratio']
        if sharpe > 3:
            rating = "卓越 ⭐⭐⭐⭐⭐"
        elif sharpe > 2:
            rating = "优秀 ⭐⭐⭐⭐"
        elif sharpe > 1:
            rating = "良好 ⭐⭐⭐"
        elif sharpe > 0:
            rating = "一般 ⭐⭐"
        else:
            rating = "较差 ⭐"
        
        print(f"  {sharpe:.4f} - {rating}")
        
        print("\n✓ 回测引擎测试成功")
        
    except Exception as e:
        print(f"\n✗ 回测失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("量化交易系统 - 新功能测试")
    print("=" * 60)
    
    try:
        # Test 1: Extended indicators
        test_extended_indicators()
        
        # Test 2: Custom indicator engine
        test_custom_indicator_engine()
        
        # Test 3: Backtest engine
        test_backtest_engine()
        
        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
