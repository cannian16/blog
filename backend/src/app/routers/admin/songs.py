from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Song
from app.schemas.common import BulkCreateRead
from app.schemas.song import SongCreate, SongRead, SongUpdate
from app.services.resources import delete, save, save_all

router = APIRouter(tags=["admin-songs"])


@router.post("/songs", response_model=SongRead, status_code=status.HTTP_201_CREATED)
def create_song(data: SongCreate, db: Session = Depends(get_db)):
    item = Song(**data.model_dump())
    return save(db, item)


@router.post("/songs/bulk", response_model=BulkCreateRead, status_code=status.HTTP_201_CREATED)
def create_song_bulk(data: list[SongCreate], db: Session = Depends(get_db)):
    items = [Song(**entry.model_dump()) for entry in data]
    save_all(db, items)
    return BulkCreateRead(created=len(items))


@router.patch("/songs/{song_id}", response_model=SongRead)
def update_song(song_id: int, data: SongUpdate, db: Session = Depends(get_db)):
    item = db.get(Song, song_id)
    if item is None:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    for field, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(item, field, value)
    return save(db, item)


@router.delete("/songs/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_song(song_id: int, db: Session = Depends(get_db)):
    item = db.get(Song, song_id)
    if item is None:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    delete(db, item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
