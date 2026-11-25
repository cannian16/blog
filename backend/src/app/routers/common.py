from typing import Any

from fastapi import Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.core.security import require_admin


class FlaskHTTPError(Exception):
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


_ERROR_DETAILS = {
    400: ("Bad Request", "The browser (or proxy) sent a request that this server could not understand."),
    404: (
        "Not Found",
        "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.",
    ),
    415: (
        "Unsupported Media Type",
        "Did not attempt to load JSON data because the request Content-Type was not 'application/json'.",
    ),
}


def flask_error_response(status_code: int) -> HTMLResponse:
    title, description = _ERROR_DETAILS[status_code]
    content = (
        "<!doctype html>\n"
        "<html lang=en>\n"
        f"<title>{status_code} {title}</title>\n"
        f"<h1>{title}</h1>\n"
        f"<p>{description}</p>\n"
    )
    return HTMLResponse(content=content, status_code=status_code)


async def get_json(request: Request) -> Any:
    mimetype = request.headers.get("content-type", "").partition(";")[0].strip().lower()
    if mimetype != "application/json" and not (mimetype.startswith("application/") and mimetype.endswith("+json")):
        raise FlaskHTTPError(415)
    try:
        return await request.json()
    except (ValueError, UnicodeDecodeError) as exc:
        raise FlaskHTTPError(400) from exc


async def get_admin_json(
    _: dict = Depends(require_admin),
    data: Any = Depends(get_json),
) -> Any:
    return data


def validate_required(data: Any, required_fields: list[str]) -> None:
    if not data or not isinstance(data, dict):
        raise HTTPException(status_code=400, detail={"error": "请求体不能为空"})
    missing = []
    for field in required_fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    if missing:
        raise HTTPException(status_code=400, detail={"error": f"缺少必填字段或内容为空: {', '.join(missing)}"})


def require_found(instance: Any, label: str) -> Any:
    del label
    if instance is None:
        raise FlaskHTTPError(404)
    return instance
