from __future__ import annotations

from pydantic import BaseModel


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    username: str
    avatar_url: str
    role: str
