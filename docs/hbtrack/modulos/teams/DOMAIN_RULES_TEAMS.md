---
module: "teams"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/teams.yaml"
schemas_ref: "../../../../contracts/schemas/teams/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_TEAMS.md

## Objetivo
Registrar as regras de negócio do módulo `teams`.

## Fonte do domínio
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `contracts/schemas/teams/team.schema.json`
- `docs/hbtrack/modulos/teams/INVARIANTS_TEAMS.md`

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-TEAM-001 | `teams` é soberano do elenco, comissão esportiva, categoria competitiva e associação da equipe à temporada. | `Team` | Authority matrix `roster`, `sports_staff`, `season_association`, `category` | Fonte de verdade de composição |
| DR-TEAM-002 | `athleteIds` e `staffUserIds` representam vínculos explícitos; presença em treino, scout ou login não cria vínculo de equipe automaticamente. | `Team` | Authority matrix `athlete_staff_links` | Sem inferência operacional |
| DR-TEAM-003 | `categoryLabel` descreve categoria esportiva/competitiva e não pode ser usada como papel de autorização técnica. | `Team` | `SYSTEM_SCOPE.md` | Boundary com `identity_access` |
| DR-TEAM-004 | `seasonId` contextualiza a composição da equipe para planejamento, competição e analytics, sem transferir a soberania da temporada para `teams`. | `Team` | Schema local + `seasons` boundary | Referência, não duplicação |
| DR-TEAM-005 | `rosterNotes` é campo operacional de contexto e não pode carregar credenciais, dados clínicos detalhados ou ownership de perfil pessoal. | `Team` | Authority matrix `must_not_infer` | Limita uso de texto livre |

## Limites de inferência
- Não inferir credenciais, sessão ou política de segurança em `teams`.
- Não transferir para `teams` a soberania de perfil pessoal, prontuário médico ou estado de treino.
- Não deduzir elenco oficial a partir de attendance, lineups ou eventos históricos sem referência explícita.

## Source Graph
- Entidades: [graph/entities.yaml](graph/entities.yaml)
- Endpoints: [graph/endpoints.yaml](graph/endpoints.yaml)
- Erros: [graph/errors.yaml](graph/errors.yaml)
- Obrigações: [graph/test_obligations.yaml](graph/test_obligations.yaml)
