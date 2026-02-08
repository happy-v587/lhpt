"""
IndicatorCalculator class for computing technical indicators.
Implements MA, MACD, RSI, and BOLL calculations with data validation.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)


class IndicatorCalculationError(Exception):
    """Exception raised when indicator calculation fails."""
    pass


class IndicatorCalculator:
    """
    Calculator for technical indicators used in quantitative trading.
    
    Responsibilities:
    - Calculate Moving Average (MA)
    - Calculate MACD (Moving Average Convergence Divergence)
    - Calculate RSI (Relative Strength Index)
    - Calculate Bollinger Bands (BOLL)
    - Validate data sufficiency before calculations
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
    """
    
    def __init__(self):
        """Initialize the IndicatorCalculator."""
        logger.info("IndicatorCalculator initialized")
    
    def _validate_data(self, data: pd.DataFrame, required_columns: List[str]) -> None:
        """
        Validate that the input data contains required columns.
        
        Args:
            data: Input DataFrame
            required_columns: List of required column names
        
        Raises:
            IndicatorCalculationError: If validation fails
        
        Requirements: 3.5, 3.6
        """
        if data is None or data.empty:
            raise IndicatorCalculationError("Input data is empty")
        
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise IndicatorCalculationError(
                f"Missing required columns: {missing_columns}"
            )
    
    def _validate_data_length(self, data: pd.DataFrame, min_length: int, indicator_name: str) -> None:
        """
        Validate that the data has sufficient length for calculation.
        
        Args:
            data: Input DataFrame
            min_length: Minimum required data points
            indicator_name: Name of the indicator being calculated
        
        Raises:
            IndicatorCalculationError: If data is insufficient
        
        Requirements: 3.6
        """
        if len(data) < min_length:
            raise IndicatorCalculationError(
                f"Insufficient data for {indicator_name}: "
                f"requires at least {min_length} data points, got {len(data)}"
            )
    
    def _validate_period(self, period: int, indicator_name: str) -> None:
        """
        Validate that the period parameter is positive.
        
        Args:
            period: Period parameter
            indicator_name: Name of the indicator
        
        Raises:
            IndicatorCalculationError: If period is invalid
        
        Requirements: 3.5
        """
        if not isinstance(period, int) or period <= 0:
            raise IndicatorCalculationError(
                f"Invalid period for {indicator_name}: must be a positive integer, got {period}"
            )

    
    def calculate_ma(
        self,
        data: pd.DataFrame,
        periods: List[int]
    ) -> Dict[str, pd.Series]:
        """
        Calculate Moving Average (MA) for multiple periods.
        
        The moving average is calculated as the arithmetic mean of the closing prices
        over the specified period.
        
        Args:
            data: DataFrame containing at least a 'close' column
            periods: List of periods for MA calculation (e.g., [5, 10, 20, 60])
        
        Returns:
            Dictionary mapping MA names to Series (e.g., {'MA5': Series, 'MA10': Series})
        
        Raises:
            IndicatorCalculationError: If data validation fails or calculation errors occur
        
        Requirements: 3.1, 3.5, 3.6
        
        Property 5: For any K-line data sequence and period N, the calculated N-day
        moving average at each point should equal the arithmetic mean of the previous
        N closing prices.
        """
        # Validate input data
        self._validate_data(data, ['close'])
        
        if not periods or not isinstance(periods, list):
            raise IndicatorCalculationError("Periods must be a non-empty list")
        
        # Validate each period and check data sufficiency
        for period in periods:
            self._validate_period(period, f"MA{period}")
            self._validate_data_length(data, period, f"MA{period}")
        
        result = {}
        
        try:
            for period in periods:
                # Calculate simple moving average
                ma_values = data['close'].rolling(window=period, min_periods=period).mean()
                result[f'MA{period}'] = ma_values
                
                logger.debug(f"Calculated MA{period} with {len(ma_values)} values")
            
            logger.info(f"Successfully calculated MA for periods: {periods}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating MA: {str(e)}")
            raise IndicatorCalculationError(f"Failed to calculate MA: {str(e)}")

    
    def calculate_macd(
        self,
        data: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence) indicator.
        
        MACD consists of three components:
        - DIF (Difference): Fast EMA - Slow EMA
        - DEA (Signal): EMA of DIF
        - MACD (Histogram): DIF - DEA
        
        Args:
            data: DataFrame containing at least a 'close' column
            fast_period: Period for fast EMA (default: 12)
            slow_period: Period for slow EMA (default: 26)
            signal_period: Period for signal line EMA (default: 9)
        
        Returns:
            Dictionary with keys 'DIF', 'DEA', 'MACD' mapping to Series
        
        Raises:
            IndicatorCalculationError: If data validation fails or calculation errors occur
        
        Requirements: 3.2, 3.5, 3.6
        
        Property 7: For any K-line data sequence, when MACD's DIF line and DEA line
        cross, the MACD histogram (DIF-DEA) should cross the zero axis.
        """
        # Validate input data
        self._validate_data(data, ['close'])
        
        # Validate periods
        self._validate_period(fast_period, "MACD fast_period")
        self._validate_period(slow_period, "MACD slow_period")
        self._validate_period(signal_period, "MACD signal_period")
        
        if fast_period >= slow_period:
            raise IndicatorCalculationError(
                f"Fast period ({fast_period}) must be less than slow period ({slow_period})"
            )
        
        # Check data sufficiency (need at least slow_period + signal_period data points)
        min_length = slow_period + signal_period
        self._validate_data_length(data, min_length, "MACD")
        
        try:
            # Calculate EMAs
            fast_ema = data['close'].ewm(span=fast_period, adjust=False).mean()
            slow_ema = data['close'].ewm(span=slow_period, adjust=False).mean()
            
            # Calculate DIF (Difference)
            dif = fast_ema - slow_ema
            
            # Calculate DEA (Signal line - EMA of DIF)
            dea = dif.ewm(span=signal_period, adjust=False).mean()
            
            # Calculate MACD histogram
            macd = dif - dea
            
            result = {
                'DIF': dif,
                'DEA': dea,
                'MACD': macd
            }
            
            logger.info(
                f"Successfully calculated MACD with periods "
                f"(fast={fast_period}, slow={slow_period}, signal={signal_period})"
            )
            return result
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {str(e)}")
            raise IndicatorCalculationError(f"Failed to calculate MACD: {str(e)}")

    
    def calculate_rsi(
        self,
        data: pd.DataFrame,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate RSI (Relative Strength Index) indicator.
        
        RSI measures the magnitude of recent price changes to evaluate
        overbought or oversold conditions. RSI values range from 0 to 100.
        
        Formula:
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss over the period
        
        Args:
            data: DataFrame containing at least a 'close' column
            period: Period for RSI calculation (default: 14)
        
        Returns:
            Series containing RSI values
        
        Raises:
            IndicatorCalculationError: If data validation fails or calculation errors occur
        
        Requirements: 3.3, 3.5, 3.6
        
        Property 6: For any K-line data sequence and period parameter, the calculated
        RSI values should always be between 0 and 100 (inclusive).
        """
        # Validate input data
        self._validate_data(data, ['close'])
        
        # Validate period
        self._validate_period(period, f"RSI{period}")
        
        # Check data sufficiency (need at least period + 1 for price changes)
        min_length = period + 1
        self._validate_data_length(data, min_length, f"RSI{period}")
        
        try:
            # Calculate price changes
            delta = data['close'].diff()
            
            # Separate gains and losses
            gains = delta.where(delta > 0, 0.0)
            losses = -delta.where(delta < 0, 0.0)
            
            # Calculate average gains and losses using EMA
            avg_gains = gains.ewm(span=period, adjust=False).mean()
            avg_losses = losses.ewm(span=period, adjust=False).mean()
            
            # Calculate RS (Relative Strength)
            rs = avg_gains / avg_losses
            
            # Calculate RSI
            rsi = 100.0 - (100.0 / (1.0 + rs))
            
            # Handle edge cases where avg_losses is 0
            rsi = rsi.fillna(100.0)
            
            logger.info(f"Successfully calculated RSI{period}")
            return rsi
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            raise IndicatorCalculationError(f"Failed to calculate RSI: {str(e)}")

    
    def calculate_boll(
        self,
        data: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands (BOLL) indicator.
        
        Bollinger Bands consist of three lines:
        - Middle Band: Simple Moving Average (SMA)
        - Upper Band: Middle Band + (std_dev * standard deviation)
        - Lower Band: Middle Band - (std_dev * standard deviation)
        
        Args:
            data: DataFrame containing at least a 'close' column
            period: Period for moving average calculation (default: 20)
            std_dev: Number of standard deviations for bands (default: 2.0)
        
        Returns:
            Dictionary with keys 'upper', 'middle', 'lower' mapping to Series
        
        Raises:
            IndicatorCalculationError: If data validation fails or calculation errors occur
        
        Requirements: 3.4, 3.5, 3.6
        
        Property 8: For any K-line data sequence, using standard parameters (20-day, 2x
        standard deviation), the calculated Bollinger Bands should contain at least 90%
        of closing prices between the upper and lower bands.
        """
        # Validate input data
        self._validate_data(data, ['close'])
        
        # Validate period
        self._validate_period(period, f"BOLL{period}")
        
        # Validate std_dev
        if not isinstance(std_dev, (int, float)) or std_dev <= 0:
            raise IndicatorCalculationError(
                f"Invalid std_dev for BOLL: must be a positive number, got {std_dev}"
            )
        
        # Check data sufficiency
        self._validate_data_length(data, period, f"BOLL{period}")
        
        try:
            # Calculate middle band (SMA)
            middle_band = data['close'].rolling(window=period, min_periods=period).mean()
            
            # Calculate standard deviation
            std = data['close'].rolling(window=period, min_periods=period).std()
            
            # Calculate upper and lower bands
            upper_band = middle_band + (std_dev * std)
            lower_band = middle_band - (std_dev * std)
            
            result = {
                'upper': upper_band,
                'middle': middle_band,
                'lower': lower_band
            }
            
            logger.info(
                f"Successfully calculated BOLL with period={period}, std_dev={std_dev}"
            )
            return result
            
        except Exception as e:
            logger.error(f"Error calculating BOLL: {str(e)}")
            raise IndicatorCalculationError(f"Failed to calculate BOLL: {str(e)}")
    
    def calculate_kdj(
        self,
        data: pd.DataFrame,
        n: int = 9,
        m1: int = 3,
        m2: int = 3
    ) -> Dict[str, pd.Series]:
        """
        Calculate KDJ (Stochastic Oscillator) indicator.
        
        Args:
            data: DataFrame with 'close', 'high', 'low' columns
            n: Period for RSV calculation (default: 9)
            m1: Period for K smoothing (default: 3)
            m2: Period for D smoothing (default: 3)
        
        Returns:
            Dictionary with 'K', 'D', 'J' values
        """
        self._validate_data(data, ['close', 'high', 'low'])
        self._validate_data_length(data, n, "KDJ")
        
        try:
            # Calculate RSV (Raw Stochastic Value)
            low_min = data['low'].rolling(window=n, min_periods=n).min()
            high_max = data['high'].rolling(window=n, min_periods=n).max()
            rsv = (data['close'] - low_min) / (high_max - low_min) * 100
            rsv = rsv.fillna(50)
            
            # Calculate K, D, J
            k = rsv.ewm(alpha=1/m1, adjust=False).mean()
            d = k.ewm(alpha=1/m2, adjust=False).mean()
            j = 3 * k - 2 * d
            
            return {'K': k, 'D': d, 'J': j}
        except Exception as e:
            raise IndicatorCalculationError(f"Failed to calculate KDJ: {str(e)}")
    
    def calculate_cci(
        self,
        data: pd.DataFrame,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate CCI (Commodity Channel Index) indicator.
        
        Args:
            data: DataFrame with 'close', 'high', 'low' columns
            period: Period for CCI calculation (default: 14)
        
        Returns:
            Series containing CCI values
        """
        self._validate_data(data, ['close', 'high', 'low'])
        self._validate_data_length(data, period, "CCI")
        
        try:
            # Calculate Typical Price
            tp = (data['high'] + data['low'] + data['close']) / 3
            
            # Calculate SMA of TP
            sma_tp = tp.rolling(window=period).mean()
            
            # Calculate Mean Deviation
            mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
            
            # Calculate CCI
            cci = (tp - sma_tp) / (0.015 * mad)
            
            return cci
        except Exception as e:
            raise IndicatorCalculationError(f"Failed to calculate CCI: {str(e)}")
    
    def calculate_atr(
        self,
        data: pd.DataFrame,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate ATR (Average True Range) indicator.
        
        Args:
            data: DataFrame with 'close', 'high', 'low' columns
            period: Period for ATR calculation (default: 14)
        
        Returns:
            Series containing ATR values
        """
        self._validate_data(data, ['close', 'high', 'low'])
        self._validate_data_length(data, period + 1, "ATR")
        
        try:
            # Calculate True Range
            high_low = data['high'] - data['low']
            high_close = np.abs(data['high'] - data['close'].shift())
            low_close = np.abs(data['low'] - data['close'].shift())
            
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            
            # Calculate ATR (EMA of TR)
            atr = tr.ewm(span=period, adjust=False).mean()
            
            return atr
        except Exception as e:
            raise IndicatorCalculationError(f"Failed to calculate ATR: {str(e)}")
    
    def calculate_obv(
        self,
        data: pd.DataFrame
    ) -> pd.Series:
        """
        Calculate OBV (On-Balance Volume) indicator.
        
        Args:
            data: DataFrame with 'close', 'volume' columns
        
        Returns:
            Series containing OBV values
        """
        self._validate_data(data, ['close', 'volume'])
        
        try:
            # Calculate price direction
            direction = np.sign(data['close'].diff())
            direction = direction.fillna(0)
            
            # Calculate OBV
            obv = (direction * data['volume']).cumsum()
            
            return obv
        except Exception as e:
            raise IndicatorCalculationError(f"Failed to calculate OBV: {str(e)}")
    
    def calculate_wr(
        self,
        data: pd.DataFrame,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate WR (Williams %R) indicator.
        
        Args:
            data: DataFrame with 'close', 'high', 'low' columns
            period: Period for WR calculation (default: 14)
        
        Returns:
            Series containing WR values
        """
        self._validate_data(data, ['close', 'high', 'low'])
        self._validate_data_length(data, period, "WR")
        
        try:
            high_max = data['high'].rolling(window=period).max()
            low_min = data['low'].rolling(window=period).min()
            
            wr = -100 * (high_max - data['close']) / (high_max - low_min)
            
            return wr
        except Exception as e:
            raise IndicatorCalculationError(f"Failed to calculate WR: {str(e)}")
    
    def calculate_dmi(
        self,
        data: pd.DataFrame,
        period: int = 14
    ) -> Dict[str, pd.Series]:
        """
        Calculate DMI (Directional Movement Index) indicator.
        
        Args:
            data: DataFrame with 'close', 'high', 'low' columns
            period: Period for DMI calculation (default: 14)
        
        Returns:
            Dictionary with 'PDI', 'MDI', 'ADX' values
        """
        self._validate_data(data, ['close', 'high', 'low'])
        self._validate_data_length(data, period * 2, "DMI")
        
        try:
            # Calculate directional movements
            high_diff = data['high'].diff()
            low_diff = -data['low'].diff()
            
            pdm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
            mdm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
            
            # Calculate ATR
            atr = self.calculate_atr(data, period)
            
            # Calculate directional indicators
            pdi = 100 * pdm.ewm(span=period, adjust=False).mean() / atr
            mdi = 100 * mdm.ewm(span=period, adjust=False).mean() / atr
            
            # Calculate ADX
            dx = 100 * np.abs(pdi - mdi) / (pdi + mdi)
            adx = dx.ewm(span=period, adjust=False).mean()
            
            return {'PDI': pdi, 'MDI': mdi, 'ADX': adx}
        except Exception as e:
            raise IndicatorCalculationError(f"Failed to calculate DMI: {str(e)}")
    
    def calculate_ema(
        self,
        data: pd.DataFrame,
        periods: List[int]
    ) -> Dict[str, pd.Series]:
        """
        Calculate EMA (Exponential Moving Average) for multiple periods.
        
        Args:
            data: DataFrame with 'close' column
            periods: List of periods (e.g., [12, 26, 50])
        
        Returns:
            Dictionary mapping EMA names to Series
        """
        self._validate_data(data, ['close'])
        
        result = {}
        try:
            for period in periods:
                self._validate_period(period, f"EMA{period}")
                ema = data['close'].ewm(span=period, adjust=False).mean()
                result[f'EMA{period}'] = ema
            
            return result
        except Exception as e:
            raise IndicatorCalculationError(f"Failed to calculate EMA: {str(e)}")
    
    def calculate_vwap(
        self,
        data: pd.DataFrame
    ) -> pd.Series:
        """
        Calculate VWAP (Volume Weighted Average Price) indicator.
        
        Args:
            data: DataFrame with 'close', 'high', 'low', 'volume' columns
        
        Returns:
            Series containing VWAP values
        """
        self._validate_data(data, ['close', 'high', 'low', 'volume'])
        
        try:
            # Calculate typical price
            tp = (data['high'] + data['low'] + data['close']) / 3
            
            # Calculate VWAP
            vwap = (tp * data['volume']).cumsum() / data['volume'].cumsum()
            
            return vwap
        except Exception as e:
            raise IndicatorCalculationError(f"Failed to calculate VWAP: {str(e)}")
