from __future__ import annotations

import importlib


def test_settings_append_healthcheck_hosts(monkeypatch):
    monkeypatch.setenv("ALLOWED_HOSTS", "staging.handballtrack.app,191.252.185.34")

    import config.settings as settings

    settings = importlib.reload(settings)

    assert "staging.handballtrack.app" in settings.ALLOWED_HOSTS
    assert "191.252.185.34" in settings.ALLOWED_HOSTS
    assert "localhost" in settings.ALLOWED_HOSTS
    assert "127.0.0.1" in settings.ALLOWED_HOSTS
    assert "[::1]" in settings.ALLOWED_HOSTS
