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
        "hb_runtime_promotions_module",
        importlib.machinery.SourceFileLoader(
            "hb_runtime_promotions_module",
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


class TestRuntimePromotionPolicyParity:
    def test_catalog_registers_active_runtime_workers(self):
        catalog = yaml.safe_load((ROOT / ".contract_driven" / "TASK_CATALOG.yaml").read_text(encoding="utf-8"))
        staging = catalog["task_catalog"]["staging_promotion"]
        release = catalog["task_catalog"]["release_promotion"]

        assert staging["status"] == "active"
        assert release["status"] == "active"
        assert staging["worker_path"].endswith("staging_promotion.prompt.md")
        assert release["worker_path"].endswith("release_promotion.prompt.md")
        assert 0 in staging["stage_allowed"]
        assert 0 in release["stage_allowed"]

    def test_prompt_pipeline_registry_and_rules_align_on_formal_runtime_routes(self):
        staging_prompt = (
            ROOT / ".contract_driven" / "agent_prompts" / "staging_promotion.prompt.md"
        ).read_text(encoding="utf-8")
        release_prompt = (
            ROOT / ".contract_driven" / "agent_prompts" / "release_promotion.prompt.md"
        ).read_text(encoding="utf-8")
        pipeline = (ROOT / "docs" / "_canon" / "CONTRACT_PIPELINE.md").read_text(encoding="utf-8")
        registry = yaml.safe_load((ROOT / "docs" / "_canon" / "MODULE_REGISTRY.yaml").read_text(encoding="utf-8"))
        rules = (ROOT / ".contract_driven" / "CONTRACT_SYSTEM_RULES.md").read_text(encoding="utf-8")

        assert "único caminho formal" in staging_prompt.lower()
        assert "único caminho formal" in release_prompt.lower()
        assert "staging_promotion" in pipeline
        assert "release_promotion" in pipeline
        assert "staging_promotion" in registry["policy"]["status_semantics"]["staging_validated"]
        assert "release_promotion" in registry["policy"]["status_semantics"]["released"]
        assert "staging_promotion" in rules
        assert "release_promotion" in rules

    def test_session_start_schema_accepts_runtime_promotion_task_types(self):
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

        for task_type in ("staging_promotion", "release_promotion"):
            assert task_type in schema["properties"]["task_type"]["enum"]
            assert task_type in generated["properties"]["task_type"]["enum"]


class TestRuntimePromotionEligibility:
    def test_helpers_enforce_exact_statuses_and_pipeline_prereqs(self, tmp_path):
        cli = HBCLIv2()
        cli.root = tmp_path
        cli.module_registry = {
            "modules": {
                "reports": {"status": "implemented"},
                "training": {"status": "staging_validated"},
                "analytics": {"status": "implementation_ready"},
            }
        }
        _write(
            tmp_path / "_reports" / "contract_gates" / "latest.json",
            json.dumps(
                {
                    "overall_status": "PASS",
                    "gates": [
                        {"gate_id": "DEPLOY_READINESS_GATE", "status": "PASS"},
                        {"gate_id": "HTTP_RUNTIME_CONTRACT_GATE", "status": "SKIP_NOT_APPLICABLE"},
                    ],
                }
            ),
        )

        assert cli._check_staging_promotion_eligibility("reports") == 0
        assert cli._check_release_promotion_eligibility("training") == 0

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = cli._check_staging_promotion_eligibility("analytics")
        assert result == 1
        assert "BLOCKED_STAGING_PROMOTION_INELIGIBLE" in stderr.getvalue()

    def test_hb_verify_accepts_staging_promotion_for_real_repo_module(self):
        import subprocess
        import sys

        session_path = ROOT / "_reports" / "session_start.json"
        latest_path = ROOT / "_reports" / "contract_gates" / "latest.json"
        original_session = session_path.read_bytes() if session_path.exists() else None
        original_latest = latest_path.read_bytes() if latest_path.exists() else None

        try:
            latest_path.write_text(
                json.dumps(
                    {
                        "overall_status": "PASS",
                        "gates": [
                            {"gate_id": "DEPLOY_READINESS_GATE", "status": "PASS"},
                            {"gate_id": "HTTP_RUNTIME_CONTRACT_GATE", "status": "SKIP_NOT_APPLICABLE"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(HB_SCRIPT),
                    "verify",
                    "--task-type",
                    "staging_promotion",
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
            assert session["task_type"] == "staging_promotion"
            assert session["write_scope"] == "docs"
        finally:
            if original_latest is None:
                latest_path.unlink(missing_ok=True)
            else:
                latest_path.write_bytes(original_latest)
            if original_session is None:
                session_path.unlink(missing_ok=True)
            else:
                session_path.write_bytes(original_session)

    def test_hb_verify_accepts_release_promotion_when_registry_is_temporarily_aligned(self):
        import subprocess
        import sys

        registry_path = ROOT / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
        session_path = ROOT / "_reports" / "session_start.json"
        latest_path = ROOT / "_reports" / "contract_gates" / "latest.json"

        original_registry = registry_path.read_bytes()
        original_session = session_path.read_bytes() if session_path.exists() else None
        original_latest = latest_path.read_bytes() if latest_path.exists() else None

        try:
            registry = yaml.safe_load(original_registry.decode("utf-8"))
            registry["modules"]["reports"]["status"] = "staging_validated"
            registry_path.write_text(
                yaml.safe_dump(registry, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            latest_path.write_text(
                json.dumps(
                    {
                        "overall_status": "PASS",
                        "gates": [
                            {"gate_id": "DEPLOY_READINESS_GATE", "status": "PASS"},
                            {"gate_id": "HTTP_RUNTIME_CONTRACT_GATE", "status": "SKIP_NOT_APPLICABLE"},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(HB_SCRIPT),
                    "verify",
                    "--task-type",
                    "release_promotion",
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
            assert session["task_type"] == "release_promotion"
            assert session["write_scope"] == "docs"
        finally:
            if original_latest is None:
                latest_path.unlink(missing_ok=True)
            else:
                latest_path.write_bytes(original_latest)
            registry_path.write_bytes(original_registry)
            if original_session is None:
                session_path.unlink(missing_ok=True)
            else:
                session_path.write_bytes(original_session)
