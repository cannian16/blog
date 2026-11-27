from __future__ import annotations

from fastapi.testclient import TestClient

import app.core.logging_config as logging_config
import app.main as main_module


def test_create_app_enables_docs_when_debug(tmp_path, monkeypatch):
    calls: list[bool] = []
    monkeypatch.setattr(main_module, "setup_logging", calls.append)

    application = main_module.create_app(
        f"sqlite:///{(tmp_path / 'debug.db').as_posix()}",
        create_tables=True,
        debug=True,
    )
    assert calls == [True]

    with TestClient(application) as client:
        assert client.get("/docs").status_code == 200
        assert client.get("/redoc").status_code == 200
        schema = client.get("/openapi.json")
        assert schema.status_code == 200
        assert "/links/get" in schema.json()["paths"]


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
