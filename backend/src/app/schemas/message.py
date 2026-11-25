from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    username: str
    website_url: str = ""
    content: str
    email: str


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    website_url: str | None
    content: str
    email: str
    created_at: datetime | None
