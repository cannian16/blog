from __future__ import annotations

import logging
import os
import sys
from collections.abc import Mapping

from dotenv import load_dotenv
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

logger = logging.getLogger(__name__)


def require_database_url(environ: Mapping[str, str] | None = None) -> str:
    source = os.environ if environ is None else environ
    database_url = source.get("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is required. Configure a PostgreSQL connection URL "
            "in the environment or backend/.env before starting the application."
        )
    return database_url


class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool = False

    SECRET_KEY: str | None = None
    ADMIN_USERNAME: str | None = None
    ADMIN_PASSWORD: str | None = None
    GITHUB_TOKEN: str | None = None
    GITHUB_REPO: str | None = None

    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )


def load_settings() -> Settings:
    database_url = require_database_url()
    try:
        return Settings(DATABASE_URL=database_url)
    except ValidationError as exc:
        logger.critical("❌ 服务启动失败：环境变量校验未通过")
        for error in exc.errors():
            location = "->".join(map(str, error["loc"]))
            logger.error("  - 缺失/错误项: %s | 原因: %s", location, error["msg"])
        sys.exit(1)


settings = load_settings()
