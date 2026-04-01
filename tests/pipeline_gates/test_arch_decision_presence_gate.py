from __future__ import annotations

import json
from pathlib import Path

from scripts.contracts.validate import validate_contracts as gates


ROOT = Path(__file__).resolve().parents[2]


def _write_backlog(root: Path, status: str, affected_modules: str, *, criticidade: str = "**obrigatória**") -> None:
    backlog = root / "docs" / "_canon" / "ARCHITECTURE_DECISION_BACKLOG.md"
    backlog.parent.mkdir(parents=True, exist_ok=True)
    backlog.write_text(
        f"""# Architecture Decision Backlog — Teste

### ARCH-900 — Decisão em teste

| Campo | Valor |
|-------|-------|
| ID | ARCH-900 |
| Criticidade | {criticidade} |
| Status | {status} |
| Módulos afetados | {affected_modules} |
| Contexto | teste |

## 3. Decisões Resolvidas
""",
        encoding="utf-8",
    )


def _write_session(root: Path, *, task_type: str = "new_contract", module: str = "training") -> None:
    session = root / "_reports" / "session_start.json"
    session.parent.mkdir(parents=True, exist_ok=True)
    session.write_text(json.dumps({"task_type": task_type, "module": module}), encoding="utf-8")


def test_arch_decision_presence_gate_fails_for_module_specific_pending_decision(tmp_path):
    _write_backlog(tmp_path, "open", "`training`")
    _write_session(tmp_path, module="training")

    result = gates._g2m_arch_decision_presence(tmp_path)

    assert result["status"] == "FAIL"
    assert result["blocking_code"] == "BLOCKED_MISSING_ARCH_DECISION"
    assert "training" in result["summary"]


def test_arch_decision_presence_gate_fails_for_global_pending_decision(tmp_path):
    _write_backlog(tmp_path, "pending_approval", "todos os módulos com endpoints públicos")
    _write_session(tmp_path, module="matches")

    result = gates._g2m_arch_decision_presence(tmp_path)

    assert result["status"] == "FAIL"
    assert result["blocking_code"] == "BLOCKED_MISSING_ARCH_DECISION"
    assert any("ARCH-900" in item["message"] for item in result.get("violations", []))


def test_arch_decision_presence_gate_passes_when_only_resolved_decisions_exist(tmp_path):
    _write_backlog(tmp_path, "resolved — ADR-999", "`training`")
    _write_session(tmp_path, task_type="readiness_promotion", module="training")

    result = gates._g2m_arch_decision_presence(tmp_path)

    assert result["status"] == "PASS"
    assert result["blocking_code"] is None


def test_arch_decision_presence_gate_is_wired_in_executor_and_prompts():
    validator = (ROOT / "scripts" / "contracts" / "validate" / "validate_contracts.py").read_text(
        encoding="utf-8"
    )
    decision_prompt = (
        ROOT / ".contract_driven" / "agent_prompts" / "decision_discovery.prompt.md"
    ).read_text(encoding="utf-8")
    readiness_prompt = (
        ROOT / ".contract_driven" / "agent_prompts" / "readiness_promotion.prompt.md"
    ).read_text(encoding="utf-8")

    assert "ARCH_DECISION_PRESENCE_GATE" in validator
    assert "_g2m_arch_decision_presence" in validator
    assert "pending_approval" in decision_prompt
    assert "ARCH_DECISION_PRESENCE_GATE" in readiness_prompt
