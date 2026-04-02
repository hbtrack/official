from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def test_decision_support_system_has_traceable_sources_and_enforcement():
    decision_policy = (ROOT / "docs" / "_canon" / "DECISION_POLICY.md").read_text(encoding="utf-8")
    prompt = (
        ROOT / ".contract_driven" / "agent_prompts" / "decision_discovery.prompt.md"
    ).read_text(encoding="utf-8")
    registry = yaml.safe_load(
        (ROOT / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml").read_text(encoding="utf-8")
    )
    executor = (
        ROOT / "scripts" / "contracts" / "validate" / "validate_contracts.py"
    ).read_text(encoding="utf-8")

    prompt_lower = prompt.lower()
    assert "aprovação humana" in decision_policy.lower()
    assert "aprovação humana" in prompt_lower
    assert "aguardar" in prompt_lower or "aguarde" in prompt_lower

    gate_ids = {gate["gate_id"] for gate in registry.get("gates", [])}
    assert "DECISION_IR_CONFORMANCE_GATE" in gate_ids
    assert "ARCH_DECISION_PRESENCE_GATE" in gate_ids
    assert "DECISION_IR_CONFORMANCE_GATE" in executor
    assert "ARCH_DECISION_PRESENCE_GATE" in executor
