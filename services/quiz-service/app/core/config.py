from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "quiz-service"
    database_url: str = "postgresql+asyncpg://postgres@localhost:5432/quiz"
    cors_origins: str = "*"


def get_settings() -> Settings:
    return Settings()
