from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Link
from app.schemas.common import BulkCreateRead
from app.schemas.link import LinkCreate, LinkRead, LinkUpdate
from app.services.resources import delete, save, save_all

router = APIRouter(tags=["admin-links"])


@router.post("/links", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
def create_link(data: LinkCreate, db: Session = Depends(get_db)):
    item = Link(**data.model_dump())
    return save(db, item)


@router.post("/links/bulk", response_model=BulkCreateRead, status_code=status.HTTP_201_CREATED)
def create_link_bulk(data: list[LinkCreate], db: Session = Depends(get_db)):
    items = [Link(**entry.model_dump()) for entry in data]
    save_all(db, items)
    return BulkCreateRead(created=len(items))


@router.patch("/links/{link_id}", response_model=LinkRead)
def update_link(link_id: int, data: LinkUpdate, db: Session = Depends(get_db)):
    item = db.get(Link, link_id)
    if item is None:
        raise HTTPException(status_code=404, detail="友链不存在")
    for field, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(item, field, value)
    return save(db, item)


@router.delete("/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(link_id: int, db: Session = Depends(get_db)):
    item = db.get(Link, link_id)
    if item is None:
        raise HTTPException(status_code=404, detail="友链不存在")
    delete(db, item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
