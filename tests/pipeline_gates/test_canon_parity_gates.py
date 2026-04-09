from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml"


def _registry_gates() -> dict[str, dict]:
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {g["gate_id"]: g for g in data.get("gates", [])}


# ---------------------------------------------------------------------------
# Registry checks — gate ordering
# ---------------------------------------------------------------------------


def test_three_parity_gates_orders_are_sequential():
    """20O, 20P, 20Q devem existir e ser os três últimos gates do batch 20."""
    orders = {g["gate_id"]: g.get("order") for g in _registry_gates().values()}
    assert orders.get("DOC_USAGE_GATE") == "20O"
    assert orders.get("CANON_CONTRACT_DRIVEN_PARITY_GATE") == "20P"
    assert orders.get("HBTRACK_CANON_PARITY_GATE") == "20Q"


# ---------------------------------------------------------------------------
# CANON_CONTRACT_DRIVEN_PARITY_GATE — unit tests
# ---------------------------------------------------------------------------


def test_canon_contract_driven_parity_gate_skips_without_catalog(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    result = vc._g_canon_contract_driven_parity(tmp_path)
    assert result["status"] == "SKIP_NOT_APPLICABLE", (
        f"Gate deve SKIP sem TASK_CATALOG, obteve: {result['status']}"
    )


def test_canon_contract_driven_parity_gate_fail_when_worker_path_missing(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    cd_dir = tmp_path / ".contract_driven"
    cd_dir.mkdir()
    catalog = {
        "task_catalog": {
            "my_task": {
                "task_type": "my_task",
                "worker_id": "my_worker",
                "worker_path": ".contract_driven/agent_prompts/my_worker.prompt.md",
                "status": "active",
            }
        }
    }
    (cd_dir / "TASK_CATALOG.yaml").write_text(yaml.dump(catalog), encoding="utf-8")

    result = vc._g_canon_contract_driven_parity(tmp_path)
    assert result["status"] == "FAIL", (
        f"Gate deve FAIL quando worker_path ativo não existe, obteve: {result['status']}"
    )
    violations = result.get("violations", [])
    assert any(v.get("type") == "missing_worker_prompt" for v in violations)


def test_canon_contract_driven_parity_gate_skip_frozen_tasks(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    cd_dir = tmp_path / ".contract_driven"
    cd_dir.mkdir()
    catalog = {
        "task_catalog": {
            "frozen_task": {
                "task_type": "frozen_task",
                "worker_id": "frozen_worker",
                "worker_path": ".contract_driven/agent_prompts/frozen_worker.prompt.md",
                "status": "frozen",
            }
        }
    }
    (cd_dir / "TASK_CATALOG.yaml").write_text(yaml.dump(catalog), encoding="utf-8")

    result = vc._g_canon_contract_driven_parity(tmp_path)
    # Frozen tasks não devem causar falha mesmo sem arquivo de prompt
    assert result["status"] in ("PASS", "SKIP_NOT_APPLICABLE"), (
        f"Gate não deve FAIL para tarefas frozen, obteve: {result['status']}"
    )


def test_canon_contract_driven_parity_gate_fail_when_module_registry_matrix_mismatch(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    cd_dir = tmp_path / ".contract_driven"
    cd_dir.mkdir()
    (cd_dir / "TASK_CATALOG.yaml").write_text("task_catalog: {}", encoding="utf-8")

    canon_dir = tmp_path / "docs" / "_canon"
    canon_dir.mkdir(parents=True)

    reg = {"modules": {"module_a": {"status": "active"}, "module_b": {"status": "active"}}}
    (canon_dir / "MODULE_REGISTRY.yaml").write_text(yaml.dump(reg), encoding="utf-8")

    matrix = {"modules": {"module_a": {}}}  # module_b ausente
    (canon_dir / "MODULE_SOURCE_AUTHORITY_MATRIX.yaml").write_text(
        yaml.dump(matrix), encoding="utf-8"
    )

    result = vc._g_canon_contract_driven_parity(tmp_path)
    assert result["status"] == "FAIL", (
        f"Gate deve FAIL quando MODULE_REGISTRY e AUTHORITY_MATRIX divergem, obteve: {result['status']}"
    )
    violations = result.get("violations", [])
    assert any(
        v.get("type") == "module_in_registry_not_in_matrix" and v.get("module") == "module_b"
        for v in violations
    ), "Deve haver violação para module_b ausente na matrix"


# ---------------------------------------------------------------------------
# HBTRACK_CANON_PARITY_GATE — unit tests
# ---------------------------------------------------------------------------


def test_hbtrack_canon_parity_gate_skips_without_registry(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    result = vc._g_hbtrack_canon_parity(tmp_path)
    assert result["status"] == "SKIP_NOT_APPLICABLE", (
        f"Gate deve SKIP sem MODULE_REGISTRY, obteve: {result['status']}"
    )


def test_hbtrack_canon_parity_gate_fail_when_module_dir_missing(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    canon_dir = tmp_path / "docs" / "_canon"
    canon_dir.mkdir(parents=True)

    # Create global docs
    (canon_dir / "GLOBAL_INVARIANTS.md").write_text("# Global\n", encoding="utf-8")
    (canon_dir / "DOMAIN_GLOSSARY.md").write_text("# Glossary\n", encoding="utf-8")

    reg = {"modules": {"phantom_module": {"status": "active"}}}
    (canon_dir / "MODULE_REGISTRY.yaml").write_text(yaml.dump(reg), encoding="utf-8")

    # docs/hbtrack/modulos/ exists but phantom_module dir does NOT
    (tmp_path / "docs" / "hbtrack" / "modulos").mkdir(parents=True)

    result = vc._g_hbtrack_canon_parity(tmp_path)
    assert result["status"] == "FAIL", (
        f"Gate deve FAIL quando diretório do módulo não existe, obteve: {result['status']}"
    )
    violations = result.get("violations", [])
    assert any(
        v.get("module") == "phantom_module" for v in violations
    ), "Deve haver violação para phantom_module"


def test_hbtrack_canon_parity_gate_fail_when_global_doc_missing(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    canon_dir = tmp_path / "docs" / "_canon"
    canon_dir.mkdir(parents=True)

    # GLOBAL_INVARIANTS.md faltando — DOMAIN_GLOSSARY.md presente
    (canon_dir / "DOMAIN_GLOSSARY.md").write_text("# Glossary\n", encoding="utf-8")

    reg = {"modules": {}}
    (canon_dir / "MODULE_REGISTRY.yaml").write_text(yaml.dump(reg), encoding="utf-8")

    result = vc._g_hbtrack_canon_parity(tmp_path)
    assert result["status"] == "FAIL", (
        f"Gate deve FAIL quando GLOBAL_INVARIANTS.md está ausente, obteve: {result['status']}"
    )
    violations = result.get("violations", [])
    assert any(
        v.get("type") == "missing_global_doc" and "GLOBAL_INVARIANTS" in v.get("doc", "")
        for v in violations
    )


def test_hbtrack_canon_parity_gate_fail_when_graph_dir_missing(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    canon_dir = tmp_path / "docs" / "_canon"
    canon_dir.mkdir(parents=True)

    (canon_dir / "GLOBAL_INVARIANTS.md").write_text("# Global\n", encoding="utf-8")
    (canon_dir / "DOMAIN_GLOSSARY.md").write_text("# Glossary\n", encoding="utf-8")

    reg = {"modules": {"training": {"status": "active"}}}
    (canon_dir / "MODULE_REGISTRY.yaml").write_text(yaml.dump(reg), encoding="utf-8")

    # Module dir exists but graph/ does NOT
    module_dir = tmp_path / "docs" / "hbtrack" / "modulos" / "training"
    module_dir.mkdir(parents=True)

    result = vc._g_hbtrack_canon_parity(tmp_path)
    assert result["status"] == "FAIL", (
        f"Gate deve FAIL quando graph/ não existe, obteve: {result['status']}"
    )
    violations = result.get("violations", [])
    assert any(
        v.get("module") == "training" and "graph" in v.get("type", "")
        for v in violations
    )


# ---------------------------------------------------------------------------
# Real-world integration: gates pass against actual repo
# ---------------------------------------------------------------------------


def test_canon_contract_driven_parity_gate_pass_on_real_repo():
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    result = vc._g_canon_contract_driven_parity(ROOT)
    assert result["status"] == "PASS", (
        f"CANON_CONTRACT_DRIVEN_PARITY_GATE deve PASS no repositório real, "
        f"obteve: {result['status']}\nViolações: {result.get('violations', [])}"
    )


def test_hbtrack_canon_parity_gate_pass_on_real_repo():
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    result = vc._g_hbtrack_canon_parity(ROOT)
    assert result["status"] == "PASS", (
        f"HBTRACK_CANON_PARITY_GATE deve PASS no repositório real, "
        f"obteve: {result['status']}\nViolações: {result.get('violations', [])}"
    )
