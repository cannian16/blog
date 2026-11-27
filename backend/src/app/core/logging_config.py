from __future__ import annotations

from logging.config import dictConfig

STANDARD_FORMAT = "%(levelname)-8s | %(asctime)s | %(name)s | %(message)s"


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
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
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
