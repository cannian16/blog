from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import create_access_token, require_admin
from app.schemas.auth import TokenRead, UserRead
from app.services.auth import verify_admin

router = APIRouter(prefix="/auth", tags=["auth"])

AVATAR_URL = "https://vip.123pan.cn/1826899604/yk6baz03t0m000d7w33girwfizdpc39iDIYvAqY2BIQOAcx1AdFy.jpg"


@router.post("/login", response_model=TokenRead)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    valid, error_response = verify_admin(form_data.username, form_data.password)
    if not valid:
        body, status_code = error_response
        raise HTTPException(status_code=status_code, detail=body["message"])
    return TokenRead(access_token=create_access_token(form_data.username))


@router.get("/me", response_model=UserRead)
def is_auth(_: dict = Depends(require_admin)):
    return UserRead(
        username=settings.ADMIN_USERNAME or "",
        avatar_url=AVATAR_URL,
        role="admin",
    )
