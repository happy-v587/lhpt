"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
import logging

from config import settings
from exceptions import QuantTradingError
from api import stocks, indicators, strategies
from middleware.rate_limiter import RateLimiterMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="中国A股量化交易系统",
    description="A-share quantitative trading system API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure rate limiting
if settings.rate_limit_enabled:
    app.add_middleware(
        RateLimiterMiddleware,
        requests_per_minute=settings.rate_limit_requests_per_minute,
        burst_size=settings.rate_limit_burst_size
    )


# Global exception handlers
@app.exception_handler(QuantTradingError)
async def quant_trading_error_handler(request: Request, exc: QuantTradingError):
    """
    Handle custom application errors.
    
    Requirements: 4.6, 8.1, 8.3
    Property 13: Error response format consistency
    """
    logger.error(f"Application error: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=exc.to_dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.
    
    Requirements: 4.6, 8.3
    Property 13: Error response format consistency
    """
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "请求参数验证失败",
                "details": str(exc.errors()),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all other unhandled exceptions.
    
    Requirements: 4.6, 8.1, 8.3
    Property 13: Error response format consistency
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误",
                "details": str(exc),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    )


# Include routers
app.include_router(stocks.router)
app.include_router(indicators.router)
app.include_router(strategies.router)

# Import new routers
from api import custom_indicators, backtests
app.include_router(custom_indicators.router)
app.include_router(backtests.router)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "中国A股量化交易系统 API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
