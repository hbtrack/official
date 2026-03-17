---
module: "analytics"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/analytics.yaml"
schemas_ref: "../../../../contracts/schemas/analytics/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_ANALYTICS.md

## Objetivo
Registrar invariantes do módulo `analytics`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-ANL-001 | `id`, `metricName` e `computedAt` são obrigatórios em todo snapshot derivado. | `AnalyticsSnapshot` | `analytics_snapshot.schema.json` | JSON Schema validation |
| INV-ANL-002 | `sourceModuleLabels` é uma coleção sem duplicidade e documenta proveniência do cálculo. | `AnalyticsSnapshot` | Schema local | `uniqueItems` + revisão de domínio |
| INV-ANL-003 | Nenhum KPI pode ser exposto sem definição canônica verificável; benchmark ou visualização isolada não cria métrica normativa. | `AnalyticsSnapshot` | Authority matrix `must_not_infer` | Revisão de contrato + governança de métricas |
| INV-ANL-004 | `analytics` não substitui o dado-fonte bruto nem reescreve regras de negócio de módulos soberanos. | `AnalyticsSnapshot` | Authority matrix `must_not_infer` | Cross-spec alignment |

## Relação com outros documentos
- `docs/hbtrack/modulos/analytics/DOMAIN_RULES_ANALYTICS.md`
- `contracts/schemas/analytics/analytics_snapshot.schema.json`
