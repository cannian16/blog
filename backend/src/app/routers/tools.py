from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Tool
from app.schemas.tool import ToolListRead

router = APIRouter(tags=["tools"])


@router.get("/tools", response_model=ToolListRead)
def get_tools(db: Session = Depends(get_db)):
    items = db.scalars(select(Tool).order_by(Tool.id.desc())).all()
    return ToolListRead(items=items)
