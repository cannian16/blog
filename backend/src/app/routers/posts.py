from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Post
from app.schemas.post import PostListRead, PostRead

router = APIRouter(tags=["posts"])


@router.get("/posts", response_model=PostListRead)
def get_posts(db: Session = Depends(get_db)):
    items = db.scalars(select(Post).order_by(Post.published.desc())).all()
    return PostListRead(items=items)


@router.get("/posts/{post_id}", response_model=PostRead)
def get_post(post_id: int, db: Session = Depends(get_db)):
    item = db.get(Post, post_id)
    if item is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    return item
