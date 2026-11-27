from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, StripModel


class SongCreate(StripModel):
    title: str = Field(min_length=1, max_length=50)
    artist: str = Field(min_length=1, max_length=50)
    url: str = Field(min_length=1, max_length=200)
    cover: str = Field(min_length=1, max_length=200)


class SongUpdate(StripModel):
    title: str | None = Field(default=None, min_length=1, max_length=50)
    artist: str | None = Field(default=None, min_length=1, max_length=50)
    url: str | None = Field(default=None, min_length=1, max_length=200)
    cover: str | None = Field(default=None, min_length=1, max_length=200)


class SongRead(ORMModel):
    id: int
    title: str
    artist: str
    url: str
    cover: str


class SongListRead(BaseModel):
    items: list[SongRead]
