from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import app.core.logging_config as logging_config

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _run_app_check(debug: bool, code: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.update(
        {
            "DEBUG": "true" if debug else "false",
            "SECRET_KEY": "test-secret-key-with-at-least-32-bytes",
            "ADMIN_USERNAME": "admin",
            "ADMIN_PASSWORD": "password",
        }
    )
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=BACKEND_DIR,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def test_debug_mode_enables_docs():
    code = (
        "from fastapi.testclient import TestClient; "
        "from app.main import app; "
        "client = TestClient(app); "
        "assert client.get('/docs').status_code == 200; "
        "assert client.get('/redoc').status_code == 200; "
        "assert '/links' in client.get('/openapi.json').json()['paths']"
    )
    result = _run_app_check(True, code)
    assert result.returncode == 0, result.stdout + result.stderr


def test_docs_disabled_by_default():
    code = (
        "from fastapi.testclient import TestClient; "
        "from app.main import app; "
        "client = TestClient(app); "
        "assert client.get('/docs').status_code == 404; "
        "assert client.get('/redoc').status_code == 404; "
        "assert client.get('/openapi.json').status_code == 404"
    )
    result = _run_app_check(False, code)
    assert result.returncode == 0, result.stdout + result.stderr


def test_setup_logging_levels_follow_debug(monkeypatch):
    configs: list[dict] = []
    monkeypatch.setattr(logging_config, "dictConfig", configs.append)

    logging_config.setup_logging(True)
    debug_config = configs[-1]
    assert debug_config["loggers"][""]["level"] == "DEBUG"
    assert debug_config["loggers"]["uvicorn.access"]["level"] == "DEBUG"
    assert debug_config["loggers"]["sqlalchemy.engine"]["level"] == "INFO"
    assert debug_config["loggers"]["httpx"]["level"] == "INFO"

    logging_config.setup_logging(False)
    info_config = configs[-1]
    assert info_config["loggers"][""]["level"] == "INFO"
    assert "level" not in info_config["loggers"]["uvicorn.access"]
    assert info_config["loggers"]["sqlalchemy.engine"]["level"] == "WARNING"
    assert info_config["loggers"]["httpx"]["level"] == "WARNING"
