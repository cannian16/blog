from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str] = mapped_column(String(200), nullable=False)
    imgUrl: Mapped[str] = mapped_column("imgUrl", String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "subtitle": self.subtitle, "url": self.url, "imgUrl": self.imgUrl, "content": self.content}
