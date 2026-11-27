from __future__ import annotations

from fastapi import APIRouter

from app.routers import auth, health, links, messages, posts, skills, songs, tools
from app.routers.admin import router as admin_router

router = APIRouter()

for child in (
    auth.router,
    health.router,
    messages.router,
    links.router,
    songs.router,
    skills.router,
    tools.router,
    posts.router,
):
    router.include_router(child)

router.include_router(admin_router)
