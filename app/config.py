"""
Configuration management
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    DEBUG: bool = True
    API_KEYS: List[str] = []
    ENABLE_API_AUTH: bool = False
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins - parses comma-separated string or JSON array"""
        import json
        origins_str = self.CORS_ORIGINS
        if not origins_str:
            return ["http://localhost:3000", "http://127.0.0.1:3000"]
        
        # Try to parse as JSON array first
        if origins_str.startswith("["):
            try:
                return json.loads(origins_str)
            except json.JSONDecodeError:
                pass
        
        # Fall back to comma-separated
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
    
    # Data storage
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    DB_PATH: str = os.getenv("DB_PATH", "data/market_hours.db")
    
    # Scraper settings
    SCRAPER_ENABLED: bool = True
    SCRAPER_SCHEDULE_HOUR: int = 6  # 6 AM UTC daily
    SCRAPER_TIMEOUT: int = 30
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # API Documentation
    DOCS_PASSWORD: str = "market2025"
    DOCS_SESSION_SECRET: str = "your-secret-key-change-in-production"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "env_parse_none_str": "null"
    }
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """Customize how settings are loaded"""
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


settings = Settings()

# Ensure data directory exists
os.makedirs(settings.DATA_DIR, exist_ok=True)

