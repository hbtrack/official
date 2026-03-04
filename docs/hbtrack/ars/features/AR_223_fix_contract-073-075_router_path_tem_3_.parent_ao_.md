# AR_223 — Fix CONTRACT-073-075: ROUTER_PATH tem 3 .parent ao invés de 4

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Em tests/training/contracts/test_contract_train_073_075_wellness_rankings.py (gerado em AR_217/Batch 14), ROUTER_PATH é definido como:

  ROUTER_PATH = (
      Path(__file__).parent.parent.parent
      / 'app' / 'api' / 'v1' / 'routers' / 'analytics.py'
  )

O arquivo __file__ está em tests/training/contracts/, então 3 .parent resolve para tests/ e o path final é tests/app/api/v1/routers/analytics.py (não existe, 14 FAILs do tipo 'Router não encontrado').

Fix: adicionar um .parent extra na definição de ROUTER_PATH (~linhas 19-24), deixando:

  ROUTER_PATH = (
      Path(__file__).parent.parent.parent.parent
      / 'app' / 'api' / 'v1' / 'routers' / 'analytics.py'
  )

Isso faz o path resolver para 'Hb Track - Backend/app/api/v1/routers/analytics.py' (existe e contém as rotas wellness-rankings conforme confirmado).

Precedente: fix idêntico já aplicado em AR_206 (Batch 9) para test_contract_train_077_085_alerts_suggestions.py.

## Critérios de Aceite
pytest tests/training/contracts/test_contract_train_073_075_wellness_rankings.py -v --tb=short retorna 0 FAILs e 0 ERRORs (14 testes PASS); ROUTER_PATH resolve para 'Hb Track - Backend/app/api/v1/routers/analytics.py'; Apenas a linha do ROUTER_PATH modificada — nenhuma lógica de teste alterada.

## Write Scope
- Hb Track - Backend/tests/training/contracts/test_contract_train_073_075_wellness_rankings.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && pytest tests/training/contracts/test_contract_train_073_075_wellness_rankings.py -v --tb=short 2>&1
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_223/executor_main.log`

## Riscos
- Confirmar que analytics.py contém as rotas 'wellness-rankings' antes de executar (já confirmado na investigação do Arquiteto, mas Executor deve re-verificar).
- Não alterar nenhuma linha além do ROUTER_PATH — qualquer mudança extra fora do write_scope é FORBIDDEN.

## Análise de Impacto

**Arquivo modificado**: `Hb Track - Backend/tests/training/contracts/test_contract_train_073_075_wellness_rankings.py`

**Mudança**: linha 20 — `Path(__file__).parent.parent.parent` → `Path(__file__).parent.parent.parent.parent`

**Impacto em produto**: zero — arquivo de teste apenas, sem toque em `app/`, `db/` ou Frontend.

**Impacto em outros testes**: zero — a mudança é estritamente local ao `ROUTER_PATH` deste arquivo.

**Verificação pré-patch**: `analytics.py` existe em `Hb Track - Backend/app/api/v1/routers/analytics.py` e contém rotas `wellness-rankings` (confirmado pelo Arquiteto).

**Rollback**: `git checkout -- "Hb Track - Backend/tests/training/contracts/test_contract_train_073_075_wellness_rankings.py"`

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 142a146
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest tests/training/contracts/test_contract_train_073_075_wellness_rankings.py -v --tb=short 2>&1`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T17:59:38.768494+00:00
**Behavior Hash**: d9f527ec46e3e19d70b2db715c69f6fd196bf22978e473bc470bca5487712245
**Evidence File**: `docs/hbtrack/evidence/AR_223/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 142a146
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_223_142a146/result.json`

### Selo Humano em 142a146
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T18:35:37.867811+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_223_142a146/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_223/executor_main.log`
