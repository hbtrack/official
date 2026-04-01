from __future__ import annotations

from pathlib import Path

from scripts.contracts.validate import validate_contracts as gates


def _write_minimal_parity_workspace(root: Path) -> None:
    (root / "docs" / "_canon" / "gates").mkdir(parents=True, exist_ok=True)
    (root / ".contract_driven" / "agent_prompts").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "contracts" / "validate").mkdir(parents=True, exist_ok=True)
    (root / "scripts").mkdir(parents=True, exist_ok=True)

    (root / "docs" / "_canon" / "AGENT_INSTRUCTIONS.md").write_text(
        "Boot usa BOOT_PROFILES.yaml e TASK_CATALOG.yaml.\n",
        encoding="utf-8",
    )
    (root / "docs" / "_canon" / "CONTRACT_PIPELINE.md").write_text(
        "Fluxo usa TASK_CATALOG.yaml e scripts/hb.\n",
        encoding="utf-8",
    )
    (root / "docs" / "_canon" / "DECISION_POLICY.md").write_text(
        "Operacionalizado por decision_discovery.prompt.md.\n",
        encoding="utf-8",
    )
    (root / ".contract_driven" / "BOOT_PROFILES.yaml").write_text(
        "required_sections:\n  - docs/_canon/AGENT_INSTRUCTIONS.md\n",
        encoding="utf-8",
    )
    (root / ".contract_driven" / "TASK_CATALOG.yaml").write_text(
        "reference: docs/_canon/AGENT_INSTRUCTIONS.md\n",
        encoding="utf-8",
    )
    (root / ".contract_driven" / "agent_prompts" / "decision_discovery.prompt.md").write_text(
        "Ler docs/_canon/DECISION_POLICY.md\n"
        "Ler docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md\n"
        "Emitir BLOCKED_MISSING_ARCH_DECISION quando aplicável.\n",
        encoding="utf-8",
    )
    (root / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml").write_text(
        "gates:\n"
        "  - gate_id: DOC_USAGE_GATE\n"
        "    status: active\n"
        "  - gate_id: CANON_CONTRACT_DRIVEN_PARITY_GATE\n"
        "    status: active\n",
        encoding="utf-8",
    )
    (root / "scripts" / "contracts" / "validate" / "validate_contracts.py").write_text(
        "DOC_USAGE_GATE\nCANON_CONTRACT_DRIVEN_PARITY_GATE\n",
        encoding="utf-8",
    )
    (root / "scripts" / "hb").write_text("# hb entrypoint\n", encoding="utf-8")


def test_canon_contract_driven_parity_gate_passes_when_minimum_scope_is_aligned(tmp_path):
    _write_minimal_parity_workspace(tmp_path)

    result = gates._g2p_canon_contract_driven_parity(tmp_path)

    assert result["status"] == "PASS"


def test_canon_contract_driven_parity_gate_fails_when_agent_instructions_lose_boot_reference(tmp_path):
    _write_minimal_parity_workspace(tmp_path)
    (tmp_path / "docs" / "_canon" / "AGENT_INSTRUCTIONS.md").write_text(
        "Boot sem referência operacional.\n",
        encoding="utf-8",
    )

    result = gates._g2p_canon_contract_driven_parity(tmp_path)

    assert result["status"] == "FAIL"
    assert any("AGENT_INSTRUCTIONS.md" in item["artifact"] for item in result.get("violations", []))


def test_canon_contract_driven_parity_gate_fails_when_decision_prompt_loses_block_code(tmp_path):
    _write_minimal_parity_workspace(tmp_path)
    (tmp_path / ".contract_driven" / "agent_prompts" / "decision_discovery.prompt.md").write_text(
        "Ler docs/_canon/DECISION_POLICY.md\nLer docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md\n",
        encoding="utf-8",
    )

    result = gates._g2p_canon_contract_driven_parity(tmp_path)

    assert result["status"] == "FAIL"
    assert any("decision_discovery.prompt.md" in item["artifact"] for item in result.get("violations", []))


def test_canon_contract_driven_parity_gate_fails_when_active_registry_gate_is_missing_from_validator(tmp_path):
    _write_minimal_parity_workspace(tmp_path)
    (tmp_path / "scripts" / "contracts" / "validate" / "validate_contracts.py").write_text(
        "DOC_USAGE_GATE\n",
        encoding="utf-8",
    )

    result = gates._g2p_canon_contract_driven_parity(tmp_path)

    assert result["status"] == "FAIL"
    assert any("validate_contracts.py" in item["artifact"] for item in result.get("violations", []))
