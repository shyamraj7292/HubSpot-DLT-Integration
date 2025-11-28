"""
Application settings and configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    env: str = "dev"
    
    # HubSpot Configuration
    hubspot_api_base_url: str = "https://api.hubapi.com"
    hubspot_api_timeout: int = 30
    hubspot_access_token: Optional[str] = None
    
    # DLT Configuration
    dlt_pipeline_name: str = "hubspot_deals"
    dlt_database_schema: str = "hubspot_deals"
    
    # Database Configuration
    database_url: Optional[str] = None
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "hubspot_deals_db"
    db_user: str = "user"
    db_password: str = "password"
    
    # Service Configuration
    service_port: int = 5200
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

