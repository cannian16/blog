from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, StripModel


class LinkCreate(StripModel):
    name: str = Field(min_length=1, max_length=50)
    url: str = Field(min_length=1, max_length=500)
    description: str = Field(default="", max_length=200)
    icon: str = Field(default="", max_length=500)


class LinkUpdate(StripModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    url: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=200)
    icon: str | None = Field(default=None, max_length=500)


class LinkRead(ORMModel):
    id: int
    name: str
    url: str
    description: str
    icon: str
    created_at: datetime | None


class LinkListRead(BaseModel):
    items: list[LinkRead]
