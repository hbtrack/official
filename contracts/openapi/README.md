# contracts/openapi/

Fonte primária da verdade para a **interface HTTP pública** do HB Track.

## Estrutura

```
contracts/openapi/
  openapi.yaml              # Entrypoint canônico da spec (ler primeiro)
  paths/
    users.yaml              # Path items do módulo users
    seasons.yaml            # Path items do módulo seasons
    teams.yaml              # Path items do módulo teams
    training.yaml           # Path items do módulo training
    wellness.yaml           # Path items do módulo wellness
    medical.yaml            # Path items do módulo medical
    competitions.yaml       # Path items do módulo competitions
    matches.yaml            # Path items do módulo matches
    scout.yaml              # Path items do módulo scout
    exercises.yaml          # Path items do módulo exercises
    analytics.yaml          # Path items do módulo analytics
    reports.yaml            # Path items do módulo reports
    ai_ingestion.yaml       # Path items do módulo ai_ingestion
    identity_access.yaml    # Path items do módulo identity_access
    audit.yaml              # Path items do módulo audit
    notifications.yaml      # Path items do módulo notifications
  components/
    schemas/shared/         # Schemas HTTP-facing compartilhados entre módulos
    schemas/<module>/       # Schemas HTTP-facing específicos do módulo
    parameters/             # Parâmetros reutilizáveis (ex: pageSize, pageToken)
    responses/              # Respostas reutilizáveis
    requestBodies/          # Request bodies reutilizáveis
    securitySchemes/        # Esquemas de segurança (JWT Bearer)
    examples/               # Exemplos de payload
```

## Regras de uso

- **Soberania**: `contracts/openapi/openapi.yaml` é a única fonte de verdade para a interface HTTP. Nenhum código ou documento pode redefinir paths ou schemas sem alterar este contrato.
- **Um módulo por arquivo**: cada arquivo em `paths/` pertence a exatamente um módulo canônico.
- **Validação obrigatória**: toda alteração deve passar em `redocly lint contracts/openapi/openapi.yaml` antes de ser considerada válida.
- **Sem edição manual de derivados**: tipos e clients gerados a partir desta spec vivem em `generated/` e não são editados manualmente.

## Referências normativas

- Layout canônico: `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` seções 4 e 6
- SSOT de regras/templates/validações de API HTTP: `.contract_driven/templates/api/api_rules.yaml`
- Guia/ponteiros (API): `docs/_canon/API_CONVENTIONS.md`
- Modelo de erro HTTP: `docs/_canon/ERROR_MODEL.md`
- Ferramenta de validação: Redocly CLI (`redocly lint contracts/openapi/openapi.yaml`)
- Ferramenta de rulesets: Spectral (`spectral lint contracts/openapi/openapi.yaml --ruleset .spectral.yaml`)
