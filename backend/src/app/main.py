from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException

from app.core.config import settings
from app.core.db import Base, configure_database
from app.core.logging_config import setup_logging
from app.core.security import AuthenticationError, authentication_error_handler
from app.models import Link, Message, Post, Skill, Song, Tool  # noqa: F401
from app.routers import router as api_router
from app.routers.common import FlaskHTTPError, flask_error_response


def _options_endpoint(allow: str) -> Callable[[], HTMLResponse]:
    def options() -> HTMLResponse:
        return HTMLResponse(content="", status_code=200, headers={"Allow": allow})

    return options


def _add_method_compatibility(application: FastAPI) -> set[str]:
    routes = [route for route in application.routes if isinstance(route, APIRoute)]
    methods_by_path: dict[str, set[str]] = defaultdict(set)

    for route in routes:
        methods_by_path[route.path].update(route.methods)
        if "GET" in route.methods:
            methods_by_path[route.path].add("HEAD")
            application.add_api_route(
                route.path,
                route.endpoint,
                methods=["HEAD"],
                response_class=route.response_class,
                include_in_schema=False,
            )

    method_order = {method: index for index, method in enumerate(("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"))}
    for path, methods in methods_by_path.items():
        methods.add("OPTIONS")
        allow = ", ".join(sorted(methods, key=lambda method: method_order.get(method, len(method_order))))
        application.add_api_route(
            path,
            _options_endpoint(allow),
            methods=["OPTIONS"],
            include_in_schema=False,
        )
    return set(methods_by_path)


def create_app(
    database_url: str | None = None,
    *,
    create_tables: bool = False,
    debug: bool | None = None,
) -> FastAPI:
    debug_enabled = settings.DEBUG if debug is None else debug
    setup_logging(debug_enabled)

    selected_engine = configure_database(database_url or settings.DATABASE_URL)
    if create_tables:
        Base.metadata.create_all(selected_engine)

    application = FastAPI(
        docs_url="/docs" if debug_enabled else None,
        redoc_url="/redoc" if debug_enabled else None,
        openapi_url="/openapi.json" if debug_enabled else None,
    )
    application.add_exception_handler(AuthenticationError, authentication_error_handler)

    @application.exception_handler(FlaskHTTPError)
    async def flask_http_error(_, exc: FlaskHTTPError):
        return flask_error_response(exc.status_code)

    @application.exception_handler(HTTPException)
    async def compatibility_http_error(_, exc: HTTPException):
        if exc.status_code == 404 and not isinstance(exc.detail, dict):
            return flask_error_response(404)
        content = exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail}
        return JSONResponse(status_code=exc.status_code, content=content, headers=exc.headers)

    @application.get("/", response_class=PlainTextResponse)
    def hello() -> str:
        return "Hello, World!"

    application.include_router(api_router)
    business_paths = set(application.openapi()["paths"])
    _add_method_compatibility(application)

    @application.middleware("http")
    async def reject_unknown_options(request, call_next):
        if request.method == "OPTIONS" and request.url.path not in business_paths:
            return flask_error_response(404)
        return await call_next(request)

    return application


app = create_app()
