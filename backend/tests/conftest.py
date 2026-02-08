"""
Pytest configuration and fixtures for tests.
"""

import pytest
import os
import sys


# Disable rate limiting BEFORE any modules are imported
os.environ["RATE_LIMIT_ENABLED"] = "False"


@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """
    Configure test environment settings.
    
    This fixture runs automatically before any tests and ensures
    rate limiting is disabled for test execution.
    """
    # Ensure rate limiting is disabled
    os.environ["RATE_LIMIT_ENABLED"] = "False"
    
    # Reload config module to pick up the environment variable
    if 'config' in sys.modules:
        import importlib
        import config
        importlib.reload(config)
    
    yield
    
    # Cleanup after tests
    os.environ.pop("RATE_LIMIT_ENABLED", None)
