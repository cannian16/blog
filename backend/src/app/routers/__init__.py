from collections import defaultdict
from collections.abc import Callable

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute

from app.routers import auth, health, links, messages, posts, skills, songs, system, tools


def _options_endpoint(allow: str) -> Callable[[], HTMLResponse]:
    def options() -> HTMLResponse:
        return HTMLResponse(content="", status_code=200, headers={"Allow": allow})

    return options


def _add_method_compatibility(router: APIRouter) -> None:
    routes = [route for route in router.routes if isinstance(route, APIRoute)]
    methods_by_path: dict[str, set[str]] = defaultdict(set)
    method_order = {
        method: index
        for index, method in enumerate(
            ("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
        )
    }

    for route in routes:
        methods_by_path[route.path].update(route.methods)
        relative_path = route.path.removeprefix(router.prefix) or "/"
        if "GET" in route.methods:
            methods_by_path[route.path].add("HEAD")
            router.add_api_route(
                relative_path,
                route.endpoint,
                methods=["HEAD"],
                response_class=route.response_class,
                include_in_schema=False,
            )

    for path, methods in methods_by_path.items():
        methods.add("OPTIONS")
        allow = ", ".join(
            sorted(
                methods,
                key=lambda method: method_order.get(method, len(method_order)),
            )
        )
        relative_path = path.removeprefix(router.prefix) or "/"
        router.add_api_route(
            relative_path,
            _options_endpoint(allow),
            methods=["OPTIONS"],
            include_in_schema=False,
        )


router = APIRouter()
for child in (
    messages.router,
    links.router,
    songs.router,
    skills.router,
    tools.router,
    posts.router,
    auth.router,
    system.router,
    health.router,
):
    _add_method_compatibility(child)
    router.include_router(child)
