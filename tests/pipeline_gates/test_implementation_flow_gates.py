from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATE_SCRIPT = REPO_ROOT / "scripts" / "contracts" / "validate" / "validate_contracts.py"


def _load_validate_module():
    module_name = "validate_contracts_impl_flow"
    loader = importlib.machinery.SourceFileLoader(module_name, str(VALIDATE_SCRIPT))
    spec = importlib.util.spec_from_loader(module_name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


vc = _load_validate_module()


def _write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, (dict, list)):
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    else:
        path.write_text(str(payload), encoding="utf-8")


def _copy_shared_schemas(tmp_path: Path) -> None:
    shared = REPO_ROOT / "contracts" / "schemas" / "shared"
    target = tmp_path / "contracts" / "schemas" / "shared"
    target.mkdir(parents=True, exist_ok=True)
    for name in (
        "implementation_flow_state.schema.json",
        "plan_to_diff_trace.schema.json",
        "negative_test_manifest.schema.json",
        "implementation_evidence_pack.schema.json",
    ):
        (target / name).write_text((shared / name).read_text(encoding="utf-8"), encoding="utf-8")


def _seed_active_session(tmp_path: Path, task_type: str = "implementation_execution") -> None:
    _write(
        tmp_path / "_reports" / "session_start.json",
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "session_timestamp": "2026-04-28T00:00:00+00:00",
            "branch": "main",
            "pipeline_version": "1.0.0",
            "boot_profile_id": "implementation_execution" if task_type == "implementation_execution" else "adversarial_validation",
            "task_type": task_type,
            "module": "notifications",
            "stage": 0,
            "write_scope": "implementation" if task_type == "implementation_execution" else "readonly",
            "worker_id": "worker",
            "operation_mode": "CDD",
        },
    )


def test_implementation_scope_firewall_gate_fails_on_extra_file(tmp_path: Path):
    _copy_shared_schemas(tmp_path)
    _seed_active_session(tmp_path)
    _write(
        tmp_path / "_reports" / "implementation_flow" / "current_state.json",
        {
            "schema_version": "1.0.0",
            "current_state": "PLAN_APPROVED",
            "approved_plan_path": ".claude/plans/a.md",
            "allowed_files": ["scripts/hb"],
            "changed_files": ["scripts/hb", "docs/_canon/README.md"],
            "transitions": [],
        },
    )
    result = vc._g_implementation_scope_firewall(tmp_path)
    assert result["status"] == "FAIL"
    assert result["blocking_code"] == "BLOCKED_SCOPE_OVERFLOW"


def test_plan_diff_trace_gate_fails_on_extra_files(tmp_path: Path):
    _copy_shared_schemas(tmp_path)
    _seed_active_session(tmp_path)
    _write(tmp_path / "_reports" / "implementation_flow" / "current_state.json", {
        "schema_version": "1.0.0",
        "current_state": "PLAN_APPROVED",
        "approved_plan_path": ".claude/plans/a.md",
        "transitions": [],
    })
    _write(tmp_path / "_reports" / "implementation_flow" / "plan_to_diff_trace.json", {
        "schema_version": "1.0.0",
        "approved_plan_path": ".claude/plans/a.md",
        "base_sha": "abcdef1",
        "head_sha": "abcdef2",
        "entries": [],
        "extra_files": ["src/x.py"],
        "uncovered_requirements": [],
    })
    result = vc._g_plan_diff_trace(tmp_path)
    assert result["status"] == "FAIL"


def test_negative_test_coverage_gate_fails_below_threshold(tmp_path: Path):
    _copy_shared_schemas(tmp_path)
    _seed_active_session(tmp_path, task_type="adversarial_test_execution")
    _write(tmp_path / "_reports" / "implementation_flow" / "current_state.json", {
        "schema_version": "1.0.0",
        "current_state": "ADVERSARIAL_TESTS_RUN",
        "approved_plan_path": ".claude/plans/a.md",
        "decision_ids_affected": ["ADR-001"],
        "transitions": [],
    })
    _write(tmp_path / "_reports" / "implementation_flow" / "negative_test_manifest.json", {
        "schema_version": "1.0.0",
        "pr_url": "https://github.com/acme/hbtrack/pull/1",
        "decision_ids_tested": ["ADR-001"],
        "rules_tested": [],
        "coverage_ratio": 0.5,
        "verdict": "PARTIAL",
    })
    result = vc._g_negative_test_coverage(tmp_path)
    assert result["status"] == "FAIL"
    assert result["blocking_code"] == "BLOCKED_ADVERSARIAL_NOT_RUN"


def test_post_pr_adversarial_gate_fails_on_pr_mismatch(tmp_path: Path):
    _copy_shared_schemas(tmp_path)
    _seed_active_session(tmp_path, task_type="adversarial_test_execution")
    _write(tmp_path / "_reports" / "implementation_flow" / "current_state.json", {
        "schema_version": "1.0.0",
        "current_state": "IMPLEMENTATION_PR_OPENED",
        "approved_plan_path": ".claude/plans/a.md",
        "pr_url": "https://github.com/acme/hbtrack/pull/1",
        "transitions": [],
    })
    _write(tmp_path / "_reports" / "implementation_flow" / "adversarial_report.json", {
        "pr_url": "https://github.com/acme/hbtrack/pull/999",
        "verdict": "PASS",
    })
    result = vc._g_post_pr_adversarial(tmp_path)
    assert result["status"] == "FAIL"


def test_implementation_state_gate_fails_on_invalid_transition(tmp_path: Path):
    _copy_shared_schemas(tmp_path)
    _seed_active_session(tmp_path)
    _write(tmp_path / "_reports" / "implementation_flow" / "current_state.json", {
        "schema_version": "1.0.0",
        "current_state": "IMPLEMENTATION_PR_OPENED",
        "approved_plan_path": ".claude/plans/a.md",
        "transitions": [
            {
                "from_state": "IMPLEMENTATION_PR_OPENED",
                "to_state": "PLAN_APPROVED",
                "timestamp": "2026-04-28T00:00:00Z",
                "evidence_sha": "abcdef1",
            }
        ],
    })
    result = vc._g_implementation_state(tmp_path)
    assert result["status"] == "FAIL"
    assert result["blocking_code"] == "BLOCKED_STATE_TRANSITION_INVALID"


def test_evidence_pack_completeness_gate_fails_without_pr_url(tmp_path: Path):
    _copy_shared_schemas(tmp_path)
    _seed_active_session(tmp_path)
    _write(tmp_path / "_reports" / "implementation_flow" / "current_state.json", {
        "schema_version": "1.0.0",
        "current_state": "EVIDENCE_GENERATED",
        "approved_plan_path": ".claude/plans/a.md",
        "transitions": [],
    })
    output_path = tmp_path / "_reports" / "implementation_flow" / "validate.log"
    _write(output_path, "ok\n")
    _write(tmp_path / "_reports" / "implementation_flow" / "adversarial_report.json", {"pr_url": "https://github.com/acme/hbtrack/pull/1", "verdict": "PASS"})
    _write(tmp_path / "_reports" / "implementation_flow" / "implementation_evidence_pack.json", {
        "schema_version": "1.0.0",
        "generated_at": "2026-04-28T00:00:00Z",
        "generated_by_task_type": "implementation_execution",
        "base_sha": "abcdef1",
        "head_sha": "abcdef2",
        "pr_number": 1,
        "approved_plan_path": ".claude/plans/a.md",
        "changed_files": [],
        "allowed_files": [],
        "forbidden_files_touched": [],
        "gate_results": [],
        "validation_commands_run": [
            {"command": "pytest", "exit_code": 0, "output_path": "_reports/implementation_flow/validate.log"}
        ],
        "positive_tests": [],
        "negative_tests": [],
        "adversarial_report_path": "_reports/implementation_flow/adversarial_report.json",
        "blocking_status": "PASS",
    })
    result = vc._g_evidence_pack_completeness(tmp_path)
    assert result["status"] == "FAIL"
    assert result["blocking_code"] == "REPROVADO_OPERACIONALMENTE"
