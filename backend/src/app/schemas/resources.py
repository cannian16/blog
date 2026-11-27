from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LinkSchema(ORMModel):
    id: int | None = None
    name: str
    url: str
    description: str
    icon: str
    created_at: datetime | None = None


class SongSchema(ORMModel):
    id: int | None = None
    title: str
    artist: str
    url: str
    cover: str


class SkillSchema(ORMModel):
    id: int | None = None
    name: str
    logo: str
    url: str


class ToolSchema(ORMModel):
    id: int | None = None
    title: str
    subtitle: str
    url: str
    imgUrl: str
    content: str


class PostSchema(ORMModel):
    id: int
    title: str
    published: datetime | None = None
    description: str = ""
    image: str = ""
    tags: list[Any] = []
    category: str = ""
    content: str
