from __future__ import annotations

import importlib.machinery
import importlib.util
import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HB_SCRIPT = REPO_ROOT / "scripts" / "hb"
SESSION_FILE = REPO_ROOT / "_reports" / "session_start.json"


def _load_hbcli():
    spec = importlib.util.spec_from_loader(
        "hb_stage_allowed_module",
        importlib.machinery.SourceFileLoader("hb_stage_allowed_module", str(HB_SCRIPT)),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.HBCLIv2


HBCLIv2 = _load_hbcli()


def _pick_generate_code_module(cli: HBCLIv2) -> str:
    modules = cli.module_registry.get("modules", {})
    adversarial_root = REPO_ROOT / "_reports" / "adversarial"

    eligible_statuses = {
        "validated_contract",
        "implementation_ready",
        "implemented",
        "staging_validated",
        "released",
    }

    for module_name, meta in sorted(modules.items()):
        if meta.get("status") not in eligible_statuses:
            continue
        report = adversarial_root / module_name / "ALL.adversarial.json"
        if not report.exists():
            continue
        data = json.loads(report.read_text(encoding="utf-8"))
        if data.get("overall_status") == "PASS":
            return module_name

    raise AssertionError("Nenhum módulo elegível com adversarial PASS encontrado para generate_code.")


class TestStageAllowedCatalog:
    def test_tasks_started_via_hb_verify_include_stage_zero(self):
        cli = HBCLIv2()
        task_catalog = cli.task_catalog.get("task_catalog", {})

        for task_type in (
            "readiness_promotion",
            "architecture_review",
            "decision_discovery",
            "generate_code",
        ):
            stage_allowed = (task_catalog.get(task_type) or {}).get("stage_allowed", [])
            assert 0 in stage_allowed, (
                f"{task_type} deve incluir stage 0 para permitir bootstrap via hb verify; "
                f"atual={stage_allowed}"
            )

    def test_stage_outside_allowed_window_returns_false_with_block_code(self):
        cli = HBCLIv2()
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            result = cli._check_stage_allowed("generate_code", 1)

        assert result is False
        assert cli.STAGE_NOT_ALLOWED_BLOCK_CODE in stderr.getvalue()
        assert "stage_allowed" in stderr.getvalue()


class TestStageAllowedCliEnforcement:
    def test_hb_check_blocks_when_task_disallows_stage_one(self):
        cli = HBCLIv2()
        module = _pick_generate_code_module(cli)

        original_session = SESSION_FILE.read_bytes() if SESSION_FILE.exists() else None

        try:
            cli.session = {
                "session_id": "test-stage-allowed",
                "task_type": "generate_code",
                "module": module,
            }
            cli._save_session()

            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = cli.cmd_check(module)

            assert result != 0, "hb check deveria bloquear task_type generate_code em stage 1"
            assert cli.STAGE_NOT_ALLOWED_BLOCK_CODE in (stdout.getvalue() + stderr.getvalue())
        finally:
            if original_session is None:
                SESSION_FILE.unlink(missing_ok=True)
            else:
                SESSION_FILE.write_bytes(original_session)
