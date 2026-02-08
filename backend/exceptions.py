"""
Custom exception classes for the A-share quantitative trading system.
Provides structured error handling with consistent error responses.
"""

from typing import Optional, Dict, Any
from datetime import datetime


class QuantTradingError(Exception):
    """Base exception class for all application errors."""
    
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", details: Optional[str] = None):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            code: Error code for programmatic handling
            details: Additional error details
        """
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary format for API responses.
        
        Returns:
            Dictionary containing error information
        
        Requirements: 4.6, 8.3
        Property 13: Error response format consistency
        """
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }


class DataSourceError(QuantTradingError):
    """Exception raised when data source operations fail (AkShare call failures)."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message=message,
            code="DATA_SOURCE_ERROR",
            details=details
        )


class DataValidationError(QuantTradingError):
    """Exception raised when data validation fails."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message=message,
            code="DATA_VALIDATION_ERROR",
            details=details
        )


class IndicatorCalculationError(QuantTradingError):
    """Exception raised when indicator calculation fails."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message=message,
            code="INDICATOR_CALCULATION_ERROR",
            details=details
        )


class DatabaseError(QuantTradingError):
    """Exception raised when database operations fail."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            details=details
        )
