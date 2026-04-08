# Dashboard de Readiness - HB Track
> Gerado em 2026-04-08T06:08:34Z | run_id: `20260408T060834_f96126` | health: **100/100** | overall: **PASS**

## Modulos

| Modulo | Status | Superficies |
|---|---|---|
| users | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo, permissions, decision_ir |
| seasons | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo |
| teams | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo |
| training | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, state_model, permissions, errors, sport_science, ui_contract, arazzo, asyncapi, decision_ir |
| wellness | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, sport_science, asyncapi, arazzo |
| medical | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, sport_science |
| competitions | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo |
| matches | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo |
| scout | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo, permissions, decision_ir |
| exercises | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, permissions |
| analytics | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix |
| reports | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix |
| ai_ingestion | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo |
| identity_access | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, permissions, arazzo, asyncapi, decision_ir |
| audit | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo, permissions, decision_ir |
| notifications | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo |
| video | `implemented` | module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo, permissions, decision_ir |

## Gates

| Gate | Status | Blocking |
|---|---|---|
| AXIOM_INTEGRITY_GATE | PASS | sim |
| PATH_CANONICALITY_GATE | PASS | sim |
| REQUIRED_ARTIFACT_PRESENCE_GATE | PASS | sim |
| MODULE_DOC_CROSSREF_GATE | PASS | sim |
| API_NORMATIVE_DUPLICATION_GATE | PASS | nao |
| OWASP_API_CONTROL_MATRIX_GATE | PASS | sim |
| MODULE_SOURCE_AUTHORITY_MATRIX_GATE | PASS | sim |
| MODULE_REGISTRY_GATE | PASS | sim |
| BOUNDARY_USERS_IDENTITY_ACCESS_GATE | PASS | sim |
| WELLNESS_MEDICAL_BOUNDARY_GATE | PASS | sim |
| SCOUT_TAXONOMY_GATE | PASS | sim |
| ASYNC_REQUIRED_MODULE_GATE | PASS | sim |
| EXTERNAL_SOURCE_AUTHORITY_GATE | PASS | sim |
| PRE_CONTRACT_EVIDENCE_GATE | PASS | sim |
| SHADOW_AUTHORITY_GATE | PASS | sim |
| DECISION_IR_CONFORMANCE_GATE | PASS | sim |
| CANON_ALLOWLIST_GATE | PASS | sim |
| PLACEHOLDER_RESIDUE_GATE | PASS | sim |
| REF_HERMETICITY_GATE | PASS | sim |
| TOOLING_CONFIG_GATE | PASS | sim |
| OPENAPI_ROOT_STRUCTURE_GATE | PASS | sim |
| OPENAPI_ROOT_MODULE_SYNC_GATE | PASS | sim |
| OPENAPI_POLICY_RULESET_GATE | PASS | sim |
| JSON_SCHEMA_VALIDATION_GATE | PASS | sim |
| CROSS_SPEC_ALIGNMENT_GATE | PASS | sim |
| CONTRACT_BREAKING_CHANGE_GATE | PASS | sim |
| TRANSFORMATION_FEASIBILITY_GATE | PASS | sim |
| HTTP_RUNTIME_CONTRACT_GATE | SKIP_NOT_APPLICABLE | sim |
| ASYNCAPI_VALIDATION_GATE | PASS | sim |
| ARAZZO_VALIDATION_GATE | PASS | sim |
| SPECTRAL_LINTING_GATE | PASS | sim |
| ARAZZO_COMPLETENESS_GATE | PASS | sim |
| UI_DOC_VALIDATION_GATE | PASS | sim |
| DERIVED_DRIFT_GATE | PASS | sim |
| ADVERSARIAL_ANALYSIS_GATE | PASS | nao |
| FEATURE_READINESS_GATE | PASS | nao |
| VERSIONING_POLICY_GATE | PASS | nao |
| PACT_PROVIDER_GATE | SKIP_NOT_APPLICABLE | nao |
| CODE_ARCHITECTURE_GATE | PASS | nao |
| DEPLOY_READINESS_GATE | PASS | nao |
| DATA_MIGRATION_GATE | PASS | nao |
| MONITORING_POLICY_GATE | PASS | nao |
| HANDOFF_COHERENCE_GATE | PASS | sim |
| MODULE_STATUS_COHERENCE_GATE | PASS | sim |
| SURFACE_PROMOTION_COHERENCE_GATE | PASS | sim |
| CROSS_MODULE_BOUNDARY_GATE | PASS | nao |
| MODULE_DEPENDENCY_RESOLUTION_GATE | PASS | sim |
| WAIVER_VALIDITY_GATE | PASS | sim |
| READINESS_GENERATION_COMPATIBILITY_GATE | PASS | sim |
| READINESS_HUMAN_CONFIRMATION_GATE | SKIP_NOT_APPLICABLE | sim |
| FEATURE_COVERAGE_GATE | PASS | sim |
| LEGACY_CRITICAL_PATH_GATE | PASS | sim |
| WORKER_PROMPT_AUTHORITY_GATE | PASS | sim |
| DOMAIN_GLOSSARY_CONSISTENCY_GATE | PASS | nao |
| READINESS_SUMMARY_GATE | PASS | nao |
