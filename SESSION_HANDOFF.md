---
data_ultima_sessao: "2026-04-29"
branch_ativo: chore/openapi-lint-toolchain-scripts
modo_operacao: CDD
ci_status: FAIL
modulo_foco: openapi
fase_roadmap: 1
task_type: tooling_config
boot_profile_id: contract_execution
task_id: OPENAPI_LINT_TOOLCHAIN
resultado: PENDENTE
proxima_acao_permitida: "Regenerar _reports/session_start.json e compiled_context para eliminar HANDOFF_COHERENCE_GATE e CONTEXT_BUNDLE_FRESHNESS_GATE no CI; em seguida reexecutar Contract Gates."
bloqueios_ativos:
  - "HANDOFF_COHERENCE_GATE"
  - "CONTEXT_BUNDLE_FRESHNESS_GATE"
evidence_paths:
  - "_reports/session_start.json"
  - "package.json"
  - ".spectral.yaml"
  - "redocly.yaml"
  - "contracts/openapi/openapi.yaml"
  - "contracts/schemas/analytics/analytics_query_request.schema.json"
  - "contracts/schemas/analytics/analytics_query_response.schema.json"
  - "contracts/schemas/analytics/analytics_snapshot.schema.json"
---
# SESSION HANDOFF — OPENAPI_LINT_TOOLCHAIN

## Estado Geral
**Data:** 2026-04-29 | **Branch:** chore/openapi-lint-toolchain-scripts | **CI:** FAIL
**Modo:** CDD | **task_type:** tooling_config | **boot_profile:** contract_execution
**Módulo foco:** openapi | **Fase ROADMAP:** 1 | **task_id:** OPENAPI_LINT_TOOLCHAIN | **Resultado:** PENDENTE

## O que foi feito
- Scripts canônicos adicionados ao `package.json`: `openapi:redocly`, `openapi:bundle`, `openapi:spectral`, `contracts:lint`
- `openapi:spectral` tornado auto-suficiente: invoca `openapi:bundle` antes de rodar o lint
- `_reports/openapi/` adicionado ao `.gitignore` para prevenir commit acidental do bundle transitório
- Spectral configurado para rodar contra o bundle gerado pelo Redocly (não apenas o root OpenAPI com `$ref`)
- Tags ausentes/fora do registry global corrigidas em training/exercises
- `$id` canônicos restaurados nos schemas soberanos de analytics e nos espelhos em `generated/contracts/schemas/analytics`

## Evidências
- `package.json` — scripts `openapi:redocly`, `openapi:bundle`, `openapi:spectral`, `contracts:lint`
- `.spectral.yaml` — ruleset Spectral ativo
- `redocly.yaml` — configuração Redocly ativa
- `contracts/openapi/openapi.yaml` — root OpenAPI validado
- `contracts/schemas/analytics/analytics_query_request.schema.json` — `$id` canônico restaurado
- `contracts/schemas/analytics/analytics_query_response.schema.json` — `$id` canônico restaurado
- `contracts/schemas/analytics/analytics_snapshot.schema.json` — `$id` canônico restaurado
- `_reports/session_start.json` — ainda precisa ser regenerado para refletir esta trilha OpenAPI

## Gates OpenAPI observados como PASS no CI anterior
- `TOOLING_CONFIG_GATE`
- `OPENAPI_ROOT_STRUCTURE_GATE`
- `OPENAPI_ROOT_MODULE_SYNC_GATE`
- `OPENAPI_POLICY_RULESET_GATE`
- `JSON_SCHEMA_VALIDATION_GATE`
- `SPECTRAL_LINTING_GATE`

## Bloqueios ativos no CI anterior
- `HANDOFF_COHERENCE_GATE` — `_reports/session_start.json` ainda indicava `module_focus=notifications`, divergindo do handoff OpenAPI
- `CONTEXT_BUNDLE_FRESHNESS_GATE` — context bundles stale para analytics, exercises e training
- `READINESS_SUMMARY_GATE` — consequência dos gates bloqueantes acima

## Próxima ação permitida
Regenerar `_reports/session_start.json` e os context bundles (`compiled_context/analytics/FT-038.json`, `compiled_context/exercises/FT-037.json`, `compiled_context/training/FT-001.json` e demais drifts relatados) usando o pipeline canônico; depois reexecutar `python3 scripts/hb validate --profile ci` e atualizar este handoff para `DONE` somente quando o CI estiver verde.
