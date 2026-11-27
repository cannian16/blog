from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Link
from app.schemas.link import LinkListRead

router = APIRouter(tags=["links"])


@router.get("/links", response_model=LinkListRead)
def get_links(db: Session = Depends(get_db)):
    items = db.scalars(select(Link).order_by(Link.created_at.desc())).all()
    return LinkListRead(items=items)
