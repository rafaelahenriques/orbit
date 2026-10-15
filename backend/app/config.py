from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings, read from environment variables.

    Defaults match the local Docker Compose services so the app runs out of the box
    in development. Deployed environments must set every value explicitly.
    """

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "postgresql+psycopg://orbit:orbit@localhost:5433/orbit"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = ["http://localhost:3000"]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
