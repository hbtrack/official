from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
HB_SCRIPT = REPO_ROOT / "scripts" / "hb"
MODULE_REGISTRY_PATH = REPO_ROOT / "docs" / "_canon" / "MODULE_REGISTRY.yaml"


def _load_hbcli():
    spec = importlib.util.spec_from_loader(
        "hb_generate_code_module",
        importlib.machinery.SourceFileLoader("hb_generate_code_module", str(HB_SCRIPT)),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.HBCLIv2


HBCLIv2 = _load_hbcli()


def _pick_module_with_adversarial_pass() -> str:
    registry = yaml.safe_load(MODULE_REGISTRY_PATH.read_text(encoding="utf-8"))
    adversarial_root = REPO_ROOT / "_reports" / "adversarial"

    eligible_statuses = {
        "implementation_ready",
        "implemented",
        "staging_validated",
        "released",
    }

    for module_name, meta in sorted(registry["modules"].items()):
        if meta.get("status") not in eligible_statuses:
            continue
        report = adversarial_root / module_name / "ALL.adversarial.json"
        if not report.exists():
            continue
        data = json.loads(report.read_text(encoding="utf-8"))
        if data.get("overall_status") == "PASS":
            return module_name

    raise AssertionError("Nenhum módulo real em implementation_ready+ com adversarial PASS foi encontrado.")


class TestGenerateCodeEligibility:
    def test_generate_code_rejects_validated_contract_and_accepts_implementation_ready(self, tmp_path):
        cli = HBCLIv2()
        cli.root = tmp_path
        cli.module_registry = {
            "modules": {
                "training": {"status": "validated_contract"},
                "analytics": {"status": "implementation_ready"},
            }
        }

        adv_root = tmp_path / "_reports" / "adversarial"
        for module_name in ("training", "analytics"):
            module_dir = adv_root / module_name
            module_dir.mkdir(parents=True, exist_ok=True)
            (module_dir / "ALL.adversarial.json").write_text(
                json.dumps({"module": module_name, "overall_status": "PASS"}),
                encoding="utf-8",
            )

        assert cli._check_generate_code_eligibility("training") == 1
        assert cli._check_generate_code_eligibility("analytics") == 0

    def test_hb_verify_blocks_generate_code_below_implementation_ready(self):
        module = _pick_module_with_adversarial_pass()
        original_registry = MODULE_REGISTRY_PATH.read_bytes()

        try:
            registry = yaml.safe_load(original_registry.decode("utf-8"))
            registry["modules"][module]["status"] = "validated_contract"
            MODULE_REGISTRY_PATH.write_text(
                yaml.safe_dump(registry, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(HB_SCRIPT),
                    "verify",
                    "--task-type",
                    "generate_code",
                    "--module",
                    module,
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            combined = result.stdout + result.stderr
            assert result.returncode != 0, "hb verify deveria bloquear generate_code para validated_contract"
            assert "BLOCKED_GENERATION_INELIGIBLE" in combined
            assert "implementation_ready" in combined
        finally:
            MODULE_REGISTRY_PATH.write_bytes(original_registry)


class TestGenerateCodePolicyParity:
    def test_catalog_prompt_guard_and_pipeline_align_on_implementation_ready(self):
        task_catalog = (REPO_ROOT / ".contract_driven" / "TASK_CATALOG.yaml").read_text(encoding="utf-8")
        prompt = (
            REPO_ROOT / ".contract_driven" / "agent_prompts" / "generate_code.prompt.md"
        ).read_text(encoding="utf-8")
        guard = (
            REPO_ROOT / ".github" / "instructions" / "hb-contract-guards.instructions.md"
        ).read_text(encoding="utf-8")
        pipeline = (REPO_ROOT / "docs" / "_canon" / "CONTRACT_PIPELINE.md").read_text(
            encoding="utf-8"
        )

        assert "status>=implementation_ready" in task_catalog
        assert "implementation_ready" in prompt
        assert "validated_contract\"   # mínimo para generate_code" not in guard
        assert "implementation_ready" in guard
        assert "somente módulos em `implementation_ready+`" in pipeline
