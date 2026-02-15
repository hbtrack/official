# HB Track - Backend Scripts

Pasta centralizada para scripts operacionais, de manutenção e automação.

## Regra Determinística (MANDATÓRIA)
- **scripts/checks/**: Estritamente **READ-ONLY**. Scripts aqui não podem alterar banco de dados, arquivos ou estados do sistema.
- **scripts/fixes/**: Scripts que aplicam correções ou patches.
- **scripts/run/**: Ponto de entrada para automação (PowerShell).

## Estrutura
- **artifacts/**: Saídas de scripts (ignorados pelo git, exceto README).
- **diagnostics/**: Scripts de análise profunda (Read-only mais complexos).
- **generate/**: Geradores de código, hashes, schemas.
- **migrate/**: Migrações de dados e backfills.
- **ops/**: Operações de infraestrutura e banco (maintenance/refresh).
- **reset/**: Scripts para resetar ambiente ou serviços.
- **security/**: Auditorias e correções de segurança.
- **seeds/**: População de dados (dev/test/official).
- **temp/**: Scripts temporários e testes locais (ignorados pelo git).
