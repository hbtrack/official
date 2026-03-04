# AR_228 — Fix residuais mistos + validação done gate (suite 0 FAILs)

**Status**: 🔴 REJEITADO
**Versão do Protocolo**: 1.3.0

## Descrição
Corrigir FAILs residuais não cobertos por AR-TRAIN-044..046 e validar que a suite completa atinge 0 FAILs.

Arquivos com FAILs residuais conhecidos:
- test_inv_train_010_wellness_post_uniqueness.py (2 FAILs)
- test_inv_train_018_training_session_microcycle_status.py (1 FAIL)
- test_inv_train_018_training_session_microcycle_status_runtime*.py (1 FAIL)
- test_inv_train_019_training_session_audit_logs.py (1 FAIL)
- test_inv_train_054_standalone_session.py (2 FAILs setup)
- test_inv_train_057_session_within_microcycle.py (1 FAIL)
- test_inv_train_065_close_pending_guard.py (2 FAILs)
- test_inv_train_066_pending_items.py (2 FAILs)
- test_inv_train_067_athlete_pending_rbac.py (3 FAILs)

PROCESSO:
1. Rodar `pytest tests/training/ -q --tb=short` (após 044+045+046 aplicados)
2. Para cada FAIL residual: identificar causa (fixture, assertion, lógica) e aplicar fix mínimo
3. Verificar que 0 FAILs, 0 ERRORs na suite completa

Se durante a execução surgir novo tipo de FAIL não listado acima → Executor para, documenta no executor_main.log e reporta BLOCKED para o Arquiteto. Não tentar corrigir bugs de produto.

## Critérios de Aceite
AC-001: `pytest tests/training/ -q --tb=no` = 0 failed, 0 errors (suite completa verde).
AC-002: nenhum FAIL residual nos arquivos listados.

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_010_wellness_post_uniqueness.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_018_training_session_microcycle_status.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_019_training_session_audit_logs.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_054_standalone_session.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_057_session_within_microcycle.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_065_close_pending_guard.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_066_pending_items.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_067_athlete_pending_rbac.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -m pytest tests/training/ -q --tb=no 2>&1
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_228/executor_main.log`

## Riscos
- FAILs residuais podem revelar novo tipo após 044+045+046 — Executor deve parar e reportar BLOCKED se houver novo tipo não mapeado.
- Não alterar lógica de produto (app/) — se FAIL só é corrigível em app/, reportar BLOCKED_PRODUCT para o Arquiteto criar AR de implementação.

## Análise de Impacto

**Causas identificadas (dentro do write_scope):**
- test_018: `db.execute.return_value = _Result(team)` retorna `Team` para todas as chamadas; quando o serviço busca o microciclo recebe o objeto `Team`, que não tem `week_start` → `AttributeError`. Fix: `db.execute.side_effect` com sequência correta (team, microcycle, audit_mock) × 2 chamadas.
- test_019: `Person(id=..., full_name=...)` criados sem `birth_date` (NOT NULL no DB) → `NotNullViolationError`. Fix: adicionar `birth_date=date(1985, 1, 1)` às 2 instâncias Person do teste.
- test_065: `athlete_id = str(athlete.person_id)` → FK `fk_pending_items_athlete` aponta para `athletes.id`, não para `person_id`. Fix: trocar para `str(athlete.id)`.
- test_066: mesmo padrão de test_065. Fix: idem.
- test_067: mesmo padrão de test_065. Fix: idem.

**BLOCKED_PRODUCT — fora do write_scope (app/):**
- test_057: `service.create()` faz `TrainingSession(standalone=standalone)` mas `app/models/training_session.py` não mapeia a coluna `standalone` (existe em schema.sql). Requer AR de implementação de app/models.

**BLOCKED_SCOPE — arquivos não listados no write_scope:**
- test_018_route.py: 1 FAIL (mesmo tipo de mock, mas fora do scope).
- test_035_runtime.py: 4 FAILs (cobertura de runtime, fora do scope).
- test_058/059/063/064/076/acl_006: 10 ERRORs de setup (category_id NOT NULL em Team criado sem fixture padrão — novo tipo não listado).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 142a146
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && python -m pytest tests/training/ -q --tb=no 2>&1 | tail -3`
**Exit Code**: 255
**Timestamp UTC**: 2026-03-03T22:51:40.860087+00:00
**Behavior Hash**: d7f0027db1b9f614c9423cc40145a57f68b1cffb191d13110e7ed140b25fbadd
**Evidence File**: `docs/hbtrack/evidence/AR_228/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 142a146
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && python -m pytest tests/training/ -q --tb=no 2>&1`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-03T23:08:40.992315+00:00
**Behavior Hash**: 9000391b61fd2b2a840a961f61861b4716136cca497980eb88103e6afd5faa11
**Evidence File**: `docs/hbtrack/evidence/AR_228/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 142a146
**Status Testador**: 🔴 REJEITADO
**Consistency**: OK
**Triple-Run**: TRIPLE_FAIL (3x)
**Exit Testador**: 1 | **Exit Executor**: 1
**TESTADOR_REPORT**: `_reports/testador/AR_228_142a146/result.json`
