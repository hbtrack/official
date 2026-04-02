---
module: "analytics"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/analytics.yaml"
schemas_ref: "../../../../contracts/schemas/analytics/"
type: "domain-rules"
updated: "2026-03-20"
---

# DOMAIN_RULES_ANALYTICS.md

## Objetivo
Registrar as regras de negócio do módulo `analytics`.

## Fonte do domínio
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `contracts/schemas/analytics/analytics_snapshot.schema.json`
- `contracts/schemas/analytics/analytics_metric_key.schema.json`
- `contracts/schemas/analytics/analytics_query_request.schema.json`
- `contracts/schemas/analytics/analytics_query_response.schema.json`
- `docs/hbtrack/modulos/analytics/INVARIANTS_ANALYTICS.md`
- `docs/hbtrack/modulos/analytics/ERRORS_ANALYTICS.md`
- `docs/hbtrack/modulos/analytics/graph/entities.yaml`
- `docs/hbtrack/modulos/analytics/graph/errors.yaml`
- Fontes técnico-científicas permitidas via authority matrix (`EHF`, `ACSM`) quando aplicável

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-ANL-001 | `analytics` é soberano apenas de métricas derivadas, filtros, janelas temporais, granularidade, projeções e semântica de refresh. | `AnalyticsSnapshot` | Authority matrix `analytics` | Não é dono do dado-fonte |
| DR-ANL-002 | Toda métrica exposta deve possuir definição canônica antes de virar contrato; benchmark ou dashboard isolado não cria KPI normativo. | `AnalyticsSnapshot` | Authority matrix `must_not_infer` | Bloqueia KPI inventado |
| DR-ANL-003 | `sourceModuleLabels` registra a proveniência do cálculo, sem transferir soberania do dado-fonte para `analytics`. | `AnalyticsSnapshot` | Schema local | Proveniência explícita |
| DR-ANL-004 | `timeWindowLabel`, `granularityLabel`, `projectionKey` e `refreshModeLabel` são parte do significado do snapshot e não podem ser implícitos. | `AnalyticsSnapshot` | Authority matrix `time_windows`, `granularity`, `refresh_semantics` | Reprodutibilidade |
| DR-ANL-005 | `analytics` pode orientar decisão, mas não reescreve regra de negócio de `training`, `medical`, `matches` ou qualquer módulo soberano. | `AnalyticsSnapshot` | Authority matrix `must_not_infer` | Derived ≠ source of truth |
| DR-ANL-006 | As métricas canônicas expostas por `analytics` nesta fase usam os transport labels `READINESS_SCORE`, `DROPOUT_RISK_SIGNAL` e `ENGAGEMENT_SIGNAL`. Nova métrica exige artefato soberano antes de entrar em contrato. | `AnalyticsSnapshot`, `AnalyticsQuery` | TRAIN-DEC-046 + schema local | Catálogo fechado |
| DR-ANL-007 | `/analytics/query` aceita apenas filtros estruturados por escopo (`teamIds` ou `athleteIds`). Expressões textuais livres são proibidas. | `AnalyticsQueryRequest` | Schema local | Sem DSL implícita |
| DR-ANL-008 | `/analytics/query` retorna envelope fixo de linhas. Dimensões não aplicáveis ficam `null`; não existem colunas ad hoc por métrica. | `AnalyticsQueryResponse` | Schema local | Resultado determinístico |
| DR-ANL-009 | Os sinais canônicos atuais de `analytics` consultáveis via query aceitam apenas `TRAINING` e `WELLNESS` como labels de módulo-fonte; combinação fora desse boundary é inválida. | `AnalyticsQuery` | TRAIN-DEC-046 | Boundary fechado |

## Limites de inferência
- Não inventar KPI sem definição canônica.
- Não misturar dado bruto protegido com insight derivado no mesmo contrato sem explicitação.
- Não reescrever regra de domínio a partir de visualização analítica.
- Não aceitar linguagem de query aberta quando o contrato não define gramática soberana.

## Âncoras estruturadas
- As entidades soberanas e seus campos mapeados para runtime estão em `docs/hbtrack/modulos/analytics/graph/entities.yaml`.
- O mapa mínimo de erros transport/domain do módulo está em `docs/hbtrack/modulos/analytics/graph/errors.yaml`.
