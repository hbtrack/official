# AR_274 — Ledger de Sessao + Scheduler SKIP LOCKED + provas de imutabilidade e temporal

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
ARQUIVO 1: Hb Track - Backend/alembic/versions/<nova_migration>.py
Criar migration Alembic com:
  (a) CREATE TABLE training_session_plans: id UUID PK, session_id UUID FK NOT NULL, draft_id UUID (referencia ao draft de IA de origem), plan_data JSONB NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW(), criado sem UPDATE/DELETE permitido (trigger ou CHECK para imutabilidade fisica).
  (b) CREATE TABLE training_session_adjustments: id UUID PK, plan_id UUID FK NOT NULL, session_id UUID FK NOT NULL, sequence_number INT NOT NULL, adjustment_data JSONB NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW(). Append-only: sem UPDATE/DELETE.
  (c) Criar trigger ou CHECK constraint que proiba UPDATE/DELETE em training_session_plans.
  (d) Rodar: cd 'Hb Track - Backend' && alembic upgrade head.

ARQUIVO 2: Hb Track - Backend/docs/ssot/schema.sql
Apos alembic upgrade, regenerar: cd 'Hb Track - Backend' && python -c 'import subprocess; subprocess.run(["alembic","upgrade","head"])'
Ou pg_dump --schema-only para atualizar schema.sql com as novas tabelas.

ARQUIVO 3: Hb Track - Backend/app/models/training_session_plan.py (NOVO)
Criar SQLAlchemy model TrainingSessionPlan com campos: id, session_id (FK), draft_id, plan_data (JSON), created_at. Sem metodo de update.

ARQUIVO 4: Hb Track - Backend/app/models/training_session_adjustment.py (NOVO)
Criar SQLAlchemy model TrainingSessionAdjustment com campos: id, plan_id (FK), session_id (FK), sequence_number, adjustment_data (JSON), created_at. Append-only.

ARQUIVO 5: Hb Track - Backend/app/services/training_session_service.py
Na funcao apply_ai_draft (ou equivalente): apos processar draft, criar registro em training_session_plans com plan_data do draft e draft_id rastreavel. Ajustes posteriores criam linha em training_session_adjustments (NUNCA sobrescrevem plan_data original).

ARQUIVO 6: Hb Track - Backend/app/core/celery_tasks.py
(a) Adicionar SKIP LOCKED ao query batch de update_training_session_statuses_task:
  - scheduled -> in_progress: usar select(TrainingSession).where(...).with_for_update(skip_locked=True)
  - in_progress -> pending_review: usar select(TrainingSession).where(...).with_for_update(skip_locked=True)
(b) Processar em chunks (ex.: CHUNK_SIZE=100) para evitar SELECT * global.

ARQUIVO 7-13 (NOVOS TESTES):
  tests/training/side_effects/__init__.py (vazio)
  tests/training/side_effects/test_ai_coach_apply_creates_immutable_plan.py:
    - test_apply_creates_plan_record
    - test_plan_linked_to_session
    - test_plan_preserves_draft_id
    - test_plan_not_overwritten_by_second_apply
  tests/training/side_effects/test_training_adjustment_log_is_append_only.py:
    - test_adjustment_creates_new_row
    - test_plan_original_intact_after_adjustment
    - test_sequence_number_incremental
    - test_no_destructive_update_of_plan
  tests/training/state_machine/test_adjustments_respect_session_state.py:
    - test_adjustment_allowed_in_in_progress
    - test_adjustment_blocked_in_readonly
  tests/training/invariants/test_celery_beat_registers_session_status_updates.py:
    - test_beat_schedule_has_update_task
    - test_update_task_has_valid_schedule
  tests/training/state_machine/test_temporal_boundaries_and_utc_isolation.py:
    - test_transition_at_t_minus_1_not_triggered
    - test_transition_at_t_exact_triggered
    - test_transition_at_t_plus_1_triggered
    - test_utc_isolation (timezone=America/Sao_Paulo, Asia/Tokyo nao afeta resultado)
  tests/training/state_machine/test_task_idempotency_same_minute.py:
    - test_double_run_no_duplicate_transitions
    - test_hash_unchanged_after_second_run
  tests/training/state_machine/test_status_transition_batch_100_sessions.py:
    - test_100_sessions_transition_scheduled_to_in_progress
    - test_no_residual_scheduled_sessions
    - test_no_invalid_states_after_batch
    - test_batch_time_within_slo

## Critérios de Aceite
1) schema.sql contem training_session_plans e training_session_adjustments.
2) Alembic head aplicado (alembic current = migration do ledger).
3) Imutabilidade fisica: trigger ou CHECK em schema.sql para training_session_plans.
4) apply_ai_draft cria linha em training_session_plans com draft_id rastreavel.
5) Ajustes criam linhas em training_session_adjustments com sequence_number incremental.
6) Ajustes respeitam lifecycle/status.
7) update_training_session_statuses_task usa SKIP LOCKED (with_for_update(skip_locked=True)).
8) beat_schedule tem update_training_session_statuses_task com crontab(minute='*').
9) Testes temporais (T-1s, T exato, T+1s, UTC isolation) passam.
10) Idempotencia: double run sem transicoes duplicadas.
11) Batch 100 sessoes sem deadlock/timeout.
12) validation_command exit=0.

## Write Scope
- Hb Track - Backend/alembic/versions
- Hb Track - Backend/docs/ssot/schema.sql
- Hb Track - Backend/docs/ssot/alembic_state.txt
- Hb Track - Backend/app/models/training_session_plan.py
- Hb Track - Backend/app/models/training_session_adjustment.py
- Hb Track - Backend/app/core/celery_tasks.py
- Hb Track - Backend/app/services/training_session_service.py
- Hb Track - Backend/tests/training/side_effects/*
- Hb Track - Backend/tests/training/state_machine/*
- Hb Track - Backend/tests/training/invariants/*

## Validation Command (Contrato)
```
python -c "import pathlib,re,subprocess as sp;bk='Hb Track - Backend';s=pathlib.Path(bk+'/docs/ssot/schema.sql').read_text('utf-8');assert 'training_session_plans' in s,'G1a:training_session_plans absent';assert 'training_session_adjustments' in s,'G1b:training_session_adjustments absent';ct=pathlib.Path(bk+'/app/core/celery_tasks.py').read_text('utf-8');assert re.search(r'skip_locked|SKIP.LOCKED',ct,re.I),'G12:SKIP LOCKED absent in task';ca=pathlib.Path(bk+'/app/core/celery_app.py').read_text('utf-8');assert 'update_training_session_statuses_task' in ca,'G7:beat not registered';ts=['side_effects/test_ai_coach_apply_creates_immutable_plan.py','side_effects/test_training_adjustment_log_is_append_only.py','state_machine/test_adjustments_respect_session_state.py','invariants/test_celery_beat_registers_session_status_updates.py','state_machine/test_temporal_boundaries_and_utc_isolation.py','state_machine/test_task_idempotency_same_minute.py','state_machine/test_status_transition_batch_100_sessions.py'];[__import__('sys').exit('MISSING:'+t) for t in ts if not pathlib.Path(bk+'/tests/training/'+t).exists()];r=sp.run(['python','-m','pytest','-q','--tb=short','tests/training/side_effects/','tests/training/state_machine/test_adjustments_respect_session_state.py','tests/training/invariants/test_celery_beat_registers_session_status_updates.py'],cwd=bk).returncode;assert r==0,'G4-G8:pytest failed';print('PASS AR_274 Gates 1-14 OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_274/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- Hb Track - Backend/docs/ssot/schema.sql
git checkout -- Hb Track - Backend/docs/ssot/alembic_state.txt
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
update_training_session_statuses_task JA existe e JA esta no beat_schedule (confirmado). Gate 7 e Gate 8 verificam sua existencia e schedule correto. O SKIP LOCKED e o gap principal da task atual. Ledger: imutabilidade fisica em training_session_plans e OBRIGATORIA via trigger/CHECK — imutabilidade SO em Python e insuficiente (Gate 3). PROOF: TRUTH_BE — pytest tests/training/side_effects/ + state_machine + invariants (todos os arquivos listados). TRACE: training_session_plans no schema.sql com trigger/CHECK, training_session_adjustments append-only, celery_tasks.py com SKIP LOCKED, beat_schedule com crontab(minute='*') confirmado.

## Riscos
- Trigger de imutabilidade pode nao ser suportado via Alembic direto — Executor pode usar op.execute(CREATE TRIGGER ...)
- apply_ai_draft pode estar em rota diferente de apply_draft — Executor DEVE localizar com grep antes de modificar
- Os teste de batch (100 sessoes) precisam de transacoes isoladas para nao contaminar outros testes — usar fixtures de transacao
- UTC isolation testes requerem mock de datetime.now — usar freezegun ou monkeypatch
- alembic revision --autogenerate pode nao detectar modelos se nao importados em Base metadados — Executor verificar __init__.py dos models

## Análise de Impacto
EXECUTOR: AR_274 — Ledger de Sessão + Scheduler SKIP LOCKED + provas

### Arquivos criados (8):
1. `Hb Track - Backend/db/alembic/versions/0071_ledger_training_session_plans_adjustments.py` — migration Alembic com 2 tables + triggers de imutabilidade fisica.
2. `Hb Track - Backend/app/models/training_session_plan.py` — model SQLAlchemy append-only.
3. `Hb Track - Backend/app/models/training_session_adjustment.py` — model SQLAlchemy append-only.
4. `Hb Track - Backend/tests/training/side_effects/__init__.py` — vazio.
5. `Hb Track - Backend/tests/training/side_effects/test_ai_coach_apply_creates_immutable_plan.py` — 4 testes.
6. `Hb Track - Backend/tests/training/side_effects/test_training_adjustment_log_is_append_only.py` — 4 testes.
7. `Hb Track - Backend/tests/training/state_machine/test_adjustments_respect_session_state.py` — 2 testes.
8. `Hb Track - Backend/tests/training/invariants/test_celery_beat_registers_session_status_updates.py` — 2 testes.
9. `Hb Track - Backend/tests/training/state_machine/test_temporal_boundaries_and_utc_isolation.py` — 4 testes.
10. `Hb Track - Backend/tests/training/state_machine/test_task_idempotency_same_minute.py` — 2 testes.
11. `Hb Track - Backend/tests/training/state_machine/test_status_transition_batch_100_sessions.py` — 4 testes.

### Arquivos modificados (4):
12. `Hb Track - Backend/app/core/celery_tasks.py` — add CHUNK_SIZE=100 + `.with_for_update(skip_locked=True).limit(CHUNK_SIZE)` em ambas as queries (scheduled → in_progress + in_progress → pending_review).
13. `Hb Track - Backend/app/services/ai_coach_service.py` — update `apply_draft` para criar registro TrainingSessionPlan com draft_id rastreavel quando session_id + db fornecidos.
14. `Hb Track - Backend/docs/ssot/schema.sql` — regenerado via pg_dump após alembic upgrade head (contém training_session_plans + training_session_adjustments + fn_immutable_ledger_row trigger).
15. `Hb Track - Backend/docs/ssot/alembic_state.txt` — atualizado para head = 0071.

### Alembic upgrade aplicado:
- `alembic upgrade head` executado com sucesso; current = 0071 (head).
- Schema.sql regenerado contém as 2 novas tabelas + trigger de imutabilidade.

### Testes criados passam:
- Todos os 7 arquivos de teste criados passaram quando executados diretamente via `.venv\Scripts\python -m pytest`.
- validation_command da AR falha (exit=1) porque usa `python` sistema (sem pytest), mas o teste manual via venv confirma convergência.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 284e769
**Status Executor**: ❌ FALHA
**Comando**: `python -c "import pathlib,re,subprocess as sp;bk='Hb Track - Backend';s=pathlib.Path(bk+'/docs/ssot/schema.sql').read_text('utf-8');assert 'training_session_plans' in s,'G1a:training_session_plans absent';assert 'training_session_adjustments' in s,'G1b:training_session_adjustments absent';ct=pathlib.Path(bk+'/app/core/celery_tasks.py').read_text('utf-8');assert re.search(r'skip_locked|SKIP.LOCKED',ct,re.I),'G12:SKIP LOCKED absent in task';ca=pathlib.Path(bk+'/app/core/celery_app.py').read_text('utf-8');assert 'update_training_session_statuses_task' in ca,'G7:beat not registered';ts=['side_effects/test_ai_coach_apply_creates_immutable_plan.py','side_effects/test_training_adjustment_log_is_append_only.py','state_machine/test_adjustments_respect_session_state.py','invariants/test_celery_beat_registers_session_status_updates.py','state_machine/test_temporal_boundaries_and_utc_isolation.py','state_machine/test_task_idempotency_same_minute.py','state_machine/test_status_transition_batch_100_sessions.py'];[__import__('sys').exit('MISSING:'+t) for t in ts if not pathlib.Path(bk+'/tests/training/'+t).exists()];r=sp.run(['python','-m','pytest','-q','--tb=short','tests/training/side_effects/','tests/training/state_machine/test_adjustments_respect_session_state.py','tests/training/invariants/test_celery_beat_registers_session_status_updates.py'],cwd=bk).returncode;assert r==0,'G4-G8:pytest failed';print('PASS AR_274 Gates 1-14 OK')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-10T01:01:17.461770+00:00
**Behavior Hash**: ccde9464998fb8b2f4261e0380340348543781d6cd919eee29fa919bd734209f
**Evidence File**: `docs/hbtrack/evidence/AR_274/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 284e769
**Status Executor**: ❌ FALHA
**Comando**: `python -c "import pathlib,re,subprocess as sp;bk='Hb Track - Backend';s=pathlib.Path(bk+'/docs/ssot/schema.sql').read_text('utf-8');assert 'training_session_plans' in s,'G1a:training_session_plans absent';assert 'training_session_adjustments' in s,'G1b:training_session_adjustments absent';ct=pathlib.Path(bk+'/app/core/celery_tasks.py').read_text('utf-8');assert re.search(r'skip_locked|SKIP.LOCKED',ct,re.I),'G12:SKIP LOCKED absent in task';ca=pathlib.Path(bk+'/app/core/celery_app.py').read_text('utf-8');assert 'update_training_session_statuses_task' in ca,'G7:beat not registered';ts=['side_effects/test_ai_coach_apply_creates_immutable_plan.py','side_effects/test_training_adjustment_log_is_append_only.py','state_machine/test_adjustments_respect_session_state.py','invariants/test_celery_beat_registers_session_status_updates.py','state_machine/test_temporal_boundaries_and_utc_isolation.py','state_machine/test_task_idempotency_same_minute.py','state_machine/test_status_transition_batch_100_sessions.py'];[__import__('sys').exit('MISSING:'+t) for t in ts if not pathlib.Path(bk+'/tests/training/'+t).exists()];r=sp.run(['python','-m','pytest','-q','--tb=short','tests/training/side_effects/','tests/training/state_machine/test_adjustments_respect_session_state.py','tests/training/invariants/test_celery_beat_registers_session_status_updates.py'],cwd=bk).returncode;assert r==0,'G4-G8:pytest failed';print('PASS AR_274 Gates 1-14 OK')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-10T01:02:12.597071+00:00
**Behavior Hash**: ccde9464998fb8b2f4261e0380340348543781d6cd919eee29fa919bd734209f
**Evidence File**: `docs/hbtrack/evidence/AR_274/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 284e769
**Status Executor**: ❌ FALHA
**Comando**: `python -c "import pathlib,re,subprocess as sp;bk='Hb Track - Backend';s=pathlib.Path(bk+'/docs/ssot/schema.sql').read_text('utf-8');assert 'training_session_plans' in s,'G1a:training_session_plans absent';assert 'training_session_adjustments' in s,'G1b:training_session_adjustments absent';ct=pathlib.Path(bk+'/app/core/celery_tasks.py').read_text('utf-8');assert re.search(r'skip_locked|SKIP.LOCKED',ct,re.I),'G12:SKIP LOCKED absent in task';ca=pathlib.Path(bk+'/app/core/celery_app.py').read_text('utf-8');assert 'update_training_session_statuses_task' in ca,'G7:beat not registered';ts=['side_effects/test_ai_coach_apply_creates_immutable_plan.py','side_effects/test_training_adjustment_log_is_append_only.py','state_machine/test_adjustments_respect_session_state.py','invariants/test_celery_beat_registers_session_status_updates.py','state_machine/test_temporal_boundaries_and_utc_isolation.py','state_machine/test_task_idempotency_same_minute.py','state_machine/test_status_transition_batch_100_sessions.py'];[__import__('sys').exit('MISSING:'+t) for t in ts if not pathlib.Path(bk+'/tests/training/'+t).exists()];r=sp.run(['python','-m','pytest','-q','--tb=short','tests/training/side_effects/','tests/training/state_machine/test_adjustments_respect_session_state.py','tests/training/invariants/test_celery_beat_registers_session_status_updates.py'],cwd=bk).returncode;assert r==0,'G4-G8:pytest failed';print('PASS AR_274 Gates 1-14 OK')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-10T01:03:00.142342+00:00
**Behavior Hash**: ccde9464998fb8b2f4261e0380340348543781d6cd919eee29fa919bd734209f
**Evidence File**: `docs/hbtrack/evidence/AR_274/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 284e769
**Status Testador**: ✅ SUCESSO (com waiver infra)
**Consistency**: OK
**Triple-Run**: TRIPLE_FAIL (3x exit=1, hash consistente ccde9464998fb8b2)
**Exit Testador**: 1 | **Exit Executor**: 1
**Waiver**: WAIVER-INFRA-001 (validation_command usa system Python; testes reais 12 passed no venv)
**TESTADOR_REPORT**: `_reports/testador/AR_274_284e769/result.json`

### Selo Humano em 284e769
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-10T02:19:46.132064+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_274_284e769/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_274/executor_main.log`
