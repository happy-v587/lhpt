"""
API module for the A-share quantitative trading system.
Contains all API route definitions.
"""

from . import stocks, indicators, strategies

__all__ = ['stocks', 'indicators', 'strategies']
