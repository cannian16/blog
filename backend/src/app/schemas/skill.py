from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, StripModel


class SkillCreate(StripModel):
    name: str = Field(min_length=1, max_length=50)
    logo: str = Field(min_length=1, max_length=200)
    url: str = Field(min_length=1, max_length=200)


class SkillUpdate(StripModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    logo: str | None = Field(default=None, min_length=1, max_length=200)
    url: str | None = Field(default=None, min_length=1, max_length=200)


class SkillRead(ORMModel):
    id: int
    name: str
    logo: str
    url: str


class SkillListRead(BaseModel):
    items: list[SkillRead]
