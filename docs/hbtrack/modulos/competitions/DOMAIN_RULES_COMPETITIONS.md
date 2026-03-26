---
module: "competitions"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/competitions.yaml"
schemas_ref: "../../../../contracts/schemas/competitions/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_COMPETITIONS.md

## Objetivo
Registrar as regras de negócio do módulo `competitions`.

## Fonte do domínio
- `docs/_canon/HANDBALL_RULES_DOMAIN.md`
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `contracts/schemas/competitions/competition.schema.json`
- `docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md`

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-COMP-001 | `competitions` é soberano da competição, estágios, fases, inscrições e calendário competitivo. | `Competition` | Authority matrix `competition`, `stage`, `registration`, `calendar` | Semântica oficial do torneio |
| DR-COMP-002 | Toda competição pertence a uma temporada explícita via `seasonId`; competição sem contexto temporal é inválida como shape estável. | `Competition` | Schema local | Boundary com `seasons` |
| DR-COMP-003 | `registrationTeamIds` representa inscrição formal de equipes na competição e não pode ser inferido por participação histórica em partidas. | `Competition` | Authority matrix `registration` | Relação oficial |
| DR-COMP-004 | `stageLabels` descreve fases/etapas da competição segundo a semântica competitiva vigente; UI ou dashboard não criam novas fases por inferência. | `Competition` | IHF/CBHb quando aplicável | Fase é contrato |
| DR-COMP-005 | `standingsSummary` é projeção resumida da competição e não substitui a verdade oficial de partidas, scout ou arbitragem. | `Competition` | Boundary com `matches` e `scout` | Resumo não redefine fonte primária |

## Limites de inferência
- Não inferir taxonomia detalhada de scout neste módulo.
- Não derivar regra oficial de competição a partir de benchmark ou UI.
- Não mover scorekeeping oficial ou semântica médica para `competitions`.
