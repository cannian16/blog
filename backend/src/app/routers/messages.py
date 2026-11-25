from math import ceil
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Message
from app.routers.common import get_json
from app.services.message import email_hash, validate_data
from app.services.resources import save

router = APIRouter(prefix="/messages", tags=["messages"])


def _int_query(request: Request, name: str, default: int) -> int:
    try:
        value = int(request.query_params.get(name, default))
        return value if value > 0 else default
    except (TypeError, ValueError):
        return default


@router.get("/get")
def get_messages(request: Request, db: Session = Depends(get_db)):
    page = _int_query(request, "page", 1)
    limit = _int_query(request, "limit", 20)
    total = db.scalar(select(func.count()).select_from(Message)) or 0
    messages = list(db.scalars(select(Message).order_by(Message.created_at.desc()).offset((page - 1) * limit).limit(limit)))
    return {
        "messages": email_hash(messages),
        "pagination": {"total": total, "page": page, "limit": limit, "pages": ceil(total / limit) if total else 0},
    }


@router.post("/add")
def create_message(request: Request, data: Any = Depends(get_json), db: Session = Depends(get_db)):
    valid, error_message = validate_data(data if isinstance(data, dict) else None)
    if not valid:
        return JSONResponse(content={"error": error_message}, status_code=400)
    username = data.get("username").strip()
    website_url = data.get("website_url", "").strip() or None
    message = Message(
        username=username,
        website_url=website_url,
        content=data.get("content").strip(),
        email=data.get("email").strip(),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )
    save(db, message)
    return JSONResponse(content={"message": "留言创建成功", "id": message.id}, status_code=201)
