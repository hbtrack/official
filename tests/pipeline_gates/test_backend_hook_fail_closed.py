from __future__ import annotations

import importlib.machinery
import importlib.util
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / "scripts" / "hooks" / "check_backend_gate.py"


def _load_hook_module():
    spec = importlib.util.spec_from_loader(
        "backend_gate_module",
        importlib.machinery.SourceFileLoader("backend_gate_module", str(HOOK_PATH)),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_hook(raw_input: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=raw_input,
        text=True,
        capture_output=True,
        cwd=REPO_ROOT,
        check=False,
    )


class TestBackendHookFailClosed:
    def test_invalid_json_blocks_instead_of_allowing(self):
        result = _run_hook("{invalid json")

        assert result.returncode == 2
        payload = json.loads(result.stdout)
        reason = payload["hookSpecificOutput"]["permissionDecisionReason"]
        assert payload["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "BLOCKED_BACKEND_GATE_INTERNAL" in reason
        assert "JSON" in reason

    def test_empty_event_blocks_instead_of_allowing(self):
        result = _run_hook("")

        assert result.returncode == 2
        payload = json.loads(result.stdout)
        reason = payload["hookSpecificOutput"]["permissionDecisionReason"]
        assert payload["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "BLOCKED_BACKEND_GATE_INTERNAL" in reason
        assert "vazio" in reason or "ausente" in reason

    def test_internal_exception_blocks_instead_of_allowing(self, monkeypatch):
        module = _load_hook_module()
        event = {
            "toolName": "editFiles",
            "toolInput": {"filePath": "src/training/api.py"},
        }

        monkeypatch.setattr(module, "extract_file_path", lambda _: (_ for _ in ()).throw(RuntimeError("boom")))
        monkeypatch.setattr(module.sys, "stdin", io.StringIO(json.dumps(event)))

        output = io.StringIO()
        with redirect_stdout(output):
            try:
                module.main()
            except SystemExit as exc:
                assert exc.code == 2

        payload = json.loads(output.getvalue())
        reason = payload["hookSpecificOutput"]["permissionDecisionReason"]
        assert payload["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "BLOCKED_BACKEND_GATE_INTERNAL" in reason
        assert "boom" in reason

    def test_valid_out_of_scope_event_still_passes(self):
        result = _run_hook(
            json.dumps(
                {
                    "toolName": "editFiles",
                    "toolInput": {"filePath": "src/shared/middleware.py"},
                }
            )
        )

        assert result.returncode == 0
        assert result.stdout == ""
