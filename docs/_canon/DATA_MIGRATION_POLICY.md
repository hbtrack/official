# DATA_MIGRATION_POLICY.md
> Documento normativo — SSOT para estratégia de migração de dados do HB Track.
> Versão: 1.0.0 | Status: active | Criado: 2026-03-17
> Decisão: ADR-028 | Stack: Alembic (Python/SQLAlchemy 2.x) + PostgreSQL 16

## 1. Princípio

Qualquer mudança em schema que afete dados persistidos **requer migration script**.
Nenhuma migration pode ser aplicada em produção sem ser validada em staging primeiro.

O contrato de dados segue a mesma lógica do contrato de API: muda o schema → muda a migration → revisão obrigatória.

## 2. Regras Obrigatórias

| # | Regra | Consequência se violada |
|---|---|---|
| R1 | Toda mudança em `contracts/schemas/` que **adiciona campo obrigatório** → migration obrigatória | DATA_MIGRATION_GATE → FAIL |
| R2 | Toda mudança em `contracts/schemas/` que **remove campo** → migration + período de deprecation mínimo de 30 dias | DATA_MIGRATION_GATE → FAIL |
| R3 | Toda migration **deve ser reversível** (down migration obrigatória) | DATA_MIGRATION_GATE → FAIL |
| R4 | Migrations vivem em `migrations/<MODULE>/<timestamp>_<description>.py` | PATH_CANONICALITY_GATE → FAIL |
| R5 | Nenhuma migration é aplicada diretamente em produção sem passar por staging | Bloqueio no deploy pipeline |
| R6 | Migration com `--sql` mode deve ser revisada antes de aplicar (DDL explícito) | Revisão manual obrigatória |

## 3. Estrutura de Diretórios

```
migrations/
  alembic.ini          ← configuração global do Alembic
  env.py               ← Alembic env (aponta para DATABASE_URL)
  script.py.mako       ← template de migration
  users/
    versions/
      20260317_001_create_users_table.py
  training/
    versions/
      20260317_001_create_training_sessions_table.py
  seasons/
    versions/
  teams/
    versions/
  wellness/
    versions/
  medical/
    versions/
  ...
```

## 4. Formato de Migration

Cada arquivo de migration deve seguir o padrão:

```python
"""<description>

Revision ID: <auto>
Revises: <previous>
Create Date: YYYY-MM-DD HH:MM:SS
Module: <module>
Contract ref: contracts/schemas/<module>/
"""

from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Operações de upgrade (aplicar mudança)
    pass

def downgrade() -> None:
    # Operações de downgrade (reverter mudança) — OBRIGATÓRIO
    pass
```

## 5. Ciclo de Vida de uma Migration

```
[mudança em contracts/schemas/]
    │
    ▼
[DATA_MIGRATION_GATE verifica se migration existe]
    │ MISSING → FAIL
    ▼
[migration criada em migrations/<MODULE>/versions/]
    │
    ▼
[alembic upgrade head em staging]
    │ FAIL → rollback (alembic downgrade -1)
    ▼
[validação em staging — testes de integração]
    │ PASS
    ▼
[aprovação humana no deploy pipeline]
    │
    ▼
[alembic upgrade head em produção]
    │ FAIL → rollback automático (alembic downgrade -1)
    ▼
[health check → OK]
```

## 6. Comandos Úteis

```bash
# Criar nova migration
alembic revision --autogenerate -m "add_field_x_to_training_sessions" --rev-id "20260317_002"

# Aplicar migrations pendentes
alembic upgrade head

# Reverter última migration
alembic downgrade -1

# Ver histórico
alembic history --verbose

# Ver estado atual
alembic current
```

## 7. Política de Deprecation

Quando um campo é **removido** de um schema:

1. Marcar como `deprecated: true` no JSON Schema (`contracts/schemas/<module>/`)
2. Manter o campo funcional por **mínimo 30 dias** (um ciclo de release)
3. Notificar consumers via SESSION_HANDOFF.md e FEATURE_REGISTRY.yaml
4. Após prazo: criar migration de remoção + down migration de restauração

## 8. Gate

`DATA_MIGRATION_GATE` (order 15H) verifica:
- Se existir mudança em `contracts/schemas/` sem migration correspondente → FAIL
- Se migration existir mas sem `downgrade()` implementado → DEGRADED
- Se `migrations/` não existir → SKIP_NOT_APPLICABLE (pré-implementação)
- Caso contrário → PASS

## 9. Referências

- ADR: `docs/_canon/decisions/ADR-028-data-migration-strategy.md`
- Arquitetura: `docs/_canon/CODE_ARCHITECTURE.md` (stack: SQLAlchemy 2.x async + Alembic)
- Deploy: `docs/_canon/DEPLOY_PIPELINE.md` (staging obrigatório antes de produção)
