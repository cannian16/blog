from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, StripModel


class PostCreate(StripModel):
    id: int
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=200)
    image: str = Field(default="", max_length=500)
    tags: list[str] = Field(default_factory=list)
    category: str = Field(default="", max_length=100)
    content: str = Field(min_length=1)


class PostUpdate(StripModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=200)
    image: str | None = Field(default=None, max_length=500)
    tags: list[str] | None = None
    category: str | None = Field(default=None, max_length=100)
    content: str | None = Field(default=None, min_length=1)


class PostRead(ORMModel):
    id: int
    title: str
    published: datetime | None
    description: str
    image: str
    tags: list[str]
    category: str
    content: str


class PostListRead(BaseModel):
    items: list[PostRead]
