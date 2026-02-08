"""
Configuration module for the A-share quantitative trading system.
Loads environment variables and provides configuration settings.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = "sqlite:///./quant_trading.db"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_echo: bool = False
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    environment: str = "development"
    
    # CORS Configuration
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Cache Configuration (optional)
    redis_url: str = ""  # Empty string means use in-memory cache
    cache_enabled: bool = True
    cache_ttl_stock_list: int = 600  # 10 minutes
    cache_ttl_kline_data: int = 300  # 5 minutes
    cache_ttl_indicators: int = 300  # 5 minutes
    cache_ttl_stock_info: int = 3600  # 1 hour
    
    # Logging
    log_level: str = "INFO"
    log_file: str = ""
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst_size: int = 10
    rate_limit_per_minute: int = 60  # Alias for compatibility
    
    # Data Source Configuration
    data_fetch_retry_times: int = 3
    data_fetch_timeout: int = 30
    
    # Other Configuration
    timezone: str = "Asia/Shanghai"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
