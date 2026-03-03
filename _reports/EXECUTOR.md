# EXECUTOR.md — EXECUTOR_REPORT

## ⚡ CICLO ATUAL — AR_210 (2026-03-03)

| Campo             | Valor                                                           |
|-------------------|-----------------------------------------------------------------|
| **Protocolo**     | v1.3.0                                                          |
| **Branch**        | dev-changes-2                                                   |
| **HEAD**          | b123a58                                                         |
| **Data execução** | 2026-03-03                                                      |
| **Status**        | PRONTO PARA VERIFICAÇÃO — AR_210 executado, evidência gerada    |

### AR_210 — Fix `compute_behavior_hash`: normalizar timings pytest

**E1 — AR lida:** `docs/hbtrack/ars/features/AR_210_fix_compute_behavior_hash_normalizar_timings_pytes.md`

**E2 — Análise de Impacto:**
- Função alvo: `compute_behavior_hash(exit_code, stdout, stderr)` em `scripts/run/hb_cli.py` (linha ~314)
- Causava `FLAKY_OUTPUT`: `_norm_newlines` só normaliza CRLF→LF; pytest emite timings flutuantes (`N passed in X.XXs`) que variam entre runs, gerando hashes SHA-256 distintos no triple-run
- Fix: adicionar `re.sub(r'\b\d+\.\d+s\b', 'X.Xs', payload)` antes do SHA-256
- `import re` já existia na linha 36 — sem novo import
- Assinatura pública inalterada; zero outros arquivos alterados

**E3 — Patch:** `scripts/run/hb_cli.py`
```python
payload = re.sub(r'\b\d+\.\d+s\b', 'X.Xs', payload)  # adicionado antes do hashlib.sha256
```

**E4 — `hb report 210`:** Exit Code 0 ✅
- STDOUT: `OK: timing-agnostic + exit_code still discriminates`
- Behavior Hash: `d51c1fe3a50f943bfac361e303d29a7b1fd0a9bd64b5fcedacb04271c58830aa`

**E5 — Evidência:** `docs/hbtrack/evidence/AR_210/executor_main.log` ✅

**Stage exato (tracked-unstaged = 0):**
```
A  docs/hbtrack/evidence/AR_210/executor_main.log
A  docs/hbtrack/ars/features/AR_210_fix_compute_behavior_hash_normalizar_timings_pytes.md
M  scripts/run/hb_cli.py
M  docs/hbtrack/_INDEX.md
```

**Instrução ao Testador:**
> Executar `hb verify 210` (triple-run). Após APROVADO, re-verificar AR_202..206 e AR_124 — devem
> produzir 3/3 hashes idênticos. Aprovações desbloqueiam AR_207/208/209.

---

## HISTÓRICO — Batch 9 (2026-03-03) — AR_202..AR_206

| Campo | Valor |
|---|---|
| **Batch** | Batch 9 — Fix FAILs Críticos Test-Layer (TRAINING) |
| **ARs executadas** | AR_202, AR_203, AR_204, AR_205, AR_206 |
| **Data** | 2026-03-03 |
| **Branch** | dev-changes-2 |
| **HEAD** | b123a58 |
| **Protocolo** | v1.3.0 |
| **Status** | ✅ CONCLUÍDO — 5/5 Exit Code: 0 |

---

## Status de Execução

| AR | Título | Exit Code | Evidence |
|---|---|---|---|
| AR_202 | Fix INV-001 test_invalid_case_2 expects wrong constraint | 0 | docs/hbtrack/evidence/AR_202/executor_main.log |
| AR_203 | Fix INV-008 schema path tem 3x .parent ao invés de 2x | 0 | docs/hbtrack/evidence/AR_203/executor_main.log |
| AR_204 | Fix INV-030 schema path tem 3x .parent ao invés de 2x | 0 | docs/hbtrack/evidence/AR_204/executor_main.log |
| AR_205 | Fix INV-032 6 async fixtures usam @pytest.fixture (+bugs adicionais) | 0 | docs/hbtrack/evidence/AR_205/executor_main.log |
| AR_206 | Fix CONTRACT-077-085 router path tem 3x .parent ao invés de 2x | 0 | docs/hbtrack/evidence/AR_206/executor_main.log |

---

## Ações Executadas por AR

### AR_202 — Fix INV-001 test_invalid_case_2

**E1 — AR lida**: `docs/hbtrack/ars/features/AR_202_fix_inv-001_test_invalid_case_2_expects_wrong_cons.md`

**E2 — Análise de Impacto**: `test_invalid_case_2__negative_focus` estava truncado — faltava o corpo do método. O arquivo de teste foi completado com a implementação correta do caso de teste que verifica `HTTP 422` ao receber valor de foco negativo.

**E3 — Patch**: `Hb Track - Backend/tests/training/invariants/test_inv_train_001_focus_sum_constraint.py`
- Método `test_invalid_case_2__negative_focus` completado com corpo funcional
- Verifica que `session_rpe` negativo dispara erro HTTP 422

**E4 — hb report 202**: Exit Code: 0 ✅
- 3/3 testes PASSED: `test_valid_case__sum_at_120`, `test_invalid_case_1__sum_exceeds_120`, `test_invalid_case_2__negative_focus`

---

### AR_203 — Fix INV-008 3x .parent

**E1 — AR lida**: `docs/hbtrack/ars/features/AR_203_fix_inv-008_schema_path_tem_3_.parent_ao_invés_de_.md`

**E2 — Análise de Impacto**: `sys.path.insert` usava `Path(__file__).parent.parent.parent` (3x) causando ImportError ao resolver raiz do projeto. Correto é 2x`.parent` (tests/training/invariants/ → tests/training/ → Hb Track - Backend/).

**E3 — Patch**: `Hb Track - Backend/tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py`
- 6 ocorrências de `.parent.parent.parent` → `.parent.parent`

**E4 — hb report 203**: Exit Code: 0 ✅
- Todos os testes PASSED

---

### AR_204 — Fix INV-030 3x .parent

**E1 — AR lida**: `docs/hbtrack/ars/features/AR_204_fix_inv-030_schema_path_tem_3_.parent_ao_invés_de_.md`

**E2 — Análise de Impacto**: Mesmo padrão de AR_203 — `Path(__file__).parent.parent.parent` desnecessário.

**E3 — Patch**: `Hb Track - Backend/tests/training/invariants/test_inv_train_030_attendance_correction_fields.py`
- 7 ocorrências de `.parent.parent.parent` → `.parent.parent`

**E4 — hb report 204**: Exit Code: 0 ✅

---

### AR_205 — Fix INV-032 múltiplos bugs (mais complexa do batch)

**E1 — AR lida**: `docs/hbtrack/ars/features/AR_205_fix_inv-032_6_async_fixtures_usam_@pytest.fixture_.md`

**E2 — Análise de Impacto** (4 bugs encadeados descobertos em série):
1. **Bug de import de `date`**: `birth_date="1995-01-01"` (str) → asyncpg rejeita, precisa de `datetime.date`
2. **Campo inexistente `overall_feeling`**: `WellnessPost` não possui esse campo; campos reais: `fatigue_after` + `mood_after`
3. **FK errada `athlete_id=person.id`**: `wellness_post.athlete_id` faz FK para `athletes.id`, não `persons.id`
4. **UniqueViolationError**: constraint parcial `ux_wellness_post_session_athlete WHERE deleted_at IS NULL` — dois registros ativos para mesmo par `(training_session_id, athlete_id)`

**E3 — Patch**: `Hb Track - Backend/tests/training/invariants/test_inv_train_032_wellness_post_rpe.py`
- `from datetime import datetime` → `from datetime import date, datetime`
- Novo import: `from app.models.athlete import Athlete`
- `birth_date="1995-01-01"` → `birth_date=date(1995, 1, 1)` em `inv032_person`
- Nova fixture `inv032_athlete` adicionada (cria `Athlete` vinculado a `inv032_person`)
- 3 métodos de teste: assinatura `inv032_person: Person` → `inv032_athlete: Athlete`
- 3 métodos de teste: `overall_feeling=X` → `fatigue_after=X, mood_after=X`
- 3 métodos de teste: `athlete_id=inv032_person.id` → `athlete_id=inv032_athlete.id`
- `test_valid_case`: soft-delete de `wellness_min` (`deleted_at=datetime.now()`, `deleted_reason="superseded"`) antes de criar `wellness_max` — libera a unique constraint parcial

**Bugs pré-existentes no produto corrigidos** (necessários para importação):
- `Hb Track - Backend/app/api/v1/routers/post_training.py`: `from app.core.database` → `from app.core.db`
- `Hb Track - Backend/app/services/ai_coach_service.py`: `from app.core.database` → `from app.core.db`

**E4 — hb report 205** (após 4 iterações): Exit Code: 0 ✅
- 3/3 testes PASSED: `test_valid_case`, `test_invalid_rpe_too_low`, `test_invalid_rpe_too_high`

---

### AR_206 — Fix CONTRACT-077-085 ROUTER_PATH

**E1 — AR lida**: `docs/hbtrack/ars/features/AR_206_fix_contract-077-085_router_path_tem_3_.parent_ao_.md`

**E2 — Análise de Impacto**: `ROUTER_PATH` definido com 3x `.parent` causando `ModuleNotFoundError` ao importar o roteador. Mesmo padrão das ARs 203/204.

**E3 — Patch**: `Hb Track - Backend/tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py`
- `ROUTER_PATH` e `sys.path.insert`: `.parent.parent.parent` → `.parent.parent`

**E4 — hb report 206**: Exit Code: 0 ✅

---

## Nota Técnica: `| tail -20` removido dos validation commands

Os validation commands originais nas ARs continham `| tail -20` (incompatível com Windows cmd.exe). Todos foram executados sem esse sufixo, passando `2>&1` diretamente para o pytest.

---

## Stage Exato

```
docs/hbtrack/evidence/AR_202/executor_main.log  ✅ staged
docs/hbtrack/evidence/AR_203/executor_main.log  ✅ staged
docs/hbtrack/evidence/AR_204/executor_main.log  ✅ staged
docs/hbtrack/evidence/AR_205/executor_main.log  ✅ staged
docs/hbtrack/evidence/AR_206/executor_main.log  ✅ staged
docs/hbtrack/ars/features/AR_202_*.md           ✅ staged
docs/hbtrack/ars/features/AR_203_*.md           ✅ staged
docs/hbtrack/ars/features/AR_204_*.md           ✅ staged
docs/hbtrack/ars/features/AR_205_*.md           ✅ staged
docs/hbtrack/ars/features/AR_206_*.md           ✅ staged
```

---

## Nota para o Testador

- Executar `hb verify 202` → `hb verify 203` → `hb verify 204` → `hb verify 205` → `hb verify 206` (triple-run cada)
- Validar exit_code=0 e hashes idênticos nos 3 runs
- `hb seal` em ordem crescente (202 → 206) após verificação humana
