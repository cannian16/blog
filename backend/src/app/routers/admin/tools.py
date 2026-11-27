from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Tool
from app.schemas.common import BulkCreateRead
from app.schemas.tool import ToolCreate, ToolRead, ToolUpdate
from app.services.resources import delete, save, save_all

router = APIRouter(tags=["admin-tools"])


@router.post("/tools", response_model=ToolRead, status_code=status.HTTP_201_CREATED)
def create_tool(data: ToolCreate, db: Session = Depends(get_db)):
    item = Tool(**data.model_dump(by_alias=True))
    return save(db, item)


@router.post("/tools/bulk", response_model=BulkCreateRead, status_code=status.HTTP_201_CREATED)
def create_tool_bulk(data: list[ToolCreate], db: Session = Depends(get_db)):
    items = [Tool(**entry.model_dump(by_alias=True)) for entry in data]
    save_all(db, items)
    return BulkCreateRead(created=len(items))


@router.patch("/tools/{tool_id}", response_model=ToolRead)
def update_tool(tool_id: int, data: ToolUpdate, db: Session = Depends(get_db)):
    item = db.get(Tool, tool_id)
    if item is None:
        raise HTTPException(status_code=404, detail="工具不存在")
    for field, value in data.model_dump(exclude_unset=True, exclude_none=True, by_alias=True).items():
        setattr(item, field, value)
    return save(db, item)


@router.delete("/tools/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tool(tool_id: int, db: Session = Depends(get_db)):
    item = db.get(Tool, tool_id)
    if item is None:
        raise HTTPException(status_code=404, detail="工具不存在")
    delete(db, item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
