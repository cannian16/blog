from app.extensions import db
from sqlalchemy import JSON

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    published = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    description = db.Column(db.String(200), server_default="''", nullable=False)
    image = db.Column(db.String(500), server_default="''", nullable=False)
    tags = db.Column(JSON, default=[], nullable=False)
    category = db.Column(db.String(100), server_default="''", nullable=False)
    content = db.Column(db.Text, nullable=False)
    

    def to_dict(self):
        return {
            "id": self.id,
            "metadata": {
                "title": self.title,
                "published": self.published.date().isoformat() if self.published else "",
                "description": self.description,
                "image": self.image,
                "tags": self.tags,
                "category": self.category
            },
            "content": self.content 
        }