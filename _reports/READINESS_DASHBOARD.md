# Dashboard de Readiness - HB Track
> Gerado em 2026-03-18T02:43:26Z | run_id: `20260318T024326_6ea116` | health: **93/100** | overall: **FAIL**

## Modulos

| Modulo | Status | Superficies |
|---|---|---|
| users | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix |
| seasons | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix |
| teams | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix |
| training | `validated_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix, state_model, permissions, errors, sport_science, ui_contract, arazzo, asyncapi, decision_ir |
| wellness | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix, sport_science |
| medical | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix, sport_science |
| competitions | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix |
| matches | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix |
| scout | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi |
| exercises | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix, permissions |
| analytics | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi |
| reports | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix, arazzo |
| ai_ingestion | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi |
| identity_access | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix, permissions, arazzo |
| audit | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi |
| notifications | `draft_contract` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo |

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
| DECISION_IR_CONFORMANCE_GATE | SKIP_NOT_APPLICABLE | sim |
| CANON_ALLOWLIST_GATE | PASS | sim |
| PLACEHOLDER_RESIDUE_GATE | PASS | sim |
| REF_HERMETICITY_GATE | SKIP_NOT_APPLICABLE | sim |
| TOOLING_CONFIG_GATE | SKIP_NOT_APPLICABLE | sim |
| OPENAPI_ROOT_STRUCTURE_GATE | SKIP_NOT_APPLICABLE | sim |
| OPENAPI_ROOT_MODULE_SYNC_GATE | SKIP_NOT_APPLICABLE | sim |
| OPENAPI_POLICY_RULESET_GATE | SKIP_NOT_APPLICABLE | sim |
| JSON_SCHEMA_VALIDATION_GATE | SKIP_NOT_APPLICABLE | sim |
| CROSS_SPEC_ALIGNMENT_GATE | SKIP_NOT_APPLICABLE | sim |
| CONTRACT_BREAKING_CHANGE_GATE | SKIP_NOT_APPLICABLE | sim |
| TRANSFORMATION_FEASIBILITY_GATE | SKIP_NOT_APPLICABLE | sim |
| HTTP_RUNTIME_CONTRACT_GATE | SKIP_NOT_APPLICABLE | sim |
| ASYNCAPI_VALIDATION_GATE | SKIP_NOT_APPLICABLE | sim |
| ARAZZO_VALIDATION_GATE | SKIP_NOT_APPLICABLE | sim |
| UI_DOC_VALIDATION_GATE | FAIL | sim |
| DERIVED_DRIFT_GATE | FAIL | sim |
| ADVERSARIAL_ANALYSIS_GATE | SKIP_NOT_APPLICABLE | nao |
| FEATURE_READINESS_GATE | PASS | nao |
| VERSIONING_POLICY_GATE | SKIP_NOT_APPLICABLE | nao |
| PACT_PROVIDER_GATE | SKIP_NOT_APPLICABLE | nao |
| CODE_ARCHITECTURE_GATE | SKIP_NOT_APPLICABLE | nao |
| DEPLOY_READINESS_GATE | SKIP_NOT_APPLICABLE | nao |
| DATA_MIGRATION_GATE | SKIP_NOT_APPLICABLE | nao |
| MONITORING_POLICY_GATE | SKIP_NOT_APPLICABLE | nao |
| HANDOFF_COHERENCE_GATE | PASS | nao |
| MODULE_STATUS_COHERENCE_GATE | PASS | sim |
| CROSS_MODULE_BOUNDARY_GATE | SKIP_NOT_APPLICABLE | nao |
| READINESS_SUMMARY_GATE | FAIL | nao |
