"""
Database utilities for DLT pipeline configuration
"""
from config.settings import get_settings


def get_dlt_database_config() -> dict:
    """
    Get database configuration for DLT pipeline
    
    Returns:
        Dictionary with database connection parameters
    """
    settings = get_settings()
    
    # Use DATABASE_URL if provided, otherwise construct from components
    if settings.database_url:
        return {
            "database_url": settings.database_url
        }
    else:
        return {
            "database_url": (
                f"postgresql://{settings.db_user}:{settings.db_password}"
                f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
            )
        }

