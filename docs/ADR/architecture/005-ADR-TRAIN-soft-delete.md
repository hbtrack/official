# 005-ADR-TRAIN — Soft-Delete com Motivo Obrigatório

**Status:** Aceita
**Data:** 2026-02-08
**Autor:** Equipe HB Track
**Fase:** F2
**Módulos Afetados:** backend | database

---

## Contexto

A exclusão de treinos impacta histórico, métricas e auditoria. Remoções físicas (hard-delete) dificultam rastreabilidade, compliance LGPD e análise retrospectiva de cargas de treino.

O padrão `deleted_at` + `deleted_reason` é aplicado de forma consistente em todas as entidades core do sistema (athletes, teams, training_sessions, attendance, matches, etc.).

**Componentes Relacionados:**
- Modelo de dados: `training_sessions`, `athletes`, `teams`, `attendance`, `matches`, `competitions`
- Constraints: `ck_training_sessions_deleted_reason`, `ck_athletes_deleted_reason`, `ck_teams_deleted_reason`, etc.
- Índices condicionais: `WHERE (deleted_at IS NULL)` em queries de listagem

---

## Decisão

Treinos e entidades core **não devem ser hard-deleted**. Toda exclusão deve:

1. Ser **soft-delete** via campo `deleted_at` (timestamp)
2. Exigir **`deleted_reason`** obrigatório quando `deleted_at` é preenchido
3. Preservar dados históricos para auditoria e métricas

O par `deleted_at` / `deleted_reason` é mutuamente obrigatório: ambos NULL ou ambos NOT NULL.

### Detalhes Técnicos

```sql
-- Padrão aplicado em todas as entidades core (schema.sql)

-- training_sessions (schema.sql:2634)
CONSTRAINT ck_training_sessions_deleted_reason CHECK (
  ((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR
  ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL))
)

-- athletes (schema.sql:630)
CONSTRAINT ck_athletes_deleted_reason CHECK (
  ((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR
  ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL))
)

-- teams (schema.sql:2274)
CONSTRAINT ck_teams_deleted_reason CHECK (...)

-- attendance (schema.sql:674)
CONSTRAINT ck_attendance_deleted_reason CHECK (...)

-- matches (schema.sql:1508)
CONSTRAINT ck_matches_deleted_reason CHECK (...)
```

**Índices condicionais para performance:**
```sql
-- schema.sql:4114
CREATE INDEX idx_training_sessions_org ON public.training_sessions
  USING btree (organization_id, deleted_at) WHERE (deleted_at IS NULL);

-- schema.sql:4207
CREATE INDEX ix_athletes_organization_id ON public.athletes
  USING btree (organization_id) WHERE (deleted_at IS NULL);
```

---

## Alternativas Consideradas

### Alternativa 1: Hard-delete físico

**Prós:**
- Implementação trivial (DELETE FROM)
- Sem dados residuais

**Contras:**
- Perda irreversível de dados históricos
- Impossível auditar "quem deletou o quê e por quê"
- Viola requisitos LGPD de rastreabilidade
- Quebra métricas retrospectivas

**Razão da rejeição:** A perda de dados históricos é inaceitável para um sistema de gestão esportiva com requisitos de auditoria.

### Alternativa 2: Soft-delete sem motivo obrigatório

**Prós:**
- Mais simples (apenas `deleted_at`)
- Menos friction na operação de exclusão

**Contras:**
- Sem rastreabilidade do motivo
- "Por que este treino foi excluído?" fica sem resposta
- Dificulta análise de padrões de exclusão

**Razão da rejeição:** O motivo é essencial para auditoria e análise de padrões. O overhead de exigir um texto é mínimo comparado ao benefício.

---

## Consequências

### Positivas
- ✅ Histórico sempre preservado para métricas e análise retrospectiva
- ✅ Auditoria simplificada: quem, quando e por quê
- ✅ Base sólida para políticas LGPD (dados são "marcados", não destruídos)
- ✅ Padrão consistente em todas as entidades core (mesma CHECK em 10+ tabelas)

### Negativas
- ⚠️ Queries de listagem devem sempre filtrar `WHERE deleted_at IS NULL`
- ⚠️ Dados "deletados" permanecem no banco, aumentando volume ao longo do tempo

### Neutras
- ℹ️ Índices condicionais com `WHERE (deleted_at IS NULL)` mitigam impacto de performance

---

## Validação

### Critérios de Conformidade
- [x] CHECK constraint `ck_*_deleted_reason` presente em todas as entidades core
- [x] Par `deleted_at`/`deleted_reason` mutuamente obrigatório (ambos NULL ou ambos NOT NULL)
- [x] Índices condicionais criados para queries de listagem

---

## Referências

- `Hb Track - Backend/docs/_generated/schema.sql:2634`: `ck_training_sessions_deleted_reason`
- `Hb Track - Backend/docs/_generated/schema.sql:630`: `ck_athletes_deleted_reason`
- `Hb Track - Backend/docs/_generated/schema.sql:2274`: `ck_teams_deleted_reason`
- `docs/TRD_TRAINING.md`: regras de exclusão
- `docs/INVARIANTS_TRAINING.md`: invariantes de pares obrigatórios
- ADRs relacionados: ADR-TRAIN-001 (SSOT — DB prevalece)

---

## Revisões

| Data | Autor | Mudança | Versão |
|------|-------|---------|--------|
| 2026-02-08 | Equipe HB Track | Criação inicial | 1.0 |
| 2026-02-08 | Equipe HB Track | Adequação ao template padrão ADR com evidências de schema | 1.1 |
