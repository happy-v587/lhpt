"""
Tests for K-line data validator.

Requirements: 9.1, 9.2
Property 1: K线数据完整性约束
Property 11: 异常数据拒绝
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
from datetime import date
from validators.kline_validator import KLineDataValidator
from exceptions import DataValidationError


class TestKLineDataValidator:
    """Test suite for KLineDataValidator."""
    
    def test_validate_single_record_valid(self):
        """Test validation of a valid single record."""
        data = {
            'open': 10.0,
            'close': 10.5,
            'high': 11.0,
            'low': 9.5,
            'volume': 1000000
        }
        
        # Should not raise any exception
        KLineDataValidator.validate_single_record(data)
    
    def test_validate_single_record_negative_price(self):
        """Test validation rejects negative prices."""
        data = {
            'open': -10.0,
            'close': 10.5,
            'high': 11.0,
            'low': 9.5,
            'volume': 1000000
        }
        
        with pytest.raises(DataValidationError) as exc_info:
            KLineDataValidator.validate_single_record(data)
        
        assert "开盘价不能为负数" in str(exc_info.value.message)
    
    def test_validate_single_record_high_less_than_low(self):
        """Test validation rejects high < low."""
        data = {
            'open': 10.0,
            'close': 10.5,
            'high': 9.0,  # Invalid: high < low
            'low': 9.5,
            'volume': 1000000
        }
        
        with pytest.raises(DataValidationError) as exc_info:
            KLineDataValidator.validate_single_record(data)
        
        assert "最高价必须大于等于最低价" in str(exc_info.value.message)
    
    def test_validate_single_record_high_less_than_open(self):
        """Test validation rejects high < open."""
        data = {
            'open': 11.0,
            'close': 10.5,
            'high': 10.0,  # Invalid: high < open
            'low': 9.5,
            'volume': 1000000
        }
        
        with pytest.raises(DataValidationError) as exc_info:
            KLineDataValidator.validate_single_record(data)
        
        assert "最高价必须大于等于开盘价" in str(exc_info.value.message)
    
    def test_validate_dataframe_valid(self):
        """Test validation of a valid DataFrame."""
        df = pd.DataFrame({
            'open': [10.0, 11.0, 12.0],
            'close': [10.5, 11.5, 12.5],
            'high': [11.0, 12.0, 13.0],
            'low': [9.5, 10.5, 11.5],
            'volume': [1000000, 1100000, 1200000]
        })
        
        # Should not raise any exception
        KLineDataValidator.validate_dataframe(df)
    
    def test_validate_dataframe_negative_volume(self):
        """Test validation rejects negative volume."""
        df = pd.DataFrame({
            'open': [10.0, 11.0, 12.0],
            'close': [10.5, 11.5, 12.5],
            'high': [11.0, 12.0, 13.0],
            'low': [9.5, 10.5, 11.5],
            'volume': [1000000, -1100000, 1200000]  # Invalid: negative volume
        })
        
        with pytest.raises(DataValidationError) as exc_info:
            KLineDataValidator.validate_dataframe(df)
        
        assert "成交量不能为负数" in str(exc_info.value.message)
    
    def test_validate_dataframe_price_relationship_violation(self):
        """Test validation rejects price relationship violations."""
        df = pd.DataFrame({
            'open': [10.0, 11.0, 12.0],
            'close': [10.5, 11.5, 12.5],
            'high': [11.0, 12.0, 13.0],
            'low': [9.5, 12.0, 11.5],  # Invalid: low > open at index 1
            'volume': [1000000, 1100000, 1200000]
        })
        
        with pytest.raises(DataValidationError) as exc_info:
            KLineDataValidator.validate_dataframe(df)
        
        assert "最低价必须小于等于开盘价" in str(exc_info.value.message)
    
    def test_validate_stock_code_valid(self):
        """Test validation of valid stock codes."""
        valid_codes = ['600000.SH', '000001.SZ', '123456.SH']
        
        for code in valid_codes:
            # Should not raise any exception
            KLineDataValidator.validate_stock_code(code)
    
    def test_validate_stock_code_invalid(self):
        """Test validation rejects invalid stock codes."""
        invalid_codes = [
            '60000.SH',  # Only 5 digits
            '6000000.SH',  # 7 digits
            '600000.XX',  # Invalid exchange
            '600000',  # Missing exchange
            'AAAA00.SH'  # Non-numeric
        ]
        
        for code in invalid_codes:
            with pytest.raises(DataValidationError):
                KLineDataValidator.validate_stock_code(code)
    
    def test_validate_date_range_valid(self):
        """Test validation of valid date ranges."""
        # Should not raise any exception
        KLineDataValidator.validate_date_range('2023-01-01', '2023-12-31')
    
    def test_validate_date_range_start_after_end(self):
        """Test validation rejects start date after end date."""
        with pytest.raises(DataValidationError) as exc_info:
            KLineDataValidator.validate_date_range('2023-12-31', '2023-01-01')
        
        assert "日期范围无效" in str(exc_info.value.message)
    
    def test_validate_date_range_invalid_format(self):
        """Test validation rejects invalid date formats."""
        with pytest.raises(DataValidationError) as exc_info:
            KLineDataValidator.validate_date_range('2023/01/01', '2023-12-31')
        
        assert "日期格式无效" in str(exc_info.value.message)
    
    def test_validate_missing_fields(self):
        """Test validation rejects records with missing fields."""
        data = {
            'open': 10.0,
            'close': 10.5,
            # Missing 'high', 'low', 'volume'
        }
        
        with pytest.raises(DataValidationError) as exc_info:
            KLineDataValidator.validate_single_record(data)
        
        assert "缺少必需字段" in str(exc_info.value.message)
