# 003-ADR-TRAIN — Lifecycle e State Machine de Training

**Status:** Aceita
**Data:** 2026-02-08
**Autor:** Equipe HB Track
**Fase:** F2
**Módulos Afetados:** backend | database | frontend

---

## Contexto

Treinos (training sessions) possuem estados distintos que afetam permissões, mutabilidade e regras de negócio. Sem uma máquina de estados formal, surgem problemas como edição de treinos já finalizados, transições inválidas e comportamento inconsistente entre backend e frontend.

**Componentes Relacionados:**
- Modelo de dados: `training_sessions.status`
- Constraint: `check_training_session_status` em `schema.sql:2627`
- Hierarquia de usuários: Treinador (owner), Coordenador (supervisor)
- API endpoints: `updateTrainingSession`, `transitionTrainingStatus`

---

## Decisão

O lifecycle oficial de Training Sessions é:

```
draft → scheduled → in_progress → pending_review → readonly
```

### Regras de transição:
- Transições são **unidirecionais** (não há rollback de estado)
- `draft`: editável livremente pelo autor
- `scheduled`: agendado, editável com restrições
- `in_progress`: treino em andamento, apenas dados de execução
- `pending_review`: aguardando aprovação do coordenador
- `readonly`: estado final, **imutável**

### Detalhes Técnicos

```sql
-- schema.sql:2627
CONSTRAINT check_training_session_status CHECK (
  (status)::text = ANY (
    ARRAY['draft', 'scheduled', 'in_progress', 'pending_review', 'readonly']::text[]
  )
)
```

**Stack envolvida:**
- Database: PostgreSQL CHECK constraint para estados válidos
- Backend: Service layer valida transições permitidas
- Frontend: UI mapeia labels em português, mas respeita estados do DB

---

## Alternativas Consideradas

### Alternativa 1: Status livre (campo texto sem restrição)

**Prós:**
- Flexibilidade total
- Sem necessidade de migrations para novos estados

**Contras:**
- Sem garantia de integridade
- Typos criam estados fantasma
- Impossível validar transições

**Razão da rejeição:** A integridade do lifecycle é crítica para audit trail e imutabilidade.

### Alternativa 2: Enum PostgreSQL (CREATE TYPE)

**Prós:**
- Validação nativa mais estrita que CHECK
- Melhor semântica no schema

**Contras:**
- Alterar enum em PostgreSQL requer ALTER TYPE (mais complexo que alterar CHECK)
- Não suporta remoção de valores facilmente

**Razão da rejeição:** CHECK com ARRAY oferece mais flexibilidade para evoluir estados sem ALTER TYPE.

---

## Consequências

### Positivas
- ✅ Serviços validam transições de estado deterministicamente
- ✅ Invariantes garantem imutabilidade em estados finais (`readonly`)
- ✅ Transições inválidas são bloqueadas na camada de DB

### Negativas
- ⚠️ Adicionar novos estados requer migration
- ⚠️ Frontend deve manter mapeamento de labels sincronizado

### Neutras
- ℹ️ UI pode mapear labels alternativos (ex: "Rascunho" para `draft`), mas o DB mantém o estado canônico

---

## Validação

### Critérios de Conformidade
- [x] CHECK constraint `check_training_session_status` presente em `schema.sql:2627`
- [x] 5 estados definidos: draft, scheduled, in_progress, pending_review, readonly
- [x] Invariantes dependentes de status documentadas em `INVARIANTS_TRAINING.md`

---

## Referências

- `Hb Track - Backend/docs/_generated/schema.sql:2627`: constraint `check_training_session_status`
- `docs/TRD_TRAINING.md`: definição explícita do lifecycle
- `docs/INVARIANTS_TRAINING.md`: invariantes dependentes de status
- ADRs relacionados: ADR-TRAIN-001 (SSOT — DB prevalece)

---

## Revisões

| Data | Autor | Mudança | Versão |
|------|-------|---------|--------|
| 2026-02-08 | Equipe HB Track | Criação inicial | 1.0 |
| 2026-02-08 | Equipe HB Track | Adequação ao template padrão ADR | 1.1 |
