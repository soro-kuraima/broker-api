# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Broker API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-super-secret-key"
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite:///./app.db"
    CSV_FILE_PATH: Path = Path("backend_table.csv")
    BACKUP_DIR: Path = Path("broker-api-backup")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    class Config:
        case_sensitive = True

@lru_cache
def get_settings():
    return Settings()