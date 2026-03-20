# Dashboard de Readiness - HB Track
> Gerado em 2026-03-20T05:40:09Z | run_id: `20260320T054009_61b076` | health: **94/100** | overall: **FAIL**

## Modulos

| Modulo | Status | Superficies |
|---|---|---|
| users | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo, permissions, decision_ir |
| seasons | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo |
| teams | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo |
| training | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, state_model, permissions, errors, sport_science, ui_contract, arazzo, asyncapi, decision_ir |
| wellness | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, sport_science, asyncapi, arazzo |
| medical | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, sport_science |
| competitions | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo |
| matches | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo |
| scout | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo, permissions, decision_ir |
| exercises | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, permissions |
| analytics | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix |
| reports | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix |
| ai_ingestion | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo |
| identity_access | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, permissions, arazzo, asyncapi, decision_ir |
| audit | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo, permissions, decision_ir |
| notifications | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo |
| video | `implementation_ready` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo, permissions, decision_ir |

## Gates

| Gate | Status | Blocking |
|---|---|---|
| AXIOM_INTEGRITY_GATE | PASS | sim |
| PATH_CANONICALITY_GATE | PASS | sim |
| REQUIRED_ARTIFACT_PRESENCE_GATE | SKIP_NOT_APPLICABLE | sim |
| MODULE_DOC_CROSSREF_GATE | SKIP_NOT_APPLICABLE | sim |
| API_NORMATIVE_DUPLICATION_GATE | SKIP_NOT_APPLICABLE | nao |
| OWASP_API_CONTROL_MATRIX_GATE | SKIP_NOT_APPLICABLE | sim |
| MODULE_SOURCE_AUTHORITY_MATRIX_GATE | SKIP_NOT_APPLICABLE | sim |
| MODULE_REGISTRY_GATE | PASS | sim |
| BOUNDARY_USERS_IDENTITY_ACCESS_GATE | SKIP_NOT_APPLICABLE | sim |
| WELLNESS_MEDICAL_BOUNDARY_GATE | SKIP_NOT_APPLICABLE | sim |
| SCOUT_TAXONOMY_GATE | SKIP_NOT_APPLICABLE | sim |
| ASYNC_REQUIRED_MODULE_GATE | SKIP_NOT_APPLICABLE | sim |
| EXTERNAL_SOURCE_AUTHORITY_GATE | SKIP_NOT_APPLICABLE | sim |
| PRE_CONTRACT_EVIDENCE_GATE | SKIP_NOT_APPLICABLE | sim |
| SHADOW_AUTHORITY_GATE | SKIP_NOT_APPLICABLE | sim |
| DECISION_IR_CONFORMANCE_GATE | PASS | sim |
| CANON_ALLOWLIST_GATE | PASS | sim |
| PLACEHOLDER_RESIDUE_GATE | PASS | sim |
| REF_HERMETICITY_GATE | SKIP_NOT_APPLICABLE | sim |
| TOOLING_CONFIG_GATE | SKIP_NOT_APPLICABLE | sim |
| OPENAPI_ROOT_STRUCTURE_GATE | PASS | sim |
| OPENAPI_ROOT_MODULE_SYNC_GATE | PASS | sim |
| OPENAPI_POLICY_RULESET_GATE | SKIP_NOT_APPLICABLE | sim |
| JSON_SCHEMA_VALIDATION_GATE | PASS | sim |
| CROSS_SPEC_ALIGNMENT_GATE | FAIL | sim |
| CONTRACT_BREAKING_CHANGE_GATE | SKIP_NOT_APPLICABLE | sim |
| TRANSFORMATION_FEASIBILITY_GATE | SKIP_NOT_APPLICABLE | sim |
| HTTP_RUNTIME_CONTRACT_GATE | SKIP_NOT_APPLICABLE | sim |
| ASYNCAPI_VALIDATION_GATE | PASS | sim |
| ARAZZO_VALIDATION_GATE | PASS | sim |
| SPECTRAL_LINTING_GATE | PASS | sim |
| ARAZZO_COMPLETENESS_GATE | SKIP_NOT_APPLICABLE | sim |
| UI_DOC_VALIDATION_GATE | PASS | sim |
| DERIVED_DRIFT_GATE | FAIL | sim |
| ADVERSARIAL_ANALYSIS_GATE | PASS | nao |
| FEATURE_READINESS_GATE | PASS | nao |
| VERSIONING_POLICY_GATE | SKIP_NOT_APPLICABLE | nao |
| PACT_PROVIDER_GATE | SKIP_NOT_APPLICABLE | nao |
| CODE_ARCHITECTURE_GATE | SKIP_NOT_APPLICABLE | nao |
| DEPLOY_READINESS_GATE | SKIP_NOT_APPLICABLE | nao |
| DATA_MIGRATION_GATE | SKIP_NOT_APPLICABLE | nao |
| MONITORING_POLICY_GATE | SKIP_NOT_APPLICABLE | nao |
| HANDOFF_COHERENCE_GATE | PASS | nao |
| MODULE_STATUS_COHERENCE_GATE | PASS | sim |
| SURFACE_PROMOTION_COHERENCE_GATE | PASS | sim |
| CROSS_MODULE_BOUNDARY_GATE | SKIP_NOT_APPLICABLE | nao |
| MODULE_DEPENDENCY_RESOLUTION_GATE | SKIP_NOT_APPLICABLE | sim |
| WAIVER_VALIDITY_GATE | PASS | sim |
| READINESS_GENERATION_COMPATIBILITY_GATE | PASS | sim |
| READINESS_HUMAN_CONFIRMATION_GATE | SKIP_NOT_APPLICABLE | sim |
| READINESS_SUMMARY_GATE | FAIL | nao |
