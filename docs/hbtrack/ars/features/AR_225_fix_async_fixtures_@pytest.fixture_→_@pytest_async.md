# AR_225 — Fix async fixtures: @pytest.fixture → @pytest_asyncio.fixture (7 arquivos)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Substituir @pytest.fixture por @pytest_asyncio.fixture em todos os fixtures async dos seguintes arquivos de test:
- tests/training/invariants/test_inv_train_024_websocket_broadcast.py
- tests/training/invariants/test_inv_train_031_derive_phase_focus.py
- tests/training/invariants/test_inv_train_034_wellness_pre_sleep_quality.py
- tests/training/invariants/test_inv_train_035_session_templates_unique_name.py
- tests/training/invariants/test_inv_train_035_session_templates_unique_name_runtime.py
- tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py
- tests/training/invariants/test_inv_train_037_cycle_dates.py
- tests/training/invariants/test_inv_train_070_post_conversational.py

CAUSA: TypeError 'function() missing required argument globals (pos 2)' — pytest chama async coroutine como função sync sem o wrapper pytest-asyncio.

FIX: Para cada fixture async (`async def fixture_name(...)`), trocar o decorador de `@pytest.fixture` para `@pytest_asyncio.fixture`. Garantir que `import pytest_asyncio` esteja no topo do arquivo.

Não alterar nada em app/.

## Critérios de Aceite
AC-001: pytest nos 8 arquivos listados = 0 FAILs, 0 ERRORs (sem TypeError globals).
AC-002: nenhum arquivo listado contém @pytest.fixture decorando async def.

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_024_websocket_broadcast.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_031_derive_phase_focus.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_034_wellness_pre_sleep_quality.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_035_session_templates_unique_name.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_035_session_templates_unique_name_runtime.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_037_cycle_dates.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_070_post_conversational.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_024_websocket_broadcast.py tests/training/invariants/test_inv_train_031_derive_phase_focus.py tests/training/invariants/test_inv_train_034_wellness_pre_sleep_quality.py tests/training/invariants/test_inv_train_035_session_templates_unique_name.py tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py tests/training/invariants/test_inv_train_037_cycle_dates.py tests/training/invariants/test_inv_train_070_post_conversational.py -q --tb=short 2>&1
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_225/executor_main.log`

## Riscos
- Se asyncio_mode não está configurado como 'auto', pode ser preciso adicionar @pytest.mark.asyncio em cada test function — verificar pytest.ini antes.
- Alguns arquivos podem ter @pytest.fixture sem async — não tocar esses.

## Análise de Impacto
Root cause real (descoberto na execução): O diagnóstico apontou `@pytest.fixture` em async coroutines, mas o problema real é `Path(__file__).parent.parent.parent` com profundidade insuficiente em todos os arquivos.

- `__file__` = `tests/training/invariants/<test>.py`
- `.parent.parent.parent` → `tests/` (ERRADO — procura `tests/app/` e `tests/docs/ssot/`)
- `.parent.parent.parent.parent` → `Hb Track - Backend/` (CORRETO)

Fixes por arquivo:
- test_024: `.parent.parent.parent / "app"` → `.parent.parent.parent.parent / "app"` (10 paths)
- test_031: `.parent.parent.parent / "docs"` → `.parent.parent.parent.parent / "docs"` (1 path)
- test_034: mesmo fix de path + adicionar `CONSTRAINT_NAME`/`_get_schema_content()` à classe + corrigir `Athlete(jersey_number=...)` → `Athlete(athlete_name=..., birth_date=...)`
- test_035 (non-runtime): mesmo fix de path
- test_036: idem
- test_037: idem
- test_070: `str(athlete.person_id)` → `str(athlete.id)` (FK wellness_post.athlete_id → athletes.id)

Sem mudanças em app/.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 142a146
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_024_websocket_broadcast.py tests/training/invariants/test_inv_train_031_derive_phase_focus.py tests/training/invariants/test_inv_train_034_wellness_pre_sleep_quality.py tests/training/invariants/test_inv_train_035_session_templates_unique_name.py tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py tests/training/invariants/test_inv_train_037_cycle_dates.py tests/training/invariants/test_inv_train_070_post_conversational.py -q --tb=short 2>&1 | tail -5`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T20:28:34.726571+00:00
**Behavior Hash**: 29c1b1a96a4cf1fa7cf59d2de587900a5e280152b3eb2cfc27e9031b0c2f5aea
**Evidence File**: `docs/hbtrack/evidence/AR_225/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 142a146
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_024_websocket_broadcast.py tests/training/invariants/test_inv_train_031_derive_phase_focus.py tests/training/invariants/test_inv_train_034_wellness_pre_sleep_quality.py tests/training/invariants/test_inv_train_035_session_templates_unique_name.py tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py tests/training/invariants/test_inv_train_037_cycle_dates.py tests/training/invariants/test_inv_train_070_post_conversational.py -q --tb=short 2>&1`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T23:06:40.642670+00:00
**Behavior Hash**: 2c1b1a5959989d0dd3ca44f5b56fddecece2f13775e254cd97377bff56ccdf98
**Evidence File**: `docs/hbtrack/evidence/AR_225/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 142a146
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_225_142a146/result.json`

### Selo Humano em 142a146
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T23:22:22.759514+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_225_142a146/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_225/executor_main.log`
