from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import require_admin
from app.routers.admin import links, posts, skills, songs, tools

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])

for child in (links.router, songs.router, skills.router, tools.router, posts.router):
    router.include_router(child)
