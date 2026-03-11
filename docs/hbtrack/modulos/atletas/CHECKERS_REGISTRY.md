# CHECKERS_REGISTRY — Mapa checker_id → Implementação Python

**Fonte RAG:** `MOTORES.md` (CHECKERS dict + estrutura `hbtrack_lint/`); `00_ATLETAS_CROSS_LINTER_RULES.json` (todos os `checker_id` declarados).
**Propósito:** G-010 — `hb_plan.py` retorna FAIL para qualquer `checker_id` sem função Python. Este documento mapeia o estado de implementação de cada regra.

---

## Estrutura de módulos (`hbtrack_lint/checkers/`)

Fonte: `MOTORES.md` — "Estrutura de diretórios recomendada"

```
scripts/hbtrack_lint/checkers/
  __init__.py
  documents.py      → regras DOC-*
  cross.py          → regras X-*, TYPE-*
  db.py             → regras X-003, X-004, X-010, X-015, CC-001, CC-002
  ui.py             → regras X-005, X-006, X-011, CC-003, UIST-*
  invariants.py     → regras X-007, X-008, X-009, TIME-*
  handoff.py        → regras X-012, X-013, X-014, HO-*, DIFF-*
  events.py         → regras EV-*
  side_effects.py   → regras SE-*, PROJ-005
  time.py           → regras TIME-001, TIME-002, TIME-003
  tests.py          → regras TSC-*
  anchors.py        → regras STUB-*
  restrictions.py   → regras RP-*
  projections.py    → regras PROJ-*
```

---

## Tabela completa: checker_id → status → módulo

### Regras TYPE-* (global_type_system)

| rule_id | checker_id | Status | Módulo |
|---|---|---|---|
| TYPE-001 | `check_canonical_scalar_mappings_are_complete` | ❌ SEM IMPL | `cross.py` |
| TYPE-002 | `check_uuid_fields_preserve_canonical_format_across_layers` | ❌ SEM IMPL | `cross.py` |
| TYPE-003 | `check_frontend_types_derive_from_openapi_snapshot` | ❌ SEM IMPL | `cross.py` |
| TYPE-004 | `check_enum_consistency_across_layers` | ❌ SEM IMPL | `cross.py` |
| TYPE-005 | `check_collection_element_types_preserve_canonical_mapping` | ❌ SEM IMPL | `cross.py` |
| TYPE-006 | `check_polymorphic_discriminator_strategy_is_canonical` | ❌ SEM IMPL | `cross.py` |

### Regras DOC-* (document_shape_rules)

| rule_id | checker_id | Status | Módulo |
|---|---|---|---|
| DOC-001 | `check_required_documents_exist` | ❌ SEM IMPL | `documents.py` |
| DOC-002 | `check_required_document_metadata_fields_exist` | ❌ SEM IMPL | `documents.py` |
| DOC-003 | `check_promoted_documents_do_not_contain_placeholders` | ❌ SEM IMPL | `documents.py` |
| DOC-004 | `check_execution_bindings_validate_against_schema` | ❌ SEM IMPL | `documents.py` |
| DOC-005 | `check_generated_documents_exist_and_have_integrity` | ❌ SEM IMPL | `documents.py` |

### Regras X-* (cross_rules)

| rule_id | checker_id | Status | Módulo |
|---|---|---|---|
| X-001 | `check_openapi_operation_ids_are_traceable` | ✅ IMPL | `cross.py` |
| X-002 | `check_traceability_operations_exist_in_openapi` | ✅ IMPL | `cross.py` |
| X-003 | `check_write_operations_have_db_bindings` | ❌ SEM IMPL | `db.py` |
| X-004 | `check_db_nullability_matches_api_write_contract` | ✅ IMPL | `db.py` |
| X-005 | `check_ui_fields_bind_to_openapi_properties` | ❌ SEM IMPL | `ui.py` |
| X-006 | `check_required_selectors_are_traceable` | ❌ SEM IMPL | `ui.py` |
| X-007 | `check_traceability_invariants_exist_and_are_executable` | ❌ SEM IMPL | `invariants.py` |
| X-008 | `check_hard_fail_invariants_bind_to_operations_and_tests` | ❌ SEM IMPL | `invariants.py` |
| X-009 | `check_bound_symbols_are_reachable_from_traceability` | ❌ SEM IMPL | `invariants.py` |
| X-010 | `check_tables_in_concurrent_write_paths_declare_locking_policy` | ❌ SEM IMPL | `db.py` |
| X-011 | `check_ui_submit_state_policies_are_declared` | ❌ SEM IMPL | `ui.py` |
| X-012 | `check_handoff_hashes_match_snapshot` | ✅ IMPL | `handoff.py` |
| X-013 | `check_handoff_task_plan_references_only_contracted_targets` | ❌ SEM IMPL | `handoff.py` |
| X-014 | `check_generated_frontend_types_are_current` | ❌ SEM IMPL | `handoff.py` |
| X-015 | `check_required_migrations_exist_before_execution` | ❌ SEM IMPL | `db.py` |
| X-016 | `check_execution_bindings_are_traceable` | ❌ SEM IMPL | `cross.py` |
| X-017 | `check_execution_bindings_do_not_override_constitution` | ❌ SEM IMPL | `cross.py` |
| X-018 | `check_execution_bindings_prohibited_keys_are_complete` | ❌ SEM IMPL | `cross.py` |
| X-019 | `check_execution_flags_match_overwrite_policy` | ❌ SEM IMPL | `cross.py` |
| X-020 | `check_canonical_test_scenarios_pass_with_deterministic_report` | ❌ SEM IMPL | `cross.py` |

### Regras EV-* (event_rules)

| rule_id | checker_id | Status | Módulo |
|---|---|---|---|
| EV-001 | `check_projection_event_types_exist` | ❌ SEM IMPL | `events.py` |
| EV-002 | `check_projection_versions_are_supported_or_upcasted` | ❌ SEM IMPL | `events.py` |
| EV-003 | `check_side_effects_reference_declared_events` | ❌ SEM IMPL | `events.py` |
| EV-004 | `check_projection_and_side_effect_handlers_are_separated` | ❌ SEM IMPL | `events.py` |
| EV-005 | `check_read_models_have_event_provenance` | ❌ SEM IMPL | `events.py` |
| EV-006 | `check_event_aggregate_id_type_matches_db_contract` | ❌ SEM IMPL | `events.py` |
| EV-007 | `check_event_partition_key_matches_aggregate_id` | ❌ SEM IMPL | `events.py` |
| EV-008 | `check_upcasters_are_pure_functions` | ❌ SEM IMPL | `events.py` |
| EV-009 | `check_pydantic_model_construct_forbidden_in_event_pipeline` | ❌ SEM IMPL | `events.py` |

### Regras PROJ-* (projection_rules)

| rule_id | checker_id | Status | Módulo |
|---|---|---|---|
| PROJ-001 | `check_projection_fields_have_event_or_derived_mapping` | ❌ SEM IMPL | `projections.py` |
| PROJ-002 | `check_projection_writes_do_not_bypass_declared_handlers` | ❌ SEM IMPL | `projections.py` |
| PROJ-003 | `check_projection_consumed_versions_are_explicit` | ❌ SEM IMPL | `projections.py` |
| PROJ-004 | `check_new_event_versions_require_compatibility_strategy` | ❌ SEM IMPL | `projections.py` |
| PROJ-005 | `check_projection_handlers_are_side_effect_free` | ✅ IMPL | `side_effects.py` |
| PROJ-006 | `check_projection_atomic_shell_integrity` | ❌ SEM IMPL | `projections.py` |
| PROJ-007 | `check_projection_handlers_forbid_nested_transactions` | ❌ SEM IMPL | `projections.py` |
| PROJ-008 | `check_projection_tables_are_write_protected` | ❌ SEM IMPL | `projections.py` |
| PROJ-009 | `check_projection_idempotency_ledger_is_declared` | ❌ SEM IMPL | `projections.py` |
| PROJ-010 | `check_projection_accumulator_fields_declare_sequencing_dependency` | ❌ SEM IMPL | `projections.py` |

### Regras SE-* (side_effect_rules)

| rule_id | checker_id | Status | Módulo |
|---|---|---|---|
| SE-001 | `check_side_effect_idempotency_keys_are_declared_and_safe` | ❌ SEM IMPL | `side_effects.py` |
| SE-002 | `check_side_effect_replay_policy_is_declared` | ❌ SEM IMPL | `side_effects.py` |
| SE-003 | `check_side_effect_retry_policy_is_declared_when_retryable` | ❌ SEM IMPL | `side_effects.py` |
| SE-004 | `check_side_effects_are_skipped_during_projection_rebuild` | ❌ SEM IMPL | `side_effects.py` |
| SE-005 | `check_no_undeclared_external_calls_exist` | ❌ SEM IMPL | `side_effects.py` |
| SE-006 | `check_side_effect_handlers_do_not_write_read_models` | ❌ SEM IMPL | `side_effects.py` |
| SE-007 | `check_side_effect_handlers_do_not_import_projection_modules` | ❌ SEM IMPL | `side_effects.py` |
| SE-008 | `check_side_effect_handlers_forbid_system_clock` | ❌ SEM IMPL | `side_effects.py` |
| SE-009 | `check_side_effect_handlers_use_declared_integration_symbols` | ❌ SEM IMPL | `side_effects.py` |
| SE-010 | `check_side_effect_result_usage` | ❌ SEM IMPL | `side_effects.py` |
| SE-011 | `check_side_effect_trigger_logic_equivalence` | ❌ SEM IMPL | `side_effects.py` |
| SE-012 | `check_side_effect_predicate_manifest_is_present` | ❌ SEM IMPL | `side_effects.py` |

### Regras CC-* (concurrency_rules)

| rule_id | checker_id | Status | Módulo |
|---|---|---|---|
| CC-001 | `check_aggregates_with_concurrent_update_risk_declare_strategy` | ❌ SEM IMPL | `db.py` |
| CC-002 | `check_optimistic_locking_contract_is_complete` | ❌ SEM IMPL | `db.py` |
| CC-003 | `check_ui_duplicate_submit_protection_exists` | ❌ SEM IMPL | `ui.py` |

### Regras UIST-* (ui_state_rules)

| rule_id | checker_id | Status | Módulo |
|---|---|---|---|
| UIST-001 | `check_submit_states_define_control_policy` | ❌ SEM IMPL | `ui.py` |
| UIST-002 | `check_success_and_error_states_define_feedback_selector` | ❌ SEM IMPL | `ui.py` |
| UIST-003 | `check_required_selectors_use_primary_strategy` | ❌ SEM IMPL | `ui.py` |

### Regras TIME-* (time_determinism_rules)

| rule_id | checker_id | Status | Módulo |
|---|---|---|---|
| TIME-001 | `check_temporal_invariants_require_reference_inputs` | ❌ SEM IMPL | `time.py` |
| TIME-002 | `check_temporal_invariants_forbid_system_clock` | ✅ IMPL | `time.py` |
| TIME-003 | `check_frozen_time_enabled_for_temporal_scenarios` | ❌ SEM IMPL | `time.py` |

### Regras TSC-* (test_scenario_rules)

| rule_id | checker_id | Status | Módulo |
|---|---|---|---|
| TSC-001 | `check_test_scenarios_are_canonical_only` | ❌ SEM IMPL | `tests.py` |
| TSC-002 | `check_new_domain_scenarios_require_contract_update` | ❌ SEM IMPL | `tests.py` |
| TSC-003 | `check_property_based_tests_do_not_redefine_domain_truth` | ❌ SEM IMPL | `tests.py` |

### Regras STUB-* (stub_anchor_rules)

| rule_id | checker_id | Status | Módulo |
|---|---|---|---|
| STUB-001 | `check_stub_edits_stay_within_anchors` | ✅ IMPL | `anchors.py` |
| STUB-002 | `check_generated_symbols_are_immutable` | ❌ SEM IMPL | `anchors.py` |
| STUB-003 | `check_no_uncontracted_public_symbols` | ❌ SEM IMPL | `anchors.py` |
| STUB-004 | `check_contract_hash_comment_matches_snapshot` | ❌ SEM IMPL | `anchors.py` |

### Regras HO-* (handoff_rules)

| rule_id | checker_id | Status | Módulo |
|---|---|---|---|
| HO-001 | `check_markdown_handoff_is_not_authoritative` | ❌ SEM IMPL | `handoff.py` |
| HO-002 | `check_executor_starts_only_from_structured_manifest` | ❌ SEM IMPL | `handoff.py` |
| HO-003 | `check_execution_blocks_on_hash_drift` | ❌ SEM IMPL | `handoff.py` |
| HO-004 | `check_handoff_scope_is_subset_of_allowed_targets` | ❌ SEM IMPL | `handoff.py` |

### Regras RP-* (restriction_prompt_rules)

| rule_id | checker_id | Status | Módulo |
|---|---|---|---|
| RP-001 | `check_executor_prompt_is_fail_closed` | ❌ SEM IMPL | `restrictions.py` |
| RP-002 | `check_executor_prompt_forbids_chat_history_as_truth` | ❌ SEM IMPL | `restrictions.py` |
| RP-003 | `check_executor_prompt_requires_blocked_input_on_contract_gap` | ❌ SEM IMPL | `restrictions.py` |
| RP-004 | `check_prompt_textual_compliance_with_constitution` | ❌ SEM IMPL | `restrictions.py` |

### Regras DIFF-* (diff_validation_rules)

| rule_id | checker_id | Status | Módulo |
|---|---|---|---|
| DIFF-001 | `check_only_allowed_file_paths_changed` | ❌ SEM IMPL | `handoff.py` |
| DIFF-002 | `check_no_structural_diff_outside_anchors` | ❌ SEM IMPL | `anchors.py` |
| DIFF-003 | `check_regenerated_files_match_template_outside_anchors` | ❌ SEM IMPL | `anchors.py` |

---

## Resumo de cobertura

| Status | Quantidade | % |
|---|---|---|
| ✅ IMPL (em MOTORES.md) | 7 | 10% |
| ❌ SEM IMPL | 61 | 90% |
| **TOTAL declarado** | **68** | — |

**Checkers implementados** (fonte: `MOTORES.md` CHECKERS dict):
```python
CHECKERS = {
    "check_openapi_operation_ids_are_traceable":        cross.py,
    "check_traceability_operations_exist_in_openapi":   cross.py,
    "check_db_nullability_matches_api_write_contract":  db.py,
    "check_handoff_hashes_match_snapshot":              handoff.py,
    "check_projection_handlers_are_side_effect_free":   side_effects.py,
    "check_temporal_invariants_forbid_system_clock":    time.py,
    "check_stub_edits_stay_within_anchors":             anchors.py,
}
```

---

## Implicação para `hb_plan.py`

Fonte: `MOTORES.md` — `run_rule()`:
```python
def run_rule(rule: dict, context: ValidationContext) -> RuleResult:
    checker_id = rule["checker_id"]
    fn = CHECKERS.get(checker_id)
    if fn is None:
        return RuleResult.fail(rule["rule_id"], f"Unknown checker_id: {checker_id}")
    return fn(rule, context)
```

**Consequência direta:** com 56 checkers sem implementação, `hb_plan.py` retornaria `FAIL_ACTIONABLE` (exit=2) para 89% das regras em qualquer execução real. O sistema não pode atingir `PASS` no estado atual.

**Prioridade de implementação sugerida** (baseada em regras `cannot_waive`):

| Prioridade | checker_id | Rule | Motivo |
|---|---|---|---|
| 1 | `check_required_documents_exist` | DOC-001 | cannot_waive; gate de entrada mais básico |
| 2 | `check_write_operations_have_db_bindings` | X-003 | cannot_waive; toda escrita sem DB binding bloqueia |
| 3 | `check_hard_fail_invariants_bind_to_operations_and_tests` | X-008 | cannot_waive; invariantes sem enforcement = sem domínio |
| 4 | `check_tables_in_concurrent_write_paths_declare_locking_policy` | X-010 | cannot_waive; race condition sem detecção |
| 5 | `check_required_migrations_exist_before_execution` | X-015 | cannot_waive; Executor pode rodar sem schema |
| 6 | `check_stub_edits_stay_within_anchors` | STUB-001 | cannot_waive; já implementado ✅ |
| 7 | `check_execution_bindings_are_traceable` | X-016 | G-002; resolve alucinação de símbolo |
| 8 | `check_execution_bindings_do_not_override_constitution` | X-017 | G-002; fecha ciclo bidirecional |
