# AR_249 — AR_249 | AR-TRAIN-065 | Bucket C: Fix 4 SKIP em test_inv_train_058 e test_inv_train_059

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
PLANO_FINAL.md Fase 2.3 + Fase 3. Bucket C (Regra/Invariante) — 4 testes marcados como skip em test_inv_train_058_session_structure_mutable.py (INV-TRAIN-058: sessao standalone mutavel) e test_inv_train_059_exercise_order_contiguous.py (INV-TRAIN-059: order_index contiguos). Procedimento: (1) Reproduzir cada teste isolado: reset + pytest -q tests/training/invariants/test_inv_train_058* e test_inv_train_059*. (2) Identificar motivo do skip (ausencia de feature, dependencia nao satisfeita, ou comportamento nao implementado). (3) Corrigir o produto no enforcement point correto (router/service/schema) para satisfazer o comportamento esperado pela invariante. (4) Remover o skip marker ou verificar que o teste passe organicamente. (5) Reexecutar TRUTH SUITE completa. DoD: 4 tests convertidos de skip para PASS na TRUTH SUITE. INV-TRAIN-058: sessao standalone pode ter estrutura editada (mutavel). INV-TRAIN-059: order_index de exercicios deve ser contiguos sem gaps. SSOT: INVARIANTS_TRAINING.md INV-TRAIN-058/059.

## Critérios de Aceite
AC-001: pytest test_inv_train_058* retorna PASS (ambos os testes, sem skip marker). AC-002: pytest test_inv_train_059* retorna PASS (ambos os testes, sem skip marker). AC-003: TRUTH SUITE completa retorna 0 skipped para esses 2 arquivos. AC-004: Nenhum mock introduzido no codigo de producao ou teste. AC-005: Corrrecao feita no produto (service/router/schema), nunca no teste.

## Write Scope
- Hb Track - Backend/app/services/session_exercise_service.py
- Hb Track - Backend/app/api/v1/routers/training_sessions.py
- Hb Track - Backend/app/api/v1/routers/athlete_training.py

## Validation Command (Contrato)
```
python -X utf8 scripts/db/reset_hb_track_test.py && cd "Hb Track - Backend" && python -m pytest -q tests/training/invariants/test_inv_train_058_session_structure_mutable.py tests/training/invariants/test_inv_train_059_exercise_order_contiguous.py -v 2>&1 | python -c "import sys, re; lines=sys.stdin.readlines(); [print(re.sub(r' - \d+\.\d+s', '', l).rstrip()) for l in lines[-30:] if any(w in l for w in ['PASSED','FAILED','ERROR','xfailed','xpassed','passed','failed','error','XFAIL','XPASS','skipped']) and 'warnings' not in l] or [print(lines[-1].rstrip())]"
```

**REPLAN-3 (2026-03-05)**: dois fixes Windows aplicados:
- P1 (UnicodeEncodeError): prefixo `$env:PYTHONUTF8='1'` — reset_hb_track_test.py imprime chars Unicode que falham em cp1252.
- P2 (`tail` nao existe no Windows): substituido por `python -c` inline que filtra as ultimas 30 linhas mostrando apenas resultados de teste (incluindo skipped).

**REPLAN-4 (2026-03-05)**: fix cmd.exe compat:
- P3 (shell=True → cmd.exe): `hb_cli.py` usa `subprocess.run(shell=True)` que invoca `cmd.exe /c`, NAO PowerShell. `$env:PYTHONUTF8='1';` e `;` como separador sao sintaxe PowerShell-only — exit=255 no cmd.exe.
- Fix P3: substituido `$env:PYTHONUTF8='1';` por `set PYTHONUTF8=1 &&` e todos os `;` separadores por `&&`.

**REPLAN-5 (2026-03-05)**: fix definitivo Unicode:
- P4 (espaço à direita antes do &&): `set PYTHONUTF8=1 &&` define o valor como `"1 "` (com espaço trailing) — Python retorna "Fatal Python error: environment variable PYTHONUTF8 must be '1' or '0'" com exit=1.
- Fix P4: substituido `set PYTHONUTF8=1 && python scripts/db/reset_hb_track_test.py` por `python -X utf8 scripts/db/reset_hb_track_test.py` — flag direta `-X utf8`, sem variável de ambiente, funciona em cmd.exe e PowerShell.

**REPLAN-6 (2026-03-05)**: fix FLAKY_OUTPUT — hash divergia por timing em linhas de teste:
- P5 (timing por teste em output `-v`): pytest `-v` emite linhas `PASSED test::name - 0.23s` onde `0.23s` varia entre runs → hash do stdout diverge mesmo com conteúdo estrutural idêntico.
- Fix P5: adicionado `import re` + `re.sub(r' - \d+\.\d+s', '', l)` no filtro inline para strip do timing antes de print.

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_249/executor_main.log`

## Notas do Arquiteto
Classe: B/E (Regra de Dominio/Service + Contrato). Fase: PLANO_FINAL Fase 2.3 + 3. Enforcement point a determinar apos leitura dos testes: pode ser session_exercise_service.py (order_index logic) ou training_sessions router. Verificar INVARIANTS_TRAINING.md para ACs de INV-TRAIN-058/059 antes de corrigir. Dependencia: AR_248 concluido (TRUTH baseline estabilizado).

## Riscos
- Motivo do skip pode indicar feature nao implementada no produto — se for case assim, escalar ao Arquiteto antes de implementar.
- order_index contiguo pode requerer logica de renumeracao que afeta performance — verificar volume esperado.
- Fix pode afetar contratos existentes de CONTRACT-TRAIN-* — verificar openapi.json antes e depois.

## Análise de Impacto

**Executor**: GitHub Copilot | **Data**: 2026-03-05

### Escopo Real

| Arquivo | Alteração | Motivo |
|---------|-----------|--------|
| `app/services/session_exercise_service.py` | Adicionar `_validate_session_mutable()` chamado em `add_exercise()` | Guard INV-058: bloquear add em sessão readonly/in_progress |
| `app/services/session_exercise_service.py` | Adicionar validação de contiguidade em `reorder_exercises()` | Guard INV-059: rejeitar gaps (ex: [1,2,4]) no order_index |
| `tests/training/invariants/test_inv_train_058_session_structure_mutable.py` | Remover `@pytest.mark.skip` de `test_invalid_session_readonly_rejects_add_exercise` | Ativar teste após guard implementado |
| `tests/training/invariants/test_inv_train_059_exercise_order_contiguous.py` | Remover `@pytest.mark.skip` de `test_invalid_gap_in_order_2_4` | Ativar teste após guard implementado |

### Análise de Risco

- **INV-058 guard**: `_validate_session_mutable()` verifica `session.status in ["readonly", "in_progress"]` → `ForbiddenError("Sessão encerrada. Estrutura não pode ser alterada.")`. Risco baixo: apenas adiciona verificação, não altera fluxo existente para sessões draft.
- **INV-059 guard**: valida `sorted(new_order_values) == list(range(1, len+1))`. Risco baixo: testa apenas os índices do payload de reordenação. Sessões com ordens pré-existentes com gaps não são afetadas (guard só atua no `reorder_exercises`).
- **`remove_exercise`** já tem lógica de reindexação contígua (INV-059: após remoção, decrementa order_index dos subsequentes). Novo guard em `reorder_exercises` é complementar.
- **Testes modificados**: apenas remoção de `@pytest.mark.skip` — nenhuma lógica de teste alterada (AC-005 preservado: correção no produto, skip era marcador temporário de GAP).

### Impacto em Contratos

- `openapi.json` não alterado (nenhum endpoint novo ou schema modificado).
- `session_exercise_service.add_exercise` agora lança `ForbiddenError` para sessões encerradas — comportamento novo, documentado na AR.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -X utf8 scripts/db/reset_hb_track_test.py && cd "Hb Track - Backend" && python -m pytest -q tests/training/invariants/test_inv_train_058_session_structure_mutable.py tests/training/invariants/test_inv_train_059_exercise_order_contiguous.py -v 2>&1 | python -c "import sys; lines=sys.stdin.readlines(); [print(l.rstrip()) for l in lines[-30:] if any(w in l for w in ['PASSED','FAILED','ERROR','xfailed','xpassed','passed','failed','error','XFAIL','XPASS','skipped']) and 'warnings' not in l] or [print(lines[-1].rstrip())]"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-05T16:02:05.402722+00:00
**Behavior Hash**: ab5a8e330cd36314b542230a8c0d31960eec6671b2aca605c4e2cb2acfdc98fb
**Evidence File**: `docs/hbtrack/evidence/AR_249/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -X utf8 scripts/db/reset_hb_track_test.py && cd "Hb Track - Backend" && python -m pytest -q tests/training/invariants/test_inv_train_058_session_structure_mutable.py tests/training/invariants/test_inv_train_059_exercise_order_contiguous.py -v 2>&1 | python -c "import sys, re; lines=sys.stdin.readlines(); [print(re.sub(r' - \d+\.\d+s', '', l).rstrip()) for l in lines[-30:] if any(w in l for w in ['PASSED','FAILED','ERROR','xfailed','xpassed','passed','failed','error','XFAIL','XPASS','skipped']) and 'warnings' not in l] or [print(lines[-1].rstrip())]"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-05T17:47:57.018400+00:00
**Behavior Hash**: bed06af647c5c1d79fc6dbea495a48f61507eea8f4d39c91f638738bfa59d51f
**Evidence File**: `docs/hbtrack/evidence/AR_249/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -X utf8 scripts/db/reset_hb_track_test.py && cd "Hb Track - Backend" && python -m pytest -q tests/training/invariants/test_inv_train_058_session_structure_mutable.py tests/training/invariants/test_inv_train_059_exercise_order_contiguous.py -v 2>&1 | python -c "import sys, re; lines=sys.stdin.readlines(); [print(re.sub(r' - \d+\.\d+s', '', l).rstrip()) for l in lines[-30:] if any(w in l for w in ['PASSED','FAILED','ERROR','xfailed','xpassed','passed','failed','error','XFAIL','XPASS','skipped']) and 'warnings' not in l] or [print(lines[-1].rstrip())]"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-05T17:49:39.659386+00:00
**Behavior Hash**: ab5a8e330cd36314b542230a8c0d31960eec6671b2aca605c4e2cb2acfdc98fb
**Evidence File**: `docs/hbtrack/evidence/AR_249/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em a7ab568
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_249_a7ab568/result.json`

### Selo Humano em a7ab568
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-05T18:26:27.230252+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_249_a7ab568/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_249/executor_main.log`
