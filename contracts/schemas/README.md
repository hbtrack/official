# contracts/schemas/

Fonte primária da verdade para **shapes de dados reutilizáveis** de domínio no HB Track.

## Estrutura

```
contracts/schemas/
  shared/           # Shapes reutilizadas entre múltiplos módulos
  users/            # Shapes de domínio do módulo users
  seasons/          # Shapes de domínio do módulo seasons
  teams/            # Shapes de domínio do módulo teams
  training/         # Shapes de domínio do módulo training
  wellness/         # Shapes de domínio do módulo wellness
  medical/          # Shapes de domínio do módulo medical
  competitions/     # Shapes de domínio do módulo competitions
  matches/          # Shapes de domínio do módulo matches
  scout/            # Shapes de domínio do módulo scout
  exercises/        # Shapes de domínio do módulo exercises
  analytics/        # Shapes de domínio do módulo analytics
  reports/          # Shapes de domínio do módulo reports
  ai_ingestion/     # Shapes de domínio do módulo ai_ingestion
  identity_access/  # Shapes de domínio do módulo identity_access
  audit/            # Shapes de domínio do módulo audit
  notifications/    # Shapes de domínio do módulo notifications
```

## Regras de uso

- **Soberania**: `contracts/schemas/<module>/*.schema.json` é a fonte de verdade para shapes de dados de domínio. Schemas HTTP-facing específicos de request/response vivem em `contracts/openapi/components/schemas/`.
- **Naming**: arquivos devem terminar em `.schema.json` e seguir o padrão `<entity>.schema.json` em `lower_snake_case`.
- **Escopo por módulo**: schemas de domínio de um módulo não devem ser colocados na pasta de outro módulo.
- **Shared**: shapes reutilizadas entre módulos vão em `shared/`.
- **Validação obrigatória**: todo schema deve ser validável por um JSON Schema validator (ex: AJV) antes de ser considerado pronto.

## Referências normativas

- Layout canônico: `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` seções 4 e 7
- Convenções de dados: `docs/_canon/DATA_CONVENTIONS.md`
- Ferramenta de validação: AJV (`ajv compile -s contracts/schemas/<module>/*.schema.json`)