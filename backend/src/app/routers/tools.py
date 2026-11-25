from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Tool
from app.routers.common import get_admin_json, require_found, validate_required
from app.services.resources import delete, save, save_all

router = APIRouter(prefix="/tools", tags=["tools"])
FIELDS = ("title", "subtitle", "url", "imgUrl", "content")


@router.get("/get")
def get_tools(db: Session = Depends(get_db)):
    return [item.to_dict() for item in db.scalars(select(Tool).order_by(Tool.id.desc()))]


@router.post("/add")
def create_tool(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    validate_required(data, list(FIELDS))
    item = Tool(**{field: data.get(field).strip() for field in FIELDS})
    save(db, item)
    return JSONResponse(content=item.to_dict(), status_code=201)


@router.post("/delete")
def delete_tool(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    validate_required(data, ["id"])
    item = require_found(db.get(Tool, data.get("id")), "工具")
    delete(db, item)
    return {"message": "工具已删除"}


@router.post("/update")
def update_tool(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    validate_required(data, ["id"])
    item = require_found(db.get(Tool, data.get("id")), "工具")
    for field in FIELDS:
        setattr(item, field, data.get(field, getattr(item, field)).strip())
    save(db, item)
    return item.to_dict()


@router.post("/addlist")
def add_tools(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    items = []
    for value in data:
        validate_required(value, list(FIELDS))
        items.append(Tool(**{field: value.get(field).strip() for field in FIELDS}))
    save_all(db, items)
    return JSONResponse(content={"message": f"成功添加 {len(items)} 个工具"}, status_code=201)
