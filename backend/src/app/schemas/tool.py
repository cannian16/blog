from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ORMModel, StripModel


class ToolCreate(StripModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    title: str = Field(min_length=1, max_length=50)
    subtitle: str = Field(min_length=1, max_length=50)
    url: str = Field(min_length=1, max_length=200)
    img_url: str = Field(alias="imgUrl", min_length=1, max_length=200)
    content: str = Field(min_length=1)


class ToolUpdate(StripModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    title: str | None = Field(default=None, min_length=1, max_length=50)
    subtitle: str | None = Field(default=None, min_length=1, max_length=50)
    url: str | None = Field(default=None, min_length=1, max_length=200)
    img_url: str | None = Field(default=None, alias="imgUrl", min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)


class ToolRead(ORMModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    title: str
    subtitle: str
    url: str
    img_url: str = Field(alias="imgUrl")
    content: str


class ToolListRead(BaseModel):
    items: list[ToolRead]
