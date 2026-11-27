from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    artist: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str] = mapped_column(String(200), nullable=False)
    cover: Mapped[str] = mapped_column(String(200), nullable=False)

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "artist": self.artist, "url": self.url, "cover": self.cover}
