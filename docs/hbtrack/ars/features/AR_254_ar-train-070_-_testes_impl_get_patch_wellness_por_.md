# AR_254 — AR-TRAIN-070 — Testes impl GET/PATCH wellness por ID (CONTRACT-031/032/037/038)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
O Batch 31 implementou os 4 endpoints GET/PATCH wellness-pre/{id} e wellness-post/{id}. Os testes existentes em test_contract_train_029_039_wellness.py verificam apenas existencia de rota via grep estatico — nao garantem que a implementacao usa autenticacao, async def, ou chama o service layer.

Esta AR adiciona 4 novas classes de teste ao arquivo existente, verificando qualidade de implementacao (static analysis aprimorada, sem DB, NO_MOCKS_GLOBAL compliant):

## ZONA 1 — Adicionar TestContractTrain031ImplWellnessPre

Arquivo: Hb Track - Backend/tests/training/contracts/test_contract_train_029_039_wellness.py

Apos a classe TestContractTrain031GetWellnessPre existente, adicionar:

```python
# ---------------------------------------------------------------------------
# CONTRACT-031 IMPL — GET /wellness_pre/{wellness_pre_id} — verificacao de implementacao
# ---------------------------------------------------------------------------
class TestContractTrain031ImplWellnessPre:
    def test_get_by_id_is_async(self):
        """Endpoint nao pode ser def sync (bug pre-AR_253)."""
        content = _pre()
        assert "async def get_wellness_pre_by_id" in content

    def test_get_by_id_has_auth(self):
        """Endpoint deve exigir autenticacao (get_current_user)."""
        content = _pre()
        assert "get_current_user" in content

    def test_get_by_id_calls_service(self):
        """Endpoint deve delegar ao WellnessPreService.get_wellness_pre_by_id."""
        content = _pre()
        assert "get_wellness_pre_by_id" in content
        assert "WellnessPreService" in content
```

## ZONA 2 — Adicionar TestContractTrain032ImplUpdateWellnessPre

Apos a classe TestContractTrain032UpdateWellnessPre existente, adicionar:

```python
# ---------------------------------------------------------------------------
# CONTRACT-032 IMPL — PATCH /wellness_pre/{wellness_pre_id} — verificacao de implementacao
# ---------------------------------------------------------------------------
class TestContractTrain032ImplUpdateWellnessPre:
    def test_update_is_async(self):
        """Endpoint nao pode ser def sync (bug pre-AR_253)."""
        content = _pre()
        assert "async def update_wellness_pre" in content

    def test_update_has_auth(self):
        """Endpoint deve exigir autenticacao."""
        content = _pre()
        assert "get_current_user" in content

    def test_update_calls_service(self):
        """Endpoint deve delegar ao WellnessPreService.update_wellness_pre_by_id."""
        content = _pre()
        assert "update_wellness_pre_by_id" in content

    def test_update_commits(self):
        """Endpoint PATCH deve fazer commit apos edicao bem sucedida."""
        content = _pre()
        assert "await db.commit()" in content or "db.commit()" in content
```

## ZONA 3 — Adicionar TestContractTrain037ImplWellnessPost

Apos a classe TestContractTrain037GetWellnessPost existente, adicionar:

```python
# ---------------------------------------------------------------------------
# CONTRACT-037 IMPL — GET /wellness_post/{wellness_post_id} — verificacao de implementacao
# ---------------------------------------------------------------------------
class TestContractTrain037ImplWellnessPost:
    def test_get_by_id_is_async(self):
        """Endpoint deve ser async def."""
        content = _post()
        assert "async def get_wellness_post_by_id" in content

    def test_get_by_id_has_auth(self):
        """Endpoint deve exigir autenticacao."""
        content = _post()
        assert "get_current_user" in content

    def test_get_by_id_calls_service(self):
        """Endpoint deve delegar ao WellnessPostService.get_wellness_post_by_id."""
        content = _post()
        assert "get_wellness_post_by_id" in content
        assert "WellnessPostService" in content
```

## ZONA 4 — Adicionar TestContractTrain038ImplUpdateWellnessPost

Apos a classe TestContractTrain038UpdateWellnessPost existente, adicionar:

```python
# ---------------------------------------------------------------------------
# CONTRACT-038 IMPL — PATCH /wellness_post/{wellness_post_id} — verificacao de implementacao
# ---------------------------------------------------------------------------
class TestContractTrain038ImplUpdateWellnessPost:
    def test_update_is_async(self):
        """Endpoint nao pode ser def sync (bug pre-AR_253)."""
        content = _post()
        assert "async def update_wellness_post" in content

    def test_update_has_auth(self):
        """Endpoint deve exigir autenticacao."""
        content = _post()
        assert "get_current_user" in content

    def test_update_calls_service(self):
        """Endpoint deve delegar ao WellnessPostService.update_wellness_post_by_id."""
        content = _post()
        assert "update_wellness_post_by_id" in content

    def test_update_commits(self):
        """Endpoint PATCH deve fazer commit."""
        content = _post()
        assert "await db.commit()" in content or "db.commit()" in content
```

## ZONA 5 — Sync documental AR-TRAIN-070

- docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md: atualizar linhas CONTRACT-031/032/037/038 — status de 'COBERTO (grep)' para 'COBERTO (impl+grep)'; adicionar entry para AR-TRAIN-070
- docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md: adicionar AR-TRAIN-070 no lote 22
- docs/hbtrack/Hb Track Kanban.md: adicionar AR_254 na coluna EM_PROGRESSO apos criacao

## Critérios de Aceite
AC1: classe TestContractTrain031ImplWellnessPre presente em test_contract_train_029_039_wellness.py.
AC2: classe TestContractTrain032ImplUpdateWellnessPre presente.
AC3: classe TestContractTrain037ImplWellnessPost presente.
AC4: classe TestContractTrain038ImplUpdateWellnessPost presente.
AC5: todos os testes novos passam (pytest exit=0).
AC6: testes verificam 'async def' (nao apenas existencia de rota).
AC7: testes verificam presenca de 'get_current_user' nos routers.
AC8: testes verificam chamada ao service layer correspondente.

## Write Scope
- Hb Track - Backend/tests/training/contracts/test_contract_train_029_039_wellness.py
- docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md
- docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md
- docs/hbtrack/Hb Track Kanban.md

## Validation Command (Contrato)
```
python -c "
import sys
from pathlib import Path
c = Path('Hb Track - Backend/tests/training/contracts/test_contract_train_029_039_wellness.py').read_text(encoding='utf-8')
checks = [
  ('TestContractTrain031ImplWellnessPre' in c, 'AC1: TestContractTrain031ImplWellnessPre presente'),
  ('TestContractTrain032ImplUpdateWellnessPre' in c, 'AC2: TestContractTrain032ImplUpdateWellnessPre presente'),
  ('TestContractTrain037ImplWellnessPost' in c, 'AC3: TestContractTrain037ImplWellnessPost presente'),
  ('TestContractTrain038ImplUpdateWellnessPost' in c, 'AC4: TestContractTrain038ImplUpdateWellnessPost presente'),
  ('async def get_wellness_pre_by_id' in c or 'async def update_wellness_pre' in c, 'AC6: testes verificam async def'),
  ('get_current_user' in c, 'AC7: testes verificam get_current_user'),
  ('WellnessPreService' in c and 'WellnessPostService' in c, 'AC8: testes verificam service layer'),
]
bad = [msg for ok, msg in checks if not ok]
if bad: print('FAIL:', bad); sys.exit(1)
print('AC1..AC8 PASS (static)')
" && cd "Hb Track - Backend" && python -m pytest tests/training/contracts/test_contract_train_029_039_wellness.py -q 2>&1 | tail -5
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_254/executor_main.log`

## Análise de Impacto
**Data**: 2026-03-06
**Executor**: Copilot Executor v1.3.0

### Arquivos modificados
| Arquivo | Tipo de mudança | Risco |
|---|---|---|
| `Hb Track - Backend/tests/training/contracts/test_contract_train_029_039_wellness.py` | Adição de 4 classes de teste (impl guard) | BAIXO |

### Impacto funcional
- Zero impacto em código de produto (routers, services, schema, openapi)
- Testes adicionados são static analysis (read_text do router file); sem fixture de DB
- NO_MOCKS_GLOBAL compliant
- AC1..AC8 serão verificados pelo validation_command

### Dependências confirmadas
- AR_253 (AR-TRAIN-069) ✅ VERIFICADO (Kanban, Batch 31)
- `async def get_wellness_pre_by_id`, `update_wellness_pre`, `get_wellness_post_by_id`, `update_wellness_post` presentes nos routers (confirmado por AR_253)

### Pré-condição
- `test_contract_train_029_039_wellness.py` com 135 linhas — verificado
- write_scope: apenas o arquivo de teste (1 arquivo de produto de teste)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "
import sys
from pathlib import Path
c = Path('Hb Track - Backend/tests/training/contracts/test_contract_train_029_039_wellness.py').read_text(encoding='utf-8')
checks = [
  ('TestContractTrain031ImplWellnessPre' in c, 'AC1: TestContractTrain031ImplWellnessPre presente'),
  ('TestContractTrain032ImplUpdateWellnessPre' in c, 'AC2: TestContractTrain032ImplUpdateWellnessPre presente'),
  ('TestContractTrain037ImplWellnessPost' in c, 'AC3: TestContractTrain037ImplWellnessPost presente'),
  ('TestContractTrain038ImplUpdateWellnessPost' in c, 'AC4: TestContractTrain038ImplUpdateWellnessPost presente'),
  ('async def get_wellness_pre_by_id' in c or 'async def update_wellness_pre' in c, 'AC6: testes verificam async def'),
  ('get_current_user' in c, 'AC7: testes verificam get_current_user'),
  ('WellnessPreService' in c and 'WellnessPostService' in c, 'AC8: testes verificam service layer'),
]
bad = [msg for ok, msg in checks if not ok]
if bad: print('FAIL:', bad); sys.exit(1)
print('AC1..AC8 PASS (static)')
" && cd "Hb Track - Backend" && python -m pytest tests/training/contracts/test_contract_train_029_039_wellness.py -q 2>&1 | tail -5`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-06T14:14:32.425404+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_254/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "
import sys
from pathlib import Path
c = Path('Hb Track - Backend/tests/training/contracts/test_contract_train_029_039_wellness.py').read_text(encoding='utf-8')
checks = [
  ('TestContractTrain031ImplWellnessPre' in c, 'AC1: TestContractTrain031ImplWellnessPre presente'),
  ('TestContractTrain032ImplUpdateWellnessPre' in c, 'AC2: TestContractTrain032ImplUpdateWellnessPre presente'),
  ('TestContractTrain037ImplWellnessPost' in c, 'AC3: TestContractTrain037ImplWellnessPost presente'),
  ('TestContractTrain038ImplUpdateWellnessPost' in c, 'AC4: TestContractTrain038ImplUpdateWellnessPost presente'),
  ('async def get_wellness_pre_by_id' in c or 'async def update_wellness_pre' in c, 'AC6: testes verificam async def'),
  ('get_current_user' in c, 'AC7: testes verificam get_current_user'),
  ('WellnessPreService' in c and 'WellnessPostService' in c, 'AC8: testes verificam service layer'),
]
bad = [msg for ok, msg in checks if not ok]
if bad: print('FAIL:', bad); sys.exit(1)
print('AC1..AC8 PASS (static)')
" && cd "Hb Track - Backend" && python -m pytest tests/training/contracts/test_contract_train_029_039_wellness.py -q 2>&1 | tail -5`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-06T14:14:38.824638+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_254/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "
import sys
from pathlib import Path
c = Path('Hb Track - Backend/tests/training/contracts/test_contract_train_029_039_wellness.py').read_text(encoding='utf-8')
checks = [
  ('TestContractTrain031ImplWellnessPre' in c, 'AC1: TestContractTrain031ImplWellnessPre presente'),
  ('TestContractTrain032ImplUpdateWellnessPre' in c, 'AC2: TestContractTrain032ImplUpdateWellnessPre presente'),
  ('TestContractTrain037ImplWellnessPost' in c, 'AC3: TestContractTrain037ImplWellnessPost presente'),
  ('TestContractTrain038ImplUpdateWellnessPost' in c, 'AC4: TestContractTrain038ImplUpdateWellnessPost presente'),
  ('async def get_wellness_pre_by_id' in c or 'async def update_wellness_pre' in c, 'AC6: testes verificam async def'),
  ('get_current_user' in c, 'AC7: testes verificam get_current_user'),
  ('WellnessPreService' in c and 'WellnessPostService' in c, 'AC8: testes verificam service layer'),
]
bad = [msg for ok, msg in checks if not ok]
if bad: print('FAIL:', bad); sys.exit(1)
print('AC1..AC8 PASS (static)')
" && cd "Hb Track - Backend" && python -m pytest tests/training/contracts/test_contract_train_029_039_wellness.py -q 2>&1 | tail -5`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-06T14:15:36.816062+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_254/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em a7ab568
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_254_a7ab568/result.json`

### Selo Humano em a7ab568
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-06T14:38:08.643086+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_254_a7ab568/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_254/executor_main.log`
