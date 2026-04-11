# ADR-028 — Data Migration Strategy

**Status:** accepted (§Ferramenta supersedida por ADR-031)
**Data:** 2026-03-17
**Decisores:** Equipe técnica (sem decisão humana adicional necessária)
**Stack:** ~~Alembic + SQLAlchemy~~ → **Django Migrations + Django ORM + PostgreSQL 16** (ADR-031)

> **ADR-031 (2026-03-17):** A ferramenta de migração foi alterada de Alembic para Django Migrations
> devido à mudança de framework para Django Ninja. A ESTRATÉGIA abaixo permanece válida.
> Apenas substituir "Alembic" por "Django Migrations" e `migrations/<MODULE>/versions/` por `src/<MODULE>/migrations/`.

## Contexto

O HB Track usa PostgreSQL 16 como banco de dados principal (definido em ADR-026).
A medida que os contratos de schema evoluem, é necessária uma estratégia de migração
que garanta que mudanças não quebrem dados existentes em produção.

## Decisão

**Ferramenta:** Django Migrations (nativo do Django — substituiu Alembic em ADR-031).

**Razões:**
1. Integração nativa com Django ORM (stack definida no ADR-031)
2. Suporte a autogenerate via `makemigrations` — detecta mudanças no modelo automaticamente
3. Migrations versionadas e rastreáveis via git
4. Suporte completo a operações reversíveis (`RunSQL` com `reverse_sql`)

**Estrutura:** migrations dentro de cada Django app: `src/<module>/migrations/`.
Isolamento por módulo mantido — apenas a localização muda de `migrations/<MODULE>/versions/` para `src/<MODULE>/migrations/`.

**Regra de ouro:** nenhuma migration chega a produção sem passar por staging primeiro.
Isso está reforçado no DEPLOY_PIPELINE.md (ADR-027).

## Fluxo

```
mudança em contracts/schemas/ → DATA_MIGRATION_GATE verifica → migration criada
→ python manage.py migrate (staging) → validação → aprovação humana → produção
```

## Consequências

**Positivas:**
- Evoluções de schema são auditáveis e reversíveis
- Gate automatizado previne deploy com schema inconsistente
- Alinhado com o ciclo de vida de contratos (schema é parte do contrato)
- Django squashmigrations para compactar histórico longo

**Negativas:**
- Adiciona passo obrigatório para qualquer mudança de schema
- makemigrations pode criar migrations incorretas — sempre revisar antes de aplicar

## Nota sobre artefatos existentes

O arquivo `migrations/training/versions/20260317_001_create_training_tables.py` na raiz
é um ARTEFATO DE REFERÊNCIA de schema (criado com estrutura Alembic).
**Não será executado.** As migrações reais serão criadas com `manage.py makemigrations`
em `src/training/migrations/` quando a implementação começar.

## Alternativas consideradas

- **Flyway:** descartado — ecossistema Java, fora do stack Python definido
- **Alembic:** ~~escolha original~~ — substituído por Django Migrations (ADR-031)
- **Migrations manuais (SQL puro):** descartado — sem versioning automático, propenso a erro

## Referências

- `docs/_canon/DATA_MIGRATION_POLICY.md` — política normativa completa
- ADR-031: stack atual (Django Ninja + Django Migrations)
- ADR-027: deploy pipeline (staging obrigatório para migrations)

---

<details>
<summary>📜 Versão original (Alembic) — histórico, supersedida por ADR-031</summary>

A versão original deste ADR usava Alembic + SQLAlchemy como ferramenta de migração.
Foi substituída por Django Migrations quando o backend migrou para Django Ninja (ADR-031, 2026-03-17).
O conteúdo original foi removido em 2026-04-10 (SAN-007) para eliminar ambiguidade.
Consultar git history para referência.

</details>
