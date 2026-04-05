---
module: "reports"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/reports.yaml"
schemas_ref: "../../../../contracts/schemas/reports/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_REPORTS.md

## Objetivo
Registrar as regras de negócio do módulo `reports`.

## Fonte do domínio
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `contracts/schemas/reports/report_job.schema.json`
- `docs/hbtrack/modulos/reports/INVARIANTS_REPORTS.md`
- `docs/hbtrack/modulos/reports/graph/entity_graph.yaml`
- `docs/hbtrack/modulos/reports/graph/errors.yaml`
- Artefatos assíncronos do módulo quando aplicável (`Arazzo`)

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-RPT-001 | `reports` é soberano do pedido de relatório, parâmetros, formato, owner, retenção e referência ao artefato gerado. | `ReportJob` | Authority matrix `reports` | Escopo de job e entrega |
| DR-RPT-002 | Conteúdo analítico de um relatório deve derivar de projeções, métricas ou datasets já contratados em módulos soberanos; `reports` não inventa conteúdo analítico novo. | `ReportJob` | Authority matrix `must_not_infer` | Boundary com `analytics` e módulos-fonte |
| DR-RPT-003 | `parameterSummary` deve explicitar o recorte operacional do relatório; parâmetro implícito em UI não pode virar contrato silencioso. | `ReportJob` | Schema local | Reprodutibilidade |
| DR-RPT-004 | `generatedArtifactRef` referencia artefato externo já produzido e não transfere para `reports` a soberania do storage. | `ReportJob` | `SYSTEM_SCOPE.md` | Adapter externo encapsulado |
| DR-RPT-005 | Geração de relatório potencialmente custosa ou demorada é tratada como processo assíncrono e auditável. | `ReportJob` | Authority matrix `ARAZZO_WHEN_ASYNC_GENERATION` | Sem job invisível |

## Limites de inferência
- Não gerar conteúdo fora dos limites de acesso dos módulos-fonte.
- Não inferir insight analítico apenas do nome do relatório.
- Não usar `reports` para contornar retenção, auditoria ou proteção de dados.

## Âncoras estruturadas
- A entidade soberana e seus campos mapeados para runtime estão em `docs/hbtrack/modulos/reports/graph/entity_graph.yaml`.
- O mapa de erros transport/domain do módulo está em `docs/hbtrack/modulos/reports/graph/errors.yaml`.
