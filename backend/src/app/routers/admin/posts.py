from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Post
from app.schemas.post import PostCreate, PostRead, PostUpdate
from app.services.resources import delete, save

router = APIRouter(tags=["admin-posts"])


@router.post("/posts", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(data: PostCreate, db: Session = Depends(get_db)):
    item = Post(**data.model_dump())
    return save(db, item)


@router.patch("/posts/{post_id}", response_model=PostRead)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):
    item = db.get(Post, post_id)
    if item is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    for field, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(item, field, value)
    return save(db, item)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    item = db.get(Post, post_id)
    if item is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    delete(db, item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
