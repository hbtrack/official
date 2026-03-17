---
module: "analytics"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/analytics.yaml"
schemas_ref: "../../../../contracts/schemas/analytics/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_ANALYTICS.md

## Objetivo
Registrar as regras de negócio do módulo `analytics`.

## Fonte do domínio
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `contracts/schemas/analytics/analytics_snapshot.schema.json`
- `docs/hbtrack/modulos/analytics/INVARIANTS_ANALYTICS.md`
- Fontes técnico-científicas permitidas via authority matrix (`EHF`, `ACSM`) quando aplicável

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-ANL-001 | `analytics` é soberano apenas de métricas derivadas, filtros, janelas temporais, granularidade, projeções e semântica de refresh. | `AnalyticsSnapshot` | Authority matrix `analytics` | Não é dono do dado-fonte |
| DR-ANL-002 | Toda métrica exposta deve possuir definição canônica antes de virar contrato; benchmark ou dashboard isolado não cria KPI normativo. | `AnalyticsSnapshot` | Authority matrix `must_not_infer` | Bloqueia KPI inventado |
| DR-ANL-003 | `sourceModuleLabels` registra a proveniência do cálculo, sem transferir soberania do dado-fonte para `analytics`. | `AnalyticsSnapshot` | Schema local | Proveniência explícita |
| DR-ANL-004 | `timeWindowLabel`, `granularityLabel`, `projectionKey` e `refreshModeLabel` são parte do significado do snapshot e não podem ser implícitos. | `AnalyticsSnapshot` | Authority matrix `time_windows`, `granularity`, `refresh_semantics` | Reprodutibilidade |
| DR-ANL-005 | `analytics` pode orientar decisão, mas não reescreve regra de negócio de `training`, `medical`, `matches` ou qualquer módulo soberano. | `AnalyticsSnapshot` | Authority matrix `must_not_infer` | Derived ≠ source of truth |

## Limites de inferência
- Não inventar KPI sem definição canônica.
- Não misturar dado bruto protegido com insight derivado no mesmo contrato sem explicitação.
- Não reescrever regra de domínio a partir de visualização analítica.
