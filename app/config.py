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
    # Use env var DATABASE_URL if provided, otherwise default to the secure path.
    DATABASE_URL: str = "sqlite:////data/app.db"
    # CSV_FILE_PATH will point to the secure /data directory.
    CSV_FILE_PATH: Path = Path("/data/backend_table.csv")
    BACKUP_DIR: Path = Path("/data/broker-api-backup")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    class Config:
        case_sensitive = True

@lru_cache
def get_settings():
    return Settings()
