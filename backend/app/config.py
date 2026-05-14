from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    frontend_url: str = "http://localhost:5173"
    secret_key: str = "change-me"
    database_url: str = "sqlite:///./listcraft.db"
    session_cookie_name: str = "listcraft_session"
    session_ttl_days: int = 7
    session_cookie_secure: bool = False
    s3_bucket_name: str = ""
    s3_region: str = ""
    s3_public_base_url: str = ""
    s3_key_prefix: str = "draft-images"
    openai_api_key: str = ""
    openai_model: str = "gpt-5.4-mini"
    ebay_client_id: str = ""
    ebay_client_secret: str = ""
    ebay_redirect_uri: str = ""
    ebay_env: Literal["sandbox", "production"] = "sandbox"
    ebay_marketplace_id: str = "EBAY_CA"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
