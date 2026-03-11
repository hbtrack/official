"""
Builder do handoff de execução (16_ATLETAS_AGENT_HANDOFF.json).

SSOT: docs/hbtrack/modulos/atletas/MOTORES.md
"""
from __future__ import annotations

from pathlib import Path

from hbtrack_lint.hashing import sha256_file


# Documentos incluídos no snapshot do handoff
_ARTIFACT_NAMES = [
    "00_ATLETAS_CROSS_LINTER_RULES.json",
    "01_ATLETAS_OPENAPI.yaml",
    "05_ATLETAS_EVENTS.asyncapi.yaml",
    "08_ATLETAS_TRACEABILITY.yaml",
    "12_ATLETAS_EXECUTION_BINDINGS.yaml",
    "13_ATLETAS_DB_CONTRACT.yaml",
    "14_ATLETAS_UI_CONTRACT.yaml",
    "15_ATLETAS_INVARIANTS.yaml",
    "17_ATLETAS_PROJECTIONS.yaml",
    "18_ATLETAS_SIDE_EFFECTS.yaml",
    "19_ATLETAS_TEST_SCENARIOS.yaml",
    "20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md",
]

_ROLE_MAP = {
    "00_ATLETAS_CROSS_LINTER_RULES.json": "constitution",
    "01_ATLETAS_OPENAPI.yaml": "api_contract",
    "05_ATLETAS_EVENTS.asyncapi.yaml": "event_contract",
    "08_ATLETAS_TRACEABILITY.yaml": "traceability",
    "12_ATLETAS_EXECUTION_BINDINGS.yaml": "execution_bindings",
    "13_ATLETAS_DB_CONTRACT.yaml": "db_contract",
    "14_ATLETAS_UI_CONTRACT.yaml": "ui_contract",
    "15_ATLETAS_INVARIANTS.yaml": "invariants",
    "17_ATLETAS_PROJECTIONS.yaml": "projections",
    "18_ATLETAS_SIDE_EFFECTS.yaml": "side_effects",
    "19_ATLETAS_TEST_SCENARIOS.yaml": "test_scenarios",
    "20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md": "executor_restriction_prompt",
}


def build_handoff(
    repo_root: Path,
    module_root: Path,
    contracts: dict,
    anchor_manifest: dict,
    reports_dir: Path,
) -> dict:
    """Constrói o handoff de execução a partir do contract pack validado."""
    traceability = contracts.get("08_ATLETAS_TRACEABILITY.yaml") or {}
    cross = contracts.get("00_ATLETAS_CROSS_LINTER_RULES.json") or {}
    meta_tr = traceability.get("meta") or {}

    allowed_operation_ids = [
        op["operation_id"] for op in traceability.get("operations", [])
    ]

    operation_file_bindings = []
    allowed_file_paths: set[str] = set()

    for op in traceability.get("operations", []):
        operation_id = op.get("operation_id", "")
        binding = op.get("implementation_binding") or {}
        file_paths: list[str] = []

        for key in [
            "backend_handler_file",
            "backend_service_file",
            "repository_file",
            "projection_file",
            "side_effect_file",
            "frontend_screen_file",
            "frontend_component_file",
            "e2e_spec_file",
        ]:
            value = binding.get(key)
            if value:
                file_paths.append(value)
                allowed_file_paths.add(value)

        public_symbols = [
            sym
            for sym in [
                binding.get("backend_handler"),
                binding.get("backend_service"),
                binding.get("frontend_component"),
            ]
            if sym
        ]

        operation_file_bindings.append({
            "operation_id": operation_id,
            "file_paths": sorted(set(file_paths)),
            "public_symbols": public_symbols,
        })

    artifacts = []
    for name in _ARTIFACT_NAMES:
        path = module_root / name
        if path.exists():
            artifacts.append({
                "path": str(path.relative_to(repo_root)).replace("\\", "/"),
                "role": _ROLE_MAP.get(name, "contract"),
                "sha256": sha256_file(path),
            })

    checker_ids = _collect_checker_ids(cross)

    ordered_steps = []
    for op_id in allowed_operation_ids:
        step_map = {
            "athletes__athlete__create": ("Implementar endpoint POST /athletes", "create_athlete", "athlete_create"),
            "athletes__athlete__list": ("Implementar endpoint GET /athletes", "list_athletes", "athlete_list"),
            "athletes__athlete__get": ("Implementar endpoint GET /athletes/{id}", "get_athlete", "athlete_get"),
            "athletes__athlete__update": ("Implementar endpoint PATCH /athletes/{id}", "update_athlete", "athlete_update"),
        }
        desc, svc, handler = step_map.get(op_id, (f"Implementar {op_id}", op_id, op_id))
        ordered_steps.append({
            "step_id": f"STEP-{len(ordered_steps) + 1:03d}",
            "operation_id": op_id,
            "description": desc,
            "backend_service": svc,
            "backend_handler": handler,
            "blocking": True,
        })

    return {
        "meta": {
            "handoff_id": "HANDOFF-ATHLETES-2026-03-08-001",
            "module_id": meta_tr.get("module_id", "ATHLETES"),
            "module_version": meta_tr.get("module_version", "1.0.0"),
            "status": "READY_FOR_EXECUTION",
            "authority_level": "EXECUTIONAL_SSOT",
            "issued_by": "hb_plan",
            "issued_at": "2026-03-08T00:00:00Z",
            "conversation_independent": True,
            "constitution_version": "1.2.7",
        },
        "integrity": {
            "snapshot_mode": "hash_locked",
            "artifacts": artifacts,
            "stale_snapshot_policy": "block_execution",
        },
        "execution_scope": {
            "allowed_operation_ids": allowed_operation_ids,
            "allowed_file_paths": sorted(allowed_file_paths),
            "forbidden_write_paths": [],
            "operation_file_bindings": operation_file_bindings,
            "public_symbol_policy": {
                "public_symbols_declared_only": True,
                "private_helper_symbols": {
                    "allowed": True,
                    "naming_pattern": "^_",
                    "allowed_scope": "inside_anchor_region_only",
                    "export_forbidden": True,
                },
            },
        },
        "codegen_requirements": {
            "openapi_codegen_required": True,
            "frontend_client_generation_required": True,
            "backend_stub_generation_required": True,
            "manual_symbol_creation_allowed": False,
        },
        "validator_requirements": {
            "allowed_checker_ids": checker_ids,
            "required_checker_ids": [
                "check_handoff_hashes_match_snapshot",
                "check_stub_edits_stay_within_anchors",
                "check_generated_symbols_are_immutable",
                "check_no_uncontracted_public_symbols",
            ],
        },
        "task_plan": {
            "ordered_steps": ordered_steps,
        },
        "entry_gates": [
            {"gate_id": "EG-001", "rule_id": "X-001", "description": "OpenAPI operationIds rastreáveis", "required": True},
            {"gate_id": "EG-002", "rule_id": "X-012", "description": "Hashes do handoff batem com snapshot", "required": True},
            {"gate_id": "EG-003", "rule_id": "DOC-001", "description": "Todos os documentos requeridos existem", "required": True},
        ],
        "exit_gates": [
            {"gate_id": "XG-001", "rule_id": "X-020", "description": "Cenários canônicos passam", "required": True},
            {"gate_id": "XG-002", "rule_id": "DOC-005", "description": "Handoff gerado com integridade", "required": True},
        ],
        "prohibitions": [
            "do_not_use_chat_history_as_source_of_truth",
            "do_not_create_new_symbols_outside_traceability",
            "do_not_edit_outside_anchor_regions",
            "do_not_bypass_constitutional_rules",
            "do_not_override_linter_prohibitions",
            "do_not_add_fields_not_in_openapi_contract",
        ],
    }


def _collect_checker_ids(cross: dict) -> list[str]:
    ids = []
    section_names = [
        "document_shape_rules", "cross_rules", "event_rules", "projection_rules",
        "side_effect_rules", "concurrency_rules", "ui_state_rules",
        "time_determinism_rules", "test_scenario_rules", "stub_anchor_rules",
        "handoff_rules", "restriction_prompt_rules", "diff_validation_rules",
    ]
    for section in section_names:
        for rule in cross.get(section, []):
            cid = rule.get("checker_id")
            if cid and cid not in ids:
                ids.append(cid)
    return ids
