from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    icon: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "url": self.url, "description": self.description, "icon": self.icon}
