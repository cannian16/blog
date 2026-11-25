from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Song
from app.routers.common import get_admin_json, require_found, validate_required
from app.services.resources import delete, save, save_all

router = APIRouter(prefix="/songs", tags=["songs"])


@router.get("/get")
def get_songs(db: Session = Depends(get_db)):
    return [item.to_dict() for item in db.scalars(select(Song).order_by(Song.id.desc()))]


@router.post("/add")
def create_song(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    validate_required(data, ["title", "artist", "url", "cover"])
    item = Song(**{field: data.get(field).strip() for field in ("title", "artist", "url", "cover")})
    save(db, item)
    return JSONResponse(content=item.to_dict(), status_code=201)


@router.post("/delete")
def delete_song(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    validate_required(data, ["id"])
    item = require_found(db.get(Song, data.get("id")), "歌曲")
    delete(db, item)
    return {"message": "歌曲已删除"}


@router.post("/update")
def update_song(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    validate_required(data, ["id"])
    item = require_found(db.get(Song, data.get("id")), "歌曲")
    for field in ("title", "artist", "url", "cover"):
        setattr(item, field, data.get(field, getattr(item, field)).strip())
    save(db, item)
    return item.to_dict()


@router.post("/addlist")
def add_song_list(data: Any = Depends(get_admin_json), db: Session = Depends(get_db)):
    items = [Song(**{field: value.get(field).strip() for field in ("title", "artist", "url", "cover")}) for value in data]
    save_all(db, items)
    return JSONResponse(content={"message": f"成功添加 {len(items)} 首歌曲"}, status_code=201)
