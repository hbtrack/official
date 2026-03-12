# contracts/workflows/

Fonte primária da verdade para **orquestração multi-step** (Arazzo) no HB Track.

## Estrutura

```
contracts/workflows/
  _global/          # Workflows cross-module (envolvem mais de um módulo)
  users/            # Workflows do módulo users
  seasons/          # Workflows do módulo seasons
  teams/            # Workflows do módulo teams
  training/         # Workflows do módulo training
  wellness/         # Workflows do módulo wellness
  medical/          # Workflows do módulo medical
  competitions/     # Workflows do módulo competitions
  matches/          # Workflows do módulo matches
  scout/            # Workflows do módulo scout
  exercises/        # Workflows do módulo exercises
  analytics/        # Workflows do módulo analytics
  reports/          # Workflows do módulo reports
  ai_ingestion/     # Workflows do módulo ai_ingestion
  identity_access/  # Workflows do módulo identity_access
  audit/            # Workflows do módulo audit
  notifications/    # Workflows do módulo notifications
```

## Regras de uso

- **Soberania**: `contracts/workflows/**/*.arazzo.yaml` é a fonte de verdade para orquestração multi-step.
- **Condição de criação**: workflows Arazzo só devem existir quando houver orquestração multi-step real (2+ chamadas de API encadeadas onde o output de A é input obrigatório de B). Não criar workflows placeholder.
- **Naming**: arquivos devem descrever o use case, não o detalhe de implementação. Formato: `<use_case>.arazzo.yaml` em `lower_snake_case`.
- **Steps linkados**: cada step de um workflow deve linkar para uma operação existente em `contracts/openapi/`.
- **Validação obrigatória**: todo workflow deve ser validável por um Arazzo validator antes de ser considerado pronto.

## Referências normativas

- Layout canônico: `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` seções 4 e 8
- Matriz de aplicabilidade: `.contract_driven/CONTRACT_SYSTEM_RULES.md` seção 11.6
- Gates e ferramentas de validação: `docs/_canon/CI_CONTRACT_GATES.md`
