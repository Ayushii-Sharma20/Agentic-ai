from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "AI Terms Analyzer API"
    API_VERSION: str = "2.0.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: list = ["chrome-extension://*", "http://localhost:3000"]
    
    # Model Settings
    SUMMARIZER_MODEL: str = "sshleifer/distilbart-cnn-12-6"
    CLASSIFIER_MODEL: str = "facebook/bart-large-mnli"
    
    # Agent Settings
    MAX_SUMMARY_LENGTH: int = 70
    MIN_SUMMARY_LENGTH: int = 20
    CHUNK_SIZE: int = 500  # tokens
    
    # Cache Settings
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 3600  # 1 hour
    
    # Risk Thresholds
    HIGH_RISK_THRESHOLD: int = 3
    MEDIUM_RISK_THRESHOLD: int = 1
    
    # Clause Categories
    CLAUSE_CATEGORIES: list = [
        "data collection",
        "data sharing with third parties",
        "tracking and cookies",
        "user content ownership",
        "liability limitation",
        "arbitration clause",
        "automatic renewal",
        "account termination",
        "privacy rights"
    ]
    
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings():
    return Settings()