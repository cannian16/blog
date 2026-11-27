from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def require_database_url(environ: Mapping[str, str] | None = None) -> str:
    source = os.environ if environ is None else environ
    database_url = source.get("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is required. Configure a PostgreSQL connection URL "
            "in the environment or backend/.env before starting the application."
        )
    return database_url


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str
    SECRET_KEY: str | None = os.getenv("SECRET_KEY")
    ADMIN_USERNAME: str | None = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD: str | None = os.getenv("ADMIN_PASSWORD")
    GITHUB_TOKEN: str | None = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO: str | None = os.getenv("GITHUB_REPO")


settings = Settings(DATABASE_URL=require_database_url())
