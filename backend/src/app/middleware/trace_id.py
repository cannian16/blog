from __future__ import annotations

import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.context import trace_id_var

logger = logging.getLogger(__name__)


class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
        token = trace_id_var.set(trace_id)
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            response.headers["X-Trace-ID"] = trace_id
            latency_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Request processed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "latency_ms": round(latency_ms, 2),
                },
            )
            return response
        except Exception:
            logger.exception(
                "Request failed",
                extra={"method": request.method, "path": request.url.path},
            )
            raise
        finally:
            trace_id_var.reset(token)
