---
module: "users"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/users.yaml"
schemas_ref: "../../../../contracts/schemas/users/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_USERS.md

## Objetivo
Registrar as regras de negócio do módulo `users`.

## Fonte do domínio
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `contracts/schemas/users/user_profile.schema.json`
- `docs/hbtrack/modulos/users/INVARIANTS_USERS.md`

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-USR-001 | `users` é soberano de perfil, vínculos esportivos e preferências do usuário. Credenciais, sessão, MFA, JWT e refresh token pertencem exclusivamente a `identity_access`. | `UserProfile` | Authority matrix (`users`, `identity_access`) | Boundary obrigatório |
| DR-USR-002 | `roleLabel` representa papel funcional mapeado aos 5 atores canônicos do sistema; permissões técnicas adicionais são concedidas por `identity_access`, nunca pelo perfil. | `UserProfile` | `SYSTEM_SCOPE.md` | Papel esportivo não redefine RBAC técnico |
| DR-USR-003 | `teamIds` e `seasonIds` materializam vínculos explícitos do usuário com equipes e temporadas; esses vínculos não podem ser inferidos de sessão, attendance ou analytics. | `UserProfile` | Authority matrix `team_season_relationships` | Relação contratada, não heurística |
| DR-USR-004 | `positionLabel` e demais atributos esportivos descrevem contexto esportivo do usuário e nunca autorização de acesso. | `UserProfile` | `SYSTEM_SCOPE.md` + boundary gate | Evita drift entre perfil e authz |
| DR-USR-005 | `preferredLanguage` e `preferenceTags` são preferências operacionais do usuário e não podem carregar estado de segurança, consentimento técnico ou credenciais. | `UserProfile` | Schema local | Preferência não substitui policy |

## Limites de inferência
- Não inferir `password_policy`, `session`, `mfa`, `jwt`, `oauth` ou qualquer regra de autenticação neste módulo.
- Não deduzir vínculo esportivo a partir de UI, login recente ou histórico operacional sem campo contratual.
- Não usar `roleLabel` como atalho para autorização técnica fora de `identity_access`.

## Source Graph
- Entidades: [graph/entity_graph.yaml](graph/entity_graph.yaml)
- Endpoints: [graph/endpoints.yaml](graph/endpoints.yaml)
- Erros: [graph/errors.yaml](graph/errors.yaml)
- Obrigações: [graph/test_obligations.yaml](graph/test_obligations.yaml)
