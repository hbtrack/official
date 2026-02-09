# 010-ADR-TRAIN — Multi-tenancy via Organization ID

**Status:** Aceita
**Data:** 2026-02-08
**Autor:** Equipe HB Track
**Fase:** F2
**Módulos Afetados:** backend | database | auth

---

## Contexto

O HB Track atende múltiplos clubes/organizações de handebol. Cada organização deve ver e gerenciar apenas seus próprios dados (atletas, equipes, treinos, competições, wellness). Sem isolamento adequado, um clube poderia acessar dados de outro.

Esta decisão é 100% evidence-first: o padrão `organization_id` FK está presente em todas as tabelas core do schema.

**Componentes Relacionados:**
- Modelo de dados: `organizations` (tabela central), FK `organization_id` em 12+ tabelas
- Constraints: `fk_*_organization_id` com ON DELETE RESTRICT
- Índices: `ix_*_organization_id`, `idx_*_org` (condicionais e não-condicionais)
- Hierarquia: Organization → Teams → Seasons → Training Sessions

---

## Decisão

O isolamento de dados entre organizações é feito via **coluna `organization_id`** como FK em todas as tabelas core, com as seguintes regras:

1. **Toda entidade pertence a uma organização** (FK NOT NULL na maioria das tabelas)
2. **ON DELETE RESTRICT** — não é possível deletar uma organização que tenha dados vinculados
3. **Índices condicionais** combinam `organization_id` com `deleted_at IS NULL` para queries eficientes
4. **Filtragem obrigatória** — toda query de listagem deve filtrar por `organization_id` do usuário autenticado

### Detalhes Técnicos

```sql
-- Tabelas com organization_id FK (evidências do schema.sql):

-- athletes (schema.sql:629, FK schema.sql:5700)
organization_id uuid,
CONSTRAINT fk_athletes_organization_id FOREIGN KEY (organization_id)
  REFERENCES public.organizations(id) ON DELETE RESTRICT;

-- teams (schema.sql:2257, FK schema.sql:6324)
organization_id uuid NOT NULL,
CONSTRAINT fk_teams_organization_id FOREIGN KEY (organization_id)
  REFERENCES public.organizations(id) ON DELETE RESTRICT;

-- training_sessions (schema.sql:2582, FK schema.sql:6364)
organization_id uuid NOT NULL,
CONSTRAINT fk_training_sessions_organization_id FOREIGN KEY (organization_id)
  REFERENCES public.organizations(id) ON DELETE RESTRICT;

-- training_cycles (schema.sql:2388, FK schema.sql:6588)
-- training_microcycles (schema.sql:2442, FK schema.sql:6628)
-- competitions (schema.sql:1209, FK schema.sql:5900)
-- wellness_pre (schema.sql:2872, FK schema.sql:6444)
-- wellness_post (schema.sql:2810, FK schema.sql:6412)
-- medical_cases (schema.sql:1541, FK schema.sql:6156)
-- exercises (FK schema.sql:5660)
-- org_memberships (schema.sql:1618, FK schema.sql:6172)
```

**Índices para performance:**
```sql
-- Índices condicionais (org + soft-delete filter)
-- schema.sql:4114
CREATE INDEX idx_training_sessions_org ON public.training_sessions
  USING btree (organization_id, deleted_at) WHERE (deleted_at IS NULL);

-- schema.sql:5019
CREATE INDEX ix_teams_organization_active ON public.teams
  USING btree (organization_id) WHERE (deleted_at IS NULL);

-- schema.sql:4207
CREATE INDEX ix_athletes_organization_id ON public.athletes
  USING btree (organization_id) WHERE (deleted_at IS NULL);
```

---

## Alternativas Consideradas

### Alternativa 1: Schema por tenant (schema-based multi-tenancy)

**Prós:**
- Isolamento total no nível do PostgreSQL
- Sem risco de cross-tenant leaks em queries

**Contras:**
- Complexidade de migrations (migrar N schemas)
- Não suportado por Neon (managed PostgreSQL)
- Escala mal com centenas de organizações

**Razão da rejeição:** Incompatível com Neon (PostgreSQL managed) e complexidade de manutenção.

### Alternativa 2: Database por tenant

**Prós:**
- Isolamento absoluto
- Backups independentes

**Contras:**
- Custo proporcional ao número de tenants
- Connection pooling complexo
- Impossível cross-tenant analytics (se necessário no futuro)

**Razão da rejeição:** Custo e complexidade operacional proibitivos para fase atual do produto.

---

## Consequências

### Positivas
- ✅ Isolamento de dados garantido por FK constraints (DB-level)
- ✅ ON DELETE RESTRICT previne perda acidental de dados organizacionais
- ✅ Índices condicionais otimizam queries por organização
- ✅ Padrão consistente em 12+ tabelas (mesmo FK pattern)

### Negativas
- ⚠️ Todo endpoint deve filtrar por `organization_id` — esquecimento causa data leak
- ⚠️ Queries cross-organization (admin/analytics global) são mais complexas

### Neutras
- ℹ️ O serviço de autenticação deve injetar `organization_id` no contexto do request
- ℹ️ `org_memberships` vincula pessoa → organização → role (ADR-TRAIN-011)

---

## Validação

### Critérios de Conformidade
- [x] FK `organization_id` presente em todas as tabelas core
- [x] ON DELETE RESTRICT em todas as FKs de organização
- [x] Índices condicionais `(organization_id) WHERE (deleted_at IS NULL)` criados
- [x] `org_memberships` vincula usuários a organizações com role

---

## Referências

- `Hb Track - Backend/docs/_generated/schema.sql:629`: `athletes.organization_id`
- `Hb Track - Backend/docs/_generated/schema.sql:2257`: `teams.organization_id NOT NULL`
- `Hb Track - Backend/docs/_generated/schema.sql:2582`: `training_sessions.organization_id NOT NULL`
- `Hb Track - Backend/docs/_generated/schema.sql:5700`: `fk_athletes_organization_id ON DELETE RESTRICT`
- `Hb Track - Backend/docs/_generated/schema.sql:6324`: `fk_teams_organization_id ON DELETE RESTRICT`
- `Hb Track - Backend/docs/_generated/schema.sql:6364`: `fk_training_sessions_organization_id ON DELETE RESTRICT`
- `Hb Track - Backend/docs/_generated/schema.sql:4114`: `idx_training_sessions_org` (conditional)
- ADRs relacionados: ADR-TRAIN-005 (soft-delete — índices condicionais), ADR-TRAIN-011 (RBAC)

---

## Revisões

| Data | Autor | Mudança | Versão |
|------|-------|---------|--------|
| 2026-02-08 | Equipe HB Track | Criação evidence-first a partir de schema.sql | 1.0 |
