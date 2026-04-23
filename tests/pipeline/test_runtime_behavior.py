import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
HB_SCRIPT = REPO_ROOT / "scripts" / "hb"
SESSION_SCHEMA = REPO_ROOT / "contracts" / "schemas" / "shared" / "session_start.schema.json"


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write_text(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _default_boot_profiles() -> dict:
    return {
        "profiles": {
            "default": {
                "load_sequence": [],
                "required_sections": [],
                "validations": {},
                "exit_on_fail": True,
            },
            "contract_execution": {
                "load_sequence": [],
                "required_sections": [],
                "validations": {},
                "exit_on_fail": True,
            },
            "roadmap_execution": {
                "load_sequence": [],
                "required_sections": [],
                "validations": {},
                "exit_on_fail": True,
            },
        }
    }


def _default_task_catalog() -> dict:
    return {
        "task_catalog": {
            "new_contract": {
                "task_type": "new_contract",
                "worker_id": "create_openapi_contract",
                "worker_path": ".contract_driven/agent_prompts/create_openapi_contract.prompt.md",
                "status": "active",
                "profile_id": "contract_execution",
                "stage_allowed": [0, 1, 2],
            },
            "pr_fix": {
                "task_type": "pr_fix",
                "worker_id": "pr_fix",
                "worker_path": ".contract_driven/agent_prompts/pr_fix.prompt.md",
                "status": "active",
                "profile_id": "contract_execution",
                "stage_allowed": [0],
            },
            "readiness_promotion": {
                "task_type": "readiness_promotion",
                "worker_id": "readiness_promotion",
                "worker_path": ".contract_driven/agent_prompts/readiness_promotion.prompt.md",
                "status": "active",
                "profile_id": "contract_execution",
                "stage_allowed": [3, 4],
            },
            "implementation_promotion": {
                "task_type": "implementation_promotion",
                "worker_id": "implementation_promotion_worker",
                "worker_path": ".contract_driven/agent_prompts/implementation_promotion.prompt.md",
                "status": "active",
                "profile_id": "contract_execution",
                "stage_allowed": [3],
            },
        }
    }


def _default_merge_readiness() -> dict:
    return {
        "checks": [
            {
                "context": "ci / Validate Contracts",
                "local_equivalent": "python3 scripts/hb validate --profile precommit",
            }
        ]
    }


def _default_bridge_docs() -> dict[str, str]:
    banner = "> ⚠️ **BRIDGE ONLY — NON-SOVEREIGN**\n\n"
    return {
        "CLAUDE.md": banner + "# Claude bridge\n",
        "AGENTS.md": banner + "# Agents bridge\n",
        ".github/copilot-instructions.md": banner + "# Copilot bridge\n",
        ".github/skills/hb-pipeline-orchestrator/SKILL.md": banner + "# Skill pipeline\n",
        ".github/skills/hb-roadmap-executor/SKILL.md": banner + "# Skill roadmap\n",
    }


def _build_workspace(
    tmp_path: Path,
    *,
    task_catalog: dict | None = None,
    boot_profiles: dict | None = None,
    merge_readiness: dict | None = None,
    bridge_docs: dict[str, str] | None = None,
    validator_rc: int = 0,
) -> Path:
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    (workspace / "scripts").mkdir(parents=True, exist_ok=True)
    (workspace / "contracts" / "schemas" / "shared").mkdir(parents=True, exist_ok=True)
    shutil.copy2(HB_SCRIPT, workspace / "scripts" / "hb")
    shutil.copy2(SESSION_SCHEMA, workspace / "contracts" / "schemas" / "shared" / "session_start.schema.json")

    _write_yaml(workspace / ".contract_driven" / "BOOT_PROFILES.yaml", boot_profiles or _default_boot_profiles())
    catalog = task_catalog or _default_task_catalog()
    _write_yaml(workspace / ".contract_driven" / "TASK_CATALOG.yaml", catalog)
    _write_yaml(workspace / "docs" / "_canon" / "MODULE_REGISTRY.yaml", {"modules": {"users": {"status": "validated_contract"}}})
    _write_json(workspace / "merge-readiness.json", merge_readiness or _default_merge_readiness())

    for relative_path, content in (bridge_docs or _default_bridge_docs()).items():
        _write_text(workspace / relative_path, content)

    for task_type, config in catalog["task_catalog"].items():
        prompt_path = workspace / config["worker_path"]
        if prompt_path.exists():
            continue
        _write_text(
            prompt_path,
            "---\n"
            f"task_type: {task_type}\n"
            "version: \"1.0.0\"\n"
            "status: active\n"
            "---\n\n"
            f"# Worker {task_type}\n",
        )

    _write_text(
        workspace / "scripts" / "contracts" / "validate" / "validate_contracts.py",
        "import sys\n"
        f"raise SystemExit({validator_rc})\n",
    )

    return workspace


def _run_hb(workspace: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/hb", *args],
        cwd=workspace,
        capture_output=True,
        text=True,
    )


class TestModeSeparation:
    def test_verify_blocks_cdd_task_with_roadmap_mode(self, tmp_path):
        catalog = _default_task_catalog()
        catalog["task_catalog"]["new_contract"]["profile_id"] = "roadmap_execution"
        workspace = _build_workspace(tmp_path, task_catalog=catalog)

        result = _run_hb(workspace, "verify", "--task-type", "new_contract", "--module", "users")

        assert result.returncode == 1
        assert "BLOCKED_MODE_MISMATCH" in (result.stderr + result.stdout)


class TestPromptUsedEvidence:
    def test_verify_writes_execution_evidence_with_prompt_sha(self, tmp_path):
        workspace = _build_workspace(tmp_path)

        result = _run_hb(workspace, "verify", "--task-type", "new_contract", "--module", "users")

        assert result.returncode == 0, result.stderr

        evidence_files = list((workspace / "_reports" / "execution_evidence").glob("*.json"))
        assert len(evidence_files) == 1

        payload = json.loads(evidence_files[0].read_text(encoding="utf-8"))
        worker_path = workspace / ".contract_driven" / "agent_prompts" / "create_openapi_contract.prompt.md"
        expected_sha = hashlib.sha256(worker_path.read_bytes()).hexdigest()

        assert payload["worker_prompt_sha256"] == expected_sha
        assert payload["worker_path"] == ".contract_driven/agent_prompts/create_openapi_contract.prompt.md"
        assert payload["stage0_exit_code"] == 0


class TestPrFixBoundedScope:
    def test_pr_fix_requires_check_context(self, tmp_path):
        workspace = _build_workspace(tmp_path)

        result = _run_hb(workspace, "verify", "--task-type", "pr_fix", "--module", "users")

        assert result.returncode == 1
        assert "GAP_DE_PARIDADE" in (result.stderr + result.stdout)
        assert "--check-context" in (result.stderr + result.stdout)

    def test_pr_fix_rejects_unknown_check_context(self, tmp_path):
        workspace = _build_workspace(tmp_path)

        result = _run_hb(
            workspace,
            "verify",
            "--task-type",
            "pr_fix",
            "--module",
            "users",
            "--check-context",
            "ci / Inexistente",
        )

        assert result.returncode == 1
        assert "GAP_DE_PARIDADE" in (result.stderr + result.stdout)
        assert "não existe em merge-readiness.json" in (result.stderr + result.stdout)


class TestIrLineage:
    def test_generate_backend_blocks_when_ir_is_missing(self, tmp_path):
        workspace = _build_workspace(tmp_path)
        _write_text(workspace / "contracts" / "openapi" / "paths" / "users.yaml", "openapi: 3.1.0\n")

        result = _run_hb(workspace, "generate", "--backend", "--module", "users")

        assert result.returncode == 1
        assert "IR_STALE_OR_MISSING" in result.stdout

    def test_generate_backend_blocks_when_ir_is_stale(self, tmp_path):
        workspace = _build_workspace(tmp_path)
        ir_file = workspace / "generated" / "source_graph" / "users" / "bundle.json"
        contract_file = workspace / "contracts" / "openapi" / "paths" / "users.yaml"
        _write_text(ir_file, "{}\n")
        _write_text(contract_file, "openapi: 3.1.0\n")

        now = time.time()
        os.utime(ir_file, (now - 60, now - 60))
        os.utime(contract_file, (now, now))

        result = _run_hb(workspace, "generate", "--backend", "--module", "users")

        assert result.returncode == 1
        assert "IR_STALE_OR_MISSING" in result.stdout


class TestPromotionGuards:
    def test_check_allows_readiness_promotion_from_validated_contract(self, tmp_path):
        workspace = _build_workspace(tmp_path)
        _write_json(
            workspace / "_reports" / "session_start.json",
            {
                "session_id": "123e4567-e89b-42d3-a456-426614174000",
                "pipeline_version": "1.0.0",
                "task_type": "readiness_promotion",
                "module": "users",
                "stage0_exit_code": 0,
            },
        )

        result = _run_hb(workspace, "check", "--module", "users")

        assert result.returncode == 0, result.stderr
        assert "Lifecycle OK" in result.stdout

    def test_check_allows_implementation_promotion_from_implementation_ready(self, tmp_path):
        workspace = _build_workspace(tmp_path)
        _write_yaml(
            workspace / "docs" / "_canon" / "MODULE_REGISTRY.yaml",
            {"modules": {"users": {"status": "implementation_ready"}}},
        )
        _write_json(
            workspace / "_reports" / "session_start.json",
            {
                "session_id": "123e4567-e89b-42d3-a456-426614174001",
                "pipeline_version": "1.0.0",
                "task_type": "implementation_promotion",
                "module": "users",
                "stage0_exit_code": 0,
            },
        )

        result = _run_hb(workspace, "check", "--module", "users")

        assert result.returncode == 0, result.stderr
        assert "Lifecycle OK" in result.stdout

    def test_artifact_blocks_readiness_promotion_without_scorecard(self, tmp_path):
        workspace = _build_workspace(tmp_path)
        _write_text(workspace / "docs" / "_canon" / "MODULE_REGISTRY.yaml", "modules:\n  users: {}\n")
        _write_json(
            workspace / "_reports" / "session_start.json",
            {
                "session_id": "123e4567-e89b-42d3-a456-426614174000",
                "pipeline_version": "1.0.0",
                "task_type": "readiness_promotion",
                "module": "users",
                "stage0_exit_code": 0,
            },
        )
        _write_json(
            workspace / "_reports" / "contract_gates" / "latest.json",
            {"overall_status": "PASS"},
        )

        result = _run_hb(workspace, "artifact", "docs/_canon/MODULE_REGISTRY.yaml")

        assert result.returncode == 1
        assert "MISSING_PROMOTION_EVIDENCE" in result.stderr
        assert "module_readiness_scorecard.json" in result.stderr


class TestAuditPromptsBridgeDocs:
    def test_audit_prompts_passes_when_all_bridge_docs_have_disclaimer(self, tmp_path):
        workspace = _build_workspace(tmp_path)

        result = _run_hb(workspace, "audit-prompts", "--check-bridge-docs")

        assert result.returncode == 0, result.stderr
        assert "bridge docs com disclaimer" in result.stdout

    def test_audit_prompts_fails_when_bridge_doc_lacks_disclaimer(self, tmp_path):
        workspace = _build_workspace(tmp_path)
        _write_text(workspace / "AGENTS.md", "# AGENTS\nsem banner\n")

        result = _run_hb(workspace, "audit-prompts", "--check-bridge-docs")

        combined = result.stdout + result.stderr
        assert result.returncode == 1
        assert "AGENTS.md" in combined
        assert "bridge docs sem disclaimer obrigatório" in combined