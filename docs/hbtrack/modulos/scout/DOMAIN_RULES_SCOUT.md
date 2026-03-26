---
module: "scout"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/scout.yaml"
schemas_ref: "../../../../contracts/schemas/scout/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_SCOUT.md

## Objetivo
Registrar as regras de negócio do módulo `scout`.

## Fonte do domínio
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `docs/hbtrack/modulos/scout/CANONICAL_EVENT_TAXONOMY_SCOUT.yaml`
- `contracts/schemas/scout/scout_event.schema.json`
- `docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md`

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-SCOUT-001 | `scout` é soberano de tags, eventos observacionais, clipes, coding schema e agregações táticas. | `ScoutEvent` | Authority matrix `scout` | Escopo observacional |
| DR-SCOUT-002 | `eventLabel`, `tagLabels` e `codingSchemaLabel` devem nascer de taxonomia explícita do módulo; não é permitido criar taxonomia tácita por histórico ou UI. | `ScoutEvent` | `CANONICAL_EVENT_TAXONOMY_SCOUT.yaml` | Taxonomia fechada |
| DR-SCOUT-003 | Todo evento de scout deve estar ancorado a `matchId`; `athleteUserId` e `teamId`, quando presentes, apenas refinam o contexto da observação. | `ScoutEvent` | Schema local | Contexto sem mudar soberania |
| DR-SCOUT-004 | `clipAssetRefs` referencia evidências externas do evento, mas o módulo `scout` não se torna dono do storage subjacente. | `ScoutEvent` | `SYSTEM_SCOPE.md` | Storage é integração, não domínio |
| DR-SCOUT-005 | `scout` não redefine placar oficial, regra da IHF ou estatística oficial de competição sem mapeamento explícito aprovado. | `ScoutEvent` | Authority matrix `must_not_infer` | Boundary com `matches`/`competitions` |

## Limites de inferência
- Não inferir taxonomia sem glossário/taxonomia canônica.
- Não tratar observação tática como fato oficial de súmula sem contrato em `matches`.
- Não mover credenciais, regras médicas ou autorização para `scout`.
