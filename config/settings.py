"""
SENTINEL Configuration Settings
Global configuration for the Geopolitical Trade Risk Navigator
"""

import os
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Main application settings"""
    
    # Application
    APP_NAME: str = "SENTINEL"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/sentinel.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Data Sources
    NEWS_API_KEY: Optional[str] = None
    WORLD_BANK_API_KEY: Optional[str] = None
    SHIPPING_API_KEY: Optional[str] = None
    
    # Risk Scoring
    RISK_SCORE_WEIGHTS: Dict[str, float] = {
        "geopolitical": 0.25,
        "economic": 0.20,
        "supply_chain": 0.20,
        "cyber": 0.15,
        "regulatory": 0.10,
        "environmental": 0.10
    }
    
    # Machine Learning
    ML_MODEL_PATH: str = "models/trained/"
    MODEL_UPDATE_FREQUENCY: int = 24  # hours
    
    # Dashboard
    DASHBOARD_HOST: str = "0.0.0.0"
    DASHBOARD_PORT: int = 8050
    
    # Data Generation
    SYNTHETIC_DATA_SIZE: Dict[str, int] = {
        "countries": 50,
        "suppliers": 1000,
        "trade_routes": 100,
        "products": 200,
        "companies": 100
    }
    
    # Monitoring
    LOG_LEVEL: str = "INFO"
    METRICS_PORT: int = 9090
    
    # File Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = BASE_DIR / "models"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(exist_ok=True)
settings.MODELS_DIR.mkdir(exist_ok=True)
settings.LOGS_DIR.mkdir(exist_ok=True) 