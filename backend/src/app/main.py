from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.db import Base, check_db_health, configure_database
from app.core.logging_config import setup_logging
from app.middleware.trace_id import TraceIDMiddleware
from app.models import Link, Message, Post, Skill, Song, Tool  # noqa: F401
from app.routers import router as api_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    check_db_health()
    yield


def create_app(
    database_url: str | None = None,
    *,
    create_tables: bool = False,
    debug: bool | None = None,
) -> FastAPI:
    debug_enabled = settings.DEBUG if debug is None else debug
    setup_logging(debug_enabled)

    selected_engine = configure_database(database_url or settings.DATABASE_URL)
    if create_tables:
        Base.metadata.create_all(selected_engine)

    application = FastAPI(
        docs_url="/docs" if debug_enabled else None,
        redoc_url="/redoc" if debug_enabled else None,
        openapi_url="/openapi.json" if debug_enabled else None,
        lifespan=lifespan,
    )
    application.add_middleware(TraceIDMiddleware)
    application.include_router(api_router)
    return application


app = create_app()
