---
module: "matches"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/matches.yaml"
schemas_ref: "../../../../contracts/schemas/matches/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_MATCHES.md

## Objetivo
Registrar as regras de negócio do módulo `matches`.

## Fonte do domínio
- `docs/_canon/HANDBALL_RULES_DOMAIN.md`
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `contracts/schemas/matches/match.schema.json`
- `docs/hbtrack/modulos/matches/INVARIANTS_MATCHES.md`

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-MATCH-001 | `matches` é soberano do registro oficial da partida: vínculo com competição, mandante/visitante, placar, súmula de incidentes e arbitragem. | `Match` | Authority matrix `match`, `score`, `official_incidents`, `refereeing` | Fonte oficial do jogo |
| DR-MATCH-002 | `homeTeamId` e `awayTeamId` representam lados oficiais distintos da partida e não podem ser colapsados nem deduzidos por conveniência de UI. | `Match` | Semântica do módulo | Estrutura básica da partida |
| DR-MATCH-003 | `lineupUserIds` materializa elenco escalado para a partida; participação observada em scout não substitui lineup oficial. | `Match` | Authority matrix `lineup` | Boundary com `scout` |
| DR-MATCH-004 | `scheduledAt`, `startedAt` e `endedAt` registram o ciclo temporal da partida; `startedAt`/`endedAt` não podem ser usados para reclassificar regras de competição fora de `competitions`. | `Match` | Schema local | Boundary temporal |
| DR-MATCH-005 | Eventos observacionais, taxonomia tática e clipping pertencem a `scout`; `matches` só mantém fatos oficiais contratados. | `Match`, `ScoutEvent` | Boundary `matches`/`scout` | Evita mistura de camadas |

## Limites de inferência
- Não inferir taxonomia tática completa sem glossário próprio de `scout`.
- Não mover credenciais, regra médica ou autorização para `matches`.
- Não usar benchmark externo como norma oficial sem mapeamento explícito.
