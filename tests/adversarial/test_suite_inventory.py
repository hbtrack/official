from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml"


CATEGORY_MATRIX = {
    "authority_drift_suite": {
        "tests": [
            "tests/pipeline_gates/test_source_authority_graph.py",
            "tests/pipeline_gates/test_doc_usage_gate.py",
            "tests/pipeline_gates/test_canon_contract_driven_parity_gate.py",
            "tests/pipeline_gates/test_hbtrack_canon_parity_gate.py",
        ],
        "gates": [
            "DOC_USAGE_GATE",
            "CANON_CONTRACT_DRIVEN_PARITY_GATE",
            "HBTRACK_CANON_PARITY_GATE",
        ],
    },
    "source_graph_ambiguity_suite": {
        "tests": [
            "tests/pipeline_gates/test_source_graph_global_integrity.py",
            "tests/pipeline_gates/test_reports_source_graph_integrity.py",
            "tests/pipeline_gates/test_analytics_source_graph_integrity.py",
            "tests/pipeline_gates/test_exercises_source_graph_integrity.py",
            "tests/pipeline_gates/test_source_graph_compiler_reports.py",
            "tests/pipeline_gates/test_source_graph_compiler_analytics.py",
            "tests/pipeline_gates/test_source_graph_compiler_exercises.py",
        ],
        "gates": [],
    },
    "partial_update_suite": {
        "tests": [
            "tests/pipeline_gates/test_impact_analysis_gate.py",
            "tests/pipeline_gates/test_partial_update_gate.py",
            "tests/pipeline_gates/test_sync_manifest_integrity.py",
        ],
        "gates": [
            "IMPACT_ANALYSIS_GATE",
            "PARTIAL_UPDATE_GATE",
        ],
    },
    "prompt_schema_parity_suite": {
        "tests": [
            "tests/pipeline_gates/test_schema_template_parity_phase4.py",
            "tests/pipeline_gates/test_context_budgets_and_parity.py",
        ],
        "gates": [],
    },
    "doc_contract_parity_suite": {
        "tests": [
            "tests/pipeline_gates/test_canon_contract_driven_parity_gate.py",
            "tests/pipeline_gates/test_hbtrack_canon_parity_gate.py",
            "tests/pipeline_gates/test_openapi_schema_equivalence_gate.py",
        ],
        "gates": [
            "CANON_CONTRACT_DRIVEN_PARITY_GATE",
            "HBTRACK_CANON_PARITY_GATE",
            "OPENAPI_SCHEMA_EQUIVALENCE_GATE",
        ],
    },
    "contract_code_parity_suite": {
        "tests": [
            "tests/pipeline_gates/test_backend_codegen_reports.py",
            "tests/pipeline_gates/test_generated_layout_reports.py",
            "tests/parity/test_reports_codegen_parity.py",
        ],
        "gates": [
            "CODE_ARCHITECTURE_GATE",
        ],
    },
    "projection_drift_suite": {
        "tests": [
            "tests/pipeline_gates/test_openapi_schema_equivalence_gate.py",
            "tests/pipeline_gates/test_reports_openapi_schema_equivalence.py",
        ],
        "gates": [
            "OPENAPI_SCHEMA_EQUIVALENCE_GATE",
        ],
    },
    "promotion_coherence_suite": {
        "tests": [
            "tests/pipeline_gates/test_implementation_promotion.py",
            "tests/pipeline_gates/test_runtime_promotions.py",
            "tests/pipeline_gates/test_module_lifecycle_governance.py",
        ],
        "gates": [
            "READINESS_GENERATION_COMPATIBILITY_GATE",
            "SURFACE_PROMOTION_COHERENCE_GATE",
        ],
    },
    "dss_traceability_suite": {
        "tests": [
            "tests/adversarial/test_dss_traceability_suite.py",
            "tests/pipeline_gates/test_arch_decision_presence_gate.py",
        ],
        "gates": [
            "DECISION_IR_CONFORMANCE_GATE",
            "ARCH_DECISION_PRESENCE_GATE",
        ],
    },
    "runtime_conformance_suite": {
        "tests": [
            "tests/pipeline_gates/test_deploy_env_rendering_flow.py",
            "tests/pipeline_gates/test_ops_source_graph_integrity.py",
            "tests/pipeline_gates/test_secret_rotation_contract.py",
            "tests/pipeline_gates/test_runtime_promotions.py",
        ],
        "gates": [
            "HTTP_RUNTIME_CONTRACT_GATE",
            "PACT_PROVIDER_GATE",
            "DEPLOY_WORKFLOW_ENV_PARITY_GATE",
        ],
    },
    "stale_bundle_suite": {
        "tests": [
            "tests/pipeline_gates/test_context_bundle_freshness_gate.py",
            "tests/pipeline_gates/test_ops_bundle_required_for_roadmap.py",
        ],
        "gates": [
            "CONTEXT_BUNDLE_FRESHNESS_GATE",
        ],
    },
    "merge_rules_enforcement_suite": {
        "tests": [
            "tests/adversarial/test_merge_rules_enforcement_suite.py",
            "tests/pipeline_gates/test_hook_governance_enforcement_phase5.py",
        ],
        "gates": [],
    },
}


def _load_registry() -> dict:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_category_matrix_covers_all_required_adversarial_suites():
    assert set(CATEGORY_MATRIX) == {
        "authority_drift_suite",
        "source_graph_ambiguity_suite",
        "partial_update_suite",
        "prompt_schema_parity_suite",
        "doc_contract_parity_suite",
        "contract_code_parity_suite",
        "projection_drift_suite",
        "promotion_coherence_suite",
        "dss_traceability_suite",
        "runtime_conformance_suite",
        "stale_bundle_suite",
        "merge_rules_enforcement_suite",
    }


def test_all_declared_suite_paths_exist():
    missing: list[str] = []
    for category, payload in CATEGORY_MATRIX.items():
        tests = payload["tests"]
        assert tests, f"{category} sem testes concretos associados"
        for relpath in tests:
            if not (ROOT / relpath).exists():
                missing.append(f"{category}: {relpath}")
    assert not missing, "Suites adversariais com paths ausentes:\n" + "\n".join(missing)


def test_declared_suite_gates_exist_in_registry():
    gate_ids = {gate["gate_id"] for gate in _load_registry().get("gates", [])}
    missing: list[str] = []
    for category, payload in CATEGORY_MATRIX.items():
        for gate_id in payload["gates"]:
            if gate_id not in gate_ids:
                missing.append(f"{category}: {gate_id}")
    assert not missing, "Suites adversariais referenciam gates ausentes:\n" + "\n".join(missing)
