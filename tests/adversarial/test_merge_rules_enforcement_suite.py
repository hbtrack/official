from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKLOG = ROOT / ".CEPRAEA" / "BACKLOG_EXECUTAVEL_DETERMINISTICO.md"
CONTRACT_GATES = ROOT / ".github" / "workflows" / "contract-gates.yml"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def test_required_merge_blocking_checks_exist_in_repo_ci_definitions():
    backlog = BACKLOG.read_text(encoding="utf-8")
    contract_gates = CONTRACT_GATES.read_text(encoding="utf-8")
    ci_workflow = CI_WORKFLOW.read_text(encoding="utf-8")

    assert "Validate Contract Gates" in backlog
    assert "Governance Tests" in backlog
    assert "Architecture Drift Check" in backlog
    assert "CI / Validate Contracts" in backlog
    assert "CI / Tests" in backlog

    assert "name: Validate Contract Gates" in contract_gates
    assert "name: Governance Tests" in contract_gates
    assert "name: Architecture Drift Check" in contract_gates
    assert "name: Validate Contracts" in ci_workflow
    assert "name: Tests" in ci_workflow


def test_merge_rules_expectations_remain_documented_as_blocking():
    backlog = BACKLOG.read_text(encoding="utf-8")
    assert "required_approving_review_count = 0" in backlog
    assert "required_review_thread_resolution = true" in backlog
    assert "merge em `main` sem esses checks deixa de ser possivel" in backlog
