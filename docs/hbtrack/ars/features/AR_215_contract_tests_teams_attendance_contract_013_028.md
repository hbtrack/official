# AR_215 — Contract Tests: Teams + Attendance (CONTRACT-013..028)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0
**AR SSOT ID**: AR-TRAIN-036
**Batch**: 14

## Descrição
Criar testes de contrato automatizados para 16 contratos de equipes e presença (CONTRACT-013..028): criar equipe, adicionar atleta, remover atleta, listar membros, registrar presença individual/em-lote, consultar histórico, etc. Atualizar TEST_MATRIX §8 para CONTRACT-013..028 = COBERTO. FORBIDDEN: zero toque em `app/`.

## Critérios de Aceite
**AC-001:** `pytest -q tests/training/contracts/test_contract_train_013_028_teams_attendance.py` retorna exit 0 — 0 FAILs.
**AC-002:** §8 da `TEST_MATRIX_TRAINING.md` mostra CONTRACT-013..028 = COBERTO.

## Write Scope
- `Hb Track - Backend/tests/training/contracts/test_contract_train_013_028_teams_attendance.py`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && pytest -q tests/training/contracts/test_contract_train_013_028_teams_attendance.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_215/executor_main.log`

## Dependências
- AR-TRAIN-034 (AR_213) — ✅ VERIFICADO (Batch 13 sealed)

## Riscos
- Models de equipe podem ter relações complexas (many-to-many atleta-equipe) — validar apenas estrutura, não fixture de DB.
- Não tocar em `app/` — somente camada de testes.

## Análise de Impacto
**Escopo**: criação de arquivo de teste de contrato + atualização TEST_MATRIX §8. Zero toque em app/.
**Routers mapeados**:
- `training_sessions.py` (scoped_router, prefix `/teams/{team_id}/trainings`) → CONTRACT-013..018
- `session_exercises.py` (prefix `/training-sessions`) → CONTRACT-019..024
- `attendance.py` (sem prefix dedicado) → CONTRACT-025..028
**Abordagem**: estática (Path + read_text + assert). Sem fixtures de DB.
**Efeito colateral**: nenhum em código de produto.

---
## Carimbo de Execução

*(a preencher pelo Executor)*

### Execução Executor em 142a146
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest -q tests/training/contracts/test_contract_train_013_028_teams_attendance.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T15:13:42.042654+00:00
**Behavior Hash**: 64f39efdb1ee3ed7fed33ba1e8654946d96dd5d4458fffb3ce6f89489e8949d5
**Evidence File**: `docs/hbtrack/evidence/AR_215/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 142a146
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_215_142a146/result.json`

### Selo Humano em 142a146
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T15:26:49.980479+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_215_142a146/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_215/executor_main.log`
