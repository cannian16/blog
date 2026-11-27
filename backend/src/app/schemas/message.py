from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import StripModel

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
WEBSITE_PATTERN = re.compile(r"^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/.*)?$")


class MessageCreate(StripModel):
    username: str = Field(min_length=1, max_length=20)
    website_url: str | None = None
    content: str = Field(min_length=1, max_length=200)
    email: str = Field(max_length=100)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not EMAIL_PATTERN.fullmatch(value):
            raise ValueError("邮箱格式不正确")
        return value

    @field_validator("website_url")
    @classmethod
    def validate_website_url(cls, value: str | None) -> str | None:
        if not value:
            return None
        if not WEBSITE_PATTERN.fullmatch(value):
            raise ValueError("网址格式不正确")
        return value


class MessageRead(BaseModel):
    id: int
    username: str
    website_url: str | None
    content: str
    created_at: datetime | None
    email_hash: str


class MessageListRead(BaseModel):
    items: list[MessageRead]
    total: int
    page: int
    limit: int
    pages: int
