from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Her zaman quiz-service/.env dosyasını oku (uvicorn başka dizinden çalışsa bile)
_SERVICE_ROOT = Path(__file__).resolve().parents[2]
_ENV_PATH = _SERVICE_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_PATH, env_file_encoding="utf-8", extra="ignore")

    app_name: str = "quiz-service"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://postgres@localhost:5432/quiz"
    cors_origins: str = "*"

    jwt_secret: str = "dev-only-change-me-use-openssl-rand-hex-32"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    admin_bootstrap_username: str | None = None
    admin_bootstrap_password: str | None = None


def get_settings() -> Settings:
    return Settings()
