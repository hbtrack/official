# AR_206 — Fix CONTRACT-077-085: ROUTER_PATH tem 3 .parent ao invés de 4

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Em test_contract_train_077_085_alerts_suggestions.py, ROUTER_PATH = Path(__file__).parent.parent.parent / 'app' / 'api' / 'v1' / 'routers' / 'training_alerts_step18.py'. O __file__ está em tests/training/contracts/, então 3 .parent resolve para tests/ e o path final é tests/app/api/v1/routers/training_alerts_step18.py (não existe). Fix: adicionar .parent extra na definição de ROUTER_PATH (~linha 29).

## Critérios de Aceite
pytest tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py passa (0 FAILs, 0 ERRORs); ROUTER_PATH resolve para 'Hb Track - Backend/app/api/v1/routers/training_alerts_step18.py' (existe); Evidência de execução atualizada em _reports/training/TEST-TRAIN-CONTRACT-077-085.md

## Write Scope
- Hb Track - Backend/tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && pytest tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py -v --tb=short 2>&1
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_206/executor_main.log`

## Análise de Impacto
**Causa raiz**: `ROUTER_PATH = Path(__file__).parent.parent.parent / "app" / ...` — com 3 `.parent` sobe para `tests/`, mas o router `training_alerts_step18.py` está em `Hb Track - Backend/app/api/v1/routers/`, que exige 4 `.parent` para chegar ao root `Hb Track - Backend/`.

**Fix aplicado**: Linha 28 — substituir `Path(__file__).parent.parent.parent` por `Path(__file__).parent.parent.parent.parent` na definição de `ROUTER_PATH`.

**Impacto colateral**: Zero — apenas corrige o path base do contrato.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py -v --tb=short 2>&1`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T03:16:12.252342+00:00
**Behavior Hash**: 7c88569fe6cd5fd72213018384880cc2ea15f3ef2cfdffc73da55eb961df1058
**Evidence File**: `docs/hbtrack/evidence/AR_206/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_206_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T04:25:47.280590+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_206_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_206/executor_main.log`
