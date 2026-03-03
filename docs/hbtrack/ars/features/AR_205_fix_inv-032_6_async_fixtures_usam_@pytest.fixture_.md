# AR_205 — Fix INV-032: 6 async fixtures usam @pytest.fixture em vez de @pytest_asyncio.fixture

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.3.0

## Descrição
Em test_inv_train_032_wellness_post_rpe.py, as funções async de fixture (linhas ~40, 54, 66, 81, 94, 110) estão decoradas com @pytest.fixture. O pytest-asyncio requer @pytest_asyncio.fixture para fixtures async. Fix: (1) adicionar 'import pytest_asyncio' no bloco de imports; (2) mudar os 6 @pytest.fixture das async def fixtures para @pytest_asyncio.fixture. NÃO mudar fixtures síncronas que possam existir.

## Critérios de Aceite
pytest tests/training/invariants/test_inv_train_032_wellness_post_rpe.py passa (0 FAILs, 0 ERRORs, 0 PytestUnraisableExceptionWarning de async); import pytest_asyncio presente; Todas as async def fixtures decoradas com @pytest_asyncio.fixture; Evidência de execução gerada em _reports/training/TEST-TRAIN-INV-032.md

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_032_wellness_post_rpe.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_032_wellness_post_rpe.py -v --tb=short 2>&1
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_205/executor_main.log`

## Riscos
- Verificar se pytest-asyncio >= 0.21 está instalado (requer @pytest_asyncio.fixture em modo strict). Checar requirements.txt e pytest.ini asyncio_mode.

## Análise de Impacto
**Causa raiz**: Os 6 fixtures do arquivo `test_inv_train_032_wellness_post_rpe.py` são funções `async def` mas decoradas com `@pytest.fixture` (síncrono). O pytest-asyncio em modo `strict` exige `@pytest_asyncio.fixture` para fixtures assíncronos. Sem isso, o pytest não awaita o fixture e os testes falham com `coroutine was never awaited`.

**Fix aplicado**: (1) Adicionar `import pytest_asyncio` após `import pytest` na linha 26. (2) Substituir os 6 `@pytest.fixture` por `@pytest_asyncio.fixture` nas linhas 40, 54, 66, 81, 94, 110.

**Impacto colateral**: Zero — mesma semântica; apenas registra os fixtures no runtime correto.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_032_wellness_post_rpe.py -v --tb=short 2>&1`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-03T02:58:53.966445+00:00
**Behavior Hash**: f03935b8c23b6413cd41491249fbaf2c5a01ceac12a7802792466c574ba435c1
**Evidence File**: `docs/hbtrack/evidence/AR_205/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b123a58
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_032_wellness_post_rpe.py -v --tb=short 2>&1`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-03T03:11:07.552322+00:00
**Behavior Hash**: 0005a644a722bfad6e997b28ea47fbaae598cb5a7755832e15c8715012b60631
**Evidence File**: `docs/hbtrack/evidence/AR_205/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b123a58
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_032_wellness_post_rpe.py -v --tb=short 2>&1`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-03T03:13:57.670149+00:00
**Behavior Hash**: 69ba4791be0b7ecbcd72e6881f1877c01486eaf19430829dfb63e0626c0de0f7
**Evidence File**: `docs/hbtrack/evidence/AR_205/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_032_wellness_post_rpe.py -v --tb=short 2>&1`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T03:15:15.765792+00:00
**Behavior Hash**: 5cf64679218fa22844cd8669c2b4ff5733501a2e8d2a00f975db9b2d1aa42471
**Evidence File**: `docs/hbtrack/evidence/AR_205/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_205_b123a58/result.json`
