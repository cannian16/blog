from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

from app.core.config import require_database_url
from app.core.db import Base
import app.models  # noqa: F401

BACKEND_DIR = Path(__file__).resolve().parents[1]
EXPECTED_TABLES = {"links", "messages", "posts", "skills", "songs", "tools"}

EXPECTED_COLUMNS = {
    "links": [
        ("id", "INTEGER", False, True, None),
        ("name", "VARCHAR(50)", False, False, None),
        ("url", "VARCHAR(500)", False, False, None),
        ("description", "VARCHAR(200)", False, False, None),
        ("icon", "VARCHAR(500)", False, False, None),
        ("created_at", "DATETIME", True, False, "now()"),
    ],
    "messages": [
        ("id", "INTEGER", False, True, None),
        ("username", "VARCHAR(50)", False, False, None),
        ("website_url", "VARCHAR(200)", True, False, None),
        ("content", "TEXT", False, False, None),
        ("email", "VARCHAR(100)", False, False, None),
        ("ip_address", "VARCHAR(45)", True, False, None),
        ("user_agent", "VARCHAR(500)", True, False, None),
        ("created_at", "DATETIME", True, False, "now()"),
    ],
    "posts": [
        ("id", "INTEGER", False, True, None),
        ("title", "VARCHAR(200)", False, False, None),
        ("published", "DATETIME", False, False, "now()"),
        ("description", "VARCHAR(200)", False, False, ""),
        ("image", "VARCHAR(500)", False, False, ""),
        ("tags", "JSON", False, False, None),
        ("category", "VARCHAR(100)", False, False, ""),
        ("content", "TEXT", False, False, None),
    ],
    "skills": [
        ("id", "INTEGER", False, True, None),
        ("name", "VARCHAR(50)", False, False, None),
        ("logo", "VARCHAR(200)", False, False, None),
        ("url", "VARCHAR(200)", False, False, None),
    ],
    "songs": [
        ("id", "INTEGER", False, True, None),
        ("title", "VARCHAR(50)", False, False, None),
        ("artist", "VARCHAR(50)", False, False, None),
        ("url", "VARCHAR(200)", False, False, None),
        ("cover", "VARCHAR(200)", False, False, None),
    ],
    "tools": [
        ("id", "INTEGER", False, True, None),
        ("title", "VARCHAR(50)", False, False, None),
        ("subtitle", "VARCHAR(50)", False, False, None),
        ("url", "VARCHAR(200)", False, False, None),
        ("imgUrl", "VARCHAR(200)", False, False, None),
        ("content", "TEXT", False, False, None),
    ],
}


def test_model_table_structure_is_unchanged():
    assert set(Base.metadata.tables) == EXPECTED_TABLES
    for table_name, expected_columns in EXPECTED_COLUMNS.items():
        table = Base.metadata.tables[table_name]
        actual_columns = [
            (
                column.name,
                str(column.type),
                column.nullable,
                column.primary_key,
                str(column.server_default.arg) if column.server_default else None,
            )
            for column in table.columns
        ]
        assert actual_columns == expected_columns


def test_database_url_is_required() -> None:
    with pytest.raises(RuntimeError, match="DATABASE_URL is required"):
        require_database_url({})

    assert require_database_url({"DATABASE_URL": " postgresql://u:p@localhost/db "}) == (
        "postgresql://u:p@localhost/db"
    )


def test_alembic_upgrade_creates_expected_schema(test_database_url: str) -> None:
    base_url = make_url(test_database_url)
    database_name = f"blog_migration_test_{uuid4().hex[:12]}"
    migration_url = base_url.set(database=database_name)

    admin_engine = create_engine(base_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))

    try:
        environment = os.environ.copy()
        environment["DATABASE_URL"] = migration_url.render_as_string(hide_password=False)

        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=BACKEND_DIR,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr

        engine = create_engine(migration_url)
        try:
            inspector = inspect(engine)
            assert set(inspector.get_table_names()) == EXPECTED_TABLES | {"alembic_version"}
            with engine.connect() as connection:
                migration_context = MigrationContext.configure(
                    connection,
                    opts={"compare_type": True},
                )
                assert compare_metadata(migration_context, Base.metadata) == []
                assert (
                    connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                    == "13a55da86116"
                )
        finally:
            engine.dispose()
    finally:
        with admin_engine.connect() as connection:
            connection.execute(text(f'DROP DATABASE IF EXISTS "{database_name}" WITH (FORCE)'))
        admin_engine.dispose()
