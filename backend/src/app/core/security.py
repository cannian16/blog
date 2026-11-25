from __future__ import annotations

import time

import jwt
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import settings


class AuthenticationError(Exception):
    def __init__(self, body: dict[str, str], status_code: int) -> None:
        self.body = body
        self.status_code = status_code


def create_access_token() -> str:
    now = int(time.time())
    return jwt.encode(
        {"admin": True, "iat": now, "exp": now + 86400 * 30},
        settings.SECRET_KEY,
        algorithm="HS256",
    )


def require_admin(request: Request) -> dict:
    authorization = request.headers.get("Authorization")
    if authorization is None or not authorization.startswith("Bearer "):
        raise AuthenticationError({"message": "未提供有效凭证"}, 401)
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        if not payload.get("admin"):
            raise AuthenticationError({"message": "权限不足"}, 403)
        return payload
    except AuthenticationError:
        raise
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError({"message": "Token 已过期"}, 401) from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError({"message": "无效的 Token"}, 401) from exc
    except Exception as exc:
        raise AuthenticationError({"message": f"验证失败: {exc}"}, 401) from exc


def authentication_error_handler(_, exc: AuthenticationError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.body)
