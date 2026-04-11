"""Invariant tests for canonical state artifact restoration in scripts/hb."""

import importlib.machinery
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).parent.parent.parent
HB_SCRIPT = REPO_ROOT / "scripts" / "hb"


def _load_hb_module():
    spec = importlib.util.spec_from_loader(
        "hb_module_state_restore",
        importlib.machinery.SourceFileLoader("hb_module_state_restore", str(HB_SCRIPT)),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hb_module = _load_hb_module()
HBCLIv2 = hb_module.HBCLIv2


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_cmd_ci_restores_canonical_state_artifacts(tmp_path, monkeypatch):
    """cmd_ci deve restaurar session_start/latest após subprocessos observacionais."""
    cli = HBCLIv2()
    cli.root = tmp_path
    cli.session_file = tmp_path / "_reports" / "session_start.json"

    _write_json(
        tmp_path / "toolchain.json",
        {
            "services": {
                "postgres": {
                    "port": 5432,
                    "test_user": "hbtrack",
                    "test_password": "hbtrack",
                    "test_db": "hbtrack_test",
                },
                "redis": {"port": 6379},
            }
        },
    )

    original_session = {
        "operation_mode": "ROADMAP",
        "module_focus": "training",
        "roadmap_phase": 5,
        "roadmap_task_id": "B10-003",
        "stage0_exit_code": 0,
    }
    original_latest = {
        "pipeline_id": "HB_TRACK_CONTRACT_GATES",
        "overall_status": "PASS",
        "exit_code": 0,
    }

    latest_path = tmp_path / "_reports" / "contract_gates" / "latest.json"
    _write_json(cli.session_file, original_session)
    _write_json(latest_path, original_latest)

    calls = []

    def fake_run(cmd, *args, **kwargs):
        calls.append(cmd)
        if isinstance(cmd, list) and len(cmd) >= 3 and cmd[1:3] == ["-m", "pytest"]:
            _write_json(
                cli.session_file,
                {
                    "operation_mode": "ROADMAP",
                    "module_focus": "training",
                    "roadmap_phase": 1,
                    "roadmap_task_id": None,
                    "stage0_exit_code": 2,
                },
            )
            _write_json(
                latest_path,
                {
                    "pipeline_id": "HB_TRACK_CONTRACT_GATES",
                    "overall_status": "FAIL",
                    "exit_code": 2,
                },
            )
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(hb_module.subprocess, "run", fake_run)

    assert cli.cmd_ci("pr") == 0
    assert json.loads(cli.session_file.read_text(encoding="utf-8")) == original_session
    assert json.loads(latest_path.read_text(encoding="utf-8")) == original_latest
    assert any(isinstance(cmd, list) and "manage.py" in cmd for cmd in calls)
    assert any(isinstance(cmd, list) and cmd[1:3] == ["-m", "pytest"] for cmd in calls)
