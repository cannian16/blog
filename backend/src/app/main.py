from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.db import check_db_health
from app.core.logging_config import setup_logging
from app.middleware.trace_id import TraceIDMiddleware
from app.routers import router as api_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    check_db_health()
    yield


setup_logging(settings.DEBUG)

app = FastAPI(
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)
app.add_middleware(TraceIDMiddleware)
app.include_router(api_router)
