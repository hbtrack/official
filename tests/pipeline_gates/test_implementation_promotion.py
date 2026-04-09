from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def _task_catalog() -> dict:
    return yaml.safe_load(
        (ROOT / ".contract_driven" / "TASK_CATALOG.yaml").read_text(encoding="utf-8")
    )


def _module_registry() -> dict:
    return yaml.safe_load(
        (ROOT / "docs" / "_canon" / "MODULE_REGISTRY.yaml").read_text(encoding="utf-8")
    )


def test_implementation_promotion_task_type_exists_in_catalog():
    catalog = _task_catalog()
    task_types = catalog.get("task_catalog", {})
    assert "implementation_promotion" in task_types, (
        "implementation_promotion deve estar em TASK_CATALOG.yaml"
    )


def test_implementation_promotion_fields():
    catalog = _task_catalog()
    entry = catalog["task_catalog"]["implementation_promotion"]

    assert entry.get("task_type") == "implementation_promotion"
    assert entry.get("status") == "active", "implementation_promotion deve estar ativo (não frozen)"
    assert entry.get("worker_id"), "worker_id deve estar definido"
    assert entry.get("description"), "description deve estar definida"


def test_implementation_promotion_requires_implementation_ready_status():
    catalog = _task_catalog()
    entry = catalog["task_catalog"]["implementation_promotion"]
    input_reqs = entry.get("input_requirements", [])

    has_module_req = any("implementation_ready" in str(r) for r in input_reqs)
    assert has_module_req, (
        "implementation_promotion deve exigir módulo com status=implementation_ready"
    )


def test_implementation_promotion_requires_evidence_ref():
    catalog = _task_catalog()
    entry = catalog["task_catalog"]["implementation_promotion"]
    input_reqs = entry.get("input_requirements", [])

    has_evidence_ref = any("evidence_ref" in str(r) for r in input_reqs)
    assert has_evidence_ref, (
        "implementation_promotion deve exigir evidence_ref (caminho para evidência de testes)"
    )


def test_implementation_promotion_stage_allowed():
    catalog = _task_catalog()
    entry = catalog["task_catalog"]["implementation_promotion"]
    stage_allowed = entry.get("stage_allowed", [])

    assert len(stage_allowed) > 0, (
        "implementation_promotion deve declarar ao menos um stage_allowed"
    )
    assert 3 in stage_allowed, (
        "implementation_promotion deve ser permitido no stage 3 (implementação)"
    )


def test_implementation_promotion_produces_module_registry_artifact():
    catalog = _task_catalog()
    entry = catalog["task_catalog"]["implementation_promotion"]
    artifacts = entry.get("artifacts_produced", [])

    has_registry = any("MODULE_REGISTRY.yaml" in str(a) for a in artifacts)
    assert has_registry, (
        "implementation_promotion deve declarar MODULE_REGISTRY.yaml como artifact_produced"
    )


def test_staging_promotion_lifecycle_transitions():
    """MODULE_REGISTRY deve declarar transição implementation_ready → implemented."""
    registry = _module_registry()
    policy = registry.get("policy", {})
    status_order = policy.get("status_order", [])

    assert "implementation_ready" in status_order
    assert "implemented" in status_order

    idx_ready = status_order.index("implementation_ready")
    idx_impl = status_order.index("implemented")
    assert idx_impl == idx_ready + 1, (
        "implemented deve ser o status imediatamente seguinte a implementation_ready"
    )


def test_release_promotion_requires_staging_validated():
    """released deve exigir staging_validated como estado anterior."""
    registry = _module_registry()
    policy = registry.get("policy", {})
    status_order = policy.get("status_order", [])

    assert "staging_validated" in status_order
    assert "released" in status_order

    idx_staging = status_order.index("staging_validated")
    idx_released = status_order.index("released")
    assert idx_released == idx_staging + 1, (
        "released deve ser o status imediatamente seguinte a staging_validated"
    )
