from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Example"
    PROJECT_VERSION: str = "0.1.0"

    DATABASE_URL: str = "sqlite+aiosqlite:///database.db"
    DATABASE_ECHO: bool = False
    DATABASE_EXPIRE_ON_COMMIT: bool = False

    REDIS_URL: str = "redis://localhost:6379/0"

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_BYTES: int = 1024 * 1024 * 10
    LOG_BACKUP_COUNT: int = 5
    LOG_ENCODING: str = "utf-8"
    LOG_FORMAT: str = "%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()