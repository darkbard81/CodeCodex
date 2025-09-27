"""Application configuration for the relay server."""
from __future__ import annotations

from functools import lru_cache
from typing import Dict

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    relay_services: Dict[str, str] = Field(
        default_factory=lambda: {
            "httpbin": "https://httpbin.org",
        },
        description=(
            "Mapping of service identifiers to the upstream base URLs that the "
            "relay server is allowed to proxy requests to."
        ),
    )

    class Config:
        env_prefix = "RELAY_"
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("relay_services", pre=True)
    def _normalize_services(cls, value: Dict[str, str]) -> Dict[str, str]:
        if isinstance(value, str):
            # Allow JSON-style strings or comma-separated "name=url" pairs
            import json

            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
            services: Dict[str, str] = {}
            for item in value.split(","):
                if not item:
                    continue
                name, _, url = item.partition("=")
                if not name or not url:
                    raise ValueError(
                        "relay_services must be provided as JSON or 'name=url' pairs"
                    )
                services[name.strip()] = url.strip()
            return services
        return value


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()


settings = get_settings()
