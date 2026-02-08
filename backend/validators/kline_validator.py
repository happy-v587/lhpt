"""
K-line data validator for validating price relationships and data integrity.

Requirements: 9.1, 9.2
Property 1: K线数据完整性约束
Property 11: 异常数据拒绝
"""

from typing import Dict, Any, List
from datetime import date
import pandas as pd
from exceptions import DataValidationError


class KLineDataValidator:
    """
    Validator for K-line data to ensure data integrity and consistency.
    
    Validates:
    - Price relationships (high >= low, high >= open, high >= close, etc.)
    - Non-negative values for prices and volume
    - Data completeness
    """
    
    @staticmethod
    def validate_single_record(data: Dict[str, Any]) -> None:
        """
        Validate a single K-line data record.
        
        Args:
            data: Dictionary containing K-line data fields
            
        Raises:
            DataValidationError: If validation fails
            
        Requirements: 9.1, 9.2
        Property 1: K线数据完整性约束
        Property 11: 异常数据拒绝
        """
        # Check required fields
        required_fields = ['open', 'close', 'high', 'low', 'volume']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise DataValidationError(
                message="K线数据缺少必需字段",
                details=f"缺少字段: {', '.join(missing_fields)}"
            )
        
        # Extract values
        open_price = float(data['open'])
        close_price = float(data['close'])
        high_price = float(data['high'])
        low_price = float(data['low'])
        volume = int(data['volume'])
        
        # Validate non-negative values
        if open_price < 0:
            raise DataValidationError(
                message="开盘价不能为负数",
                details=f"开盘价: {open_price}"
            )
        
        if close_price < 0:
            raise DataValidationError(
                message="收盘价不能为负数",
                details=f"收盘价: {close_price}"
            )
        
        if high_price < 0:
            raise DataValidationError(
                message="最高价不能为负数",
                details=f"最高价: {high_price}"
            )
        
        if low_price < 0:
            raise DataValidationError(
                message="最低价不能为负数",
                details=f"最低价: {low_price}"
            )
        
        if volume < 0:
            raise DataValidationError(
                message="成交量不能为负数",
                details=f"成交量: {volume}"
            )
        
        # Validate price relationships
        # Property 1: high >= max(open, close) and low <= min(open, close) and high >= low
        if high_price < low_price:
            raise DataValidationError(
                message="最高价必须大于等于最低价",
                details=f"最高价: {high_price}, 最低价: {low_price}"
            )
        
        if high_price < open_price:
            raise DataValidationError(
                message="最高价必须大于等于开盘价",
                details=f"最高价: {high_price}, 开盘价: {open_price}"
            )
        
        if high_price < close_price:
            raise DataValidationError(
                message="最高价必须大于等于收盘价",
                details=f"最高价: {high_price}, 收盘价: {close_price}"
            )
        
        if low_price > open_price:
            raise DataValidationError(
                message="最低价必须小于等于开盘价",
                details=f"最低价: {low_price}, 开盘价: {open_price}"
            )
        
        if low_price > close_price:
            raise DataValidationError(
                message="最低价必须小于等于收盘价",
                details=f"最低价: {low_price}, 收盘价: {close_price}"
            )
        
        # Validate amount if present
        if 'amount' in data and data['amount'] is not None:
            amount = float(data['amount'])
            if amount < 0:
                raise DataValidationError(
                    message="成交额不能为负数",
                    details=f"成交额: {amount}"
                )
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> None:
        """
        Validate a DataFrame of K-line data.
        
        Args:
            df: DataFrame containing K-line data with columns: open, close, high, low, volume
            
        Raises:
            DataValidationError: If validation fails
            
        Requirements: 9.1, 9.2
        Property 1: K线数据完整性约束
        Property 11: 异常数据拒绝
        """
        if df.empty:
            raise DataValidationError(
                message="K线数据不能为空",
                details="DataFrame为空"
            )
        
        # Check required columns
        required_columns = ['open', 'close', 'high', 'low', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise DataValidationError(
                message="K线数据缺少必需列",
                details=f"缺少列: {', '.join(missing_columns)}"
            )
        
        # Validate non-negative values
        if (df['open'] < 0).any():
            invalid_rows = df[df['open'] < 0].index.tolist()
            raise DataValidationError(
                message="开盘价不能为负数",
                details=f"发现负数开盘价，行索引: {invalid_rows[:5]}"
            )
        
        if (df['close'] < 0).any():
            invalid_rows = df[df['close'] < 0].index.tolist()
            raise DataValidationError(
                message="收盘价不能为负数",
                details=f"发现负数收盘价，行索引: {invalid_rows[:5]}"
            )
        
        if (df['high'] < 0).any():
            invalid_rows = df[df['high'] < 0].index.tolist()
            raise DataValidationError(
                message="最高价不能为负数",
                details=f"发现负数最高价，行索引: {invalid_rows[:5]}"
            )
        
        if (df['low'] < 0).any():
            invalid_rows = df[df['low'] < 0].index.tolist()
            raise DataValidationError(
                message="最低价不能为负数",
                details=f"发现负数最低价，行索引: {invalid_rows[:5]}"
            )
        
        if (df['volume'] < 0).any():
            invalid_rows = df[df['volume'] < 0].index.tolist()
            raise DataValidationError(
                message="成交量不能为负数",
                details=f"发现负数成交量，行索引: {invalid_rows[:5]}"
            )
        
        # Validate price relationships
        # Property 1: high >= low
        if (df['high'] < df['low']).any():
            invalid_rows = df[df['high'] < df['low']].index.tolist()
            raise DataValidationError(
                message="最高价必须大于等于最低价",
                details=f"发现违反约束的数据，行索引: {invalid_rows[:5]}"
            )
        
        # high >= open
        if (df['high'] < df['open']).any():
            invalid_rows = df[df['high'] < df['open']].index.tolist()
            raise DataValidationError(
                message="最高价必须大于等于开盘价",
                details=f"发现违反约束的数据，行索引: {invalid_rows[:5]}"
            )
        
        # high >= close
        if (df['high'] < df['close']).any():
            invalid_rows = df[df['high'] < df['close']].index.tolist()
            raise DataValidationError(
                message="最高价必须大于等于收盘价",
                details=f"发现违反约束的数据，行索引: {invalid_rows[:5]}"
            )
        
        # low <= open
        if (df['low'] > df['open']).any():
            invalid_rows = df[df['low'] > df['open']].index.tolist()
            raise DataValidationError(
                message="最低价必须小于等于开盘价",
                details=f"发现违反约束的数据，行索引: {invalid_rows[:5]}"
            )
        
        # low <= close
        if (df['low'] > df['close']).any():
            invalid_rows = df[df['low'] > df['close']].index.tolist()
            raise DataValidationError(
                message="最低价必须小于等于收盘价",
                details=f"发现违反约束的数据，行索引: {invalid_rows[:5]}"
            )
        
        # Validate amount if present
        if 'amount' in df.columns:
            if (df['amount'] < 0).any():
                invalid_rows = df[df['amount'] < 0].index.tolist()
                raise DataValidationError(
                    message="成交额不能为负数",
                    details=f"发现负数成交额，行索引: {invalid_rows[:5]}"
                )
    
    @staticmethod
    def validate_stock_code(stock_code: str) -> None:
        """
        Validate stock code format (6 digits + .SH or .SZ).
        
        Args:
            stock_code: Stock code to validate
            
        Raises:
            DataValidationError: If stock code format is invalid
            
        Requirements: 9.3
        Property 10: 输入验证完整性
        """
        import re
        
        pattern = r'^\d{6}\.(SH|SZ)$'
        if not re.match(pattern, stock_code):
            raise DataValidationError(
                message="股票代码格式无效",
                details=f"股票代码必须为6位数字+.SH或.SZ，当前值: {stock_code}"
            )
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> None:
        """
        Validate date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Raises:
            DataValidationError: If date range is invalid
            
        Requirements: 9.4
        Property 10: 输入验证完整性
        """
        from datetime import datetime
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError as e:
            raise DataValidationError(
                message="日期格式无效",
                details=f"日期必须为YYYY-MM-DD格式，错误: {str(e)}"
            )
        
        if start > end:
            raise DataValidationError(
                message="日期范围无效",
                details=f"开始日期 ({start_date}) 必须早于或等于结束日期 ({end_date})"
            )
        
        # Check if dates are not in the future
        today = date.today()
        if start > today:
            raise DataValidationError(
                message="日期范围无效",
                details=f"开始日期 ({start_date}) 不能是未来日期"
            )
        
        if end > today:
            raise DataValidationError(
                message="日期范围无效",
                details=f"结束日期 ({end_date}) 不能是未来日期"
            )
