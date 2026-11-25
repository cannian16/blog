from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[3]
DEFAULT_DATABASE_URL = f"sqlite:///{(BACKEND_DIR / 'instance' / 'app.db').as_posix()}"

load_dotenv()


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    SECRET_KEY: str | None = os.getenv("SECRET_KEY")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "")
    ADMIN_USERNAME: str | None = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD: str | None = os.getenv("ADMIN_PASSWORD")
    GITHUB_TOKEN: str | None = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO: str | None = os.getenv("GITHUB_REPO")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin for origin in self.ALLOWED_ORIGINS.split(",") if origin]


settings = Settings()
