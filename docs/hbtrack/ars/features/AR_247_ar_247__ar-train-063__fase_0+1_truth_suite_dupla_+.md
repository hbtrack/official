# AR_247 — AR_247 | AR-TRAIN-063 | Fase 0+1: TRUTH SUITE dupla + triage 4 buckets

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
PLANO_FINAL.md Fase 0 + Fase 1. Executar TRUTH command duas vezes consecutivas contra VPS hb_track e verificar idempotência (mesmo contagem de resultados nas 2 rodadas). Após confirmar estabilidade, classificar todos os FAILs/XFAILs/SKIPs encontrados em 4 buckets: A=Infra/DB/Seed, B=Contrato/Endpoint, C=Regra/Invariante, D=UI/E2E. Registrar triage em _reports/EXECUTOR.md e evidence pack em docs/hbtrack/evidence/AR_247/. SSOT de referência: DONE_GATE_TRAINING.md §RH-08 (TRUTH_SUITE + idempotencia). DoD da Fase 0: mesma contagem de FAIL e mesmos primeiros erros nas 2 rodadas. DoD da Fase 1: tabela de triage com todos os itens classificados. Esta AR é classe T/G (triage documental + execucao de suite). Nao toca em codigo de producao. Escopo esperado do baseline: 610p/4s/1xf/0f — se divergir, reportar divergencia antes de prosseguir.

## Critérios de Aceite
AC-001: TRUTH command executado 2x consecutivas e ambas retornam exatamente o mesmo resumo (NNNp/Xs/Yxf/Zf). AC-002: Tabela de triage com colunas (Arquivo, Tipo, Bucket) listando todos os itens nao-PASS. AC-003: evidence pack em docs/hbtrack/evidence/AR_247/ com saida completa de ambas as rodadas.

## Write Scope
- docs/hbtrack/evidence/AR_247/

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -m pytest tests/training/ -x --tb=no -q 2>&1 | python -c "import sys; [print(l.rstrip()) for l in sys.stdin if ('passed' in l or 'failed' in l or 'error' in l) and 'warnings' not in l]"
```

_Nota REPLAN-2 2026-03-05: validation_command corrigida novamente — substituido `grep` (nao existe no Windows) por filtro Python inline. Totalmente Windows-compatible (sem bash, sem grep, sem shell externo)._

PROOF: N/A (governance)
TRACE: N/A (governance)

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_247/executor_main.log`

## Notas do Arquiteto
Classe: T/G. Fase: PLANO_FINAL Fase 0+1. Dependencia: AR-TRAIN-062 VERIFICADO. Se resultado divergir do baseline 610p/4s/1xf/0f, reportar antes de prosseguir — pode indicar regressao ou schema drift. Nao corrigir produto nesta tarefa: apenas observar e classificar.

## Riscos
- Resultado pode diferir do baseline 2026-05-25 se houve mudancas de codigo entre batches — reportar antes de prosseguir.
- Se FAIL count > 0 alem dos 4 skips e 1 xfail conhecidos, parar e escalar para o Arquiteto.
- Nao contar XFAIL e SKIP como FAIL — verificar sumario exato do pytest.

## Análise de Impacto
**Classe**: T/G — somente execução de suite e documentação. Nenhum arquivo de código-produto é tocado.

**Write scope restrito a**: `docs/hbtrack/evidence/AR_247/`

**Dependência confirmada**: AR-TRAIN-062 em estado VERIFICADO (pré-requisito declarado na AR).

**Protocolo**: Duas runs consecutivas de `pytest -q tests/training/` com reset de DB antes da primeira, para verificar idempotência. O baseline esperado é 610p/4s/1xf/0f; qualquer divergência será reportada antes de prosseguir (per instrução do Arquiteto). Se FAIL > 0 além dos 4 skips e 1 xfail conhecidos, escalar imediatamente.

**Risco identificado**: Mudanças de código em ARs anteriores (batch atual) podem ter alterado a contagem — observação pura, sem correção.

**Impacto em produção**: Nulo — T/G.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em a7ab568
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && python -m pytest tests/training/ -x --tb=no -q 2>&1 | grep -E "passed|failed|error" | grep -v "warnings"`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-05T07:32:35.794414+00:00
**Behavior Hash**: a7fcaac17dbec17a5315052c25b8f61810824e8318b3f8ec949ccdc8f14380e1
**Evidence File**: `docs/hbtrack/evidence/AR_247/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -m pytest tests/training/ -x --tb=no -q 2>&1 | grep -E "passed|failed|error" | grep -v "warnings"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-05T07:39:31.201328+00:00
**Behavior Hash**: dce9f58a74ac074ff709b8921a3d3047315ff7529b5d9660527ba94b3d95c55e
**Evidence File**: `docs/hbtrack/evidence/AR_247/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && python -m pytest tests/training/ -x --tb=no -q 2>&1 | grep -E "passed|failed|error" | grep -v "warnings"`
**Exit Code**: 255
**Timestamp UTC**: 2026-03-05T13:56:37.082339+00:00
**Behavior Hash**: e1476c11f68bfc56ae3e9147a4c4a525d23ce464bb94cfe45fb955d3d598f325
**Evidence File**: `docs/hbtrack/evidence/AR_247/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -m pytest tests/training/ -x --tb=no -q 2>&1 | python -c "import sys; [print(l.rstrip()) for l in sys.stdin if ('passed' in l or 'failed' in l or 'error' in l) and 'warnings' not in l]"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-05T14:08:49.219599+00:00
**Behavior Hash**: 84a0495ffb4d37652e72a027390586fad8b547c3097f1a524a30dc868ceae892
**Evidence File**: `docs/hbtrack/evidence/AR_247/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em a7ab568
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_247_a7ab568/result.json`

### Selo Humano em a7ab568
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-05T14:33:04.106512+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_247_a7ab568/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_247/executor_main.log`
