# 009-ADR-TRAIN — Modelo de Focus Percentages (7 Áreas)

**Status:** Aceita
**Data:** 2026-02-08
**Autor:** Equipe HB Track
**Fase:** F2
**Módulos Afetados:** backend | database | frontend

---

## Contexto

O handebol possui dimensões táticas distintas que um treino pode enfatizar. Para permitir análise estratégica e planejamento de periodização, cada sessão de treino deve registrar a distribuição percentual de tempo/foco entre as áreas táticas.

Esta decisão é 100% evidence-first: toda a estrutura está implementada no schema com constraints, triggers e índices.

**Componentes Relacionados:**
- Modelo de dados: `training_sessions`, `session_templates`, `training_microcycles`, `training_analytics_cache`
- Constraints: `ck_training_sessions_focus_*_range`, `ck_training_sessions_focus_total_sum`, `ck_phase_focus_*_consistency`
- Trigger: `tr_derive_phase_focus` → `fn_derive_phase_focus()`
- API endpoints: `createTrainingSession`, `updateTrainingSession`, analytics endpoints

---

## Decisão

Cada sessão de treino registra **7 áreas de foco** como percentuais independentes:

| # | Área | Coluna | Range |
|---|------|--------|-------|
| 1 | Ataque Posicionado | `focus_attack_positional_pct` | 0-100 |
| 2 | Defesa Posicionada | `focus_defense_positional_pct` | 0-100 |
| 3 | Transição Ofensiva | `focus_transition_offense_pct` | 0-100 |
| 4 | Transição Defensiva | `focus_transition_defense_pct` | 0-100 |
| 5 | Ataque Técnico | `focus_attack_technical_pct` | 0-100 |
| 6 | Defesa Técnica | `focus_defense_technical_pct` | 0-100 |
| 7 | Físico | `focus_physical_pct` | 0-100 |

### Regras:
- Cada área: 0-100% (independente)
- **Soma total: máximo 120%** (permite sobreposição entre áreas)
- **Phase-focus booleans** derivados automaticamente via trigger (threshold ≥ 5%)
- Mesmo modelo replicado em `session_templates` e `training_microcycles` (planejado)

### Detalhes Técnicos

```sql
-- 7 colunas de focus (schema.sql:2605-2611)
focus_attack_positional_pct numeric(5,2),
focus_defense_positional_pct numeric(5,2),
focus_transition_offense_pct numeric(5,2),
focus_transition_defense_pct numeric(5,2),
focus_attack_technical_pct numeric(5,2),
focus_defense_technical_pct numeric(5,2),
focus_physical_pct numeric(5,2),

-- Range CHECK por área (schema.sql:2635-2642)
CONSTRAINT ck_training_sessions_focus_attack_positional_range CHECK (
  (focus_attack_positional_pct IS NULL) OR
  ((focus_attack_positional_pct >= 0) AND (focus_attack_positional_pct <= 100))
)
-- ... (mesmo padrão para as 7 áreas)

-- Soma total ≤ 120 (schema.sql:2640)
CONSTRAINT ck_training_sessions_focus_total_sum CHECK (
  (COALESCE(focus_attack_positional_pct, 0) +
   COALESCE(focus_defense_positional_pct, 0) +
   COALESCE(focus_transition_offense_pct, 0) +
   COALESCE(focus_transition_defense_pct, 0) +
   COALESCE(focus_attack_technical_pct, 0) +
   COALESCE(focus_defense_technical_pct, 0) +
   COALESCE(focus_physical_pct, 0)) <= 120
)

-- Consistency CHECKs: booleans derivados (schema.sql:2629-2632)
CONSTRAINT ck_phase_focus_attack_consistency CHECK (
  phase_focus_attack = (
    (COALESCE(focus_attack_positional_pct, 0) +
     COALESCE(focus_attack_technical_pct, 0)) >= 5
  )
)
-- ... (mesmo padrão para defense, transition_offense, transition_defense)

-- Trigger de derivação automática (schema.sql:5201)
CREATE TRIGGER tr_derive_phase_focus
  BEFORE INSERT OR UPDATE OF
    focus_attack_positional_pct, focus_attack_technical_pct,
    focus_defense_positional_pct, focus_defense_technical_pct,
    focus_transition_offense_pct, focus_transition_defense_pct,
    focus_physical_pct
  ON public.training_sessions
  FOR EACH ROW EXECUTE FUNCTION public.fn_derive_phase_focus();

-- Mesmo padrão em session_templates (schema.sql:2127)
CONSTRAINT chk_session_templates_total_focus CHECK (
  (focus_attack_positional_pct + focus_defense_positional_pct +
   focus_transition_offense_pct + focus_transition_defense_pct +
   focus_attack_technical_pct + focus_defense_technical_pct +
   focus_physical_pct) <= 120
)
```

**Stack envolvida:**
- Database: PostgreSQL — 7 CHECK ranges + 1 CHECK soma + 4 CHECK consistency + 1 trigger
- Backend: FastAPI/SQLAlchemy — colunas `numeric(5,2)`
- Frontend: UI de sliders/barras para distribuição visual de foco

---

## Alternativas Consideradas

### Alternativa 1: Enum único de foco (escolha de 1 área)

**Prós:**
- Mais simples (1 coluna enum)
- Sem cálculos de soma

**Contras:**
- Treinos reais combinam múltiplas áreas
- Impossível representar treino "50% ataque + 50% defesa"
- Sem granularidade para analytics

**Razão da rejeição:** A realidade tática do handebol exige representação multi-dimensional. Um treino nunca é "100% uma coisa".

### Alternativa 2: Soma exata = 100% (sem sobreposição)

**Prós:**
- Matematicamente elegante (distribuição)
- Sem ambiguidade de "quanto sobra"

**Contras:**
- Não reflete realidade: exercícios frequentemente trabalham múltiplas áreas
- Forçar 100% cria distorções (treinador reduz uma área artificialmente para somar)
- Inflexível para treinos com foco físico que permeia todas as áreas

**Razão da rejeição:** O teto de 120% acomoda sobreposição natural entre áreas táticas sem permitir abuso.

---

## Consequências

### Positivas
- ✅ Representação fiel da realidade tática do handebol (7 dimensões)
- ✅ Analytics estratégicos por área, equipe e período (via `training_analytics_cache`)
- ✅ Phase-focus booleans derivados automaticamente (zero work manual)
- ✅ Consistência garantida por trigger + CHECKs em 3 tabelas

### Negativas
- ⚠️ Complexidade: 7 colunas + 12 constraints + 1 trigger por tabela
- ⚠️ Frontend precisa de UI específica para distribuição de percentuais

### Neutras
- ℹ️ O teto de 120% (não 100%) foi calibrado para a realidade de sobreposição tática
- ℹ️ O threshold de 5% para phase_focus boolean é configuração do trigger

---

## Validação

### Critérios de Conformidade
- [x] 7 colunas `focus_*_pct` em `training_sessions` (`schema.sql:2605-2611`)
- [x] 7 CHECKs de range 0-100 (`schema.sql:2635-2642`)
- [x] CHECK de soma total ≤ 120 (`ck_training_sessions_focus_total_sum`, `schema.sql:2640`)
- [x] 4 CHECKs de consistency phase_focus (`schema.sql:2629-2632`)
- [x] Trigger `tr_derive_phase_focus` (`schema.sql:5201`)
- [x] Mesmo modelo em `session_templates` (`chk_session_templates_total_focus`, `schema.sql:2127`)
- [x] Colunas `planned_focus_*_pct` em `training_microcycles` (`schema.sql:2447-2453`)

---

## Referências

- `Hb Track - Backend/docs/_generated/schema.sql:2605-2611`: colunas de focus em training_sessions
- `Hb Track - Backend/docs/_generated/schema.sql:2635-2642`: CHECKs de range por área
- `Hb Track - Backend/docs/_generated/schema.sql:2640`: `ck_training_sessions_focus_total_sum`
- `Hb Track - Backend/docs/_generated/schema.sql:2629-2632`: CHECKs de consistency
- `Hb Track - Backend/docs/_generated/schema.sql:5201`: trigger `tr_derive_phase_focus`
- `Hb Track - Backend/docs/_generated/schema.sql:2127`: `chk_session_templates_total_focus`
- `Hb Track - Backend/docs/_generated/schema.sql:2447-2453`: planned_focus em microcycles
- ADRs relacionados: ADR-TRAIN-001 (SSOT — DB prevalece), ADR-TRAIN-003 (lifecycle)

---

## Revisões

| Data | Autor | Mudança | Versão |
|------|-------|---------|--------|
| 2026-02-08 | Equipe HB Track | Criação evidence-first a partir de schema.sql | 1.0 |
