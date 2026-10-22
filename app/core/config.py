from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Healthcare Directory Search API'
    app_env: str = 'development'
    database_url: str = 'postgresql+psycopg://postgres:postgres@localhost:5432/healthcare'
    admin_api_token: str = 'change-me'
    sync_interval_hours: int = 12
    upstream_api_url: str = 'http://example.com/healthcare'
    similarity_threshold: float = 0.2
    ambiguity_threshold: float = 0.05
    max_search_limit: int = 50
    default_search_limit: int = 10

    @property
    def is_dev(self) -> bool:
        return self.app_env.lower() in {'dev', 'development'}


@lru_cache
def get_settings() -> Settings:
    return Settings()
