from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HB_SCRIPT = REPO_ROOT / "scripts" / "hb"


def _load_hbcli():
    spec = importlib.util.spec_from_loader(
        "hb_module_impl_boot",
        importlib.machinery.SourceFileLoader("hb_module_impl_boot", str(HB_SCRIPT)),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.HBCLIv2


HBCLIv2 = _load_hbcli()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_stub_repo(tmp_path: Path) -> tuple[HBCLIv2, Path]:
    cli = object.__new__(HBCLIv2)
    cli.root = tmp_path
    cli.session_file = tmp_path / "_reports" / "session_start.json"
    cli.legacy_session_dir = tmp_path / "_reports" / "legacy"
    cli.validator_script = tmp_path / "scripts" / "contracts" / "validate" / "validate_contracts.py"
    cli.session = {}
    cli._profile_validation_context = {}
    cli.module_registry = {"modules": {"notifications": {}, "training": {}}}
    cli.task_catalog = {
        "task_catalog": {
            "implementation_execution": {
                "status": "active",
                "worker_id": "hb_implementer",
                "worker_path": ".contract_driven/agent_prompts/hb_implementer.prompt.md",
                "profile_id": "implementation_execution",
            },
            "adversarial_test_execution": {
                "status": "active",
                "worker_id": "hb_adversarial_tester",
                "worker_path": ".contract_driven/agent_prompts/hb_adversarial_tester.prompt.md",
                "profile_id": "adversarial_validation",
            },
        }
    }
    cli.boot_profiles = {
        "profiles": {
            "implementation_execution": {
                "load_sequence": [
                    "docs/_canon/AGENT_INSTRUCTIONS.md",
                    "docs/_canon/OPERATIONS.md",
                    "docs/_canon/CONTRACT_PIPELINE.md",
                ],
                "required_sections": [
                    "docs/_canon/AGENT_INSTRUCTIONS.md§0",
                    "docs/_canon/AGENT_INSTRUCTIONS.md§4",
                    "docs/_canon/AGENT_INSTRUCTIONS.md§5",
                    "docs/_canon/AGENT_INSTRUCTIONS.md§6",
                    "docs/_canon/CONTRACT_PIPELINE.md§1",
                ],
                "validations": {
                    "approved_plan_read": True,
                    "clean_worktree_required": True,
                },
                "exit_on_fail": True,
            },
            "adversarial_validation": {
                "load_sequence": [
                    "docs/_canon/AGENT_INSTRUCTIONS.md",
                    "docs/_canon/OPERATIONS.md",
                ],
                "required_sections": [
                    "docs/_canon/AGENT_INSTRUCTIONS.md§0",
                    "docs/_canon/AGENT_INSTRUCTIONS.md§4",
                    "docs/_canon/AGENT_INSTRUCTIONS.md§5",
                    "docs/_canon/AGENT_INSTRUCTIONS.md§6",
                ],
                "validations": {
                    "remote_pr_required": True,
                    "evidence_pack_required": True,
                    "implementation_state_required": True,
                },
                "exit_on_fail": True,
            },
        }
    }
    cli.session_schema = json.loads((REPO_ROOT / "contracts/schemas/shared/session_start.schema.json").read_text(encoding="utf-8"))

    _write(
        tmp_path / "docs" / "_canon" / "AGENT_INSTRUCTIONS.md",
        "## 0.\nboot\n## 4.\ntasks\n## 5.\nblocks\n## 6.\ncore\n",
    )
    _write(tmp_path / "docs" / "_canon" / "OPERATIONS.md", "# ops\n")
    _write(tmp_path / "docs" / "_canon" / "CONTRACT_PIPELINE.md", "## 1.\npipeline\n")
    _write(tmp_path / ".contract_driven" / "agent_prompts" / "hb_implementer.prompt.md", "---\ntask_type: implementation_execution\n---\n")
    _write(tmp_path / ".contract_driven" / "agent_prompts" / "hb_adversarial_tester.prompt.md", "---\ntask_type: adversarial_test_execution\n---\n")
    _write(
        cli.validator_script,
        "import sys\nsys.exit(0)\n",
    )

    return cli, tmp_path


def test_implementation_execution_verify_requires_plan(tmp_path, monkeypatch):
    cli, root = _make_stub_repo(tmp_path)
    monkeypatch.setattr(cli, "_is_git_worktree_clean", lambda: True)
    rc = cli.cmd_verify("implementation_execution", "notifications")
    assert rc == 1


def test_implementation_execution_verify_writes_state(tmp_path, monkeypatch):
    cli, root = _make_stub_repo(tmp_path)
    monkeypatch.setattr(cli, "_is_git_worktree_clean", lambda: True)
    plan_path = root / ".claude" / "plans" / "approved.md"
    _write(plan_path, "# plan\n")

    rc = cli.cmd_verify(
        "implementation_execution",
        "notifications",
        approved_plan_path=str(plan_path.relative_to(root)),
        allowed_files=["scripts/hb"],
        forbidden_files=["docs/_canon/AGENT_INSTRUCTIONS.md"],
        decision_ids=["ADR-001"],
    )
    assert rc == 0
    session = json.loads(cli.session_file.read_text(encoding="utf-8"))
    assert session["task_type"] == "implementation_execution"
    assert session["write_scope"] == "implementation"
    assert session["approved_plan_path"] == ".claude/plans/approved.md"
    state = json.loads((root / "_reports" / "implementation_flow" / "current_state.json").read_text(encoding="utf-8"))
    assert state["current_state"] == "PLAN_APPROVED"


def test_adversarial_verify_requires_pr_state_and_pack(tmp_path, monkeypatch):
    cli, root = _make_stub_repo(tmp_path)
    monkeypatch.setattr(cli, "_is_git_worktree_clean", lambda: True)
    plan_path = root / ".claude" / "plans" / "approved.md"
    _write(plan_path, "# plan\n")

    state_path = root / "_reports" / "implementation_flow" / "current_state.json"
    state_payload = {
        "schema_version": "1.0.0",
        "current_state": "IMPLEMENTATION_PR_OPENED",
        "approved_plan_path": ".claude/plans/approved.md",
        "pr_url": "https://github.com/acme/hbtrack/pull/42",
        "transitions": [],
    }
    _write(state_path, json.dumps(state_payload))

    pack_path = root / "_reports" / "implementation_flow" / "implementation_evidence_pack.json"
    pack_payload = {
        "schema_version": "1.0.0",
        "generated_at": "2026-04-28T00:00:00Z",
        "generated_by_task_type": "implementation_execution",
        "base_sha": "abcdef1",
        "head_sha": "abcdef2",
        "pr_url": "https://github.com/acme/hbtrack/pull/42",
        "pr_number": 42,
        "approved_plan_path": ".claude/plans/approved.md",
        "changed_files": [],
        "allowed_files": [],
        "forbidden_files_touched": [],
        "gate_results": [],
        "validation_commands_run": [],
        "positive_tests": [],
        "negative_tests": [],
        "adversarial_report_path": "_reports/implementation_flow/adversarial_report.json",
        "blocking_status": "PASS",
    }
    _write(pack_path, json.dumps(pack_payload))

    rc = cli.cmd_verify(
        "adversarial_test_execution",
        "notifications",
        approved_plan_path=str(plan_path.relative_to(root)),
        pr_url="https://github.com/acme/hbtrack/pull/42",
        implementation_state_path=str(state_path.relative_to(root)),
        evidence_pack_path=str(pack_path.relative_to(root)),
    )
    assert rc == 0
    session = json.loads(cli.session_file.read_text(encoding="utf-8"))
    assert session["task_type"] == "adversarial_test_execution"
    assert session["write_scope"] == "readonly"
    assert session["pr_url"] == "https://github.com/acme/hbtrack/pull/42"
