# TEST_MATRIX_TRAINING.md — Matriz de Verificação e Rastreabilidade do Módulo TRAINING

Status: DRAFT  
Versão: v1.2.0  
Tipo de Documento: Verification & Traceability Matrix (Normativo Operacional / SSOT)  
Módulo: TRAINING  
Fase: FASE_2 (PRD v2.2 — 2026-02-20) + AS-IS repo (2026-02-25) + DEC-TRAIN-* (2026-02-25)  
Autoridade: NORMATIVO_OPERACIONAL  
Owners:
- Arquitetura: Codex (Arquiteto v2.2.0)
- Auditoria/Testes: (a definir)
- Backend/Frontend: (a definir)

Última revisão: 2026-02-26  
Próxima revisão recomendada: 2026-03-04  

> Changelog v1.2.0 (2026-02-26):  
> - Adicionada Authority Matrix (separação escrita estrutural vs execução)  
> - Adicionada convenção de Classification Tags  
> - Adicionada coluna "Blocking Stage" (PRE/POST/BOTH/NO) em §5, §5b, §8  
> - Adicionada §5c Referência de Blocking Stage por invariante  

> Changelog v1.1.0 (2026-02-25):  
> - Adicionados 14 test rows para novas invariantes INV-TRAIN-047..053, INV-TRAIN-EXB-ACL-001..007  
> - Adicionados 5 contract rows para CONTRACT-TRAIN-091..095  
> - Adicionados testes normativos DEC-TRAIN-001..004 (wellness self-only, mapping, canonical, degraded)  
> - Adicionados AR-TRAIN-011..014 na matriz AR→cobertura  
> - Atualizados critérios PASS/FAIL (§10)  

Dependências:
- `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
- `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md`
- `docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md`
- `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md`
- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`

---

## Authority Matrix

| Aspecto | Regra |
|---|---|
| Fonte de verdade | Composição de todos os docs MCP + evidências de execução |
| Escrita estrutural | **Arquiteto** — estrutura, critérios, coverage obrigatório, classificação, blocking stage |
| Escrita de execução | **Testador** — status de execução, evidências, resultado PASS/FAIL, observações |
| Escrita técnica (evidência) | **Executor** — pode anexar evidência técnica de AR executada; **NÃO redefine** critério |
| Precedência em conflito | Critério do Arquiteto > Resultado do Testador > Evidência do Executor |

> **Separação "estrutura vs execução":** O Arquiteto define *o que* deve ser testado e *quando* bloqueia.
> O Testador registra *o resultado* e a *evidência*. O Executor fornece artefatos técnicos.

---

## Convenção de Tags (Classification)

| Tag | Significado |
|---|---|
| `[NORMATIVO]` | Critério/regra de teste que DEVE ser respeitado. |
| `[DESCRITIVO-AS-IS]` | Estado atual de cobertura/resultado (pode mudar com execução). |
| `[GAP]` | Teste obrigatório sem implementação ou evidência. |

**Aplicação:** Colunas "Status Cobertura" e "Evidência" são `[DESCRITIVO-AS-IS]`. Colunas "Tipo", "Tentativa de Violação", "Blocking Stage" são `[NORMATIVO]` (definidas pelo Arquiteto).

---

## 0) Nota SSOT (bloqueios conhecidos)

1. SSOT atual de schema e OpenAPI está em `docs/ssot/*`.
2. Parte dos testes existentes referencia `Hb Track - Backend/docs/_generated/*` (inexistente no repo atual) ⇒ itens ficam `BLOQUEADO` até `AR-TRAIN-010`.
3. “COBERTO” neste documento significa **teste implementado e apontado**. Resultado de execução permanece `NOT_RUN` até a produção de evidência (`_reports/*`).

Resumo rápido (AS-IS) — invariantes:
- `COBERTO`: 25
- `PARCIAL`: 9
- `BLOQUEADO`: 7
- `NAO_APLICAVEL`: 1
- `PENDENTE` (novos v1.1.0): 14

---

## 1) Objetivo (Normativo)

Garantir rastreabilidade e cobertura verificável entre:
- invariantes do módulo (`INV-TRAIN-*`),
- fluxos (`FLOW-TRAIN-*`),
- telas (`SCREEN-TRAIN-*`),
- contratos (`CONTRACT-TRAIN-*`),
- ARs de materialização (`AR-TRAIN-*`),
- testes (`TEST-TRAIN-*`) e evidências de execução (`_reports/*`).

Este documento define **o que deve ser testado**, **como provar**, e **qual status de cobertura** cada item possui.

---

## 2) Escopo

### 2.1 Dentro do escopo
- Mapeamento de cobertura por item do MCP TRAINING
- Testes de violação para invariantes de validação/constraints
- Testes funcionais dos fluxos principais (E2E ou MANUAL_GUIADO)
- Testes de contrato API (CONTRACT/INTEGRATION) para endpoints críticos
- Evidências mínimas exigidas por item bloqueante

### 2.2 Fora do escopo
- Implementação de testes (código) nesta etapa
- Performance/carga (salvo AR dedicada)
- QA visual/pixel-perfect

---

## 3) Convenções de Classificação

### 3.1 Tipos de teste
- `UNIT` — regra isolada (mocks)
- `INTEGRATION` — DB real (constraints/triggers/services)
- `CONTRACT` — API (FastAPI/TestClient/HTTPX) + contrato (status/payload)
- `E2E` — ponta a ponta automatizado (playwright/cypress) (quando existir)
- `MANUAL_GUIADO` — checklist humano com evidência mínima
- `GATE_CHECK` — checagem estrutural (existência de arquivo/trechos/SSOT)
- `REGRESSION` — re-execução de cenários críticos após mudanças

### 3.2 Severidade (para invariantes)
- `BLOQUEANTE_VALIDACAO` — deve impedir persistência/ação inválida (exige teste de violação)
- `BLOQUEANTE_ARQUITETURA` — exposição/segurança/compliance/determinismo (pode ser GATE_CHECK/CONTRACT)
- `NAO_BLOQUEANTE` — feature opcional/observabilidade
- `DEPRECATED` — mantido só por legado

### 3.3 Status de cobertura (por item)
- `COBERTO` — teste definido + apontado (e evidência de execução pode ser gerada)
- `PARCIAL` — há teste, mas falta teste de violação, falta paridade, ou item está `PARCIAL/DIVERGENTE`
- `PENDENTE` — teste ainda não definido/implementado
- `BLOQUEADO` — dependência impede execução (ex.: `_generated` inexistente; router desabilitado; contrato divergente)
- `NAO_APLICAVEL` — item não aplicável à fase/está deprecated

### 3.4 Resultado da última execução
- `PASS` | `FAIL` | `NOT_RUN`

### 3.5 Tipo de prova esperada (evidência)
- `test_output` (stdout/pytest)
- `report_json`
- `api_response`
- `db_state_before_after`
- `screenshot` (quando UI)
- `manual_checklist`

---

## 4) Regras Normativas de Verificação

1. Toda invariante `BLOQUEANTE_VALIDACAO` deve ter pelo menos 1 **teste de violação** (tentar quebrar a regra).
2. Todo `FLOW-TRAIN-*` `P0` deve ter cobertura `E2E` ou `MANUAL_GUIADO` equivalente até o fechamento da fase.
3. Todo contrato `CONTRACT-TRAIN-*` `P0` deve ter pelo menos 1 teste `CONTRACT` cobrindo:
   - 401/403 (auth),
   - 422 (validação),
   - shape mínimo de response (quando aplicável).
4. Item marcado `COBERTO` deve ter caminho de teste e caminho de evidência esperado.
5. Se o item estiver `BLOQUEADO`, deve apontar a AR que remove o bloqueio.

---

## 5) Matriz de Cobertura por Invariantes

| ID Item | Nome Curto | Severidade | Camada | ID Teste | Tipo | Tentativa de Violação | Criticidade | Blocking | Status Cobertura | Últ. Execução | Evidência (teste) | AR Relacionada |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| INV-TRAIN-001 | focus_total_max_120_pct | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-001 | INTEGRATION | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_001_focus_sum_constraint.py | - |
| INV-TRAIN-002 | wellness_pre_deadline_2h_before_session | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-002 | INTEGRATION | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_002_wellness_pre_deadline.py | AR-TRAIN-003, AR-TRAIN-004 |
| INV-TRAIN-003 | wellness_post_edit_window_24h_after_created | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-003 | UNIT | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_003_wellness_post_deadline.py | AR-TRAIN-003, AR-TRAIN-004 |
| INV-TRAIN-004 | session_edit_window_by_role | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-004 | UNIT | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_004_edit_window_time.py | - |
| INV-TRAIN-005 | session_immutable_after_60_days | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-005 | UNIT | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_005_immutability_60_days.py | - |
| INV-TRAIN-006 | training_session_status_lifecycle | BLOQUEANTE_VALIDACAO | db+calc | TEST-TRAIN-INV-006 | UNIT | NAO | CRITICA | POST | PARCIAL | NOT_RUN | test_inv_train_006_lifecycle_status.py | - |
| INV-TRAIN-007 | celery_uses_utc | BLOQUEANTE_ARQUITETURA | calc | TEST-TRAIN-INV-007 | GATE_CHECK | NAO | ALTA | POST | COBERTO | NOT_RUN | test_inv_train_007_celery_utc_timezone.py | - |
| INV-TRAIN-008 | soft_delete_reason_pair | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-008 | GATE_CHECK | NAO | CRITICA | PRE | BLOQUEADO | NOT_RUN | test_inv_train_008_soft_delete_reason_pair.py (refs _generated) | AR-TRAIN-010 |
| INV-TRAIN-009 | unique_wellness_pre_per_athlete_session | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-009 | INTEGRATION | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_009_wellness_pre_uniqueness.py | AR-TRAIN-003, AR-TRAIN-004 |
| INV-TRAIN-010 | unique_wellness_post_per_athlete_session | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-010 | INTEGRATION | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_010_wellness_post_uniqueness.py | AR-TRAIN-003, AR-TRAIN-004 |
| INV-TRAIN-011 | deviation_rules_and_min_justification | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-011 | GATE_CHECK | NAO | CRITICA | POST | PARCIAL | NOT_RUN | test_inv_train_011_deviation_rules.py | - |
| INV-TRAIN-012 | export_rate_limits_daily | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-012 | GATE_CHECK | NAO | CRITICA | POST | PARCIAL | NOT_RUN | test_inv_train_012_export_rate_limit.py | AR-TRAIN-008, AR-TRAIN-009 |
| INV-TRAIN-013 | gamification_badge_eligibility | NAO_BLOQUEANTE | service | TEST-TRAIN-INV-013 | GATE_CHECK | NAO | MEDIA | NO | PARCIAL | NOT_RUN | test_inv_train_013_gamification_badge_rules.py | AR-TRAIN-010 |
| INV-TRAIN-014 | overload_alert_threshold_multiplier | NAO_BLOQUEANTE | service | TEST-TRAIN-INV-014 | GATE_CHECK | NAO | MEDIA | NO | PARCIAL | NOT_RUN | test_inv_train_014_overload_alert_threshold.py | AR-TRAIN-001, AR-TRAIN-002 |
| INV-TRAIN-015 | training_analytics_endpoints_exposed | BLOQUEANTE_ARQUITETURA | calc+api | TEST-TRAIN-INV-015 | GATE_CHECK | NAO | ALTA | POST | COBERTO | NOT_RUN | test_inv_train_015_training_analytics_exposure.py | - |
| INV-TRAIN-016 | attendance_auth_and_scoped_route_not_exposed | BLOQUEANTE_ARQUITETURA | api | TEST-TRAIN-INV-016 | CONTRACT | SIM | ALTA | POST | COBERTO | NOT_RUN | test_inv_train_016_attendance_auth_scoped.py | - |
| INV-TRAIN-018 | microcycle_session_default_status | BLOQUEANTE_ARQUITETURA | service | TEST-TRAIN-INV-018 | CONTRACT|UNIT | NAO | ALTA | POST | COBERTO | NOT_RUN | test_inv_train_018_training_session_microcycle_status.py, test_inv_train_018_training_session_microcycle_status_route.py | - |
| INV-TRAIN-019 | audit_logs_for_training_session_actions | BLOQUEANTE_ARQUITETURA | service | TEST-TRAIN-INV-019 | INTEGRATION | NAO | ALTA | POST | COBERTO | NOT_RUN | test_inv_train_019_training_session_audit_logs.py | - |
| INV-TRAIN-020 | analytics_cache_invalidation_trigger | BLOQUEANTE_ARQUITETURA | db | TEST-TRAIN-INV-020 | GATE_CHECK | NAO | ALTA | PRE | BLOQUEADO | NOT_RUN | test_inv_train_020_cache_invalidation_trigger.py (refs _generated) | AR-TRAIN-010 |
| INV-TRAIN-021 | internal_load_trigger | BLOQUEANTE_ARQUITETURA | db | TEST-TRAIN-INV-021 | GATE_CHECK | NAO | ALTA | PRE | BLOQUEADO | NOT_RUN | test_inv_train_021_internal_load_trigger.py (refs _generated) | AR-TRAIN-010 |
| INV-TRAIN-022 | wellness_post_invalidates_training_analytics_cache | BLOQUEANTE_ARQUITETURA | calc | TEST-TRAIN-INV-022 | UNIT | NAO | ALTA | POST | COBERTO | NOT_RUN | test_inv_train_022_wellness_post_cache_invalidation.py | - |
| INV-TRAIN-023 | wellness_post_triggers_overload_alert_check | NAO_BLOQUEANTE | service+calc | TEST-TRAIN-INV-023 | UNIT | NAO | MEDIA | NO | PARCIAL | NOT_RUN | test_inv_train_023_wellness_post_overload_alert_trigger.py | AR-TRAIN-001, AR-TRAIN-002 |
| INV-TRAIN-024 | websocket_broadcast_for_alerts_and_badges | NAO_BLOQUEANTE | service+ux | TEST-TRAIN-INV-024 | GATE_CHECK | NAO | MEDIA | NO | PARCIAL | NOT_RUN | test_inv_train_024_websocket_broadcast.py | AR-TRAIN-010 |
| INV-TRAIN-025 | lgpd_export_async_jobs | BLOQUEANTE_ARQUITETURA | calc+api | TEST-TRAIN-INV-025 | GATE_CHECK | NAO | ALTA | POST | PARCIAL | NOT_RUN | test_inv_train_025_export_lgpd_endpoints.py | AR-TRAIN-008, AR-TRAIN-009 |
| INV-TRAIN-026 | lgpd_access_logging | BLOQUEANTE_ARQUITETURA | service | TEST-TRAIN-INV-026 | GATE_CHECK | NAO | ALTA | POST | COBERTO | NOT_RUN | test_inv_train_026_lgpd_access_logging.py | - |
| INV-TRAIN-027 | refresh_training_rankings_task | BLOQUEANTE_ARQUITETURA | calc | TEST-TRAIN-INV-027 | UNIT | NAO | ALTA | POST | COBERTO | NOT_RUN | test_inv_train_027_refresh_training_rankings_task.py | AR-TRAIN-006, AR-TRAIN-007 |
| INV-TRAIN-028 | deprecated_duplicate_focus_rule | DEPRECATED | tests | TEST-TRAIN-INV-028 | GATE_CHECK | NAO | BAIXA | NO | NAO_APLICAVEL | NOT_RUN | test_inv_train_028_focus_sum_constraint.py (refs _generated) | - |
| INV-TRAIN-029 | editing_rules_by_session_status | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-029 | GATE_CHECK | NAO | CRITICA | POST | PARCIAL | NOT_RUN | test_inv_train_029_edit_blocked_after_in_progress.py | - |
| INV-TRAIN-030 | attendance_correction_requires_audit_fields | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-030 | GATE_CHECK | NAO | CRITICA | PRE | BLOQUEADO | NOT_RUN | test_inv_train_030_attendance_correction_fields.py (refs _generated) | AR-TRAIN-010 |
| INV-TRAIN-031 | derive_phase_focus_from_percentages | BLOQUEANTE_ARQUITETURA | db | TEST-TRAIN-INV-031 | GATE_CHECK | NAO | ALTA | PRE | BLOQUEADO | NOT_RUN | test_inv_train_031_derive_phase_focus.py (refs _generated) | AR-TRAIN-010 |
| INV-TRAIN-032 | wellness_post_rpe_range | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-032 | INTEGRATION | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_032_wellness_post_rpe.py, test_inv_train_032_wellness_post_rpe_runtime.py | - |
| INV-TRAIN-033 | wellness_pre_sleep_hours_range | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-033 | INTEGRATION | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_033_wellness_pre_sleep_hours.py, test_inv_train_033_wellness_pre_sleep_hours_runtime.py | - |
| INV-TRAIN-034 | wellness_pre_sleep_quality_range | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-034 | INTEGRATION | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_034_wellness_pre_sleep_quality.py, test_inv_train_034_wellness_pre_sleep_quality_runtime.py | - |
| INV-TRAIN-035 | session_template_unique_name_per_org | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-035 | GATE_CHECK|INTEGRATION | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_035_session_templates_unique_name.py (refs _generated), test_inv_train_035_session_templates_unique_name_runtime.py | - |
| INV-TRAIN-036 | wellness_rankings_unique_team_month | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-036 | GATE_CHECK|INTEGRATION | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_036_wellness_rankings_unique.py (refs _generated), test_inv_train_036_wellness_rankings_unique_runtime.py | AR-TRAIN-006, AR-TRAIN-007 |
| INV-TRAIN-037 | cycle_dates_valid | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-037 | GATE_CHECK|INTEGRATION | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_037_cycle_dates.py (refs _generated), test_inv_train_037_cycle_dates_runtime.py | - |
| INV-TRAIN-040 | openapi_contract_health_public | BLOQUEANTE_ARQUITETURA | api | TEST-TRAIN-INV-040 | CONTRACT | NAO | ALTA | PRE | BLOQUEADO | NOT_RUN | test_inv_train_040_health_contract.py (refs _generated) | AR-TRAIN-010 |
| INV-TRAIN-041 | openapi_contract_teams_auth | BLOQUEANTE_ARQUITETURA | api | TEST-TRAIN-INV-041 | CONTRACT | NAO | ALTA | PRE | BLOQUEADO | NOT_RUN | test_inv_train_041_teams_contract.py (refs _generated) | AR-TRAIN-010 |
| INV-TRAIN-043 | microcycle_dates_valid | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-043 | INTEGRATION | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_043_microcycle_dates_check.py | - |
| INV-TRAIN-044 | analytics_cache_unique_lookup | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-044 | INTEGRATION | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_044_analytics_cache_unique.py | - |
| INV-TRAIN-045 | session_exercises_order_unique | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-045 | INTEGRATION | SIM | CRITICA | POST | COBERTO | NOT_RUN | test_inv_train_045_session_exercises_order_unique.py | - |
| INV-TRAIN-046 | wellness_response_trigger_updates_reminders | BLOQUEANTE_ARQUITETURA | db | TEST-TRAIN-INV-046 | INTEGRATION | NAO | ALTA | POST | COBERTO | NOT_RUN | test_inv_train_046_wellness_post_response_trigger.py | - |
| INV-TRAIN-047 | exercise_scope_valid | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-047 | INTEGRATION | SIM | CRITICA | BOTH | PENDENTE | NOT_RUN | (a criar) | AR-TRAIN-011 |
| INV-TRAIN-048 | system_exercise_immutable_for_org_users | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-048 | CONTRACT | SIM | CRITICA | BOTH | PENDENTE | NOT_RUN | (a criar) | AR-TRAIN-012 |
| INV-TRAIN-049 | org_exercise_single_organization | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-049 | INTEGRATION | SIM | CRITICA | BOTH | PENDENTE | NOT_RUN | (a criar) | AR-TRAIN-011 |
| INV-TRAIN-050 | favorite_unique_per_user_exercise | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-050 | INTEGRATION | SIM | CRITICA | BOTH | PENDENTE | NOT_RUN | (a criar) | AR-TRAIN-011 |
| INV-TRAIN-051 | catalog_visibility_respects_organization | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-051 | CONTRACT | SIM | CRITICA | BOTH | PENDENTE | NOT_RUN | (a criar) | AR-TRAIN-012, AR-TRAIN-013 |
| INV-TRAIN-052 | exercise_media_type_reference_valid | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-052 | INTEGRATION | SIM | ALTA | BOTH | PENDENTE | NOT_RUN | (a criar) | AR-TRAIN-011 |
| INV-TRAIN-053 | soft_delete_exercise_no_break_historic_session | BLOQUEANTE_ARQUITETURA | db+service | TEST-TRAIN-INV-053 | INTEGRATION | NAO | ALTA | BOTH | PENDENTE | NOT_RUN | (a criar) | AR-TRAIN-011 |
| INV-TRAIN-EXB-ACL-001 | exercise_org_visibility_mode_valid | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-EXB-ACL-001 | INTEGRATION | SIM | CRITICA | BOTH | PENDENTE | NOT_RUN | (a criar) | AR-TRAIN-011, AR-TRAIN-013 |
| INV-TRAIN-EXB-ACL-002 | acl_only_for_org_restricted | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-EXB-ACL-002 | CONTRACT | SIM | CRITICA | BOTH | PENDENTE | NOT_RUN | (a criar) | AR-TRAIN-012, AR-TRAIN-013 |
| INV-TRAIN-EXB-ACL-003 | acl_anti_cross_org | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-EXB-ACL-003 | CONTRACT | SIM | CRITICA | BOTH | PENDENTE | NOT_RUN | (a criar) | AR-TRAIN-012, AR-TRAIN-013 |
| INV-TRAIN-EXB-ACL-004 | acl_authority_creator_only | BLOQUEANTE_VALIDACAO | service+api | TEST-TRAIN-INV-EXB-ACL-004 | CONTRACT | SIM | CRITICA | BOTH | PENDENTE | NOT_RUN | (a criar) | AR-TRAIN-012 |
| INV-TRAIN-EXB-ACL-005 | creator_implicit_access | BLOQUEANTE_ARQUITETURA | service | TEST-TRAIN-INV-EXB-ACL-005 | CONTRACT | NAO | ALTA | BOTH | PENDENTE | NOT_RUN | (a criar) | AR-TRAIN-012 |
| INV-TRAIN-EXB-ACL-006 | acl_unique_per_exercise_user | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-EXB-ACL-006 | INTEGRATION | SIM | CRITICA | BOTH | PENDENTE | NOT_RUN | (a criar) | AR-TRAIN-011 |
| INV-TRAIN-EXB-ACL-007 | acl_change_no_retrobreak_historic_session | BLOQUEANTE_ARQUITETURA | service+db | TEST-TRAIN-INV-EXB-ACL-007 | INTEGRATION | NAO | ALTA | BOTH | PENDENTE | NOT_RUN | (a criar) | AR-TRAIN-012 |

### Observações (invariantes) — gaps de cobertura (AS-IS)

- `INV-TRAIN-006`, `INV-TRAIN-011`, `INV-TRAIN-012`, `INV-TRAIN-029`: faltam testes de violação (hoje a cobertura é majoritariamente `GATE_CHECK/UNIT`).
- `INV-TRAIN-008`, `INV-TRAIN-020`, `INV-TRAIN-021`, `INV-TRAIN-030`, `INV-TRAIN-031`, `INV-TRAIN-040`, `INV-TRAIN-041`: `BLOQUEADO` por dependência de `Hb Track - Backend/docs/_generated/*` (migrar para `docs/ssot/*` via `AR-TRAIN-010`).
- `INV-TRAIN-047..053`, `INV-TRAIN-EXB-ACL-001..007`: `PENDENTE` — invariantes novas (v1.1.0, DEC-TRAIN-EXB-*). Schema/service não materializado ainda (GAP-TRAIN-EXB-001..003).

### 5c) Referência de Blocking Stage `[NORMATIVO]`

| Valor | Semântica | Impacto na AR |
|---|---|---|
| **PRE** | Bloqueia **início** da AR — dependência não resolvida impede trabalho | AR não pode sair de DRAFT enquanto bloqueio persistir |
| **POST** | Bloqueia **conclusão** da AR — teste deve passar antes de fechar | AR pode ser implementada, mas não pode ser marcada VERIFICADO sem evidência |
| **BOTH** | Bloqueia início **e** conclusão — requer schema/service + teste | AR depende de materialização prévia (schema, endpoint) E validação posterior |
| **NO** | Não bloqueante — falha não impede progresso da AR | Pode ser tratado em ciclo posterior |

**Classificação padrão:**
- `BLOQUEADO` (Status Cobertura) → `PRE` (dependência impede execução)
- `PENDENTE` + `BLOQUEANTE_*` + GAP de schema → `BOTH` (precisa criar + testar)
- `COBERTO`/`PARCIAL` + `BLOQUEANTE_*` → `POST` (teste existe, deve passar)
- `NAO_BLOQUEANTE` ou `DEPRECATED` → `NO`

### 5b) Testes Normativos por Decisão (DEC-TRAIN-*) — adicionados v1.1.0

| DEC ID | Regra testada | ID Teste | Tipo | Cenário | Happy/Exceção | Blocking | Status Cobertura | AR Relacionada |
|---|---|---|---|---|---|---|---|---|
| DEC-TRAIN-001 | Wellness self-only (sem athlete_id no payload) | TEST-TRAIN-DEC-001a | CONTRACT | POST wellness_pre sem athlete_id → 201 (backend infere do JWT) | Happy | BOTH | PENDENTE | AR-TRAIN-003, AR-TRAIN-004 |
| DEC-TRAIN-001 | Wellness self-only (athlete_id rejeitado) | TEST-TRAIN-DEC-001b | CONTRACT | POST wellness_pre COM athlete_id arbitrário → 422 ou ignorado | Exceção | BOTH | PENDENTE | AR-TRAIN-003, AR-TRAIN-004 |
| DEC-TRAIN-002 | FE→payload mapping (wellness pré) | TEST-TRAIN-DEC-002 | E2E\|MANUAL_GUIADO | Cada slider UI produz campo correto no payload | Happy | POST | PENDENTE | AR-TRAIN-003 |
| DEC-TRAIN-003 | Top performers canônico (FE usa CONTRACT-TRAIN-076) | TEST-TRAIN-DEC-003 | CONTRACT\|E2E | SCREEN-TRAIN-015 faz request para `/teams/{id}/wellness-top-performers` (não 075) | Happy | POST | PENDENTE | AR-TRAIN-007 |
| DEC-TRAIN-004 | Export degradado (sem worker → 202 + degraded) | TEST-TRAIN-DEC-004a | CONTRACT | POST export-pdf sem worker → 202 Accepted com `degraded: true` (não 500) | Exceção | POST | PENDENTE | AR-TRAIN-008, AR-TRAIN-009 |
| DEC-TRAIN-004 | Export degradado (UI mostra banner) | TEST-TRAIN-DEC-004b | MANUAL_GUIADO\|E2E | SCREEN-TRAIN-013 exibe banner de degradação quando `degraded: true` | Happy | POST | PENDENTE | AR-TRAIN-009 |
| DEC-TRAIN-EXB-001 | Scope SYSTEM vs ORG (catálogo) | TEST-TRAIN-DEC-EXB-001 | CONTRACT | GET /exercises retorna SYSTEM+ORG da mesma org; não retorna ORG de outra org | Happy | BOTH | PENDENTE | AR-TRAIN-011, AR-TRAIN-013 |
| DEC-TRAIN-EXB-001B | Visibility restricted filtra por ACL | TEST-TRAIN-DEC-EXB-001B | CONTRACT | GET /exercises não retorna exercício ORG restricted de outra pessoa sem ACL | Exceção | BOTH | PENDENTE | AR-TRAIN-012, AR-TRAIN-013 |
| DEC-TRAIN-EXB-002 | ACL management (CRUD) | TEST-TRAIN-DEC-EXB-002 | CONTRACT | POST/DELETE ACL user + verifica lista | Happy | BOTH | PENDENTE | AR-TRAIN-012, AR-TRAIN-013 |
| DEC-TRAIN-RBAC-001 | Treinador gerencia exercícios ORG próprios | TEST-TRAIN-DEC-RBAC-001a | CONTRACT | PATCH exercise como Treinador creator → 200 | Happy | BOTH | PENDENTE | AR-TRAIN-012 |
| DEC-TRAIN-RBAC-001 | Org user não edita SYSTEM | TEST-TRAIN-DEC-RBAC-001b | CONTRACT | PATCH exercise SYSTEM como Treinador → 403 | Exceção | BOTH | PENDENTE | AR-TRAIN-012 |

---

## 6) Matriz de Cobertura por Fluxos

| ID Flow | Nome do Fluxo | Prioridade | ID Teste | Tipo | Cenário | Happy/Exceção | Status Cobertura | Últ. Execução | Evidência | Screens Relacionadas | Contratos Relacionados |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FLOW-TRAIN-001 | Navegar agenda semanal/mensal | P0 | TEST-TRAIN-FLOW-001 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-001.md` (a gerar) | SCREEN-TRAIN-001 | CONTRACT-TRAIN-001 |
| FLOW-TRAIN-002 | Criar sessão (draft) e publicar (scheduled) | P0 | TEST-TRAIN-FLOW-002 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-002.md` (a gerar) | SCREEN-TRAIN-003, SCREEN-TRAIN-004 | CONTRACT-TRAIN-002, CONTRACT-TRAIN-006 |
| FLOW-TRAIN-003 | Editar sessão e compor treino (foco + exercícios + notas) | P0 | TEST-TRAIN-FLOW-003 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-003.md` (a gerar) | SCREEN-TRAIN-004, SCREEN-TRAIN-005 | CONTRACT-TRAIN-004, CONTRACT-TRAIN-019..024 |
| FLOW-TRAIN-004 | Registrar presença digital (incl. justified) | P0 | TEST-TRAIN-FLOW-004 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-004.md` (a gerar) | SCREEN-TRAIN-020 | CONTRACT-TRAIN-025..028 |
| FLOW-TRAIN-005 | Atleta preencher wellness pré (deadline 2h) | P0 | TEST-TRAIN-FLOW-005 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-005.md` (a gerar) | SCREEN-TRAIN-018 | CONTRACT-TRAIN-030 |
| FLOW-TRAIN-006 | Atleta preencher wellness pós (janela 24h) | P0 | TEST-TRAIN-FLOW-006 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-006.md` (a gerar) | SCREEN-TRAIN-019 | CONTRACT-TRAIN-036 |
| FLOW-TRAIN-007 | Treinador visualizar status wellness da sessão | P1 | TEST-TRAIN-FLOW-007 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-007.md` (a gerar) | SCREEN-TRAIN-004 | CONTRACT-TRAIN-012 |
| FLOW-TRAIN-008 | Planejar ciclos e microciclos | P1 | TEST-TRAIN-FLOW-008 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-008.md` (a gerar) | SCREEN-TRAIN-007, SCREEN-TRAIN-008 | CONTRACT-TRAIN-040..052 |
| FLOW-TRAIN-009 | Gerenciar banco de exercícios e favoritos | P1 | TEST-TRAIN-FLOW-009 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-009.md` (a gerar) | SCREEN-TRAIN-010, SCREEN-TRAIN-011 | CONTRACT-TRAIN-053..062 |
| FLOW-TRAIN-010 | Gerenciar templates de sessão | P1 | TEST-TRAIN-FLOW-010 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-010.md` (a gerar) | SCREEN-TRAIN-017 | CONTRACT-TRAIN-063..068 |
| FLOW-TRAIN-011 | Visualizar analytics e desvios | P1 | TEST-TRAIN-FLOW-011 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-011.md` (a gerar) | SCREEN-TRAIN-012 | CONTRACT-TRAIN-069..071 |
| FLOW-TRAIN-012 | Exportar relatório (PDF) de analytics | P1 | TEST-TRAIN-FLOW-012 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | BLOQUEADO | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-012.md` (a gerar) | SCREEN-TRAIN-012, SCREEN-TRAIN-013 | CONTRACT-TRAIN-086..089 |
| FLOW-TRAIN-013 | Visualizar rankings wellness e top performers | P1 | TEST-TRAIN-FLOW-013 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-013.md` (a gerar) | SCREEN-TRAIN-014, SCREEN-TRAIN-015 | CONTRACT-TRAIN-073..076 |
| FLOW-TRAIN-014 | Visualizar eficácia preventiva | P2 | TEST-TRAIN-FLOW-014 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-014.md` (a gerar) | SCREEN-TRAIN-016 | CONTRACT-TRAIN-072 |
| FLOW-TRAIN-015 | Gerenciar alertas e sugestões (apply/dismiss) | P2 | TEST-TRAIN-FLOW-015 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-FLOW-015.md` (a gerar) | SCREEN-TRAIN-021 | CONTRACT-TRAIN-077..085 |

---

## 7) Matriz de Cobertura por Telas (UI funcional)

| ID Screen | Rota / Entrada | Estado de UI (mínimo) | ID Teste | Tipo | Cenário | Criticidade | Status Cobertura | Últ. Execução | Evidência | AR Relacionada |
|---|---|---|---|---|---|---|---|---|---|---|
| SCREEN-TRAIN-001 | `/training/agenda` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-001 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-001.md` (a gerar) | - |
| SCREEN-TRAIN-002 | `/training/calendario` (redirect) | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-002 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-002.md` (a gerar) | - |
| SCREEN-TRAIN-003 | `CreateSessionModal` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-003 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-003.md` (a gerar) | - |
| SCREEN-TRAIN-004 | `SessionEditorModal` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-004 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-004.md` (a gerar) | - |
| SCREEN-TRAIN-005 | `/training/sessions/[id]/edit` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-005 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-005.md` (a gerar) | - |
| SCREEN-TRAIN-006 | `/training/relatorio/[sessionId]` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-006 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-006.md` (a gerar) | - |
| SCREEN-TRAIN-007 | `/training/planejamento` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-007 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-007.md` (a gerar) | - |
| SCREEN-TRAIN-008 | `CreateCycleWizard` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-008 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-008.md` (a gerar) | - |
| SCREEN-TRAIN-009 | `CopyWeekModal` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-009 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-009.md` (a gerar) | - |
| SCREEN-TRAIN-010 | `/training/exercise-bank` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-010 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-010.md` (a gerar) | - |
| SCREEN-TRAIN-011 | `ExerciseModal` / `CreateExerciseModal` / `EditExerciseModal` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-011 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-011.md` (a gerar) | - |
| SCREEN-TRAIN-012 | `/training/analytics` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-012 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-012.md` (a gerar) | - |
| SCREEN-TRAIN-013 | `ExportPDFModal` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-013 | MANUAL_GUIADO | Smoke funcional + estados | ALTA | BLOQUEADO | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-013.md` (a gerar) | AR-TRAIN-008, AR-TRAIN-009 |
| SCREEN-TRAIN-014 | `/training/rankings` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-014 | MANUAL_GUIADO | Smoke funcional + estados | ALTA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-014.md` (a gerar) | AR-TRAIN-006, AR-TRAIN-007 |
| SCREEN-TRAIN-015 | `/training/top-performers/[teamId]` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-015 | MANUAL_GUIADO | Smoke funcional + estados | ALTA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-015.md` (a gerar) | AR-TRAIN-006, AR-TRAIN-007 |
| SCREEN-TRAIN-016 | `/training/eficacia-preventiva` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-016 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-016.md` (a gerar) | - |
| SCREEN-TRAIN-017 | `/training/configuracoes` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-017 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-017.md` (a gerar) | - |
| SCREEN-TRAIN-018 | `/athlete/wellness-pre/[sessionId]` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-018 | MANUAL_GUIADO | Smoke funcional + estados | ALTA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-018.md` (a gerar) | AR-TRAIN-003, AR-TRAIN-004 |
| SCREEN-TRAIN-019 | `/athlete/wellness-post/[sessionId]` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-019 | MANUAL_GUIADO | Smoke funcional + estados | ALTA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-019.md` (a gerar) | AR-TRAIN-003, AR-TRAIN-004 |
| SCREEN-TRAIN-020 | `/training/presencas` (placeholder) | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-020 | MANUAL_GUIADO | Smoke funcional + estados | ALTA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-020.md` (a gerar) | AR-TRAIN-005 |
| SCREEN-TRAIN-021 | (a definir) Central de Alertas/Sugestões | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-021 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | PENDENTE | NOT_RUN | `_reports/training/TEST-TRAIN-SCREEN-021.md` (a gerar) | AR-TRAIN-001, AR-TRAIN-002 |

---

## 8) Matriz de Cobertura por Contratos Front-Back

> Os shapes mínimos normativos de request/response estão em `TRAINING_FRONT_BACK_CONTRACT.md`. Aqui mapeamos a exigência de validação por endpoint.

| ID Contract | Ação (método + path) | Prioridade | ID Teste | Tipo | Blocking | Status Cobertura | Últ. Execução | Evidência | AR Relacionada |
|---|---|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-001 | GET `/training-sessions` | P0 | TEST-TRAIN-CONTRACT-001 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-002 | POST `/training-sessions` | P0 | TEST-TRAIN-CONTRACT-002 | CONTRACT | POST | PARCIAL | NOT_RUN | `Hb Track - Backend/tests/training/invariants/test_inv_train_018_training_session_microcycle_status_route.py` | - |
| CONTRACT-TRAIN-003 | GET `/training-sessions/{training_session_id}` | P0 | TEST-TRAIN-CONTRACT-003 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-004 | PATCH `/training-sessions/{training_session_id}` | P0 | TEST-TRAIN-CONTRACT-004 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-005 | DELETE `/training-sessions/{training_session_id}?reason=` | P0 | TEST-TRAIN-CONTRACT-005 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-006 | POST `/training-sessions/{training_session_id}/publish` | P0 | TEST-TRAIN-CONTRACT-006 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-007 | POST `/training-sessions/{training_session_id}/close` | P0 | TEST-TRAIN-CONTRACT-007 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-008 | POST `/training-sessions/{training_session_id}/duplicate` | P0 | TEST-TRAIN-CONTRACT-008 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-009 | POST `/training-sessions/{training_session_id}/restore` | P0 | TEST-TRAIN-CONTRACT-009 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-010 | POST `/training-sessions/copy-week` | P0 | TEST-TRAIN-CONTRACT-010 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-011 | GET `/training-sessions/{training_session_id}/deviation` | P0 | TEST-TRAIN-CONTRACT-011 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-012 | GET `/training-sessions/{training_session_id}/wellness-status` | P0 | TEST-TRAIN-CONTRACT-012 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-013 | GET `/teams/{team_id}/trainings` | P0 | TEST-TRAIN-CONTRACT-013 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-014 | POST `/teams/{team_id}/trainings` | P0 | TEST-TRAIN-CONTRACT-014 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-015 | GET `/teams/{team_id}/trainings/{training_id}` | P0 | TEST-TRAIN-CONTRACT-015 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-016 | PATCH `/teams/{team_id}/trainings/{training_id}` | P0 | TEST-TRAIN-CONTRACT-016 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-017 | DELETE `/teams/{team_id}/trainings/{training_id}?reason=` | P0 | TEST-TRAIN-CONTRACT-017 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-018 | POST `/teams/{team_id}/trainings/{training_id}/restore` | P0 | TEST-TRAIN-CONTRACT-018 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-019 | GET `/training-sessions/{session_id}/exercises` | P0 | TEST-TRAIN-CONTRACT-019 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-020 | POST `/training-sessions/{session_id}/exercises` | P0 | TEST-TRAIN-CONTRACT-020 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-021 | POST `/training-sessions/{session_id}/exercises/bulk` | P0 | TEST-TRAIN-CONTRACT-021 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-022 | PATCH `/training-sessions/exercises/{session_exercise_id}` | P0 | TEST-TRAIN-CONTRACT-022 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-023 | PATCH `/training-sessions/{session_id}/exercises/reorder` | P0 | TEST-TRAIN-CONTRACT-023 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-024 | DELETE `/training-sessions/exercises/{session_exercise_id}` | P0 | TEST-TRAIN-CONTRACT-024 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-025 | GET `/training_sessions/{training_session_id}/attendance` | P0 | TEST-TRAIN-CONTRACT-025 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-005 |
| CONTRACT-TRAIN-026 | POST `/training_sessions/{training_session_id}/attendance` | P0 | TEST-TRAIN-CONTRACT-026 | CONTRACT | POST | PARCIAL | NOT_RUN | `Hb Track - Backend/tests/training/invariants/test_inv_train_016_attendance_auth_scoped.py` | AR-TRAIN-005 |
| CONTRACT-TRAIN-027 | POST `/training_sessions/{training_session_id}/attendance/batch` | P0 | TEST-TRAIN-CONTRACT-027 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-005 |
| CONTRACT-TRAIN-028 | GET `/training_sessions/{training_session_id}/attendance/statistics` | P0 | TEST-TRAIN-CONTRACT-028 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-005 |
| CONTRACT-TRAIN-029 | GET `/wellness-pre/training_sessions/{training_session_id}/wellness_pre` | P0 | TEST-TRAIN-CONTRACT-029 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-030 | POST `/wellness-pre/training_sessions/{training_session_id}/wellness_pre` | P0 | TEST-TRAIN-CONTRACT-030 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-031 | GET `/wellness-pre/training_sessions/{training_session_id}/wellness_pre/status` | P0 | TEST-TRAIN-CONTRACT-031 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-032 | GET `/wellness-pre/wellness_pre/{wellness_pre_id}` | P0 | TEST-TRAIN-CONTRACT-032 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-033 | PATCH `/wellness-pre/wellness_pre/{wellness_pre_id}` | P0 | TEST-TRAIN-CONTRACT-033 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-034 | POST `/wellness-pre/wellness_pre/{wellness_pre_id}/request-unlock` | P0 | TEST-TRAIN-CONTRACT-034 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-035 | GET `/wellness-post/training_sessions/{training_session_id}/wellness_post` | P0 | TEST-TRAIN-CONTRACT-035 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-036 | POST `/wellness-post/training_sessions/{training_session_id}/wellness_post` | P0 | TEST-TRAIN-CONTRACT-036 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-037 | GET `/wellness-post/training_sessions/{training_session_id}/wellness_post/status` | P0 | TEST-TRAIN-CONTRACT-037 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-038 | GET `/wellness-post/wellness_post/{wellness_post_id}` | P0 | TEST-TRAIN-CONTRACT-038 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-039 | PATCH `/wellness-post/wellness_post/{wellness_post_id}` | P0 | TEST-TRAIN-CONTRACT-039 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-040 | GET `/training-cycles` | P1 | TEST-TRAIN-CONTRACT-040 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-041 | GET `/training-cycles/{cycle_id}` | P1 | TEST-TRAIN-CONTRACT-041 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-042 | POST `/training-cycles` | P1 | TEST-TRAIN-CONTRACT-042 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-043 | PATCH `/training-cycles/{cycle_id}` | P1 | TEST-TRAIN-CONTRACT-043 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-044 | DELETE `/training-cycles/{cycle_id}?reason=` | P1 | TEST-TRAIN-CONTRACT-044 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-045 | GET `/training-cycles/teams/{team_id}/active` | P1 | TEST-TRAIN-CONTRACT-045 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-046 | GET `/training-microcycles` | P1 | TEST-TRAIN-CONTRACT-046 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-047 | GET `/training-microcycles/{microcycle_id}` | P1 | TEST-TRAIN-CONTRACT-047 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-048 | POST `/training-microcycles` | P1 | TEST-TRAIN-CONTRACT-048 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-049 | PATCH `/training-microcycles/{microcycle_id}` | P1 | TEST-TRAIN-CONTRACT-049 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-050 | DELETE `/training-microcycles/{microcycle_id}?reason=` | P1 | TEST-TRAIN-CONTRACT-050 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-051 | GET `/training-microcycles/teams/{team_id}/current` | P1 | TEST-TRAIN-CONTRACT-051 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-052 | GET `/training-microcycles/{microcycle_id}/summary` | P1 | TEST-TRAIN-CONTRACT-052 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-053 | GET `/exercises` | P1 | TEST-TRAIN-CONTRACT-053 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-054 | POST `/exercises` | P1 | TEST-TRAIN-CONTRACT-054 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-055 | GET `/exercises/{exercise_id}` | P1 | TEST-TRAIN-CONTRACT-055 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-056 | PATCH `/exercises/{exercise_id}` | P1 | TEST-TRAIN-CONTRACT-056 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-057 | GET `/exercise-tags` | P1 | TEST-TRAIN-CONTRACT-057 | CONTRACT | NO | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-058 | POST `/exercise-tags` | P1 | TEST-TRAIN-CONTRACT-058 | CONTRACT | NO | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-059 | PATCH `/exercise-tags/{tag_id}` | P1 | TEST-TRAIN-CONTRACT-059 | CONTRACT | NO | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-060 | GET `/exercise-favorites` | P1 | TEST-TRAIN-CONTRACT-060 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-061 | POST `/exercise-favorites` | P1 | TEST-TRAIN-CONTRACT-061 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-062 | DELETE `/exercise-favorites/{exercise_id}` | P1 | TEST-TRAIN-CONTRACT-062 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-063 | GET `/session-templates` | P1 | TEST-TRAIN-CONTRACT-063 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-064 | POST `/session-templates` | P1 | TEST-TRAIN-CONTRACT-064 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-065 | GET `/session-templates/{template_id}` | P1 | TEST-TRAIN-CONTRACT-065 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-066 | PATCH `/session-templates/{template_id}` | P1 | TEST-TRAIN-CONTRACT-066 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-067 | DELETE `/session-templates/{template_id}` | P1 | TEST-TRAIN-CONTRACT-067 | CONTRACT | NO | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-068 | PATCH `/session-templates/{template_id}/favorite` | P1 | TEST-TRAIN-CONTRACT-068 | CONTRACT | NO | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-069 | GET `/analytics/team/{team_id}/summary` | P1 | TEST-TRAIN-CONTRACT-069 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-070 | GET `/analytics/team/{team_id}/weekly-load` | P1 | TEST-TRAIN-CONTRACT-070 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-071 | GET `/analytics/team/{team_id}/deviation-analysis` | P1 | TEST-TRAIN-CONTRACT-071 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-072 | GET `/analytics/team/{team_id}/prevention-effectiveness` | P1 | TEST-TRAIN-CONTRACT-072 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | - |
| CONTRACT-TRAIN-073 | GET `/analytics/wellness-rankings` | P1 | TEST-TRAIN-CONTRACT-073 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-006, AR-TRAIN-007 |
| CONTRACT-TRAIN-074 | POST `/analytics/wellness-rankings/calculate` | P1 | TEST-TRAIN-CONTRACT-074 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-006, AR-TRAIN-007 |
| CONTRACT-TRAIN-075 | GET `/analytics/wellness-rankings/{team_id}/athletes-90plus?month=` | P1 | TEST-TRAIN-CONTRACT-075 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-006, AR-TRAIN-007 |
| CONTRACT-TRAIN-076 | GET `/teams/{team_id}/wellness-top-performers?month=` | P1 | TEST-TRAIN-CONTRACT-076 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-006, AR-TRAIN-007 |
| CONTRACT-TRAIN-077 | GET `/training/alerts-suggestions/alerts/team/{team_id}/active` | P2 | TEST-TRAIN-CONTRACT-077 | CONTRACT | PRE | BLOQUEADO | NOT_RUN | `-` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-078 | GET `/training/alerts-suggestions/alerts/team/{team_id}/history` | P2 | TEST-TRAIN-CONTRACT-078 | CONTRACT | PRE | BLOQUEADO | NOT_RUN | `-` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-079 | GET `/training/alerts-suggestions/alerts/team/{team_id}/stats` | P2 | TEST-TRAIN-CONTRACT-079 | CONTRACT | PRE | BLOQUEADO | NOT_RUN | `-` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-080 | POST `/training/alerts-suggestions/alerts/{alert_id}/dismiss` | P2 | TEST-TRAIN-CONTRACT-080 | CONTRACT | PRE | BLOQUEADO | NOT_RUN | `-` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-081 | GET `/training/alerts-suggestions/suggestions/team/{team_id}/pending` | P2 | TEST-TRAIN-CONTRACT-081 | CONTRACT | PRE | BLOQUEADO | NOT_RUN | `-` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-082 | GET `/training/alerts-suggestions/suggestions/team/{team_id}/history` | P2 | TEST-TRAIN-CONTRACT-082 | CONTRACT | PRE | BLOQUEADO | NOT_RUN | `-` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-083 | GET `/training/alerts-suggestions/suggestions/team/{team_id}/stats` | P2 | TEST-TRAIN-CONTRACT-083 | CONTRACT | PRE | BLOQUEADO | NOT_RUN | `-` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-084 | POST `/training/alerts-suggestions/suggestions/{suggestion_id}/apply` | P2 | TEST-TRAIN-CONTRACT-084 | CONTRACT | PRE | BLOQUEADO | NOT_RUN | `-` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-085 | POST `/training/alerts-suggestions/suggestions/{suggestion_id}/dismiss` | P2 | TEST-TRAIN-CONTRACT-085 | CONTRACT | PRE | BLOQUEADO | NOT_RUN | `-` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-086 | POST `/analytics/export-pdf` | P1 | TEST-TRAIN-CONTRACT-086 | CONTRACT | PRE | BLOQUEADO | NOT_RUN | `-` | AR-TRAIN-008, AR-TRAIN-009 |
| CONTRACT-TRAIN-087 | GET `/analytics/exports/{job_id}` | P1 | TEST-TRAIN-CONTRACT-087 | CONTRACT | PRE | BLOQUEADO | NOT_RUN | `-` | AR-TRAIN-008, AR-TRAIN-009 |
| CONTRACT-TRAIN-088 | GET `/analytics/exports` | P1 | TEST-TRAIN-CONTRACT-088 | CONTRACT | PRE | BLOQUEADO | NOT_RUN | `-` | AR-TRAIN-008, AR-TRAIN-009 |
| CONTRACT-TRAIN-089 | GET `/analytics/export-rate-limit` | P1 | TEST-TRAIN-CONTRACT-089 | CONTRACT | PRE | BLOQUEADO | NOT_RUN | `-` | AR-TRAIN-008, AR-TRAIN-009 |
| CONTRACT-TRAIN-090 | GET `/athletes/me/export-data?format=json|csv` | P1 | TEST-TRAIN-CONTRACT-090 | CONTRACT | PRE | BLOQUEADO | NOT_RUN | `-` | AR-TRAIN-008, AR-TRAIN-009 |
| CONTRACT-TRAIN-091 | PATCH `/exercises/{exercise_id}/visibility` | P1 | TEST-TRAIN-CONTRACT-091 | CONTRACT | BOTH | PENDENTE | NOT_RUN | `-` | AR-TRAIN-012, AR-TRAIN-013 |
| CONTRACT-TRAIN-092 | GET `/exercises/{exercise_id}/acl` | P1 | TEST-TRAIN-CONTRACT-092 | CONTRACT | BOTH | PENDENTE | NOT_RUN | `-` | AR-TRAIN-012, AR-TRAIN-013 |
| CONTRACT-TRAIN-093 | POST `/exercises/{exercise_id}/acl` | P1 | TEST-TRAIN-CONTRACT-093 | CONTRACT | BOTH | PENDENTE | NOT_RUN | `-` | AR-TRAIN-012, AR-TRAIN-013 |
| CONTRACT-TRAIN-094 | DELETE `/exercises/{exercise_id}/acl/{user_id}` | P1 | TEST-TRAIN-CONTRACT-094 | CONTRACT | BOTH | PENDENTE | NOT_RUN | `-` | AR-TRAIN-012, AR-TRAIN-013 |
| CONTRACT-TRAIN-095 | POST `/exercises/{exercise_id}/copy-to-org` | P1 | TEST-TRAIN-CONTRACT-095 | CONTRACT | BOTH | PENDENTE | NOT_RUN | `-` | AR-TRAIN-011, AR-TRAIN-013 |

---

## 9) Mapa AR -> Cobertura -> Evidência

| AR ID | Classe | Itens SSOT alvo | Testes previstos (IDs) | Evidências mínimas esperadas | Status |
|---|---|---|---|---|---|
| AR-TRAIN-001 | E | CONTRACT-TRAIN-077..085, INV-TRAIN-014 | TEST-TRAIN-CONTRACT-077..085, TEST-TRAIN-INV-014 | diff router + OpenAPI SSOT + test_output | PENDENTE |
| AR-TRAIN-002 | B | INV-TRAIN-014, INV-TRAIN-023 | TEST-TRAIN-INV-014, TEST-TRAIN-INV-023 | db_state_before_after + test_output | PENDENTE |
| AR-TRAIN-003 | D | FLOW-TRAIN-005/006, SCREEN-TRAIN-018/019, CONTRACT-TRAIN-029..039 | TEST-TRAIN-FLOW-005/006, TEST-TRAIN-SCREEN-018/019 | screenshot + manual_checklist | PENDENTE |
| AR-TRAIN-004 | B/E | INV-TRAIN-002/003/026, CONTRACT-TRAIN-029..039 | TEST-TRAIN-INV-002/003/026, TEST-TRAIN-CONTRACT-029..039 | test_output + api_response | PENDENTE |
| AR-TRAIN-005 | D | FLOW-TRAIN-004, SCREEN-TRAIN-020, CONTRACT-TRAIN-025..028 | TEST-TRAIN-FLOW-004, TEST-TRAIN-SCREEN-020 | screenshot + manual_checklist | PENDENTE |
| AR-TRAIN-006 | B/C/E | CONTRACT-TRAIN-073..075, INV-TRAIN-036/027 | TEST-TRAIN-INV-036/027, TEST-TRAIN-CONTRACT-073..075 | test_output + api_response | PENDENTE |
| AR-TRAIN-007 | D | SCREEN-TRAIN-014/015, CONTRACT-TRAIN-073..076 | TEST-TRAIN-SCREEN-014/015, TEST-TRAIN-FLOW-013 | screenshot + manual_checklist | PENDENTE |
| AR-TRAIN-008 | E | CONTRACT-TRAIN-086..090, INV-TRAIN-012/025 | TEST-TRAIN-CONTRACT-086..090, TEST-TRAIN-INV-012/025 | OpenAPI SSOT atualizado + api_response | PENDENTE |
| AR-TRAIN-009 | D | FLOW-TRAIN-012, SCREEN-TRAIN-013, CONTRACT-TRAIN-086..089 | TEST-TRAIN-FLOW-012, TEST-TRAIN-SCREEN-013 | screenshot + manual_checklist | PENDENTE |
| AR-TRAIN-010 | T | Atualizar cobertura + corrigir referências SSOT | TEST-TRAIN-INV-008/020/021/030/031/040/041 | test_output + report_json | PENDENTE |
| AR-TRAIN-011 | A | Schema exercises+exercise_acl+exercise_media | TEST-TRAIN-INV-047/049/050/052/053, TEST-TRAIN-INV-EXB-ACL-001/006 | db_state_before_after + test_output | PENDENTE |
| AR-TRAIN-012 | C | Guards/RBAC + ACL service layer | TEST-TRAIN-INV-048/051, TEST-TRAIN-INV-EXB-ACL-002..005/007, TEST-TRAIN-DEC-RBAC-001a/b | test_output + api_response | PENDENTE |
| AR-TRAIN-013 | E | Endpoints ACL/copy/visibility (CONTRACT-TRAIN-091..095) | TEST-TRAIN-CONTRACT-091..095, TEST-TRAIN-DEC-EXB-001/001B/002 | OpenAPI SSOT + api_response | PENDENTE |
| AR-TRAIN-014 | D | UI exercise-bank FE (scope/ACL/media/copy) | TEST-TRAIN-SCREEN-010/011 (atualizado) | screenshot + manual_checklist | PENDENTE |

---

## 10) Critérios de PASS/FAIL da Fase (Matriz)

### PASS (fase TRAINING) se:
- [ ] Todos os `INV-TRAIN-*` `BLOQUEANTE_VALIDACAO` = `COBERTO` (ou `PARCIAL` com justificativa aprovada)
- [ ] Todos os flows `P0` = `COBERTO` via `E2E` ou `MANUAL_GUIADO`
- [ ] Todos os contratos `P0` = `COBERTO` via `CONTRACT`
- [ ] Evidências referenciadas em `_reports/*` para itens críticos
- [ ] Sem itens críticos `FAIL` sem plano (AR) de correção
- [ ] DEC-TRAIN-001: Teste de wellness self-only (sem athlete_id) com PASS (TEST-TRAIN-DEC-001a/b)
- [ ] DEC-TRAIN-003: FE consome CONTRACT-TRAIN-076 como canônico (TEST-TRAIN-DEC-003)
- [ ] DEC-TRAIN-004: Export degradado retorna 202 (não 500) sem worker (TEST-TRAIN-DEC-004a)
- [ ] DEC-TRAIN-EXB-*: Invariantes de scope/ACL/visibility cobertas (14 novas INV com testes)

### FAIL (fase TRAINING) se:
- [ ] Alguma invariante `BLOQUEANTE_VALIDACAO` sem teste de violação (não justificável)
- [ ] `FLOW-TRAIN-001..006` (P0) sem evidência
- [ ] Contratos `BLOQUEADO` sem AR associada
- [ ] Itens marcados `COBERTO` sem evidência mínima exigida

---

## 11) Protocolo de Atualização (normativo)

Toda mudança em:
- `INVARIANTS_TRAINING.md` ⇒ atualizar §5
- `TRAINING_USER_FLOWS.md` ⇒ atualizar §6
- `TRAINING_SCREENS_SPEC.md` ⇒ atualizar §7
- `TRAINING_FRONT_BACK_CONTRACT.md` ⇒ atualizar §8
- `AR_BACKLOG_TRAINING.md` ⇒ atualizar §9

Regra:
- Atualização desta matriz é obrigatória no mesmo ciclo da AR (ou marcar explicitamente `BLOQUEADO` com motivo).

---

## 12) Checklist do Auditor (rápido)

- [ ] Cada `INV-TRAIN-*` `BLOQUEANTE_VALIDACAO` tem teste de violação (`SIM`)
- [ ] `COBERTO` não foi usado por inferência (há caminho de teste + evidência esperada)
- [ ] Flows `P0` têm `MANUAL_GUIADO` ou `E2E` com evidência
- [ ] Contratos `P0` têm validação de auth + 422 + shape mínimo
- [ ] Itens `BLOQUEADO` têm AR associada
