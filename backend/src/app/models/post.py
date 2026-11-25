from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    published: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    description: Mapped[str] = mapped_column(String(200), server_default="''", nullable=False)
    image: Mapped[str] = mapped_column(String(500), server_default="''", nullable=False)
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    category: Mapped[str] = mapped_column(String(100), server_default="''", nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "metadata": {
                "title": self.title,
                "published": self.published.date().isoformat() if self.published else "",
                "description": self.description,
                "image": self.image,
                "tags": self.tags,
                "category": self.category,
            },
            "content": self.content,
        }
