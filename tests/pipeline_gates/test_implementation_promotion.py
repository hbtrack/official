from __future__ import annotations

import importlib.machinery
import importlib.util
import io
import json
from contextlib import redirect_stderr
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
HB_SCRIPT = ROOT / "scripts" / "hb"


def _load_hbcli():
    spec = importlib.util.spec_from_loader(
        "hb_implementation_promotion_module",
        importlib.machinery.SourceFileLoader(
            "hb_implementation_promotion_module",
            str(HB_SCRIPT),
        ),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.HBCLIv2


HBCLIv2 = _load_hbcli()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestImplementationPromotionPolicyParity:
    def test_catalog_registers_active_worker(self):
        catalog = yaml.safe_load((ROOT / ".contract_driven" / "TASK_CATALOG.yaml").read_text(encoding="utf-8"))
        entry = catalog["task_catalog"]["implementation_promotion"]

        assert entry["status"] == "active"
        assert entry["worker_id"] == "implementation_promotion"
        assert entry["worker_path"] == ".contract_driven/agent_prompts/implementation_promotion.prompt.md"
        assert entry["profile_id"] == "contract_execution"
        assert 0 in entry["stage_allowed"]
        assert "Único caminho formal para implemented." in entry["notes"]

    def test_prompt_pipeline_registry_and_rules_align_on_formal_route(self):
        prompt = (
            ROOT / ".contract_driven" / "agent_prompts" / "implementation_promotion.prompt.md"
        ).read_text(encoding="utf-8")
        pipeline = (ROOT / "docs" / "_canon" / "CONTRACT_PIPELINE.md").read_text(encoding="utf-8")
        registry = yaml.safe_load((ROOT / "docs" / "_canon" / "MODULE_REGISTRY.yaml").read_text(encoding="utf-8"))
        rules = (ROOT / ".contract_driven" / "CONTRACT_SYSTEM_RULES.md").read_text(encoding="utf-8")

        assert "único caminho formal" in prompt.lower()
        assert "FEATURE_REGISTRY.yaml" in prompt
        assert "SESSION_HANDOFF.md" in prompt
        assert "implementation_promotion" in pipeline
        assert "via promoção formal" in pipeline
        assert "implementation_promotion" in registry["policy"]["status_semantics"]["implementation_ready"]
        assert "implementation_promotion" in registry["policy"]["status_semantics"]["implemented"]
        assert "implementation_promotion" in rules

    def test_session_start_schema_accepts_task_type(self):
        schema = json.loads(
            (ROOT / "contracts" / "schemas" / "shared" / "session_start.schema.json").read_text(
                encoding="utf-8"
            )
        )
        generated = json.loads(
            (
                ROOT
                / "generated"
                / "contracts"
                / "schemas"
                / "shared"
                / "session_start.schema.json"
            ).read_text(encoding="utf-8")
        )

        assert "implementation_promotion" in schema["properties"]["task_type"]["enum"]
        assert "implementation_promotion" in generated["properties"]["task_type"]["enum"]


class TestImplementationPromotionEligibility:
    def test_helper_accepts_only_implementation_ready_with_evidence(self, tmp_path):
        cli = HBCLIv2()
        cli.root = tmp_path
        cli.module_registry = {
            "modules": {
                "reports": {"status": "implementation_ready"},
                "training": {"status": "implemented"},
            }
        }

        _write(
            tmp_path / "docs" / "_canon" / "FEATURE_REGISTRY.yaml",
            yaml.safe_dump(
                {
                    "features": [
                        {"id": "FT-REP-001", "module": "reports", "status": "implemented"},
                    ]
                },
                sort_keys=False,
                allow_unicode=True,
            ),
        )
        _write(
            tmp_path / "_reports" / "adversarial" / "reports" / "ALL.adversarial.json",
            json.dumps({"module": "reports", "overall_status": "PASS"}),
        )
        _write(tmp_path / "src" / "reports" / "api.py", "from .schemas import ReportJobOut\n")
        _write(tmp_path / "src" / "reports" / "schemas.py", "class ReportJobOut: ...\n")
        (tmp_path / "src" / "reports" / "tests").mkdir(parents=True, exist_ok=True)

        assert cli._check_implementation_promotion_eligibility("reports") == 0

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = cli._check_implementation_promotion_eligibility("training")
        assert result == 1
        assert "BLOCKED_IMPLEMENTATION_PROMOTION_INELIGIBLE" in stderr.getvalue()

    def test_hb_verify_accepts_task_when_module_is_temporarily_implementation_ready(self):
        import subprocess
        import sys

        registry_path = ROOT / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
        session_path = ROOT / "_reports" / "session_start.json"

        original_registry = registry_path.read_bytes()
        original_session = session_path.read_bytes() if session_path.exists() else None

        try:
            registry = yaml.safe_load(original_registry.decode("utf-8"))
            registry["modules"]["reports"]["status"] = "implementation_ready"
            registry_path.write_text(
                yaml.safe_dump(registry, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(HB_SCRIPT),
                    "verify",
                    "--task-type",
                    "implementation_promotion",
                    "--module",
                    "reports",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            combined = result.stdout + result.stderr
            assert result.returncode == 0, combined

            session = json.loads(session_path.read_text(encoding="utf-8"))
            assert session["task_type"] == "implementation_promotion"
            assert session["write_scope"] == "docs"
        finally:
            registry_path.write_bytes(original_registry)
            if original_session is None:
                session_path.unlink(missing_ok=True)
            else:
                session_path.write_bytes(original_session)
