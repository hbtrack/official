# Migrations — Módulo Training

## Status

✅ **Migration v1 criada:** `20260317_001_create_training_tables.py`

## Visão Geral

O módulo `training` usa **Alembic** para gerenciamento de schema, com migrations armazenadas em `migrations/training/versions/`.

### Entidades Mapeadas

| Schema JSON | Tabela SQL | Status |
|---|---|---|
| `training_session.schema.json` | `training_sessions` | ✅ v1 |
| `session_block.schema.json` | `session_blocks` | ✅ v1 |
| `execution_record.schema.json` | `execution_records` | ✅ v1 |
| `feedback_thread.schema.json` | `feedback_threads` | ✅ v1 |
| `session_objective.schema.json` | `session_objectives` | ✅ v1 |
| `attention_queue_item.schema.json` | `attention_queue_items` | ✅ v1 |

---

## v1: Create Training Tables (20260317_001)

### Tabelas Criadas

#### 1. `training_sessions` (entidade-raiz)

**Propósito:** Armazena sessões de treino com metadados de planejamento e execução.

**Campos principais:**
- **Identificação:** `id` (UUID PK), `organization_id`, `team_id`, `season_id`, `microcycle_id`
- **Temporal:** `session_at`, `duration_planned_minutes`, `duration_actual_minutes`, timestamps de ciclo de vida
- **Conteúdo:** `main_objective`, `secondary_objective`, `notes`, `continuation_notes`
- **Carga:** `planned_load`, `actual_load_recorded`, `intensity_target`, `group_climate`
- **Foco técnico (7 dimensões %):** 
  - `focus_attack_positional_pct`
  - `focus_defense_positional_pct`
  - `focus_transition_offense_pct`
  - `focus_transition_defense_pct`
  - `focus_attack_technical_pct`
  - `focus_defense_technical_pct`
  - `focus_physical_pct`
- **Handebol-specific:** flags de foco de fase (`phase_focus_defense`, `phase_focus_attack`, etc.)
- **FSM (ADR-017):** `status` ENUM (DRAFT → SCHEDULED → PUBLISHED → IN_PROGRESS → COMPLETED/CANCELLED → ARCHIVED)
- **Audit:** `created_by_user_id`, `updated_at`, soft-delete (`deleted_at`, `deleted_reason`)

**Índices:**
- `(organization_id, status)` — filtros típicos
- `(team_id, session_at)` — timeline de equipe
- `season_id` — período
- `created_at` — auditoria
- `deleted_at` — soft-delete

---

#### 2. `session_blocks` (unidades operacionais)

**Propósito:** Blocos pedagógicos dentro de uma sessão (fase + duração + objetivo).

**Campos:**
- **Referência:** `id` (PK), `session_id` (FK → `training_sessions.id`)
- **Fase:** `phase` ENUM (WARMUP, ACTIVATION, TECHNICAL, DECISION_MAKING, TACTICAL, REDUCED_GAME, COOLDOWN)
- **Organização:** `order_index` (0-based), `duration_minutes`
- **Pedagogia:** `block_objective`, `intensity`, `is_optional`
- **Exercício (TRAIN-DEC-047):** `exercise_id`, `exercise_version_id` (referência apenas, não embed)
- **Conteúdo:** `description`, `pedagogy_notes`

**Constraints:**
- Unique: `(session_id, order_index)` — ordem sequencial
- FK: `session_id` → `training_sessions.id` (CASCADE DELETE)

**Índices:**
- `session_id` (FK)
- `exercise_id` (referência)

---

#### 3. `execution_records` (append-only fatos)

**Propósito:** Registro imutável de eventos de execução (TRAIN-DEC-007/008/009).

**Campos:**
- **Referência:** `id` (PK), `session_id` (FK), `block_id` (FK nullable)
- **Tipo:** `execution_type` ENUM (SESSION_EXECUTION, BLOCK_EXECUTION, LIVE_ADJUSTMENT, CONSTRAINT_OVERRIDE, ALTERNATE_EXERCISE, LOAD_RECALCULATION)
- **Valores:** `recorded_at`, `planned_value`, `actual_value`, `reason`
- **Audit:** `created_by_user_id`, `created_at`

**Constraints:**
- FK: `session_id` → `training_sessions.id` (CASCADE DELETE)
- FK: `block_id` → `session_blocks.id` (SET NULL)

**Índices:**
- `session_id`
- `execution_type`
- `recorded_at`

---

#### 4. `session_objectives` (rastreamento de objetivos)

**Propósito:** Objetivos estruturados com origem rastreável.

**Campos:**
- **Referência:** `id` (PK), `session_id` (FK)
- **Conteúdo:** `objective_text`, `objective_origin` ENUM (NEED_DETECTED, COMPETITIVE_FOCUS, DEVELOPMENT_GOAL, MANUAL_COACH_RATIONALE)
- **Prioridade:** `priority_order`
- **Status:** `achieved_flag`

**Constraints:**
- FK: `session_id` → `training_sessions.id` (CASCADE DELETE)

**Índices:**
- `session_id`
- `objective_origin`

---

#### 5. `feedback_threads` (conversa coach-atleta)

**Propósito:** Fios de conversa com contexto operacional.

**Campos:**
- **Referência:** `id` (PK), `session_id` (FK), `athlete_id`
- **Conteúdo:** `subject`, `thread_context` (JSON para flexibilidade)
- **Status:** `is_active`, `closed_at`

**Constraints:**
- FK: `session_id` → `training_sessions.id` (CASCADE DELETE)

**Índices:**
- `session_id`
- `athlete_id`
- `is_active`

---

#### 6. `attention_queue_items` (fila de alertas)

**Propósito:** Flags técnicas que precisam de atenção (acompanhamento de problemas).

**Campos:**
- **Referência:** `id` (PK), `session_id` (FK)
- **Tipo:** `item_type`, `severity`
- **Conteúdo:** `description`
- **Status:** `is_resolved`, `resolved_at`, `resolved_by_user_id`

**Constraints:**
- FK: `session_id` → `training_sessions.id` (CASCADE DELETE)

**Índices:**
- `session_id`
- `is_resolved`
- `severity`

---

### ENUM Types Criados

| ENUM | Valores | Ref |
|---|---|---|
| `training_session_status` | DRAFT, SCHEDULED, PUBLISHED, IN_PROGRESS, COMPLETED, CANCELLED, ARCHIVED | ADR-017 |
| `session_block_phase` | WARMUP, ACTIVATION, TECHNICAL, DECISION_MAKING, TACTICAL, REDUCED_GAME, COOLDOWN | Handebol pedagogy |
| `execution_type` | SESSION_EXECUTION, BLOCK_EXECUTION, LIVE_ADJUSTMENT, CONSTRAINT_OVERRIDE, ALTERNATE_EXERCISE, LOAD_RECALCULATION | TRAIN-DEC-007/008/009 |
| `individualization_mode` | COLLECTIVE_UNIFORM, COLLECTIVE_WITH_VARIANTS, INDIVIDUAL_ONLY | INV-TRAIN-086 |
| `objective_origin` | NEED_DETECTED, COMPETITIVE_FOCUS, DEVELOPMENT_GOAL, MANUAL_COACH_RATIONALE | TRAIN-DEC-005 |

---

## Reversibilidade

✅ **Migration reversível:** downgrade implementada

```bash
alembic downgrade -1  # Remove todas as tabelas e ENUMs
```

---

## Próximas Migrations (não criadas ainda)

Conforme evolução do contrato, novas migrations serão criadas para:

1. **Adicionar campos de wellness** (inteligência de carga interna/externa)
2. **Adicionar campos de biomecânica** (se módulo medical evoluir)
3. **Alterações no FSM** (se ADR-017 evoluir)
4. **Índices de performance** (baseado em padrões de query observados)

---

## Validação

Para validar estas migrations:

```bash
# Verificar estado de migrações
alembic current

# Executar primeiro migration em staging
alembic upgrade 20260317_001

# Verificar histórico
alembic history --verbose

# Reverter se necessário
alembic downgrade -1
```

---

## Conformidade com Política

✅ **DATA_MIGRATION_POLICY.md** — Estrutura atende:
- R1: Migrations existem para mudanças em `contracts/schemas/training/`
- R2: Política de deprecation implementada (30 dias para remoções)
- R3: Downgrade implementado (reversibilidade obrigatória)
- R4: Estrutura em `migrations/training/versions/` (canonical path)
- R5: Sem aplicação direta em produção (requer aprovação)
- R6: Sem `--sql` mode (gerado por migration Python equivalente)

---

## Referências

- **Política:** `docs/_canon/DATA_MIGRATION_POLICY.md`
- **Decisão:** `docs/_canon/decisions/ADR-028-data-migration-strategy.md`
- **Schemas:** `contracts/schemas/training/`
- **Estado machine:** `docs/hbtrack/modulos/training/STATE_MODEL_TRAINING.md`
- **Invariantes:** `docs/hbtrack/modulos/training/INVARIANTS_TRAINING.md`
- **Comandos Alembic:** `scripts/db/migration_commands.md` (se existir)
