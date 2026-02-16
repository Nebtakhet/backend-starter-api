"""Application configuration loaded from environment variables."""

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Backend Starter API"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    SECRET_KEY: str = Field(..., min_length=32)
    REFRESH_TOKEN_SECRET: str = Field(..., min_length=32)
    JWT_ISSUER: str = "backend-starter-api"
    JWT_AUDIENCE: str = "backend-starter-api"
    CLOCK_SKEW_SECONDS: int = 30
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    AUTH_LOGIN_RATE_LIMIT: str = "5/minute"
    AUTH_REFRESH_RATE_LIMIT: str = "10/minute"
    SQLALCHEMY_DATABASE_URI: str = Field(...)

    @model_validator(mode="after")
    def _validate_security(self):
        # Fail fast on insecure or invalid production settings.
        if self.SECRET_KEY.lower() == "change-me":
            raise ValueError("SECRET_KEY must be set to a strong value")
        if self.REFRESH_TOKEN_SECRET.lower() == "change-me":
            raise ValueError("REFRESH_TOKEN_SECRET must be set to a strong value")
        if self.ENVIRONMENT.lower() == "production":
            if self.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
                raise ValueError("SQLALCHEMY_DATABASE_URI must not use sqlite in production")
        return self


settings = Settings()  # type: ignore[call-arg]
