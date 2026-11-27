from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Skill
from app.schemas.common import BulkCreateRead
from app.schemas.skill import SkillCreate, SkillRead, SkillUpdate
from app.services.resources import delete, save, save_all

router = APIRouter(tags=["admin-skills"])


@router.post("/skills", response_model=SkillRead, status_code=status.HTTP_201_CREATED)
def create_skill(data: SkillCreate, db: Session = Depends(get_db)):
    item = Skill(**data.model_dump())
    return save(db, item)


@router.post("/skills/bulk", response_model=BulkCreateRead, status_code=status.HTTP_201_CREATED)
def create_skill_bulk(data: list[SkillCreate], db: Session = Depends(get_db)):
    items = [Skill(**entry.model_dump()) for entry in data]
    save_all(db, items)
    return BulkCreateRead(created=len(items))


@router.patch("/skills/{skill_id}", response_model=SkillRead)
def update_skill(skill_id: int, data: SkillUpdate, db: Session = Depends(get_db)):
    item = db.get(Skill, skill_id)
    if item is None:
        raise HTTPException(status_code=404, detail="技能不存在")
    for field, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(item, field, value)
    return save(db, item)


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    item = db.get(Skill, skill_id)
    if item is None:
        raise HTTPException(status_code=404, detail="技能不存在")
    delete(db, item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
