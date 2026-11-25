from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Skill
from app.routers.common import get_admin_json, require_found, validate_required
from app.services.resources import delete, save, save_all

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/get")
def get_skills(db: Session = Depends(get_db)):
    return [item.to_dict() for item in db.scalars(select(Skill).order_by(Skill.id.asc()))]


@router.post("/add")
def create_skill(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    validate_required(data, ["name", "logo", "url"])
    item = Skill(**{field: data.get(field).strip() for field in ("name", "logo", "url")})
    save(db, item)
    return JSONResponse(content=item.to_dict(), status_code=201)


@router.post("/addlist")
def create_skills(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    items = []
    for value in data:
        validate_required(value, ["name", "logo", "url"])
        items.append(Skill(**{field: value.get(field).strip() for field in ("name", "logo", "url")}))
    save_all(db, items)
    return JSONResponse(content={"message": f"成功添加 {len(items)} 个技能"}, status_code=201)


@router.post("/delete")
def delete_skill(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    validate_required(data, ["id"])
    item = require_found(db.get(Skill, data.get("id")), "技能")
    delete(db, item)
    return {"message": "技能已删除"}


@router.post("/update")
def update_skill(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    validate_required(data, ["id"])
    item = require_found(db.get(Skill, data.get("id")), "技能")
    for field in ("name", "logo", "url"):
        setattr(item, field, data.get(field, getattr(item, field)).strip())
    save(db, item)
    return item.to_dict()
