from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str = "sqlite+aiosqlite:///./data/fastapi.db"
    DB_ECHO: bool = False

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s"
    LOG_DATEFMT: str = "%Y-%m-%d %H:%M:%S"
    LOG_FILE: str = "logs/app.log"
    LOG_FILE_MAX_BYTES: int = 1024 * 1024 * 10
    LOG_FILE_BACKUP_COUNT: int = 5
    LOG_FILE_ENCODING: str = "utf-8"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()