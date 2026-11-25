from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str | None = None
    password: str | None = None
