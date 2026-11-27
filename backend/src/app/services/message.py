from __future__ import annotations

import hashlib

from app.models.message import Message
from app.schemas.message import MessageRead


def hash_email(email: str) -> str:
    return hashlib.sha256(email.lower().encode()).hexdigest()


def message_read(message: Message) -> MessageRead:
    return MessageRead(
        id=message.id,
        username=message.username,
        website_url=message.website_url,
        content=message.content,
        created_at=message.created_at,
        email_hash=hash_email(message.email),
    )
