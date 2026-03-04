"""
Testes para check_ops_invariants.py

Cobre o contrato público:
  - run_all_checks retorna (exit_code, [CheckResult])
  - cada check individual retorna CheckResult com ok/severity/message/evidence
  - --ops-doc inexistente → INV-OPS-DOC BLOCKED_INPUT
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Adiciona scripts/ ao path para importar hb_cli e check_ops_invariants
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "gates"))

from check_ops_invariants import (  # noqa: E402
    CheckResult,
    EXIT_BLOCKED_INPUT,
    EXIT_FAIL_ACTIONABLE,
    EXIT_PASS,
    _check_agent_minimum_rules,
    _check_gate_tests_exist,
    _check_gates_registry_contains,
    _check_hb_cli_gate_runner_encoding,
    _check_ops_doc_exists,
    _check_tasks_point_to_single_hb_cli,
    run_all_checks,
)


# ─── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture()
def repo() -> Path:
    return REPO_ROOT


# ─── INV-OPS-DOC ───────────────────────────────────────────────────────


def test_ops_doc_found(repo: Path) -> None:
    r = _check_ops_doc_exists(repo, "docs/invariantes/INVARIANTS_OPERACIONAIS_HBTRACK.md")
    assert r.ok is True
    assert r.id == "INV-OPS-DOC"
    assert "OK:" in r.message


def test_ops_doc_missing(repo: Path, tmp_path: Path) -> None:
    r = _check_ops_doc_exists(tmp_path, "docs/invariantes/INVARIANTS_OPERACIONAIS_HBTRACK.md")
    assert r.ok is False
    assert "BLOCKED_INPUT" in r.message


# ─── INV-OPS-001 ───────────────────────────────────────────────────────


def test_tasks_point_to_single_hb_cli(repo: Path) -> None:
    r = _check_tasks_point_to_single_hb_cli(repo)
    assert r.ok is True
    assert r.id == "INV-OPS-001"
    assert "scripts/run/hb_cli.py" in r.message


def test_tasks_missing(tmp_path: Path) -> None:
    r = _check_tasks_point_to_single_hb_cli(tmp_path)
    assert r.ok is False
    assert "BLOCKED_INPUT" in r.message


def test_tasks_no_hb_cli(tmp_path: Path) -> None:
    vscode = tmp_path / ".vscode"
    vscode.mkdir()
    (vscode / "tasks.json").write_text('{"version":"2.0.0","tasks":[]}', encoding="utf-8")
    r = _check_tasks_point_to_single_hb_cli(tmp_path)
    assert r.ok is False
    assert "FAIL_ACTIONABLE" in r.message


def test_tasks_multiple_hb_cli(tmp_path: Path) -> None:
    vscode = tmp_path / ".vscode"
    vscode.mkdir()
    content = '{"tasks":[{"args":["a/hb_cli.py"]},{"args":["b/hb_cli.py"]}]}'
    (vscode / "tasks.json").write_text(content, encoding="utf-8")
    r = _check_tasks_point_to_single_hb_cli(tmp_path)
    assert r.ok is False
    assert "múltiplos" in r.message


# ─── INV-OPS-002 ───────────────────────────────────────────────────────


def test_hb_cli_gate_runner_encoding_pass(repo: Path) -> None:
    r = _check_hb_cli_gate_runner_encoding(repo)
    assert r.ok is True
    assert r.id == "INV-OPS-002"


def test_hb_cli_gate_runner_encoding_fail(tmp_path: Path) -> None:
    scripts_run = tmp_path / "scripts" / "run"
    scripts_run.mkdir(parents=True)
    (scripts_run / "hb_cli.py").write_text("import subprocess\n", encoding="utf-8")
    r = _check_hb_cli_gate_runner_encoding(tmp_path)
    assert r.ok is False
    assert "FAIL_ACTIONABLE" in r.message


def test_hb_cli_gate_runner_encoding_missing(tmp_path: Path) -> None:
    r = _check_hb_cli_gate_runner_encoding(tmp_path)
    assert r.ok is False
    assert "BLOCKED_INPUT" in r.message


# ─── INV-OPS-003 (registry) ────────────────────────────────────────────


def test_gates_registry_pass(repo: Path) -> None:
    r = _check_gates_registry_contains(repo, ["DOC-GATE-019", "DOC-GATE-020", "DOC-GATE-021"])
    assert r.ok is True
    assert r.id == "INV-OPS-003"


def test_gates_registry_missing_file(tmp_path: Path) -> None:
    r = _check_gates_registry_contains(tmp_path, ["DOC-GATE-019"])
    assert r.ok is False
    assert "BLOCKED_INPUT" in r.message


def test_gates_registry_missing_gate(tmp_path: Path) -> None:
    from check_ops_invariants import GATES_REGISTRY_REL
    reg = tmp_path / GATES_REGISTRY_REL
    reg.parent.mkdir(parents=True)
    reg.write_text("- id: DOC-GATE-019\n", encoding="utf-8")
    r = _check_gates_registry_contains(tmp_path, ["DOC-GATE-019", "DOC-GATE-021"])
    assert r.ok is False
    assert "DOC-GATE-021" in r.message


# ─── INV-OPS-010 (agents) ──────────────────────────────────────────────


def test_agent_minimum_rules_pass(repo: Path) -> None:
    r = _check_agent_minimum_rules(repo)
    assert r.ok is True
    assert r.id == "INV-OPS-010"


def test_agent_minimum_rules_missing_file(tmp_path: Path) -> None:
    r = _check_agent_minimum_rules(tmp_path)
    assert r.ok is False
    assert "BLOCKED_INPUT" in r.message


def test_agent_minimum_rules_missing_needle(tmp_path: Path) -> None:
    agents = tmp_path / ".github" / "agents"
    agents.mkdir(parents=True)
    (agents / "Arquiteto.agent.md").write_text("sem conteúdo útil", encoding="utf-8")
    (agents / "Executor.agent.md").write_text("workspace clean e FAIL_ACTIONABLE", encoding="utf-8")
    (agents / "Testador.agent.md").write_text("hb verify E_DOD_STRICT_WARN result.json", encoding="utf-8")
    r = _check_agent_minimum_rules(tmp_path)
    assert r.ok is False
    assert "Arquiteto.agent.md" in r.message


# ─── INV-OPS-015 (gate tests) ──────────────────────────────────────────


def test_gate_tests_exist_pass(repo: Path) -> None:
    r = _check_gate_tests_exist(repo)
    assert r.ok is True
    assert r.id == "INV-OPS-015"


def test_gate_tests_missing_gates_dir(tmp_path: Path) -> None:
    r = _check_gate_tests_exist(tmp_path)
    assert r.ok is False
    assert "BLOCKED_INPUT" in r.message


def test_gate_tests_missing_test_file(tmp_path: Path) -> None:
    gates = tmp_path / "scripts" / "gates"
    (gates / "tests").mkdir(parents=True)
    (gates / "check_something.py").write_text("# gate\n", encoding="utf-8")
    r = _check_gate_tests_exist(tmp_path)
    assert r.ok is False
    assert "check_something.py" in r.message


# ─── run_all_checks ────────────────────────────────────────────────────


def test_run_all_checks_pass(repo: Path) -> None:
    exit_code, checks = run_all_checks(
        repo, "docs/invariantes/INVARIANTS_OPERACIONAIS_HBTRACK.md"
    )
    assert exit_code == EXIT_PASS
    assert all(c.ok for c in checks)


def test_run_all_checks_blocked_on_missing_doc(repo: Path) -> None:
    exit_code, checks = run_all_checks(repo, "docs/nao/existe.md")
    assert exit_code == EXIT_BLOCKED_INPUT
    doc_check = next((c for c in checks if c.id == "INV-OPS-DOC"), None)
    assert doc_check is not None
    assert not doc_check.ok
