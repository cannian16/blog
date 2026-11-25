import hashlib
import re
from collections.abc import Iterable
from typing import Any

from app.models.message import Message


def email_hash(messages: Iterable[Message]) -> list[dict[str, Any]]:
    processed_messages = []
    for message in messages:
        message_dict = message.to_dict()
        email = message_dict["email"]
        message_dict["email_hash"] = hashlib.sha256(email.lower().encode()).hexdigest()
        del message_dict["email"]
        processed_messages.append(message_dict)
    return processed_messages


def validate_data(data: dict | None) -> tuple[bool, str | None]:
    data = data or {}
    username = data.get("username", "").strip()
    website_url = data.get("website_url", "").strip()
    content = data.get("content", "").strip()
    email = data.get("email", "").strip()

    if not 1 <= len(username) <= 20:
        return False, "用户名长度需在1-20位之间"
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return False, "邮箱格式不正确"
    if not content or len(content) > 200:
        return False, "内容不能为空且不能超过200字"
    if website_url and not re.match(r"^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/.*)?$", website_url):
        return False, "网址格式不正确"
    return True, None
