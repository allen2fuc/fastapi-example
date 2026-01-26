from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str = "sqlite+aiosqlite:///./db.sqlite3"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()