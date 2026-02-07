# TRAINING — Invariantes Candidatas

**Gerado em**: 2026-02-04
**Baseline runner**: PASS
**Commit de referência**: `e02c83ef`
**Última atualização**: Marcadas candidatas já confirmadas como DONE com referência às INV-TRAIN correspondentes.

## Resumo

| Categoria | Quantidade |
|-----------|------------|
| DB-CANDIDATE | 42 |
| CODE-CANDIDATE | 15 |
| **TOTAL** | 57 |

---

## 1) DB-CANDIDATE (Constraints/Triggers/Indexes não referenciados no INVARIANTS)

### athlete_badges

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `ck_athlete_badges_type` | CHECK | `schema.sql:588` | NEEDS_REVIEW — enum de tipos de badge |

### attendance

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `ck_attendance_correction_fields` | CHECK | `schema.sql:673` | ✅ DONE → INV-TRAIN-030 |
| `ck_attendance_participation_type` | CHECK | `schema.sql:675` | NEEDS_REVIEW — enum (full, partial, adapted, did_not_train) |
| `ck_attendance_reason` | CHECK | `schema.sql:676` | NEEDS_REVIEW — enum de reason_absence |
| `ck_attendance_source` | CHECK | `schema.sql:677` | NEEDS_REVIEW — enum (manual, import, correction) |
| `ck_attendance_status` | CHECK | `schema.sql:678` | NEEDS_REVIEW — enum (present, absent) |

### export_jobs

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `ck_export_jobs_status` | CHECK | `schema.sql:1243` | NEEDS_REVIEW — enum de status (pending, processing, completed, failed) |

### session_templates

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `chk_session_templates_icon` | CHECK | `schema.sql:2126` | ignorar — validação de ícone UI |
| `uq_session_templates_org_name` | UNIQUE | `schema.sql:3645` | ✅ DONE → INV-TRAIN-035 |

### team_wellness_rankings

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `uq_team_wellness_rankings_team_month` | UNIQUE | `schema.sql:3653` | ✅ DONE → INV-TRAIN-036 |

### training_alerts

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `ck_training_alerts_severity` | CHECK | `schema.sql:2329` | NEEDS_REVIEW — enum (warning, critical) |
| `ck_training_alerts_type` | CHECK | `schema.sql:2330` | NEEDS_REVIEW — enum alert_type |

### training_analytics_cache

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `ck_training_analytics_cache_granularity` | CHECK | `schema.sql:2371` | NEEDS_REVIEW — enum (weekly, monthly) |
| `uq_training_analytics_cache_lookup` | UNIQUE | `schema.sql:3661` | ✅ DONE → INV-TRAIN-044 |

### training_cycles

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `check_cycle_dates` | CHECK | `schema.sql:2402` | ✅ DONE → INV-TRAIN-037 |
| `check_cycle_status` | CHECK | `schema.sql:2403` | NEEDS_REVIEW — enum status (active, completed, cancelled) |
| `check_cycle_type` | CHECK | `schema.sql:2404` | NEEDS_REVIEW — enum type (macro, meso) — **referenciado no TRD** |

### training_microcycles

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `check_microcycle_dates` | CHECK | `schema.sql:2462` | ✅ DONE → INV-TRAIN-043 |

### training_session_exercises

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `ck_session_exercises_duration_positive` | CHECK | `schema.sql:2564` | NEEDS_REVIEW — duration >= 0 |
| `ck_session_exercises_order_positive` | CHECK | `schema.sql:2565` | NEEDS_REVIEW — order_index >= 0 |
| `idx_session_exercises_session_order_unique` | UNIQUE INDEX | `schema.sql:3917` | ✅ DONE → INV-TRAIN-045 |

### training_sessions

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `check_training_sessions_execution_outcome` | CHECK | `schema.sql:2628` | NEEDS_REVIEW — enum (on_time, delayed, canceled, shortened, extended) |
| `ck_phase_focus_attack_consistency` | CHECK | `schema.sql:2629` | ✅ DONE → INV-TRAIN-031 |
| `ck_phase_focus_defense_consistency` | CHECK | `schema.sql:2630` | ✅ DONE → INV-TRAIN-031 |
| `ck_phase_focus_transition_defense_consistency` | CHECK | `schema.sql:2631` | ✅ DONE → INV-TRAIN-031 |
| `ck_phase_focus_transition_offense_consistency` | CHECK | `schema.sql:2632` | ✅ DONE → INV-TRAIN-031 |
| `ck_training_sessions_climate` | CHECK | `schema.sql:2633` | NEEDS_REVIEW — group_climate 1-5 |
| `ck_training_sessions_focus_attack_positional_range` | CHECK | `schema.sql:2635` | NEEDS_REVIEW — range 0-100 |
| `ck_training_sessions_focus_attack_technical_range` | CHECK | `schema.sql:2636` | NEEDS_REVIEW — range 0-100 |
| `ck_training_sessions_focus_defense_positional_range` | CHECK | `schema.sql:2637` | NEEDS_REVIEW — range 0-100 |
| `ck_training_sessions_focus_defense_technical_range` | CHECK | `schema.sql:2638` | NEEDS_REVIEW — range 0-100 |
| `ck_training_sessions_focus_physical_range` | CHECK | `schema.sql:2639` | NEEDS_REVIEW — range 0-100 |
| `ck_training_sessions_focus_transition_defense_range` | CHECK | `schema.sql:2641` | NEEDS_REVIEW — range 0-100 |
| `ck_training_sessions_focus_transition_offense_range` | CHECK | `schema.sql:2642` | NEEDS_REVIEW — range 0-100 |
| `ck_training_sessions_intensity` | CHECK | `schema.sql:2643` | NEEDS_REVIEW — intensity_target 1-5 |
| `ck_training_sessions_type` | CHECK | `schema.sql:2644` | NEEDS_REVIEW — enum session_type — **referenciado no TRD** |
| `tr_derive_phase_focus` | TRIGGER | `schema.sql:5201` | ✅ DONE → INV-TRAIN-031 |

### training_suggestions

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `ck_training_suggestions_status` | CHECK | `schema.sql:2763` | NEEDS_REVIEW — enum (pending, applied, dismissed) |
| `ck_training_suggestions_type` | CHECK | `schema.sql:2764` | NEEDS_REVIEW — enum (compensation, reduce_next_week) |

### wellness_post

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `ck_wellness_post_fatigue` | CHECK | `schema.sql:2830` | NEEDS_REVIEW — fatigue_after 0-10 |
| `ck_wellness_post_intensity` | CHECK | `schema.sql:2831` | NEEDS_REVIEW — perceived_intensity 1-5 |
| `ck_wellness_post_mood` | CHECK | `schema.sql:2832` | NEEDS_REVIEW — mood_after 0-10 |
| `ck_wellness_post_rpe` | CHECK | `schema.sql:2833` | ✅ DONE → INV-TRAIN-032 |
| `ck_wellness_post_soreness` | CHECK | `schema.sql:2834` | NEEDS_REVIEW — muscle_soreness_after 0-10 |
| `tr_update_wellness_post_response` | TRIGGER | `schema.sql:5222` | ✅ DONE → INV-TRAIN-046 |

### wellness_pre

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `ck_wellness_pre_fatigue` | CHECK | `schema.sql:2891` | NEEDS_REVIEW — fatigue_pre 0-10 |
| `ck_wellness_pre_menstrual` | CHECK | `schema.sql:2892` | NEEDS_REVIEW — enum menstrual_cycle_phase |
| `ck_wellness_pre_readiness` | CHECK | `schema.sql:2893` | NEEDS_REVIEW — readiness_score 0-10 |
| `ck_wellness_pre_sleep_hours` | CHECK | `schema.sql:2894` | ✅ DONE → INV-TRAIN-033 |
| `ck_wellness_pre_sleep_quality` | CHECK | `schema.sql:2895` | ✅ DONE → INV-TRAIN-034 |
| `ck_wellness_pre_soreness` | CHECK | `schema.sql:2896` | NEEDS_REVIEW — muscle_soreness 0-10 |
| `ck_wellness_pre_stress` | CHECK | `schema.sql:2897` | NEEDS_REVIEW — stress_level 0-10 |
| `tr_update_wellness_pre_response` | TRIGGER | `schema.sql:5229` | promover — atualiza timestamp de resposta |
---

## 2) CODE-CANDIDATE (Regras de validação não referenciadas no INVARIANTS)

### training_session_service.py

| Linha | Regra | Ação Sugerida |
|-------|-------|---------------|
| `210` | ForbiddenError: Team belongs to another organization | promover — multi-tenant isolation |
| `299` | ValidationError: Informe o atraso em minutos (execution_outcome=delayed) | ✅ DONE → INV-TRAIN-004, INV-TRAIN-029 |
| `305` | ValidationError: Informe o motivo do cancelamento (execution_outcome=canceled) | ✅ DONE → INV-TRAIN-004, INV-TRAIN-029 |
| `311` | ValidationError: Informe a duração real em minutos (execution_outcome=shortened/extended) | ✅ DONE → INV-TRAIN-004, INV-TRAIN-029 |
| `319` | ValidationError: Especifique o tipo de encerramento (execution_outcome obrigatório) | ✅ DONE → INV-TRAIN-004, INV-TRAIN-029 |
| `381` | ValidationError: Sessão não está em rascunho (publish) | ✅ DONE → INV-TRAIN-006 |
| `522` | ValidationError: Deletion reason is required | ✅ DONE → INV-TRAIN-008 |
| `543` | ValidationError: Training session is not deleted (restore) | promover — restore requer sessão deletada |

### wellness_pre_service.py

| Linha | Regra | Ação Sugerida |
|-------|-------|---------------|
| `271` | ValidationError: Wellness bloqueado para edição (locked_at) | ✅ DONE → INV-TRAIN-002 |
| `405` | ValidationError: Sistema de aprovação ainda não implementado | ignorar — feature não implementada |

### wellness_post_service.py

| Linha | Regra | Ação Sugerida |
|-------|-------|---------------|
| `260` | ValidationError: Wellness bloqueado para edição (locked_at) | ✅ DONE → INV-TRAIN-003 |
| `469` | ValidationError: Sistema de aprovação ainda não implementado | ignorar — feature não implementada |

### attendance_service.py

| Linha | Regra | Ação Sugerida |
|-------|-------|---------------|
| `236` | ValidationError: Sessão não encontrada (batch) | NEEDS_REVIEW — validação básica |
| `241` | ValidationError: Sessão sem equipe não permite registro de presença | ✅ DONE → INV-TRAIN-016 |
| `246` | ValidationError: Lista contém atletas duplicados (batch) | promover — unicidade em batch |
| `275-286` | ValidationError: Atleta não está registrado na equipe | promover — atleta deve pertencer ao time |
| `314` | ConflictError: Presença duplicada | NEEDS_REVIEW — similar a constraint DB |
| `546` | ValidationError: Motivo da correção deve ter pelo menos 10 caracteres | ✅ DONE → INV-TRAIN-030 |

### training_cycle_service.py

| Linha | Regra | Ação Sugerida |
|-------|-------|---------------|
| `145` | ValidationError: (contexto não extraído) | NEEDS_REVIEW — verificar regra específica |

### training_microcycle_service.py

| Linha | Regra | Ação Sugerida |
|-------|-------|---------------|
| `151` | ValidationError: (contexto não extraído) | NEEDS_REVIEW — verificar regra específica |

---

## 3) Próximos Passos

1. **Revisar candidatas marcadas como "promover"** — criar 1 PR por invariante
2. **Revisar candidatas marcadas como "NEEDS_REVIEW"** — decidir se são invariantes de negócio ou apenas validações técnicas
3. **Ignorar candidatas marcadas como "ignorar"** — constraints de UI/enum básico ou features não implementadas
4. **Prioridade sugerida**:
   - Alta: ~~`ck_attendance_correction_fields`~~ ✅ INV-TRAIN-030, ~~`tr_derive_phase_focus`~~ ✅ INV-TRAIN-031, ~~`ck_wellness_post_rpe`~~ ✅ INV-TRAIN-032, ~~`ck_wellness_pre_sleep_hours`~~ ✅ INV-TRAIN-033, ~~`ck_wellness_pre_sleep_quality`~~ ✅ INV-TRAIN-034, ~~`tr_update_wellness_post_response`~~ ✅ INV-TRAIN-046
   - Média: ~~regras de execution_outcome (linhas 299-319)~~ ✅ INV-TRAIN-004, INV-TRAIN-029, unicidades (uq_*)
   - Baixa: enums de status/type (já documentados no TRD)

---

**Gerado por**: Claude Opus 4.5
**Runner final**: PASS
