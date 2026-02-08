"""
Backtest engine for simulating trading strategies.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
import logging
from dataclasses import dataclass

from services.indicator_calculator import IndicatorCalculator
from exceptions import QuantTradingError

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Trade record."""
    date: date
    action: str  # 'buy' or 'sell'
    price: float
    shares: int
    amount: float
    commission: float
    reason: str


@dataclass
class Position:
    """Current position."""
    shares: int = 0
    cost_basis: float = 0.0
    
    @property
    def is_empty(self) -> bool:
        return self.shares == 0


class BacktestEngine:
    """
    Backtest engine for strategy simulation.
    
    Features:
    - Strategy execution simulation
    - Trade recording
    - Performance metrics calculation
    - Sharpe ratio, max drawdown, win rate, etc.
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission_rate: float = 0.0003,
        slippage_rate: float = 0.0001,
        risk_free_rate: float = 0.03
    ):
        """
        Initialize backtest engine.
        
        Args:
            initial_capital: Initial capital
            commission_rate: Commission rate (default 0.03%)
            slippage_rate: Slippage rate (default 0.01%)
            risk_free_rate: Risk-free rate for Sharpe ratio (default 3%)
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.risk_free_rate = risk_free_rate
        
        self.indicator_calculator = IndicatorCalculator()
        
        # State
        self.cash = initial_capital
        self.position = Position()
        self.trades: List[Trade] = []
        self.equity_curve: List[Dict] = []
    
    def run_backtest(
        self,
        data: pd.DataFrame,
        strategy_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run backtest with given data and strategy.
        
        Args:
            data: K-line data with columns: date, open, close, high, low, volume
            strategy_config: Strategy configuration with indicators and conditions
        
        Returns:
            Backtest results with metrics and trade history
        """
        logger.info(f"Starting backtest with {len(data)} data points")
        
        # Reset state
        self.cash = self.initial_capital
        self.position = Position()
        self.trades = []
        self.equity_curve = []
        
        # Calculate indicators
        indicators_data = self._calculate_indicators(data, strategy_config['indicators'])
        
        # Merge indicators with price data
        full_data = data.copy()
        for indicator_name, indicator_values in indicators_data.items():
            if isinstance(indicator_values, pd.DataFrame):
                for col in indicator_values.columns:
                    full_data[col] = indicator_values[col]
            else:
                full_data[indicator_name] = indicator_values
        
        # Run simulation
        for i in range(len(full_data)):
            row = full_data.iloc[i]
            
            # Calculate current equity
            current_price = row['close']
            equity = self.cash + self.position.shares * current_price
            
            self.equity_curve.append({
                'date': row['date'] if 'date' in row else row.name,
                'equity': equity,
                'cash': self.cash,
                'position_value': self.position.shares * current_price
            })
            
            # Evaluate trading conditions
            signals = self._evaluate_conditions(row, strategy_config['conditions'])
            
            # Execute trades
            if signals['buy'] and self.position.is_empty:
                self._execute_buy(row)
            elif signals['sell'] and not self.position.is_empty:
                self._execute_sell(row)
        
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        # Convert equity curve dates to strings for JSON serialization
        equity_curve_serializable = []
        for point in self.equity_curve:
            date_value = point['date']
            if isinstance(date_value, pd.Timestamp):
                date_str = date_value.strftime('%Y-%m-%d')
            elif isinstance(date_value, date):
                date_str = date_value.isoformat()
            else:
                date_str = str(date_value)
            
            equity_curve_serializable.append({
                'date': date_str,
                'equity': float(point['equity']),
                'cash': float(point['cash']),
                'position_value': float(point['position_value'])
            })
        
        return {
            'metrics': metrics,
            'trades': [self._trade_to_dict(t) for t in self.trades],
            'equity_curve': equity_curve_serializable
        }
    
    def _calculate_indicators(
        self,
        data: pd.DataFrame,
        indicators_config: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate all indicators specified in strategy."""
        indicators_data = {}
        
        for indicator_config in indicators_config:
            indicator_type = indicator_config['type']
            params = indicator_config['params']
            
            try:
                if indicator_type == 'MA':
                    result = self.indicator_calculator.calculate_ma(data, params.get('periods', [5, 10, 20]))
                    indicators_data.update(result)
                elif indicator_type == 'MACD':
                    result = self.indicator_calculator.calculate_macd(
                        data,
                        params.get('fast_period', 12),
                        params.get('slow_period', 26),
                        params.get('signal_period', 9)
                    )
                    indicators_data.update(result)
                elif indicator_type == 'RSI':
                    result = self.indicator_calculator.calculate_rsi(data, params.get('period', 14))
                    indicators_data['RSI'] = result
                elif indicator_type == 'BOLL':
                    result = self.indicator_calculator.calculate_boll(
                        data,
                        params.get('period', 20),
                        params.get('std_dev', 2.0)
                    )
                    indicators_data.update(result)
            except Exception as e:
                logger.error(f"Failed to calculate indicator {indicator_type}: {e}")
                raise
        
        return indicators_data
    
    def _evaluate_conditions(
        self,
        row: pd.Series,
        conditions: List[Dict[str, Any]]
    ) -> Dict[str, bool]:
        """Evaluate trading conditions."""
        buy_signals = []
        sell_signals = []
        
        for condition in conditions:
            indicator = condition['indicator']
            operator = condition['operator']
            value = condition['value']
            
            # Get indicator value
            if indicator not in row:
                continue
            
            indicator_value = row[indicator]
            
            # Skip if NaN
            if pd.isna(indicator_value):
                continue
            
            # Evaluate condition
            signal = False
            if operator == '>':
                if isinstance(value, str) and value in row:
                    signal = indicator_value > row[value]
                else:
                    signal = indicator_value > float(value)
            elif operator == '<':
                if isinstance(value, str) and value in row:
                    signal = indicator_value < row[value]
                else:
                    signal = indicator_value < float(value)
            elif operator == '>=':
                if isinstance(value, str) and value in row:
                    signal = indicator_value >= row[value]
                else:
                    signal = indicator_value >= float(value)
            elif operator == '<=':
                if isinstance(value, str) and value in row:
                    signal = indicator_value <= row[value]
                else:
                    signal = indicator_value <= float(value)
            elif operator == '==':
                if isinstance(value, str) and value in row:
                    signal = indicator_value == row[value]
                else:
                    signal = indicator_value == float(value)
            
            # Determine if buy or sell signal
            action = condition.get('action', 'buy')
            if action == 'buy':
                buy_signals.append(signal)
            else:
                sell_signals.append(signal)
        
        return {
            'buy': all(buy_signals) if buy_signals else False,
            'sell': all(sell_signals) if sell_signals else False
        }
    
    def _execute_buy(self, row: pd.Series) -> None:
        """Execute buy order."""
        price = row['close'] * (1 + self.slippage_rate)
        shares = int(self.cash / price / 100) * 100  # Buy in lots of 100
        
        if shares == 0:
            return
        
        amount = shares * price
        commission = amount * self.commission_rate
        total_cost = amount + commission
        
        if total_cost > self.cash:
            return
        
        self.cash -= total_cost
        self.position.shares = shares
        self.position.cost_basis = price
        
        trade = Trade(
            date=row['date'] if 'date' in row else row.name,
            action='buy',
            price=price,
            shares=shares,
            amount=amount,
            commission=commission,
            reason='Strategy signal'
        )
        self.trades.append(trade)
        
        logger.debug(f"Buy: {shares} shares at {price:.2f}, cost: {total_cost:.2f}")
    
    def _execute_sell(self, row: pd.Series) -> None:
        """Execute sell order."""
        price = row['close'] * (1 - self.slippage_rate)
        shares = self.position.shares
        
        amount = shares * price
        commission = amount * self.commission_rate
        total_proceeds = amount - commission
        
        self.cash += total_proceeds
        self.position = Position()
        
        trade = Trade(
            date=row['date'] if 'date' in row else row.name,
            action='sell',
            price=price,
            shares=shares,
            amount=amount,
            commission=commission,
            reason='Strategy signal'
        )
        self.trades.append(trade)
        
        logger.debug(f"Sell: {shares} shares at {price:.2f}, proceeds: {total_proceeds:.2f}")
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics."""
        if not self.equity_curve:
            return {}
        
        # Convert equity curve to DataFrame
        equity_df = pd.DataFrame(self.equity_curve)
        
        # Final capital
        final_capital = equity_df['equity'].iloc[-1]
        
        # Total return
        total_return = (final_capital - self.initial_capital) / self.initial_capital
        
        # Annual return (assuming 252 trading days per year)
        trading_days = len(equity_df)
        years = trading_days / 252
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # Calculate daily returns
        equity_df['returns'] = equity_df['equity'].pct_change()
        daily_returns = equity_df['returns'].dropna()
        
        # Sharpe ratio
        if len(daily_returns) > 0 and daily_returns.std() > 0:
            daily_risk_free = self.risk_free_rate / 252
            sharpe_ratio = (daily_returns.mean() - daily_risk_free) / daily_returns.std() * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        # Max drawdown
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax']
        max_drawdown = equity_df['drawdown'].min()
        
        # Win rate
        winning_trades = 0
        losing_trades = 0
        for i in range(0, len(self.trades), 2):
            if i + 1 < len(self.trades):
                buy_trade = self.trades[i]
                sell_trade = self.trades[i + 1]
                if sell_trade.price > buy_trade.price:
                    winning_trades += 1
                else:
                    losing_trades += 1
        
        total_trades = winning_trades + losing_trades
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_capital': float(final_capital),
            'total_return': float(total_return),
            'annual_return': float(annual_return),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'win_rate': float(win_rate),
            'total_trades': len(self.trades),
            'winning_trades': winning_trades,
            'losing_trades': losing_trades
        }
    
    def _trade_to_dict(self, trade: Trade) -> Dict[str, Any]:
        """Convert Trade to dictionary."""
        return {
            'date': trade.date.isoformat() if isinstance(trade.date, date) else str(trade.date),
            'action': trade.action,
            'price': float(trade.price),
            'shares': trade.shares,
            'amount': float(trade.amount),
            'commission': float(trade.commission),
            'reason': trade.reason
        }
