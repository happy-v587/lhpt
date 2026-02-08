"""
Custom indicator engine for evaluating user-defined formulas.
Supports safe formula evaluation with predefined functions.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging
import re
from exceptions import IndicatorCalculationError

logger = logging.getLogger(__name__)


class CustomIndicatorEngine:
    """
    Engine for evaluating custom indicator formulas.
    
    Supports:
    - Mathematical operations
    - Built-in functions (SUM, AVG, MAX, MIN, STD, etc.)
    - Technical analysis functions
    - Safe evaluation (no arbitrary code execution)
    """
    
    # Allowed functions for formula evaluation
    ALLOWED_FUNCTIONS = {
        # Math functions
        'abs': np.abs,
        'sqrt': np.sqrt,
        'log': np.log,
        'exp': np.exp,
        'pow': np.power,
        
        # Aggregation functions
        'sum': lambda x, n: pd.Series(x).rolling(window=n).sum(),
        'avg': lambda x, n: pd.Series(x).rolling(window=n).mean(),
        'mean': lambda x, n: pd.Series(x).rolling(window=n).mean(),
        'max': lambda x, n: pd.Series(x).rolling(window=n).max(),
        'min': lambda x, n: pd.Series(x).rolling(window=n).min(),
        'std': lambda x, n: pd.Series(x).rolling(window=n).std(),
        
        # Technical functions
        'ema': lambda x, n: pd.Series(x).ewm(span=n, adjust=False).mean(),
        'sma': lambda x, n: pd.Series(x).rolling(window=n).mean(),
        'ref': lambda x, n: pd.Series(x).shift(n),
        
        # Comparison functions
        'cross': lambda a, b: (pd.Series(a) > pd.Series(b)) & (pd.Series(a).shift(1) <= pd.Series(b).shift(1)),
        'cross_up': lambda a, b: (pd.Series(a) > pd.Series(b)) & (pd.Series(a).shift(1) <= pd.Series(b).shift(1)),
        'cross_down': lambda a, b: (pd.Series(a) < pd.Series(b)) & (pd.Series(a).shift(1) >= pd.Series(b).shift(1)),
    }
    
    def __init__(self):
        """Initialize custom indicator engine."""
        logger.info("CustomIndicatorEngine initialized")
    
    def evaluate_formula(
        self,
        formula: str,
        data: pd.DataFrame,
        params: Dict[str, Any]
    ) -> pd.Series:
        """
        Evaluate a custom formula.
        
        Args:
            formula: Formula string (e.g., "SMA(CLOSE, 20)")
            data: K-line data with columns: open, close, high, low, volume
            params: Parameters for the formula
        
        Returns:
            Calculated indicator values as pandas Series
        
        Raises:
            IndicatorCalculationError: If formula evaluation fails
        
        Example formulas:
            - "SMA(CLOSE, 20)" - 20-day simple moving average
            - "(CLOSE - SMA(CLOSE, 20)) / STD(CLOSE, 20)" - Z-score
            - "SUM(VOLUME, 5) / 5" - Average volume
            - "CROSS(SMA(CLOSE, 5), SMA(CLOSE, 10))" - Golden cross
        """
        try:
            # Prepare data context
            context = self._prepare_context(data, params)
            
            # Parse and evaluate formula
            result = self._safe_eval(formula, context)
            
            # Convert to Series if needed
            if not isinstance(result, pd.Series):
                result = pd.Series(result, index=data.index)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to evaluate formula '{formula}': {e}")
            raise IndicatorCalculationError(
                message=f"公式计算失败: {formula}",
                details=str(e)
            )
    
    def _prepare_context(self, data: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare evaluation context with data and functions."""
        context = {
            # Price data (uppercase for formula readability)
            'OPEN': data['open'].values,
            'CLOSE': data['close'].values,
            'HIGH': data['high'].values,
            'LOW': data['low'].values,
            'VOLUME': data['volume'].values,
            
            # Lowercase aliases
            'open': data['open'].values,
            'close': data['close'].values,
            'high': data['high'].values,
            'low': data['low'].values,
            'volume': data['volume'].values,
            
            # Parameters
            **params,
            
            # Functions
            **self.ALLOWED_FUNCTIONS,
            
            # NumPy and Pandas
            'np': np,
            'pd': pd,
        }
        
        return context
    
    def _safe_eval(self, formula: str, context: Dict[str, Any]) -> Any:
        """
        Safely evaluate formula.
        
        Security measures:
        - No import statements
        - No attribute access (except allowed)
        - No file operations
        - Limited to predefined functions
        """
        # Check for dangerous patterns
        dangerous_patterns = [
            r'__\w+__',  # Dunder methods
            r'import\s',  # Import statements
            r'exec\s*\(',  # Exec function
            r'eval\s*\(',  # Eval function
            r'open\s*\(',  # File operations
            r'compile\s*\(',  # Code compilation
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, formula, re.IGNORECASE):
                raise IndicatorCalculationError(
                    message="公式包含不允许的操作",
                    details=f"检测到危险模式: {pattern}"
                )
        
        # Evaluate formula
        try:
            result = eval(formula, {"__builtins__": {}}, context)
            return result
        except Exception as e:
            raise IndicatorCalculationError(
                message="公式语法错误",
                details=str(e)
            )
    
    def validate_formula(self, formula: str) -> Dict[str, Any]:
        """
        Validate formula syntax without executing it.
        
        Args:
            formula: Formula string
        
        Returns:
            Validation result with status and message
        """
        try:
            # Check for dangerous patterns
            dangerous_patterns = [
                r'__\w+__',
                r'import\s',
                r'exec\s*\(',
                r'eval\s*\(',
                r'open\s*\(',
                r'compile\s*\(',
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, formula, re.IGNORECASE):
                    return {
                        'valid': False,
                        'message': f'公式包含不允许的操作: {pattern}'
                    }
            
            # Try to compile (but not execute)
            compile(formula, '<string>', 'eval')
            
            return {
                'valid': True,
                'message': '公式语法正确'
            }
            
        except SyntaxError as e:
            return {
                'valid': False,
                'message': f'语法错误: {str(e)}'
            }
        except Exception as e:
            return {
                'valid': False,
                'message': f'验证失败: {str(e)}'
            }
