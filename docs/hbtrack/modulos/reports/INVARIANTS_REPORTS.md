---
module: "reports"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/reports.yaml"
schemas_ref: "../../../../contracts/schemas/reports/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_REPORTS.md

## Objetivo
Registrar invariantes do módulo `reports`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-RPT-001 | `id`, `ownerUserId` e `reportType` são obrigatórios em todo pedido de relatório. | `ReportJob` | `report_job.schema.json` | JSON Schema validation |
| INV-RPT-002 | `sourceMetricNames`, quando presentes, formam coleção sem duplicidade. | `ReportJob` | Schema local | `uniqueItems` + auditoria de payload |
| INV-RPT-003 | `requestedAt` é obrigatório e representa o instante canônico de solicitação do job. | `ReportJob` | Schema local | JSON Schema validation |
| INV-RPT-004 | Se `generatedArtifactRef` estiver preenchido, `retentionLabel` deve estar explicitado. | `ReportJob` | Regra operacional do módulo | Teste de contrato |

## Relação com outros documentos
- `docs/hbtrack/modulos/reports/DOMAIN_RULES_REPORTS.md`
- `contracts/schemas/reports/report_job.schema.json`
