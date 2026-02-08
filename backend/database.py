"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.log_level == "DEBUG"
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Import models to register them with Base
# This ensures models are available when Base.metadata.create_all() is called
def import_models():
    """Import all models to register them with SQLAlchemy Base."""
    try:
        from models import stock, kline_data, strategy  # noqa: F401
    except ImportError:
        # Models might not be available in some contexts (e.g., during initial setup)
        pass


# Import models when this module is loaded
import_models()
