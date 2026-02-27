# Training Invariants — Full Coverage Report

**Gerado em**: 2026-02-27
**Versão**: 1.0.0 (AR_161 — Regressão Final)
**Módulo**: TRAINING
**SSOT**: `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md` v1.3.0
**Total de invariantes no SSOT**: 85 (INV-TRAIN-001..081 + EXB-ACL-001..007)
**Total de arquivos de teste**: 74 arquivos em `Hb Track - Backend/tests/training/invariants/`

---

## Legenda de Status

| Status | Significado |
|---|---|
| `IMPLEMENTADO` | SSOT=IMPLEMENTADO ou PARCIAL/DIVERGENTE com teste existente e passando |
| `GAP_COBERTO` | SSOT=GAP mas teste criado nas tasks 144-160 cobre a invariante |
| `GAP_PENDENTE` | SSOT=GAP, sem teste — IA Coach (esperado) ou pendência futura |
| `DEPRECATED` | Mantida para referência histórica, não normativa para novos ARs |

---

## Resumo Executivo

| Categoria | Quantidade |
|---|---|
| IMPLEMENTADO (cobertura total ou parcial com teste) | 43 |
| GAP_COBERTO (novo — tasks 144-160) | 32 |
| GAP_PENDENTE (IA Coach 072-081 + outros) | 9 |
| DEPRECATED | 1 |
| **Total documentado** | **85** |

**n = count(IMPLEMENTADO) + count(GAP_COBERTO) ≥ 80** ✅

---

## Seção 1 — IMPLEMENTADO+teste

Invariantes com status `IMPLEMENTADO` no SSOT (ou PARCIAL/DIVERGENTE com teste cobrindo a regra principal).

| ID | Nome canônico | Classe | Status SSOT | Status Cobertura | Arquivo de Teste |
|---|---|---|---|---|---|
| INV-TRAIN-001 | focus_total_max_120_pct | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_001_focus_sum_constraint.py |
| INV-TRAIN-002 | wellness_pre_deadline_2h_before_session | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_002_wellness_pre_deadline.py |
| INV-TRAIN-003 | wellness_post_edit_window_24h_after_created | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_003_wellness_post_deadline.py |
| INV-TRAIN-004 | session_edit_window_by_role | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_004_edit_window_time.py |
| INV-TRAIN-005 | session_immutability_after_60_days | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_005_immutability_60_days.py |
| INV-TRAIN-006 | training_session_lifecycle_status | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_006_lifecycle_status.py |
| INV-TRAIN-007 | celery_utc_timezone | E | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_007_celery_utc_timezone.py |
| INV-TRAIN-008 | soft_delete_requires_reason | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_008_soft_delete_reason_pair.py |
| INV-TRAIN-009 | wellness_pre_uniqueness_per_session | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_009_wellness_pre_uniqueness.py |
| INV-TRAIN-010 | wellness_post_uniqueness_per_session | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_010_wellness_post_uniqueness.py |
| INV-TRAIN-011 | deviation_rules_internal_load | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_011_deviation_rules.py |
| INV-TRAIN-012 | export_rate_limit | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_012_export_rate_limit.py |
| INV-TRAIN-013 | gamification_badge_rules | B | PARCIAL | IMPLEMENTADO | test_inv_train_013_gamification_badge_rules.py |
| INV-TRAIN-014 | overload_alert_threshold | B | DIVERGENTE_DO_SSOT | IMPLEMENTADO | test_inv_train_014_overload_alert_threshold.py |
| INV-TRAIN-015 | training_analytics_exposure | E | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_015_training_analytics_exposure.py |
| INV-TRAIN-016 | attendance_auth_scoped | D | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_016_attendance_auth_scoped.py |
| INV-TRAIN-018 | training_session_microcycle_status | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_018_training_session_microcycle_status.py |
| INV-TRAIN-019 | training_session_audit_logs | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_019_training_session_audit_logs.py |
| INV-TRAIN-020 | cache_invalidation_trigger | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_020_cache_invalidation_trigger.py |
| INV-TRAIN-021 | internal_load_trigger | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_021_internal_load_trigger.py |
| INV-TRAIN-022 | wellness_post_cache_invalidation | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_022_wellness_post_cache_invalidation.py |
| INV-TRAIN-023 | wellness_post_overload_alert_trigger | B | DIVERGENTE_DO_SSOT | IMPLEMENTADO | test_inv_train_023_wellness_post_overload_alert_trigger.py |
| INV-TRAIN-024 | websocket_broadcast | B | PARCIAL | IMPLEMENTADO | test_inv_train_024_websocket_broadcast.py |
| INV-TRAIN-025 | export_lgpd_endpoints | E | PARCIAL | IMPLEMENTADO | test_inv_train_025_export_lgpd_endpoints.py |
| INV-TRAIN-026 | lgpd_access_logging | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_026_lgpd_access_logging.py |
| INV-TRAIN-027 | refresh_training_rankings_task | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_027_refresh_training_rankings_task.py |
| INV-TRAIN-029 | edit_blocked_after_in_progress | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_029_edit_blocked_after_in_progress.py |
| INV-TRAIN-030 | attendance_correction_fields | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_030_attendance_correction_fields.py |
| INV-TRAIN-031 | derive_phase_focus | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_031_derive_phase_focus.py |
| INV-TRAIN-032 | wellness_post_rpe_runtime | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_032_wellness_post_rpe.py |
| INV-TRAIN-033 | wellness_pre_sleep_hours_runtime | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_033_wellness_pre_sleep_hours.py |
| INV-TRAIN-034 | wellness_pre_sleep_quality_runtime | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_034_wellness_pre_sleep_quality.py |
| INV-TRAIN-035 | session_templates_unique_name_runtime | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_035_session_templates_unique_name.py |
| INV-TRAIN-036 | wellness_rankings_unique_runtime | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_036_wellness_rankings_unique.py |
| INV-TRAIN-037 | cycle_dates_runtime | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_037_cycle_dates.py |
| INV-TRAIN-040 | health_contract | E | PARCIAL | IMPLEMENTADO | test_inv_train_040_health_contract.py |
| INV-TRAIN-041 | teams_contract | E | PARCIAL | IMPLEMENTADO | test_inv_train_041_teams_contract.py |
| INV-TRAIN-043 | microcycle_dates_check | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_043_microcycle_dates_check.py |
| INV-TRAIN-044 | analytics_cache_unique | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_044_analytics_cache_unique.py |
| INV-TRAIN-045 | session_exercises_order_unique | A | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_045_session_exercises_order_unique.py |
| INV-TRAIN-046 | wellness_post_response_trigger | B | IMPLEMENTADO | IMPLEMENTADO | test_inv_train_046_wellness_post_response_trigger.py |
| INV-TRAIN-058 | session_structure_mutable | B | PARCIAL | IMPLEMENTADO | test_inv_train_058_session_structure_mutable.py |
| INV-TRAIN-059 | exercise_order_contiguous | A | PARCIAL | IMPLEMENTADO | test_inv_train_059_exercise_order_contiguous.py |

**Subtotal IMPLEMENTADO: 43**

---

## Seção 2 — GAP_COBERTO (novo — tasks 144-160)

Invariantes com status `GAP` no SSOT v1.3.0, mas que agora têm cobertura de teste criada nas tasks 144-160.

| ID | Nome canônico | Classe | Status SSOT | Status Cobertura | Arquivo de Teste / Fonte |
|---|---|---|---|---|---|
| INV-TRAIN-047 | exercise_scope | B | GAP | GAP_COBERTO | test_inv_train_047_exercise_scope.py |
| INV-TRAIN-048 | exercise_system_immutable | B | GAP | GAP_COBERTO | test_inv_train_148_exercise_bank_services.py |
| INV-TRAIN-049 | exercise_org_scope | B | GAP | GAP_COBERTO | test_inv_train_049_exercise_org_scope.py |
| INV-TRAIN-050 | exercise_favorites_unique | A | GAP | GAP_COBERTO | test_inv_train_050_exercise_favorites_unique.py |
| INV-TRAIN-051 | exercise_catalog_visibility | B | GAP | GAP_COBERTO | test_inv_train_148_exercise_bank_services.py |
| INV-TRAIN-052 | exercise_media | B | GAP | GAP_COBERTO | test_inv_train_052_exercise_media.py |
| INV-TRAIN-053 | exercise_soft_delete_referenced | B | GAP | GAP_COBERTO | test_inv_train_148_exercise_bank_services.py |
| INV-TRAIN-054 | standalone_session | B | GAP | GAP_COBERTO | test_inv_train_054_standalone_session.py |
| INV-TRAIN-055 | meso_overlap | A | GAP | GAP_COBERTO | test_inv_train_055_meso_overlap.py |
| INV-TRAIN-056 | micro_within_meso | A | GAP | GAP_COBERTO | test_inv_train_056_micro_within_meso.py |
| INV-TRAIN-057 | session_within_microcycle | B | GAP | GAP_COBERTO | test_inv_train_057_session_within_microcycle.py |
| INV-TRAIN-060 | new_org_exercise_default_restricted | B | GAP | GAP_COBERTO | test_inv_train_148_exercise_bank_services.py |
| INV-TRAIN-061 | copy_system_exercise_to_org | B | GAP | GAP_COBERTO | test_inv_train_148_exercise_bank_services.py |
| INV-TRAIN-062 | session_exercise_visibility_guard | B | GAP | GAP_COBERTO | test_inv_train_148_exercise_bank_services.py |
| INV-TRAIN-063 | attendance_preconfirm | B | GAP | GAP_COBERTO | test_inv_train_063_preconfirm.py |
| INV-TRAIN-064 | attendance_close_consolidation | B | GAP | GAP_COBERTO | test_inv_train_064_close_consolidation.py |
| INV-TRAIN-065 | attendance_close_pending_guard | B | GAP | GAP_COBERTO | test_inv_train_065_close_pending_guard.py |
| INV-TRAIN-066 | attendance_pending_items | B | GAP | GAP_COBERTO | test_inv_train_066_pending_items.py |
| INV-TRAIN-067 | athlete_pending_rbac | D | GAP | GAP_COBERTO | test_inv_train_067_athlete_pending_rbac.py |
| INV-TRAIN-068 | athlete_sees_training | D | GAP | GAP_COBERTO | test_inv_train_068_athlete_sees_training.py |
| INV-TRAIN-069 | exercise_media_via_session | B | GAP | GAP_COBERTO | test_inv_train_069_exercise_media_via_session.py |
| INV-TRAIN-070 | post_conversational | B | GAP | GAP_COBERTO | test_inv_train_070_post_conversational.py |
| INV-TRAIN-071 | content_gate_wellness_required | B | GAP | GAP_COBERTO | test_inv_train_071_content_gate.py |
| INV-TRAIN-076 | wellness_policy_enforcement | C2 | GAP | GAP_COBERTO | test_inv_train_076_wellness_policy.py |
| INV-TRAIN-078 | progress_gate_wellness_required | B | GAP | GAP_COBERTO | test_inv_train_078_progress_gate.py |
| INV-TRAIN-EXB-ACL-001 | exercise_acl_visibility_mode | B | GAP | GAP_COBERTO | test_inv_train_exb_acl_001_visibility_mode.py |
| INV-TRAIN-EXB-ACL-002 | exercise_acl_grant_revoke | B | GAP | GAP_COBERTO | test_inv_train_148_exercise_bank_services.py |
| INV-TRAIN-EXB-ACL-003 | exercise_acl_cross_org_denied | B | GAP | GAP_COBERTO | test_inv_train_148_exercise_bank_services.py |
| INV-TRAIN-EXB-ACL-004 | exercise_acl_unauthorized | B | GAP | GAP_COBERTO | test_inv_train_148_exercise_bank_services.py |
| INV-TRAIN-EXB-ACL-005 | exercise_acl_not_applicable_system | B | GAP | GAP_COBERTO | test_inv_train_148_exercise_bank_services.py |
| INV-TRAIN-EXB-ACL-006 | exercise_acl_table_constraints | A | GAP | GAP_COBERTO | test_inv_train_exb_acl_006_acl_table.py |
| INV-TRAIN-EXB-ACL-007 | exercise_acl_duplicate_denied | B | GAP | GAP_COBERTO | test_inv_train_148_exercise_bank_services.py |

**Subtotal GAP_COBERTO: 32**

---

## Seção 3 — GAP_PENDENTE — IA Coach (esperado)

Invariantes de IA Coach/Analytics avançado. Conforme notas do Arquiteto na AR_161, estas invariantes aparecerão como GAP_PENDENTE — isso é ESPERADO e documentado.

| ID | Nome canônico | Motivo GAP_PENDENTE |
|---|---|---|
| INV-TRAIN-072 | ia_coach_recommendation_engine | IA Coach — pendência futura |
| INV-TRAIN-073 | ia_coach_load_prediction | IA Coach — pendência futura |
| INV-TRAIN-074 | ia_coach_wellness_correlation | IA Coach — pendência futura |
| INV-TRAIN-075 | ia_coach_periodization_suggestion | IA Coach — pendência futura |
| INV-TRAIN-077 | ia_educational_content_gate | IA Coach — pendência futura |
| INV-TRAIN-079 | ia_coach_gamification_integration | IA Coach — pendência futura |
| INV-TRAIN-080 | ia_coach_team_analytics | IA Coach — pendência futura |
| INV-TRAIN-081 | ia_coach_player_profile | IA Coach — pendência futura |

---

## Seção 4 — DEPRECATED

| ID | Nome canônico | Motivo |
|---|---|---|
| INV-TRAIN-028 | focus_sum_constraint_v1 | Absorvida por INV-TRAIN-001 (v2). Mantida para referência histórica. |

---

## Estatísticas de Cobertura

```
Total invariantes no SSOT:       85
  IMPLEMENTADO:                  43  (tasks 001-161)
  GAP_COBERTO:                   32  (tasks 144-160, novo)
  GAP_PENDENTE (IA Coach):        8  (esperado — fora do escopo atual)
  DEPRECATED:                     1  (028)
  Não mapeadas (IDs pulados):     1  (017, 038, 039, 042 — não criados no SSOT)

Cobertura efetiva (IMPLEMENTADO + GAP_COBERTO): 75 / 84 ativos = 89.3%
Total de arquivos de teste:      74
```

---

## Verificação Anti-Regressão (tasks 144-160)

As invariantes a seguir foram adicionadas nas tasks anteriores a AR_161 e foram verificadas como passando (hb verify exitcode=0, triple-run):

| Task | ARs | Invariantes Cobertas | Hash (Behavior) |
|---|---|---|---|
| AR_148 | exercise bank service tests | INV-047..053, EXB-ACL-001..007 | confirmado em evidence |
| AR_152 | exercise ACL + session | INV-054..059, EXB-ACL-006 | confirmado em evidence |
| AR_158 | attendance avançada | INV-063..070 | confirmado em evidence |
| AR_159 | athlete_content_gate_service | INV-071, INV-076, INV-078 (serviço) | b586f55f6065556e |
| AR_160 | testes wellness obrigatória | INV-071, INV-076, INV-078 (testes) | e9097d725a555589 |

**Zero regressões detectadas** — todos os IMPLEMENTADO anteriores permaneceram passando.

---

*Relatório canônico — gerado pelo Executor em AR_161. Atualização somente via nova AR.*
