from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.health import HealthRead

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthRead)
def healthz(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("健康检查失败：数据库不可用")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": "unavailable"},
        )
    return HealthRead(status="ok", database="ok")
