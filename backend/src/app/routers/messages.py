from __future__ import annotations

from math import ceil

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Message
from app.schemas.message import MessageCreate, MessageListRead, MessageRead
from app.services.message import message_read
from app.services.resources import save

router = APIRouter(tags=["messages"])


@router.get("/messages", response_model=MessageListRead)
def get_messages(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.scalar(select(func.count()).select_from(Message)) or 0
    messages = db.scalars(
        select(Message).order_by(Message.created_at.desc()).offset((page - 1) * limit).limit(limit)
    ).all()
    return MessageListRead(
        items=[message_read(message) for message in messages],
        total=total,
        page=page,
        limit=limit,
        pages=ceil(total / limit) if total else 0,
    )


@router.post("/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def create_message(data: MessageCreate, request: Request, db: Session = Depends(get_db)):
    message = Message(
        username=data.username,
        website_url=data.website_url,
        content=data.content,
        email=data.email,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )
    save(db, message)
    return message_read(message)
