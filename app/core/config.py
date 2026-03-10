from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Example"
    PROJECT_VERSION: str = "0.1.0"

    DATABASE_URL: str = "sqlite+aiosqlite:///database.db"
    DATABASE_ECHO: bool = False
    DATABASE_EXPIRE_ON_COMMIT: bool = False

    REDIS_URL: str = "redis://localhost:6379/0"

    PROXY_TRUSTED_HOSTS: list[str] = ["*"]

    TEMPLATES_DIR: str = "templates"

    STATIC_PATH: str = "static"
    STATIC_URL: str = "/static"
    STATIC_NAME: str = "static"

    SESSION_SECRET_KEY: str = "secret_key"  # 必须从环境变量设置，无默认值， openssl rand -hex 32
    SESSION_COOKIE: str = "session"
    SESSION_MAX_AGE: int = 60 * 60
    SESSION_HTTPS_ONLY: bool = False  # 生产环境设为 True
    SESSION_SAME_SITE: str = "lax"

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_BYTES: int = 1024 * 1024 * 10
    LOG_BACKUP_COUNT: int = 5
    LOG_ENCODING: str = "utf-8"
    LOG_FORMAT: str = "%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s"

    COOKIE_MAX_AGE_SECONDS: int = 60 * 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()