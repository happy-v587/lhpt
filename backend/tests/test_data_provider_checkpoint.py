"""
Checkpoint test to verify DataProvider implementation.
This test validates that the DataProvider can be instantiated and has the correct methods.
"""

import pytest
from services.data_provider import DataProvider, DataSourceError


class TestDataProviderCheckpoint:
    """Checkpoint tests for DataProvider validation."""
    
    def test_data_provider_instantiation(self):
        """Test that DataProvider can be instantiated."""
        provider = DataProvider()
        assert provider is not None
    
    def test_data_provider_has_required_methods(self):
        """Test that DataProvider has all required methods."""
        provider = DataProvider()
        
        # Check that all required methods exist
        assert hasattr(provider, 'get_stock_list')
        assert callable(provider.get_stock_list)
        
        assert hasattr(provider, 'get_kline_data')
        assert callable(provider.get_kline_data)
        
        assert hasattr(provider, 'get_stock_info')
        assert callable(provider.get_stock_info)
    
    def test_data_provider_validates_stock_code(self):
        """Test that DataProvider validates stock code format."""
        provider = DataProvider()
        
        # Test invalid stock codes
        with pytest.raises(ValueError, match="Invalid stock code"):
            provider.get_kline_data("", "20240101", "20240131")
        
        with pytest.raises(ValueError, match="Invalid stock code"):
            provider.get_kline_data("ABC", "20240101", "20240131")
        
        with pytest.raises(ValueError, match="Invalid stock code format"):
            provider.get_kline_data("600000.XX", "20240101", "20240131")
    
    def test_data_provider_validates_period(self):
        """Test that DataProvider validates period parameter."""
        provider = DataProvider()
        
        # Test invalid period
        with pytest.raises(ValueError, match="Invalid period"):
            provider.get_kline_data("600000.SH", "20240101", "20240131", period="invalid")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
