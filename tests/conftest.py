import socket
from dataclasses import replace
from pathlib import Path

import pytest
from src.config import load_settings


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Network access is forbidden in Phase 0 tests")
    for name in ("connect", "connect_ex"):
        monkeypatch.setattr(socket.socket, name, denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(socket, "getaddrinfo", denied)


@pytest.fixture
def config(tmp_path):
    return replace(load_settings({}, env_file=tmp_path / "absent.env"), state_dir=tmp_path)
