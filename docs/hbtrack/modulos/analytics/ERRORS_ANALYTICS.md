---
module: "analytics"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "errors"
error_model_ref: "../../../_canon/OPERATIONS.md"
problem_schema_ref: "../../../../contracts/openapi/components/schemas/shared/problem.yaml"
updated_at: "2026-03-20"
---

# ERRORS_ANALYTICS.md

> Media type canônico de erro: `application/problem+json` (RFC 7807).
> Shape: `contracts/openapi/components/schemas/shared/problem.yaml`.
> Este arquivo registra a matriz mínima de exceções críticas do módulo `analytics`.

## Erros de Query Analítica

| Código (type) | Situação | HTTP | Invariante/DR | Observação |
|---|---|---|---|---|
| `ANALYTICS_METRIC_KEY_UNSUPPORTED` | `metricKey` fora do catálogo soberano do módulo | 422 | DR-ANL-006, INV-ANL-005 | Detalha valores válidos no `detail` |
| `ANALYTICS_TIME_WINDOW_INVALID` | `timeWindow = CUSTOM` sem `dateFrom`/`dateTo`, ou janela custom inválida | 422 | INV-ANL-006 | Inclui combinação recebida no `detail` |
| `ANALYTICS_SCOPE_FILTER_CONFLICT` | `scope` conflita com o filtro estruturado (`TEAM`/`ATHLETE` vs `teamIds`/`athleteIds`) | 409 | DR-ANL-007, INV-ANL-007 | Não há fallback implícito |
| `ANALYTICS_QUERY_SOURCE_MISMATCH` | `sourceModules` incompatível com os sinais canônicos suportados pela query | 422 | DR-ANL-009 | Boundary `TRAINING`/`WELLNESS` somente |

## Erros de Snapshot

| Código (type) | Situação | HTTP | Invariante/DR | Observação |
|---|---|---|---|---|
| `ANALYTICS_SNAPSHOT_DUPLICATE` | Já existe snapshot com mesma identidade canônica (`metricKey`, `sourceModuleLabels`, `timeWindowLabel`, `granularityLabel`, `projectionKey`) | 409 | DR-ANL-004, DR-ANL-006 | Evita duplicidade silenciosa |

## Erros de Autorização e Execução

| Código (type) | Situação | HTTP | Invariante/DR | Observação |
|---|---|---|---|---|
| `ANALYTICS_FORBIDDEN` | Role insuficiente para a operação | 403 | `PERMISSIONS_ANALYTICS.md` | Segue policy de `identity_access` |
| `ANALYTICS_INTERNAL_ERROR` | Falha interna ao computar ou materializar resultado derivado | 500 | `.contract_driven/templates/api/api_rules.yaml` | Resposta obrigatória em toda operação protegida |
