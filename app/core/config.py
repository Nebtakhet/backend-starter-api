from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str = "Backend Starter API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field("change-me", min_length=8)
    REFRESH_TOKEN_SECRET: str = Field("change-me", min_length=8)
    JWT_ISSUER: str = "backend-starter-api"
    JWT_AUDIENCE: str = "backend-starter-api"
    CLOCK_SKEW_SECONDS: int = 30
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./app.db"


settings = Settings()
