from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.security import create_access_token, require_admin
from app.routers.common import get_json
from app.services.auth import verify_admin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(data: Any = Depends(get_json)):
    data = data if isinstance(data, dict) else {}
    valid, error_response = verify_admin(data.get("username"), data.get("password"))
    if not valid:
        body, status_code = error_response
        return JSONResponse(content=body, status_code=status_code)
    return {"token": create_access_token()}


@router.get("/me")
def is_auth(_: dict = Depends(require_admin)):
    return {
        "username": settings.ADMIN_USERNAME,
        "avatar_url": "https://vip.123pan.cn/1826899604/yk6baz03t0m000d7w33girwfizdpc39iDIYvAqY2BIQOAcx1AdFy.jpg",
        "role": "admin",
    }
