# ADR-028 — Data Migration Strategy

**Status:** accepted
**Data:** 2026-03-17
**Decisores:** Equipe técnica (sem decisão humana adicional necessária)
**Stack:** Alembic + SQLAlchemy 2.x async + PostgreSQL 16

## Contexto

O HB Track usa PostgreSQL 16 como banco de dados principal (definido em ADR-026).
A medida que os contratos de schema evoluem, é necessária uma estratégia de migração
que garanta que mudanças não quebrem dados existentes em produção.

## Decisão

**Ferramenta:** Alembic (migração de banco de dados padrão do ecossistema Python/SQLAlchemy).

**Razões:**
1. Integração nativa com SQLAlchemy 2.x (stack definida no ADR-026)
2. Suporte a autogenerate — detecta mudanças no modelo automaticamente
3. Migrations versionadas e rastreáveis via git
4. Suporte completo a up + down migrations (reversibilidade obrigatória)

**Estrutura:** uma pasta `migrations/<MODULE>/versions/` por módulo canônico.
Isso mantém isolamento de contexto, facilita revisão e alinha com o CDD por módulo.

**Regra de ouro:** nenhuma migration chega a produção sem passar por staging primeiro.
Isso está reforçado no DEPLOY_PIPELINE.md (ADR-027).

## Fluxo

```
mudança em contracts/schemas/ → DATA_MIGRATION_GATE verifica → migration criada
→ alembic upgrade head (staging) → validação → aprovação humana → produção
```

## Consequências

**Positivas:**
- Evoluções de schema são auditáveis e reversíveis
- Gate automatizado previne deploy com schema inconsistente
- Alinhado com o ciclo de vida de contratos (schema é parte do contrato)

**Negativas:**
- Adiciona passo obrigatório para qualquer mudança de schema
- Autogenerate pode criar migrations incorretas — sempre revisar antes de aplicar

## Alternativas consideradas

- **Flyway:** descartado — ecossistema Java, fora do stack Python definido
- **Django migrations:** descartado — HB Track usa FastAPI, não Django
- **Migrations manuais (SQL puro):** descartado — sem versioning automático, propenso a erro

## Referências

- `docs/_canon/DATA_MIGRATION_POLICY.md` — política normativa completa
- ADR-026: stack de código (Python/FastAPI/SQLAlchemy/PostgreSQL)
- ADR-027: deploy pipeline (staging obrigatório para migrations)
