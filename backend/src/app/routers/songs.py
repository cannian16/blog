from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Song
from app.schemas.song import SongListRead

router = APIRouter(tags=["songs"])


@router.get("/songs", response_model=SongListRead)
def get_songs(db: Session = Depends(get_db)):
    items = db.scalars(select(Song).order_by(Song.id.desc())).all()
    return SongListRead(items=items)
