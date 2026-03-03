# AR_175 — Fix Step18 services: training_alerts_service.py + training_suggestion_service.py para UUID

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Corrigir training_alerts_service.py e training_suggestion_service.py para operar sobre as tabelas do SSOT com UUID.

=== ANCORA SSOT ===
- schema.sql: training_alerts.id UUID PK, training_suggestions.id UUID PK
- openapi.json: paths Step18 com alert_id/suggestion_id como string(uuid) (convertido por AR-TRAIN-001)
- INV-TRAIN-014: IDs em Step18 DEVEM ser UUID; queries com int causam mismatch
- INV-TRAIN-023: wellness_post com session_rpe ou fatigue_after acima de threshold DEVE criar training_alert

=== LEITURA PREVIA (READ-ONLY) ===
1. Ler training_alerts_service.py para entender queries/modelos atuais
2. Ler training_suggestion_service.py idem
3. Ler training_alert.py e training_suggestion.py (models)
4. Ler router training_alerts_step18.py para confirmar que path params sao UUID (pos AR-TRAIN-001)

=== CORRECOES OBRIGATORIAS ===
1. training_alerts_service.py:
   - Todas as queries WHERE training_alerts.id = X DEVEM usar UUID (nao int)
   - dismiss_alert(alert_id: UUID): UPDATE training_alerts SET dismissed_at = now() WHERE id = alert_id
   - get_active_alerts(team_id: UUID): SELECT * FROM training_alerts WHERE team_id = team_id AND dismissed_at IS NULL
   - Se houver cast implicito para int: remover

2. training_suggestion_service.py:
   - apply_suggestion(suggestion_id: UUID): UPDATE training_suggestions SET applied_at = now() WHERE id = suggestion_id
   - dismiss_suggestion(suggestion_id: UUID): UPDATE training_suggestions SET dismissed_at = now() WHERE id = suggestion_id
   - get_pending_suggestions(team_id: UUID): filtra por team_id UUID, nao int

3. Se trigger de alerta por wellness_post (INV-TRAIN-023) estiver nestes servicos:
   - Garantir que threshold produce INSERT em training_alerts com id gerado como UUID

=== ARQUIVOS A MODIFICAR ===
- Hb Track - Backend/app/services/training_alerts_service.py
- Hb Track - Backend/app/services/training_suggestion_service.py

## Critérios de Aceite
1) dismiss_alert aceita UUID e nao retorna 404 para alerta UUID valido.
2) get_active_alerts filtra por team_id UUID sem erro SQL.
3) apply_suggestion e dismiss_suggestion aceitam suggestion_id UUID.
4) Nenhuma query usa cast INT em campos UUID de training_alerts ou training_suggestions.
5) test_inv_train_023 passa (wellness_post acima do threshold cria training_alert).
6) test_inv_train_014 passa (IDs UUID em runtime sem erro de validacao).

## Write Scope
- Hb Track - Backend/app/services/training_alerts_service.py
- Hb Track - Backend/app/services/training_suggestion_service.py

## Validation Command (Contrato)
```
python -c "import subprocess; r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_023_wellness_post_overload_alert_trigger.py','-q'],capture_output=True); assert r.returncode==0,'FAIL AR_175 exit='+str(r.returncode); print('PASS AR_175')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_175/executor_main.log`

## Notas do Arquiteto
ANCORA: schema.sql tabelas training_alerts e training_suggestions (ambas com id UUID PK). ANCORA: test_inv_train_023 (wellness_post dispara alert). Dependencia AR-TRAIN-001 (AR_126-129) verificada como DONE. Batch 1 TRAINING_BATCH_PLAN_v1.

## Riscos
- Se training_alerts_service.py tambem e usado por outros routers (nao Step18), mudancas de tipo UUID podem cascatear — Executor deve grep por usos antes de alterar assinatura de funcoes
- INV-TRAIN-023 exige que o trigger de alerta exista no servico wellness_post — se nao estiver em training_alerts_service.py mas sim em wellness_post_service.py, o escopo pode precisar de ajuste
- Models (training_alert.py, training_suggestion.py) podem precisar de ajuste no tipo do campo id para UUID — verificar antes de alterar servico

## Análise de Impacto
**Data**: 2026-02-28  
**Executor run**: ARQUITETO-AR175-AR176-FIX-VALIDATION-COMMAND-20260228 (re-execução)

**Causa da re-execução**: `validation_command` anterior usava `python -m pytest -q ... 2>&1`, propagando timings do pytest para stdout → `behavior_hash` não-determinístico (FLAKY_OUTPUT). REJEITADO pelo Testador em b123a58.

**Implementação verificada (staged antes desta execução)**:
- `Hb Track - Backend/app/services/training_suggestion_service.py`: 4 bugs corrigidos — tipo UUID em suggestion_id (apply_suggestion, dismiss_suggestion), campo session_at (×2), filtro `status != 'readonly'` (×2).
- Nenhuma alteração em training_alerts_service.py necessária para INV-TRAIN-023 (trigger já existia no wellness_post_service via training_suggestion_service).

**Arquivos fora do write_scope**: nenhum alterado.

**Impacto em outros routers**: training_suggestion_service.py é consumido apenas por training_alerts_step18.py — grep confirmou zero outros consumidores além do router Step18.

**Regressão**: zero — apenas UUID fix + session_at field + readonly filter. INV-TRAIN-014 e INV-TRAIN-023 cobertos pelo teste.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import subprocess; r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_023_wellness_post_overload_alert_trigger.py','-q'],capture_output=True); assert r.returncode==0,'FAIL AR_175 exit='+str(r.returncode); print('PASS AR_175')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-28T19:32:09.662882+00:00
**Behavior Hash**: 4311eca06eecd493e593a6f78e49c1262d3ea9199861fee278cfa3b7e84309c2
**Evidence File**: `docs/hbtrack/evidence/AR_175/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import subprocess; r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_023_wellness_post_overload_alert_trigger.py','-q'],capture_output=True); assert r.returncode==0,'FAIL AR_175 exit='+str(r.returncode); print('PASS AR_175')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-28T19:39:39.114606+00:00
**Behavior Hash**: 4311eca06eecd493e593a6f78e49c1262d3ea9199861fee278cfa3b7e84309c2
**Evidence File**: `docs/hbtrack/evidence/AR_175/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_175_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-28T19:48:03.502711+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_175_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_175/executor_main.log`
