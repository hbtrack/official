from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from scripts.contracts.validate import validate_contracts as gates


def _make_consumers(root: Path) -> None:
    (root / "contracts" / "consumers" / "mobile-app").mkdir(parents=True, exist_ok=True)


def test_pact_provider_gate_uses_modern_cli_and_maps_token_to_basic_auth(tmp_path, monkeypatch):
    _make_consumers(tmp_path)
    monkeypatch.setenv("PACT_BROKER_BASE_URL", "http://broker.local:9292")
    monkeypatch.setenv("PACT_BROKER_TOKEN", "top-secret")
    monkeypatch.delenv("PACT_BROKER_PASSWORD", raising=False)
    monkeypatch.delenv("PACT_BROKER_USERNAME", raising=False)
    monkeypatch.delenv("PACT_BROKER_AUTH_MODE", raising=False)

    captured: dict[str, list[str]] = {}

    monkeypatch.setattr(
        gates.shutil,
        "which",
        lambda name: "/tmp/pact-broker-cli" if name == "pact-broker-cli" else None,
    )

    def fake_run(cmd, capture_output, text, timeout):
        captured["cmd"] = cmd
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(gates.subprocess, "run", fake_run)

    result = gates._g_pact_provider(tmp_path)

    assert result["status"] == "PASS"
    assert captured["cmd"][:6] == [
        "/tmp/pact-broker-cli",
        "can-i-deploy",
        "--broker-base-url",
        "http://broker.local:9292",
        "--pacticipant",
        "hbtrack-app",
    ]
    assert "--broker-username" in captured["cmd"]
    assert "--broker-password" in captured["cmd"]
    assert "hbtrack" in captured["cmd"]
    assert "top-secret" in captured["cmd"]


def test_pact_provider_gate_supports_explicit_token_auth_mode(tmp_path, monkeypatch):
    _make_consumers(tmp_path)
    monkeypatch.setenv("PACT_BROKER_BASE_URL", "https://example.pactflow.io")
    monkeypatch.setenv("PACT_BROKER_TOKEN", "broker-token")
    monkeypatch.setenv("PACT_BROKER_AUTH_MODE", "token")

    captured: dict[str, list[str]] = {}

    monkeypatch.setattr(
        gates.shutil,
        "which",
        lambda name: "/tmp/pact-broker" if name == "pact-broker" else None,
    )

    def fake_run(cmd, capture_output, text, timeout):
        captured["cmd"] = cmd
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(gates.subprocess, "run", fake_run)

    result = gates._g_pact_provider(tmp_path)

    assert result["status"] == "PASS"
    assert "--broker-token" in captured["cmd"]
    assert "broker-token" in captured["cmd"]
    assert "--broker-username" not in captured["cmd"]
    assert "--broker-password" not in captured["cmd"]


def test_pact_provider_gate_uses_repo_local_fallback_cli(tmp_path, monkeypatch):
    _make_consumers(tmp_path)
    monkeypatch.setenv("PACT_BROKER_BASE_URL", "http://broker.local:9292")
    monkeypatch.setattr(gates.shutil, "which", lambda name: None)
    monkeypatch.setattr(gates, "_broker_has_pacticipant", lambda *args, **kwargs: True)

    pact_bin = tmp_path / "pact" / "bin" / "pact-broker"
    pact_bin.parent.mkdir(parents=True, exist_ok=True)
    pact_bin.write_text("#!/bin/sh\n")

    captured: dict[str, list[str]] = {}

    def fake_run(cmd, capture_output, text, timeout):
        captured["cmd"] = cmd
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(gates.subprocess, "run", fake_run)

    result = gates._g_pact_provider(tmp_path)

    assert result["status"] == "PASS"
    assert captured["cmd"][0] == str(pact_bin)


def test_pact_provider_gate_skips_when_first_consumer_contract_was_not_published(tmp_path, monkeypatch):
    _make_consumers(tmp_path)
    monkeypatch.setenv("PACT_BROKER_BASE_URL", "http://broker.local:9292")
    monkeypatch.setenv("PACT_BROKER_TOKEN", "top-secret")

    monkeypatch.setattr(gates, "_broker_has_pacticipant", lambda *args, **kwargs: False)
    monkeypatch.setattr(
        gates.shutil,
        "which",
        lambda name: "/tmp/pact-broker-cli" if name == "pact-broker-cli" else None,
    )

    def fake_run(cmd, capture_output, text, timeout):
        return SimpleNamespace(
            returncode=1,
            stdout="",
            stderr='Error making request to http://broker.local:9292/matrix status=400 {"errors":["Pacticipant hbtrack-app not found"]}',
        )

    monkeypatch.setattr(gates.subprocess, "run", fake_run)

    result = gates._g_pact_provider(tmp_path)

    assert result["status"] == "SKIP_NOT_APPLICABLE"
    assert "primeiro consumer contract" in result["summary"]
