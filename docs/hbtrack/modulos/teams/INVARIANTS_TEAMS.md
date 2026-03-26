---
module: "teams"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/teams.yaml"
schemas_ref: "../../../../contracts/schemas/teams/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_TEAMS.md

## Objetivo
Registrar invariantes do módulo `teams`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-TEAM-001 | `id`, `organizationId`, `name` e `categoryLabel` são obrigatórios em toda `Team`. | `Team` | `team.schema.json` | JSON Schema validation |
| INV-TEAM-002 | `athleteIds` e `staffUserIds` são listas sem duplicidade. | `Team` | Schema local | `uniqueItems` + auditoria de payload |
| INV-TEAM-003 | `seasonId`, quando presente, referencia o contexto sazonal da equipe e não substitui a soberania de `seasons`. | `Team` | Boundary `teams`/`seasons` | FK/integração + revisão de domínio |
| INV-TEAM-004 | `teams` não pode conter credenciais, sessão, MFA, prontuário clínico ou ownership de perfil pessoal. | `Team` | Authority matrix `must_not_infer` | Gates de boundary + revisão de contrato |

## Relação com outros documentos
- `docs/hbtrack/modulos/teams/DOMAIN_RULES_TEAMS.md`
- `contracts/schemas/teams/team.schema.json`
