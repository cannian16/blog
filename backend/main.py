from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
SRC_DIR = BACKEND_DIR / "src"
INSTANCE_DIR = BACKEND_DIR / "instance"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def init_db() -> None:
    from app.core.config import settings
    from app.core.db import Base, configure_database
    from app.models import Link, Message, Post, Skill, Song, Tool  # noqa: F401

    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    engine = configure_database(settings.DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Database tables initialized (existing data was preserved).")


def serve() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=5000)


def main() -> None:
    parser = argparse.ArgumentParser(description="Blog FastAPI backend")
    parser.add_argument(
        "command",
        nargs="?",
        choices=("serve", "init-db"),
        default="serve",
        help="serve (default) or safely create missing database tables",
    )
    args = parser.parse_args()

    if args.command == "init-db":
        init_db()
    else:
        serve()


if __name__ == "__main__":
    main()
