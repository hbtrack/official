from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import sys
from pathlib import Path
from urllib.error import HTTPError

import yaml


ROOT = Path(__file__).resolve().parents[2]
FRONTEND_PACKAGE_PATH = ROOT / "frontend" / "package.json"
CI_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "ci.yml"
DEPLOY_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "deploy.yml"
PACT_TEST_PATH = ROOT / "frontend" / "src" / "api" / "__tests__" / "hbtrack.consumer.pact.test.ts"
PUBLISH_SCRIPT_PATH = ROOT / "scripts" / "contracts" / "pact" / "publish_frontend_pacts.py"
VERIFY_SCRIPT_PATH = ROOT / "scripts" / "contracts" / "pact" / "verify_staging_provider.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_loader(
        name,
        importlib.machinery.SourceFileLoader(name, str(path)),
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


publish_module = _load_module("hbtrack_publish_frontend_pacts", PUBLISH_SCRIPT_PATH)
verify_module = _load_module("hbtrack_verify_staging_provider", VERIFY_SCRIPT_PATH)


def test_frontend_package_declares_pact_scripts_and_dependencies():
    package = json.loads(FRONTEND_PACKAGE_PATH.read_text(encoding="utf-8"))
    scripts = package.get("scripts", {})
    dev_deps = package.get("devDependencies", {})

    assert scripts.get("test:pact") == "vitest run src/api/__tests__/hbtrack.consumer.pact.test.ts --reporter=verbose"
    assert scripts.get("pact:publish") == "python3 ../scripts/contracts/pact/publish_frontend_pacts.py"
    assert "@pact-foundation/pact" in dev_deps
    assert "graphql" in dev_deps


def test_consumer_pact_bootstrap_artifacts_exist():
    assert PACT_TEST_PATH.exists(), "Primeira suíte Pact do consumer hbtrack-app deve existir no frontend."
    assert PUBLISH_SCRIPT_PATH.exists(), "Script de publish dos consumer pacts deve existir."
    assert VERIFY_SCRIPT_PATH.exists(), "Script de verify do provider contra o broker deve existir."


def test_publish_script_builds_publish_command_with_branch_and_basic_auth_fallback(monkeypatch, tmp_path: Path):
    (tmp_path / "frontend" / "pacts").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(publish_module, "resolve_executable", lambda *args, **kwargs: "/tmp/pact-broker")
    monkeypatch.setattr(publish_module, "resolve_version", lambda env, env_key, *, cwd: "sha-123")
    monkeypatch.setattr(publish_module, "resolve_branch", lambda env, env_key, *, cwd: "main")

    cmd = publish_module.build_publish_command(
        tmp_path,
        {
            "PACT_BROKER_BASE_URL": "http://broker.local:9292",
            "PACT_BROKER_TOKEN": "top-secret",
        },
    )

    assert cmd[:6] == [
        "/tmp/pact-broker",
        "publish",
        str(tmp_path / "frontend" / "pacts"),
        "--consumer-app-version",
        "sha-123",
        "--broker-base-url",
    ]
    assert "http://broker.local:9292" in cmd
    assert "--branch" in cmd
    assert "main" in cmd
    assert "--broker-username" in cmd
    assert "--broker-password" in cmd
    assert "hbtrack" in cmd
    assert "top-secret" in cmd


def test_verify_script_builds_provider_verifier_command(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(verify_module, "resolve_executable", lambda *args, **kwargs: "/tmp/pact-provider-verifier")
    monkeypatch.setattr(verify_module, "resolve_version", lambda env, env_key, *, cwd: "provider-sha")
    monkeypatch.setattr(verify_module, "resolve_branch", lambda env, env_key, *, cwd: "main")

    cmd = verify_module.build_verify_command(
        tmp_path,
        {
            "PACT_BROKER_BASE_URL": "http://broker.local:9292",
            "PACT_BROKER_TOKEN": "top-secret",
            "HB_STAGING_URL": "https://staging.handballtrack.app",
        },
    )

    assert cmd[:8] == [
        "/tmp/pact-provider-verifier",
        "--pact-broker-base-url",
        "http://broker.local:9292",
        "--provider",
        "hbtrack-api",
        "--provider-base-url",
        "https://staging.handballtrack.app",
        "--publish-verification-results",
    ]
    assert "--provider-app-version" in cmd
    assert "provider-sha" in cmd
    assert "--provider-version-branch" in cmd
    assert "main" in cmd
    assert "--enable-pending" in cmd
    assert "--broker-username" in cmd
    assert "--broker-password" in cmd


def test_publish_script_cli_main_returns_actionable_error_on_broker_auth_failure(monkeypatch, tmp_path: Path, capsys):
    pacts_dir = tmp_path / "frontend" / "pacts"
    pacts_dir.mkdir(parents=True, exist_ok=True)
    (pacts_dir / "hbtrack-app-hbtrack-api.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(publish_module, "repo_root", lambda: tmp_path)
    monkeypatch.setenv("PACT_BROKER_BASE_URL", "http://broker.local:9292")
    monkeypatch.setattr(publish_module, "resolve_executable", lambda *args, **kwargs: "/tmp/pact-broker")
    monkeypatch.setattr(publish_module, "resolve_version", lambda env, env_key, *, cwd: "sha-123")
    monkeypatch.setattr(publish_module, "resolve_branch", lambda env, env_key, *, cwd: "main")

    def fake_run_checked(cmd, *, cwd):
        raise publish_module.subprocess.CalledProcessError(1, cmd)

    monkeypatch.setattr(publish_module, "run_checked", fake_run_checked)

    assert publish_module.cli_main() == 1
    captured = capsys.readouterr()
    assert "Command failed with exit code 1" in captured.err
    assert "pact-broker" in captured.err


def test_verify_script_cli_main_returns_actionable_error_when_broker_requires_auth(
    monkeypatch,
    tmp_path: Path,
    capsys,
):
    monkeypatch.setattr(verify_module, "repo_root", lambda: tmp_path)
    monkeypatch.setenv("PACT_BROKER_BASE_URL", "http://broker.local:9292")
    monkeypatch.setenv("HB_STAGING_URL", "https://staging.handballtrack.app")

    def fake_broker_has_pacticipant(*args, **kwargs):
        raise HTTPError(
            "http://broker.local:9292/pacticipants/hbtrack-app",
            401,
            "Unauthorized",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(verify_module, "broker_has_pacticipant", fake_broker_has_pacticipant)

    assert verify_module.cli_main() == 1
    captured = capsys.readouterr()
    assert "Pact Broker requires authentication" in captured.err
    assert "PACT_BROKER_TOKEN" in captured.err


def test_ci_and_deploy_workflows_wire_pact_publish_and_provider_verify():
    ci_workflow = yaml.safe_load(CI_WORKFLOW_PATH.read_text(encoding="utf-8"))
    deploy_workflow = yaml.safe_load(DEPLOY_WORKFLOW_PATH.read_text(encoding="utf-8"))

    build_frontend_steps = ci_workflow["jobs"]["build-frontend"]["steps"]
    contract_conformance_steps = deploy_workflow["jobs"]["contract-conformance"]["steps"]

    assert any(step.get("name") == "Run consumer contract tests (Pact)" for step in build_frontend_steps)
    assert any(step.get("name") == "Publish consumer contracts to Pact Broker" for step in build_frontend_steps)
    assert any(
        step.get("run") == "python3 scripts/contracts/pact/publish_frontend_pacts.py"
        for step in build_frontend_steps
    )
    assert any(
        step.get("name") == "Verify staging provider against published consumer contracts"
        for step in contract_conformance_steps
    )
    assert any(
        step.get("run") == "python3 scripts/contracts/pact/verify_staging_provider.py"
        for step in contract_conformance_steps
    )
