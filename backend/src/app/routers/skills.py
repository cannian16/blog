from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Skill
from app.schemas.skill import SkillListRead

router = APIRouter(tags=["skills"])


@router.get("/skills", response_model=SkillListRead)
def get_skills(db: Session = Depends(get_db)):
    items = db.scalars(select(Skill).order_by(Skill.id.asc())).all()
    return SkillListRead(items=items)
