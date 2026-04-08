---
module: "ai_ingestion"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/ai_ingestion.yaml"
schemas_ref: "../../../../contracts/schemas/ai_ingestion/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_AI_INGESTION.md

## Objetivo
Registrar as regras de negócio do módulo `ai_ingestion`.

## Fonte do domínio
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `contracts/schemas/ai_ingestion/ingestion_job.schema.json`
- `docs/hbtrack/modulos/ai_ingestion/INVARIANTS_AI_INGESTION.md`
- `docs/hbtrack/modulos/ai_ingestion/graph/entity_graph.yaml`
- `docs/hbtrack/modulos/ai_ingestion/graph/endpoints.yaml`
- `docs/hbtrack/modulos/ai_ingestion/graph/errors.yaml`
- Artefatos assíncronos do módulo (`AsyncAPI`) quando aplicável

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-ING-001 | `ai_ingestion` é soberano do intake de dados externos: fonte, modo de ingestão, schema de entrada, mapeamento explícito, binding de execução e idempotência. | `IngestionJob` | Authority matrix `ai_ingestion` | Camada de entrada externa |
| DR-ING-002 | Normalização de dados externos exige `payloadSchemaRef` e `mappingProfile` explícitos; parser implícito ou transformação silenciosa é proibido. | `IngestionJob` | Authority matrix `must_not_infer` | Sem magia de integração |
| DR-ING-003 | `receivedAt` registra o momento de entrada do fato externo; `completedAt` registra o término do processamento interno. Os dois tempos não podem ser colapsados. | `IngestionJob` | Schema local | Preserva causalidade |
| DR-ING-004 | `idempotencyKey` é o mecanismo canônico para replay seguro e deduplicação de fatos ingeridos. | `IngestionJob` | Authority matrix `idempotency` | Determinismo operacional |
| DR-ING-005 | `ai_ingestion` não é dono do dado final de negócio; após normalização, a soberania do registro pertence ao módulo de destino. | `IngestionJob` | Authority matrix `must_not_infer` | Boundary com módulos consumidores |

## Limites de inferência
- Não deduzir semântica final do domínio a partir de prompt ou payload não mapeado.
- Não normalizar silenciosamente campos externos sem contrato de mapeamento.
- Não usar `ai_ingestion` como storage definitivo de dado de negócio.
