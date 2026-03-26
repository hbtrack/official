---
module: "ai_ingestion"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/ai_ingestion.yaml"
schemas_ref: "../../../../contracts/schemas/ai_ingestion/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_AI_INGESTION.md

## Objetivo
Registrar invariantes do módulo `ai_ingestion`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-ING-001 | `id`, `sourceLabel`, `ingestionMode` e `receivedAt` são obrigatórios em todo job de ingestão. | `IngestionJob` | `ingestion_job.schema.json` | JSON Schema validation |
| INV-ING-002 | Se `completedAt` estiver presente, então `completedAt >= receivedAt`. | `IngestionJob` | Regra temporal do módulo | Teste de contrato |
| INV-ING-003 | Integração automatizada com normalização exige `payloadSchemaRef` e `mappingProfile` explícitos. | `IngestionJob` | Authority matrix `must_not_infer` | Revisão de integração |
| INV-ING-004 | Fatos suscetíveis a replay ou redelivery devem portar `idempotencyKey` estável. | `IngestionJob` | Authority matrix `idempotency` | Teste de reprocessamento seguro |
| INV-ING-005 | `ai_ingestion` não pode se declarar fonte final de verdade do dado de negócio ingerido. | `IngestionJob` | Authority matrix `must_not_infer` | Revisão de boundaries |

## Relação com outros documentos
- `docs/hbtrack/modulos/ai_ingestion/DOMAIN_RULES_AI_INGESTION.md`
- `contracts/schemas/ai_ingestion/ingestion_job.schema.json`
