---
module: "seasons"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/seasons.yaml"
schemas_ref: "../../../../contracts/schemas/seasons/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_SEASONS.md

## Objetivo
Registrar as regras de negócio do módulo `seasons`.

## Fonte do domínio
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `contracts/schemas/seasons/season.schema.json`
- `docs/hbtrack/modulos/seasons/INVARIANTS_SEASONS.md`

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-SEAS-001 | `seasons` é soberano do ciclo esportivo, da janela oficial de calendário e da nomenclatura da temporada. | `Season` | Authority matrix `sport_cycle`, `periods`, `phases` | Base temporal para equipes e competições |
| DR-SEAS-002 | `phaseLabels` representam fases explícitas da temporada e não podem ser deduzidas automaticamente de resultados de partidas ou status de competição. | `Season` | Schema local + authority matrix | Fase é contrato, não heurística |
| DR-SEAS-003 | Relações com `competitionIds` e `teamIds` são associações canônicas da temporada e devem ser registradas explicitamente. | `Season` | Authority matrix `competition_team_relationships` | Sem vínculo implícito por histórico |
| DR-SEAS-004 | `sportCycleLabel` descreve o ciclo competitivo/operacional da temporada e não substitui regras oficiais de competição nem semântica médica. | `Season` | Authority matrix `must_not_infer` | Boundary com `competitions` e `medical` |
| DR-SEAS-005 | A temporada funciona como contêiner temporal para planejamento e competição, mas não é dona de scorekeeping, scout ou autorização. | `Season` | `SYSTEM_SCOPE.md` | Limite explícito de módulo |

## Limites de inferência
- Não inferir detalhes de súmula, placar ou arbitragem neste módulo.
- Não inferir restrição clínica, readiness ou autorização de acesso a partir da temporada.
- Não promover fase derivada de UI ou dashboard a regra de domínio.

## Source Graph
- Entidades: [graph/entity_graph.yaml](graph/entity_graph.yaml)
- Endpoints: [graph/endpoints.yaml](graph/endpoints.yaml)
- Erros: [graph/errors.yaml](graph/errors.yaml)
- Obrigações: [graph/test_obligations.yaml](graph/test_obligations.yaml)
