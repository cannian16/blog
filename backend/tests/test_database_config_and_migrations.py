from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text

from app.core.config import require_database_url

BACKEND_DIR = Path(__file__).resolve().parents[1]
EXPECTED_TABLES = {"links", "messages", "posts", "skills", "songs", "tools"}


def test_database_url_is_required() -> None:
    with pytest.raises(RuntimeError, match="DATABASE_URL is required"):
        require_database_url({})

    assert require_database_url({"DATABASE_URL": " sqlite:///:memory: "}) == "sqlite:///:memory:"


def test_alembic_upgrade_creates_expected_schema(tmp_path: Path) -> None:
    database_path = tmp_path / "alembic.db"
    database_url = f"sqlite:///{database_path.as_posix()}"
    environment = os.environ.copy()
    environment["DATABASE_URL"] = database_url

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert set(inspector.get_table_names()) == EXPECTED_TABLES | {"alembic_version"}
    assert str(inspector.get_columns("posts")[0]["type"]) == "INTEGER"
    with engine.connect() as connection:
        assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "13a55da86116"
    engine.dispose()
