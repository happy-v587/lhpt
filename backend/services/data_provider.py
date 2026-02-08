"""
DataProvider class for fetching stock data from AkShare.
Implements data retrieval with error handling and retry logic.
"""

import akshare as ak
import pandas as pd
import logging
import time
from typing import List, Optional
from datetime import datetime, date
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)


class DataSourceError(Exception):
    """Exception raised when data source operations fail."""
    pass


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry a function on failure.
    Does not retry on ValueError (validation errors).
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay in seconds between retries
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ValueError:
                    # Don't retry validation errors
                    raise
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {str(e)}"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
            
            # All retries failed
            logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            raise DataSourceError(
                f"Failed to execute {func.__name__} after {max_retries} attempts: {str(last_exception)}"
            )
        return wrapper
    return decorator


class DataProvider:
    """
    Data provider class for fetching A-share stock data from AkShare.
    
    Responsibilities:
    - Fetch stock list
    - Fetch K-line data (daily, weekly, monthly)
    - Fetch stock basic information
    - Handle errors and implement retry logic
    """
    
    def __init__(self):
        """Initialize the DataProvider."""
        logger.info("DataProvider initialized with AkShare")
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_stock_list(self) -> List[dict]:
        """
        Get list of all A-share stocks.
        
        Returns:
            List of dictionaries containing stock information:
            - code: Stock code (e.g., "600000.SH")
            - name: Stock name
            - exchange: Exchange (SH/SZ)
            - industry: Industry sector (if available)
        
        Raises:
            DataSourceError: If data retrieval fails after retries
        
        Requirements: 1.1, 1.2
        """
        try:
            logger.info("Fetching stock list from AkShare")
            
            # Fetch all A-share stocks using the stock_info_a_code_name function
            all_stocks_df = ak.stock_info_a_code_name()
            
            # The dataframe has columns: code, name
            # We need to determine exchange based on code
            all_stocks_df['exchange'] = all_stocks_df['code'].apply(
                lambda x: 'SH' if x.startswith('6') else 'SZ'
            )
            all_stocks_df['code'] = all_stocks_df['code'] + '.' + all_stocks_df['exchange']
            
            # Convert to list of dictionaries
            result = all_stocks_df[['code', 'name', 'exchange']].to_dict('records')
            
            logger.info(f"Successfully fetched {len(result)} stocks")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching stock list: {str(e)}")
            raise
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_kline_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        period: str = 'daily'
    ) -> pd.DataFrame:
        """
        Get K-line data for a specific stock.
        
        Args:
            stock_code: Stock code (e.g., "600000.SH")
            start_date: Start date in format "YYYYMMDD" or "YYYY-MM-DD"
            end_date: End date in format "YYYYMMDD" or "YYYY-MM-DD"
            period: Period type - 'daily', 'weekly', or 'monthly'
        
        Returns:
            DataFrame with columns:
            - trade_date: Trading date
            - open: Opening price
            - close: Closing price
            - high: Highest price
            - low: Lowest price
            - volume: Trading volume
            - amount: Trading amount (optional)
        
        Raises:
            DataSourceError: If data retrieval fails after retries
            ValueError: If invalid parameters are provided
        
        Requirements: 1.2, 1.3, 1.4
        """
        # Validate period
        valid_periods = ['daily', 'weekly', 'monthly']
        if period not in valid_periods:
            raise ValueError(f"Invalid period: {period}. Must be one of {valid_periods}")
        
        # Validate and parse stock code
        if not stock_code or len(stock_code) < 6:
            raise ValueError(f"Invalid stock code: {stock_code}")
        
        # Validate stock code format (6 digits + optional .SH or .SZ)
        import re
        if not re.match(r'^\d{6}(\.(SH|SZ))?$', stock_code):
            raise ValueError(f"Invalid stock code format: {stock_code}. Expected format: 6 digits or 6 digits.SH/SZ")
        
        # Extract symbol and exchange
        symbol = stock_code[:6]
        exchange = stock_code.split('.')[-1] if '.' in stock_code else None
        
        # Normalize date format (AkShare expects YYYYMMDD)
        start_date = start_date.replace('-', '')
        end_date = end_date.replace('-', '')
        
        try:
            logger.info(f"Fetching {period} K-line data for {stock_code} from {start_date} to {end_date}")
            
            # Map period to AkShare adjust parameter
            period_map = {
                'daily': 'qfq',  # Forward adjusted daily data
                'weekly': 'qfq',
                'monthly': 'qfq'
            }
            
            # Fetch data based on period
            if period == 'daily':
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period='daily',
                    start_date=start_date,
                    end_date=end_date,
                    adjust=period_map[period]
                )
            elif period == 'weekly':
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period='weekly',
                    start_date=start_date,
                    end_date=end_date,
                    adjust=period_map[period]
                )
            elif period == 'monthly':
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period='monthly',
                    start_date=start_date,
                    end_date=end_date,
                    adjust=period_map[period]
                )
            
            if df is None or df.empty:
                logger.warning(f"No data returned for {stock_code}")
                return pd.DataFrame()
            
            # Standardize column names
            column_mapping = {
                '日期': 'trade_date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Select and order columns
            required_columns = ['trade_date', 'open', 'close', 'high', 'low', 'volume']
            optional_columns = ['amount']
            
            available_columns = [col for col in required_columns if col in df.columns]
            available_columns += [col for col in optional_columns if col in df.columns]
            
            df = df[available_columns].copy()
            
            # Convert trade_date to datetime
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            
            # Add stock_code column
            df['stock_code'] = stock_code
            
            # Add period column
            df['period'] = period
            
            logger.info(f"Successfully fetched {len(df)} records for {stock_code}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching K-line data for {stock_code}: {str(e)}")
            raise
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_stock_info(self, stock_code: str) -> dict:
        """
        Get basic information for a specific stock.
        
        Args:
            stock_code: Stock code (e.g., "600000.SH")
        
        Returns:
            Dictionary containing:
            - code: Stock code
            - name: Stock name
            - exchange: Exchange (SH/SZ)
            - industry: Industry sector
            - list_date: Listing date
            - market_cap: Market capitalization (if available)
        
        Raises:
            DataSourceError: If data retrieval fails after retries
            ValueError: If invalid stock code is provided
        
        Requirements: 1.4
        """
        if not stock_code or len(stock_code) < 6:
            raise ValueError(f"Invalid stock code: {stock_code}")
        
        # Extract symbol and exchange
        symbol = stock_code[:6]
        exchange = stock_code.split('.')[-1] if '.' in stock_code else None
        
        try:
            logger.info(f"Fetching stock info for {stock_code}")
            
            # Fetch individual stock info
            stock_info_df = ak.stock_individual_info_em(symbol=symbol)
            
            if stock_info_df is None or stock_info_df.empty:
                logger.warning(f"No info found for {stock_code}")
                return {
                    'code': stock_code,
                    'name': None,
                    'exchange': exchange,
                    'industry': None,
                    'list_date': None
                }
            
            # Parse the info dataframe (it has 'item' and 'value' columns)
            info_dict = dict(zip(stock_info_df['item'], stock_info_df['value']))
            
            # Extract relevant fields
            result = {
                'code': stock_code,
                'name': info_dict.get('股票简称', None),
                'exchange': exchange or info_dict.get('上市交易所', '').replace('上海证券交易所', 'SH').replace('深圳证券交易所', 'SZ'),
                'industry': info_dict.get('行业', None),
                'list_date': info_dict.get('上市时间', None)
            }
            
            # Try to get market cap if available
            if '总市值' in info_dict:
                try:
                    result['market_cap'] = float(info_dict['总市值'])
                except (ValueError, TypeError):
                    result['market_cap'] = None
            
            logger.info(f"Successfully fetched info for {stock_code}: {result['name']}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching stock info for {stock_code}: {str(e)}")
            raise
