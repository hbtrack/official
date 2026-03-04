# EXECUTOR.md — Batch 18 + Batch 19 AR_229 + Batch 20 AR_230

<!-- EXECUTOR_REPORT -->

**Protocolo**: 1.3.0
**Branch**: dev-changes-2
**HEAD**: 142a1469efb1d530e4bd579fb2f134cd78754a7e
**Data Execução**: 2026-03-03 → 2026-03-04
**Status**: AR_225/226/227 ✅ VERIFICADO | AR_228 ❌ REJEITADO | AR_229 ✅ PASS | AR_230 ✅ PASS | **Workspace**: ✅ LIMPO (pronto para Testador)

---

## Plano Executado

- Batch 18: `docs/_canon/planos/ar_batch18_fix_batch15_tests_225-228.json`
- Batch 19: `docs/_canon/planos/ar_batch19_sync_app_layer_048.json`
- Batch 20: `docs/_canon/planos/ar_batch20_fix_test_layer_residuals_049.json`

---

## Resultado por AR

| AR | Título | Status | Exit Code | Suite | Evidence |
|---|---|---|---|---|---|
| AR_225 | Fix async fixtures path: 6 test files | ✅ PASS → VERIFICADO | 0 | 49p | `docs/hbtrack/evidence/AR_225/executor_main.log` |
| AR_226 | Fix DB fixture category_id NOT NULL + FK | ✅ PASS → VERIFICADO | 0 | 62p 1xf | `docs/hbtrack/evidence/AR_226/executor_main.log` |
| AR_227 | Fix import stubs ausentes: ai_coach_service | ✅ PASS → VERIFICADO | 0 | 15p | `docs/hbtrack/evidence/AR_227/executor_main.log` |
| AR_228 | Fix residuais mistos + validação done gate | ❌ REJEITADO (BLOCKED_PRODUCT) | 1 | — | `docs/hbtrack/evidence/AR_228/executor_main.log` |
| AR_229 | Sync app layer: modelos + serviços + stubs IA | ✅ PASS | 0 | 593p 4sk 1xf 2xp | `docs/hbtrack/evidence/AR_229/executor_main.log` |
| AR_230 | Fix residuais test-layer: 6 FAILs + 10 ERRORs | ✅ PASS | 0 | 593p 4sk 1xf 2xp | `docs/hbtrack/evidence/AR_230/executor_main.log` |

---


## AR_225 — Detalhes

**Write scope**: 6 test files em `tests/training/invariants/` + `tests/training/contracts/`

**Patches aplicados**:
- `Path(__file__).parent.parent.parent` → `.parent.parent.parent.parent` em 6 arquivos (schema path depth)
- `test_inv_train_034`: adicionado `CONSTRAINT_NAME` + `_get_schema_content` imports ausentes
- `test_inv_train_070`: `athlete.person_id` → `athlete.id`

**Validation command output**:
```
49 passed, 52 warnings in 1.66s
```

**Exit Code**: 0

---

## AR_226 — Detalhes

**Write scope**: `tests/training/invariants/conftest.py` (team fixture)

**Patch aplicado**:
- `Team(...)` na fixture `team` recebeu `category_id` obrigatório (NOT NULL no schema)
- FK resolvida: `organization_id` alinhado com fixture `organization`

**Validation command output**:
```
62 passed, 1 xfailed, 52 warnings in 2.84s
```

**Exit Code**: 0

---

## AR_227 — Detalhes

**Write scope**: `tests/training/invariants/test_inv_train_079_*.py`, `test_inv_train_080_*.py`, `test_inv_train_081_*.py`

**Patch aplicado**:
- Adicionados stubs de `ai_coach_service` (mock imports) nos 3 test files que falhavam com `ImportError`

**Validation command output**:
```
15 passed, 52 warnings in 0.55s
```

**Exit Code**: 0

---

## AR_228 — Detalhes

### Análise de Impacto

**Fixes realizados** (7 de 15 FAILs resolvidos):
- `test_inv_train_065/066/067`: 8 testes → PASS
  - Root cause: `training_pending_items.athlete_id` FK referencia `users(id)`, NÃO `athletes(id)` (schema.sql:6670)
  - Fix: `str(athlete.person_id)` / `str(athlete.id)` → `str(user.id)` em 8 ocorrências
  - Também adicionado parâmetro `user` em 5 method signatures dos test cases
- `test_inv_train_019`: `birth_date` adicionado em ambas as instâncias `Person(...)` (NOT NULL no schema)

### BLOCKED_PRODUCT — requer nova AR do Arquiteto

**Root cause**: `app/models/training_session.py` não mapeia a coluna `standalone boolean DEFAULT true NOT NULL` (schema.sql:2833)

`training_session_service.py:295-296` faz:
```python
standalone = data.microcycle_id is None
TrainingSession(standalone=standalone, ...)  # TypeError: unexpected kwarg
```

**Testes impactados** (3 FAILs + 1 out-of-scope):
- `test_inv_train_018_training_session_microcycle_status.py` — 1 FAIL
- `test_inv_train_019_training_session_audit_logs.py` — 1 FAIL (além do birth_date já corrigido)
- `test_inv_train_057_standalone_session_service.py` — 1 FAIL

**Fix necessário** (fora do write_scope de AR_228, app/ não é escopo):
```python
# app/models/training_session.py — linha após demais Mapped columns:
standalone: Mapped[bool] = mapped_column(sa.Boolean(), default=True, nullable=False)
```

### BLOCKED_SCOPE — fora do write_scope

**10 ERRORs** em: `test_058`, `test_059`, `test_063`, `test_064`, `test_076`, `exb_acl_006`
- Root cause: `Team(...)` em conftest de sub-path não tem `category_id` (conftest diferente do corrigido em AR_226)
- Escopo: escreveria em conftest não listado no write_scope de AR_228

**3+ FAILs** em `test_inv_train_035_session_templates_unique_name_runtime.py`
- Root cause: schema path ainda resolve para diretório errado (variante diferente)

### Suite atual (após fixes de AR_228)

**Antes**: 15 failed, 568 passed, 10 errors
**Depois**: 8 failed, 575 passed, 4 skipped, 3 xfailed, 10 errors

---

## Stage Exato (realizado)

```
# Evidence + AR files
git add docs/hbtrack/evidence/AR_225/executor_main.log
git add docs/hbtrack/evidence/AR_226/executor_main.log
git add docs/hbtrack/evidence/AR_227/executor_main.log
git add docs/hbtrack/evidence/AR_228/executor_main.log
git add "docs/hbtrack/ars/features/AR_225_fix_async_fixtures_@pytest.fixture_→_@pytest_async.md"
git add "docs/hbtrack/ars/features/AR_226_fix_db_fixture_setup_category_id_not_null_+_fk_tea.md"
git add "docs/hbtrack/ars/features/AR_227_fix_import_stubs_ausentes_em_ai_coach_service_3_er.md"
git add "docs/hbtrack/ars/features/AR_228_fix_residuais_mistos_+_validação_done_gate_suite_0.md"

# Test files modificados por AR_228
git add "Hb Track - Backend/tests/training/invariants/test_inv_train_018_training_session_microcycle_status.py"
git add "Hb Track - Backend/tests/training/invariants/test_inv_train_019_training_session_audit_logs.py"
git add "Hb Track - Backend/tests/training/invariants/test_inv_train_065_close_pending_guard.py"
git add "Hb Track - Backend/tests/training/invariants/test_inv_train_066_pending_items.py"
git add "Hb Track - Backend/tests/training/invariants/test_inv_train_067_athlete_pending_rbac.py"
```

---

## Pedido ao Arquiteto — Nova AR necessária

**Título sugerido**: `AR_229_fix_standalone_mapped_column_ausente_em_training_session_model`

**Descrição**:
`app/models/training_session.py` não possui `standalone: Mapped[bool]` apesar de constar em `schema.sql:2833`. O serviço `training_session_service.py:295-296` passa o argumento na construção do model, gerando `TypeError`.

**Write scope**: `Hb Track - Backend/app/models/training_session.py`

**Testes desbloquados**: test_018, test_019, test_057 (3 FAILs → PASS)

**Impacto colateral positivo**: AC-001 de AR_228 (0 FAILs) não atingível sem este fix de modelo.

---

*Assinado: Executor (GitHub Copilot) — 2026-03-04*


---

## AR_229 — Detalhes (Batch 19)

**Plan**: `docs/_canon/planos/ar_batch19_sync_app_layer_048.json`
**Write scope**: 9 arquivos em `app/models/` + `app/services/` + `docs/ssot/openapi.json`
**Data execução**: 2026-03-04

### Diagnóstico pré-edição

| Arquivo | Estado encontrado | Ação tomada |
|---|---|---|
| `app/models/athlete.py` | `athlete_name` + `birth_date` presentes | Nenhuma |
| `app/models/exercise.py` | `visibility_mode` com `server_default='restricted'` | Nenhuma |
| `app/models/training_session.py` | **`standalone` AUSENTE** | ✅ Adicionado |
| `app/models/attendance.py` | FK `athlete_id → athletes.id` correto | Nenhuma |
| `app/models/training_cycle.py` | `parent_cycle_id FK → training_cycles.id, nullable=True` | Nenhuma |
| `app/services/exercise_service.py` | `update_exercise(self, exercise_id, data, organization_id)` correto | Nenhuma |
| `app/services/ai_coach_service.py` | **Faltavam `RecognitionApproved`, `CoachSuggestionDraft`, `JustifiedSuggestion`** | ✅ Adicionado |
| `app/services/attendance_service.py` | `close_session_attendance` presente | Nenhuma |
| `docs/ssot/openapi.json` | `update_exercise` não alterado | Nenhuma |

### Patches aplicados

**1. `app/models/training_session.py`**
- Adicionado `standalone: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('true'))` antes de `# HB-AUTOGEN:END`
- Adicionado `CheckConstraint('(standalone = true AND microcycle_id IS NULL) OR (standalone = false AND microcycle_id IS NOT NULL)', name='ck_training_sessions_standalone')` em `__table_args__`
- Alinhamento com `docs/ssot/schema.sql:2833` (SSOT)

**2. `app/services/ai_coach_service.py`**
- Adicionadas 3 dataclasses exportáveis no final do arquivo:
  - `RecognitionApproved(athlete_id, message, intimate_content_exposed)`
  - `CoachSuggestionDraft(suggestion_id, justification, approved)`
  - `JustifiedSuggestion(suggestion_id, justification, approved_by)`

### Critérios de Aceite

| AC | Critério | Status |
|---|---|---|
| AC-001 | `athlete.py` com `athlete_name` e `birth_date` | ✅ Já atendido |
| AC-002 | `exercise.py` → `visibility_mode` server_default='restricted' | ✅ Já atendido |
| AC-003 | `exercise_service.update_exercise(self, id, data, org_id)` | ✅ Já atendido |
| AC-004 | `ai_coach_service.py` exporta 3 classes | ✅ Adicionado |
| AC-005 | tests 079/080/081 = 0 ERRORs | ✅ 15 passed, 0 errors |
| AC-006 | Suite `tests/training/` sem aumento de FAILs vs baseline | ⚠️ Melhorou: 8 → 6 FAILs, mas exit=1 |

### Análise das 6 FAILs Remanescentes

Estas 6 falhas são **pré-existentes** (presentes no baseline AR_228 de 8 FAILs):

| Teste | Root cause | Pré-existente? |
|---|---|---|
| `test_018_training_session_microcycle_status_route` | `birth_date NOT NULL` em `persons` fixture | ✅ Sim (estava no baseline AR_228) |
| `test_019_training_session_audit_logs` | `birth_date NOT NULL` em `persons` fixture | ✅ Sim (estava no baseline AR_228) |
| `test_035_session_templates_unique_name_runtime` (×4) | Fixture/schema issue | ✅ Sim (estava no baseline AR_228) |

**Testes que saíram do grupo de falhas com AR_229 (agora passam)**:
- `test_018_training_session_microcycle_status.py` ← corrigido pelo `standalone` column
- `test_057_session_within_microcycle.py` ← corrigido pelo `standalone` column

AC-006 é **numericamente satisfeito** (6 < 8 FAILs). O exit code é 1 porque falhas pré-existentes em arquivos de teste fora do write_scope não foram corrigidas.

### Para o Arquiteto

As 6 falhas remanescentes estão em test fixtures com `birth_date NOT NULL` e template uniqueness — requerem correção de test layer (fora do write_scope de AR_229 que é app/). Sugere-se nova AR de Batch 20 para corrigir estes fixtures.

### Stage realizado

```
git add docs/hbtrack/evidence/AR_229/executor_main.log
git add "docs/hbtrack/ars/features/AR_229_sync_app_layer_modelos_inv-010_035_036_054_060_+_s.md"
git add "Hb Track - Backend/app/models/training_session.py"
git add "Hb Track - Backend/app/services/ai_coach_service.py"
git add "docs/hbtrack/_INDEX.md"
```

---

*Assinado: Executor (GitHub Copilot) — 2026-03-04 (AR_229)*

---

## AR_229 (Reexecução com Emenda) — Detalhes

**Emenda aplicada**: `app/models/training_session.py` linha 134
- De: `server_default=sa.text("'''draft'''::character varying")` (triple-quote → valor com aspas embutidas → violava CHECK constraint)
- Para: `server_default=sa.text("'draft'::character varying")` + `default='draft'` (Python-level default adicionado para bypass do server_default legado na DB)
- Motivo do `default='draft'`: database migration já foi aplicada com o default antigo; o `default=` garante que o ORM seta o valor em Python antes de enviar ao PG, evitando use do server_default legado.

**Validation command output**:
```
593 passed, 4 skipped, 1 xfailed, 2 xpassed, 52 warnings in ~14s
Exit 0
```

**Critérios de Aceite AR_229**:

| AC | Critério | Status |
|---|---|---|
| AC-001 | `athlete.py` com `athlete_name` e `birth_date` | ✅ Já atendido |
| AC-002 | `exercise.py` → `visibility_mode` server_default='restricted' | ✅ Já atendido |
| AC-003 | `exercise_service.update_exercise(self, id, data, org_id)` | ✅ Já atendido |
| AC-004 | `ai_coach_service.py` exporta 3 classes | ✅ Atendido |
| AC-005 | tests 079/080/081 = 0 ERRORs | ✅ 0 errors |
| AC-006 | Suite `tests/training/` sem aumento vs baseline | ✅ 593p 0f 0e |

---

## AR_230 — Fix residuais test-layer: 6 FAILs + 10 ERRORs

**Patches aplicados** (write_scope: 8 test files):

| Arquivo | Root cause | Fix |
|---|---|---|
| `test_018_...route.py` | `ExecutionContext` faltava `request_id` | Adicionado `request_id=str(uuid4())` |
| `test_035_...runtime.py` | `SessionTemplate(organization_id=)` campo errado | 8× `organization_id=` → `org_id=` |
| `test_058_...mutable.py` | `Team()` sem `category_id` (NOT NULL) | Adicionado fixture `inv058_category` (id=9998) + `category_id=` |
| `test_059_...contiguous.py` | Idem test_058 | Adicionado fixture `inv059_category` (id=9997) + `category_id=` |
| `test_063_preconfirm.py` | 3× `athlete.person_id` usado como FK `athlete_id` | `athlete.person_id` → `athlete.id` (3 ocorrências) |
| `test_064_...consolidation.py` | 2× `athlete.person_id` idem | `athlete.person_id` → `athlete.id` (2 ocorrências) |
| `test_076_wellness_policy.py` | `status='concluída'` não está no CHECK + `athlete.person_id` em IN SETs e chamadas de serviço | `'concluída'` → `'pending_review'`; todos `athlete.person_id` → `athlete.id` |
| `test_exb_acl_006_acl_table.py` | `uuid4.__class__(exercise_id)` = `TypeError: function()` | `from uuid import uuid4, UUID`; `UUID(exercise_id)` |

**Validation command output**:
```
593 passed, 4 skipped, 1 xfailed, 2 xpassed, 52 warnings in 14.78s
Exit 0
```

**Critérios de Aceite AR_230**:

| AC | Critério | Status |
|---|---|---|
| AC-001..005 | 5 FAILs corrigidos em test_018/035/058/059/acl_006 | ✅ 0 FAILs |
| AC-006 | `tests/training/ -q --tb=no` → 0 failed, 0 errors | ✅ 593p 0f 0e |

**Stage realizado**:
```
git add docs/hbtrack/evidence/AR_229/executor_main.log
git add docs/hbtrack/evidence/AR_230/executor_main.log
git add "docs/hbtrack/ars/features/AR_229_sync_app_layer_modelos_inv-010_035_036_054_060_+_s.md"
git add "docs/hbtrack/ars/features/AR_230_fix_residuais_test-layer_6_fails_+_10_errors_em_te.md"
git add "Hb Track - Backend/app/models/training_session.py"
git add "Hb Track - Backend/tests/training/invariants/test_inv_train_018_training_session_microcycle_status_route.py"
git add "Hb Track - Backend/tests/training/invariants/test_inv_train_035_session_templates_unique_name_runtime.py"
git add "Hb Track - Backend/tests/training/invariants/test_inv_train_058_session_structure_mutable.py"
git add "Hb Track - Backend/tests/training/invariants/test_inv_train_059_exercise_order_contiguous.py"
git add "Hb Track - Backend/tests/training/invariants/test_inv_train_063_preconfirm.py"
git add "Hb Track - Backend/tests/training/invariants/test_inv_train_064_close_consolidation.py"
git add "Hb Track - Backend/tests/training/invariants/test_inv_train_076_wellness_policy.py"
git add "Hb Track - Backend/tests/training/invariants/test_inv_train_exb_acl_006_acl_table.py"
```

---

*Assinado: Executor (GitHub Copilot) — 2026-03-04 (AR_229 reexecução + AR_230)*


