from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Link
from app.routers.common import get_admin_json, require_found
from app.services.resources import delete, save, save_all

router = APIRouter(prefix="/links", tags=["links"])


@router.get("/get")
def get_links(db: Session = Depends(get_db)):
    return [item.to_dict() for item in db.scalars(select(Link).order_by(Link.created_at.desc()))]


@router.post("/add")
def create_link(data: dict = Depends(get_admin_json), db: Session = Depends(get_db)):
    item = Link(name=data.get("name").strip(), url=data.get("url").strip(), description=data.get("description").strip(), icon=data.get("icon").strip())
    save(db, item)
    return JSONResponse(content=item.to_dict(), status_code=201)


@router.post("/delete")
def delete_link(data: dict = Depends(get_admin_json), db: Session = Depends(get_db)):
    item = require_found(db.get(Link, data.get("id")), "友链")
    delete(db, item)
    return {"message": "友链已删除"}


@router.post("/update")
def update_link(data: dict = Depends(get_admin_json), db: Session = Depends(get_db)):
    item = require_found(db.get(Link, data.get("id")), "友链")
    for field in ("name", "url", "description", "icon"):
        setattr(item, field, data.get(field, getattr(item, field)).strip())
    save(db, item)
    return item.to_dict()


@router.post("/addlist")
def add_links(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    items = []
    for value in data:
        name, url = value.get("name", "").strip(), value.get("url", "").strip()
        if name and url:
            items.append(Link(name=name, url=url, description=value.get("description", "").strip(), icon=value.get("icon", "").strip()))
    save_all(db, items)
    return JSONResponse(content={"message": f"成功添加 {len(items)} 个友链"}, status_code=201)
