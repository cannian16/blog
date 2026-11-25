from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Post
from app.routers.common import get_admin_json, require_found, validate_required
from app.services.resources import delete, save

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/get")
def get_posts(db: Session = Depends(get_db)):
    return [item.to_dict() for item in db.scalars(select(Post).order_by(Post.published.desc()))]


@router.post("/add")
def create_post(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    validate_required(data, ["id", "title", "content"])
    item = Post(
        id=data.get("id").strip(), title=data.get("title").strip(),
        description=data.get("description", "").strip(), image=data.get("image", "").strip(),
        tags=data.get("tags", []), category=data.get("category", "").strip(), content=data.get("content").strip(),
    )
    save(db, item)
    return JSONResponse(content=item.to_dict(), status_code=201)


@router.post("/delete")
def delete_post(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    validate_required(data, ["id"])
    item = require_found(db.get(Post, data.get("id")), "文章")
    delete(db, item)
    return {"message": "文章已删除"}


@router.post("/update")
def update_post(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    validate_required(data, ["id"])
    item = require_found(db.get(Post, data.get("id")), "文章")
    for field in ("title", "description", "image", "category", "content"):
        setattr(item, field, data.get(field, getattr(item, field)).strip())
    item.tags = data.get("tags", item.tags)
    save(db, item)
    return item.to_dict()
