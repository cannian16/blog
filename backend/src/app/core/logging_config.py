from __future__ import annotations

import logging
from logging.config import dictConfig

from app.core.context import trace_id_var

STANDARD_FORMAT = "%(levelname)-8s | %(asctime)s | %(name)s | %(trace_id)s | %(message)s | %(extra_str)s"

_RESERVED_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class TraceIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        custom_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _RESERVED_ATTRS and key not in ("trace_id", "extra_str")
        }
        record.extra_str = str(custom_fields) if custom_fields else ""
        record.trace_id = trace_id_var.get()
        return True


def build_logging_config(debug: bool) -> dict:
    level = "DEBUG" if debug else "INFO"
    uvicorn_loggers: dict[str, dict] = {
        "uvicorn": {"handlers": [], "propagate": True},
        "uvicorn.error": {"handlers": [], "propagate": True},
        "uvicorn.access": {"handlers": [], "propagate": True},
    }
    if debug:
        for logger_config in uvicorn_loggers.values():
            logger_config["level"] = "DEBUG"

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": STANDARD_FORMAT},
        },
        "filters": {
            "trace_id": {"()": "app.core.logging_config.TraceIDFilter"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "filters": ["trace_id"],
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {"handlers": ["console"], "level": level},
            **uvicorn_loggers,
            "sqlalchemy.engine": {
                "handlers": [],
                "level": "INFO" if debug else "WARNING",
                "propagate": True,
            },
            "httpx": {
                "handlers": [],
                "level": "INFO" if debug else "WARNING",
                "propagate": True,
            },
        },
    }


def setup_logging(debug: bool) -> None:
    dictConfig(build_logging_config(debug))
