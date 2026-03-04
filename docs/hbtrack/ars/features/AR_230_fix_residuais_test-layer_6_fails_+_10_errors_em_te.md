# AR_230 — Fix residuais test-layer: 6 FAILs + 10 ERRORs em tests/training/invariants/ (AR-TRAIN-049)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Correção deterministíca de bugs de test-layer em 8 arquivos de teste. Diagnóstico completo:

## FAIL 1 — test_018_route.py (1 FAIL)
**Root cause:** `Person(...)` sem campo `birth_date` — `persons.birth_date NOT NULL`.
**Fix:** Adicionar `birth_date=date(1990, 1, 1)` no construtor `Person()` nas linhas 42-47.
**Ref:** Mesmo padrão já aplicado em outros arquivos (ex: test_019 linhas 32, 105, 130, 139).

## FAIL 2 — test_035_session_templates_unique_name_runtime.py (4 FAILs)
**Root cause:** `SessionTemplate(organization_id=UUID(...))` — o modelo `SessionTemplate` usa `org_id` (não `organization_id`) como campo FK para `organizations`.
**Fix:** Substituir `organization_id=` por `org_id=` em todos os 4 métodos de teste.
**Evidência:** `app/models/session_template.py` linha 52: `org_id: Mapped[UUID]`.

## ERROR 1/2 — test_058_session_structure_mutable.py (1 ERROR)
**Root cause:** Fixture `inv058_team` cria `Team(...)` sem `category_id` — `teams.category_id NOT NULL`.
**Fix:** Adicionar fixture `category` (idêntica ao padrão do conftest.py linhas 128-140) dentro da classe e passar `category_id=category.id` ao construtor `Team()`.
**Ref:** Conftest cria `category` com `id=9999` via `ON CONFLICT DO NOTHING` — usar mesmo padrão.

## ERROR 3/4 — test_059_exercise_order_contiguous.py (1 ERROR)
**Root cause:** Fixture `inv059_team` cria `Team(...)` sem `category_id`.
**Fix:** Mesmo padrão que test_058: adicionar fixture `category` local e `category_id=category.id`.

## ERROR 5/6 — test_063_preconfirm.py (2 ERRORs)
**Root cause:** Fixture `team_reg` usa `athlete_id: str(athlete.person_id)` — mas `team_registrations.athlete_id` FK refs `athletes.id` (PK auto-gerada via `gen_random_uuid()`), não `athletes.person_id`.
**Fix:** Substituir `str(athlete.person_id)` → `str(athlete.id)` na fixture `team_reg` (linha ~33) E em qualquer outro lugar do arquivo que use `athlete.person_id` como athlete_id em inserts.
**Evidência:** `app/models/athlete.py` linha 103: `id: Mapped[UUID] = mapped_column(..., primary_key=True, server_default=sa.text('gen_random_uuid()'))` — PK separada de `person_id`.

## ERROR 7 — test_064_close_consolidation.py (1 ERROR)
**Root cause:** Mesmo bug que test_063 — fixture `team_reg` usa `athlete_id: str(athlete.person_id)` ao inserir em `team_registrations`.
**Fix:** Substituir `str(athlete.person_id)` → `str(athlete.id)` na fixture `team_reg` interna.

## ERROR 8/9/10 — test_076_wellness_policy.py (3 ERRORs)
**Root cause:** SQL direto usa `status='concluída'` ao inserir em `training_sessions`, mas `check_training_session_status` só permite: `draft | scheduled | in_progress | pending_review | readonly`.
**Fix:** Localizar o INSERT de `training_sessions` no arquivo (linha ~36-40) e substituir `'concluída'` por `'pending_review'` (semanticamente mais próximo de sessão encerrada aguardando validação).
**Ref:** INVARIANTS_TRAINING.md §training_session_status_lifecycle linhas 253-254.

## ERROR 11/12 — test_exb_acl_006_acl_table.py (2 ERRORs)
**Root cause:** Fixture `exercise` retorna `type('Exercise', (), {'id': uuid4.__class__(exercise_id)})()` — `uuid4.__class__` é a classe `function`, gerando `TypeError: function() missing required argument 'globals' (pos 2)` ao tentar chamar `function(exercise_id)`.
**Fix:** Substituir `uuid4.__class__(exercise_id)` → `UUID(exercise_id)` e garantir que `UUID` está importado (`from uuid import uuid4, UUID`).

## PROCESSO SUGERIDO
1. Ler cada arquivo antes de editar — localizar exatamente as linhas a alterar
2. Fixes podem ser feitos em qualquer ordem — são independentes entre si
3. test_058/059: verificar se `category` fixture já existe na classe antes de criar duplicata
4. Ao final: rodar validation_command para confirmar 0 FAILs + 0 ERRORs em tests/training/
5. Se encontrar qualquer necessidade de alterar arquivo FORA do write_scope → BLOCKED (reportar ao Arquiteto)

## Critérios de Aceite
AC-001: pytest tests/training/invariants/test_inv_train_018_training_session_microcycle_status_route.py = 0 FAIL, 0 ERROR.
AC-002: pytest tests/training/invariants/test_inv_train_035_session_templates_unique_name_runtime.py = 0 FAIL, 0 ERROR (4 testes passando).
AC-003: pytest tests/training/invariants/test_inv_train_058_session_structure_mutable.py tests/training/invariants/test_inv_train_059_exercise_order_contiguous.py = 0 ERROR.
AC-004: pytest tests/training/invariants/test_inv_train_063_preconfirm.py tests/training/invariants/test_inv_train_064_close_consolidation.py = 0 ERROR.
AC-005: pytest tests/training/invariants/test_inv_train_076_wellness_policy.py tests/training/invariants/test_inv_train_exb_acl_006_acl_table.py = 0 ERROR.
AC-006: pytest tests/training/ -q --tb=no = saída final com 0 failed, 0 errors (suite training/ completa verde).

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_018_training_session_microcycle_status_route.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_035_session_templates_unique_name_runtime.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_058_session_structure_mutable.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_059_exercise_order_contiguous.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_063_preconfirm.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_064_close_consolidation.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_076_wellness_policy.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_exb_acl_006_acl_table.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -m pytest tests/training/ -q --tb=no 2>&1
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_230/executor_main.log`

## Rollback Plan (Contrato)
```
python scripts/run/hb_cli.py plan docs/_canon/planos/ar_batch20_fix_test_layer_residuals_049.json --dry-run
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- test_058/059: a fixture 'category' interna deve usar ON CONFLICT DO NOTHING para evitar conflito com category id=9999 já usada por outros testes rodando na mesma sessão DB.
- test_063/064: garantir que athlete.id está disponível após flush (PK auto-gerada pelo servidor) — adicionar await async_db.refresh(athlete) antes de usar athlete.id se necessário.
- test_076: substituir 'concluída' por 'pending_review' — verificar se a lógica do teste ainda faz sentido com esse status (wellness deve ser coletado antes de pending_review).
- test_acl_006: importar UUID além de uuid4 se não estiver no import ainda.
- Validar que nenhum outro arquivo de teste usa athlete.person_id como athlete_id FK — se encontrar, reportar ao Arquiteto (escopo desta AR é apenas os 8 arquivos listados).

## Análise de Impacto

**Data:** 2026-03-04  
**Executor:** Copilot Executor

### Diagnóstico (leitura dos 8 arquivos pré-edição)

| Arquivo | Root Cause Confirmado | Ação |
|---|---|---|
| `test_018_..._route.py` | `Person()` sem `birth_date` (linha 42-47) | Adicionar `birth_date=date(1990, 1, 1)` + confirmar import `date` |
| `test_035_...runtime.py` | `SessionTemplate(organization_id=...)` — kwarg inválido; modelo tem `org_id` | Substituir `organization_id=` por `org_id=` (4 ocorrências) |
| `test_058_...mutable.py` | `inv058_team` cria `Team()` sem `category_id` NOT NULL | Add `@pytest_asyncio.fixture async def inv058_category` + `category_id=category.id` na fixture `inv058_team` |
| `test_059_...contiguous.py` | `inv059_team` cria `Team()` sem `category_id` | Mesmo padrão que test_058 |
| `test_063_preconfirm.py` | `str(athlete.person_id)` como `athlete_id` em inserts de team_registrations; FK refs `athletes.id` | Substituir `athlete.person_id` → `athlete.id` + `await async_db.refresh(athlete)` após flush se necessário |
| `test_064_close_consolidation.py` | Mesmo bug do test_063 na fixture `team_reg` local | Mesmo fix |
| `test_076_wellness_policy.py` | INSERT com `status='concluída'` viola `check_training_session_status` | Substituir `'concluída'` → `'pending_review'` |
| `test_exb_acl_006_acl_table.py` | `uuid4.__class__(exercise_id)` → `TypeError` (function != UUID) | Substituir por `UUID(exercise_id)` + importar `UUID` |

### Impacto dos patches
- Zero mudança de produto — apenas bugs de test-layer
- Nenhuma migração Alembic necessária (não toca `app/`)
- Fixtures `category` locais usarão `ON CONFLICT DO NOTHING` para isolar de outros fixtures com id=9999
- Amendment em `training_session.py` (AR_229) já aplicado antes desta AR — corrige test_019 por efeito cascata

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 142a146
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -m pytest tests/training/ -q --tb=no 2>&1`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T00:32:50.276624+00:00
**Behavior Hash**: c6412ffdf17956ebfcd20fb05ed38b9e5da72ca696da3ae9b2d9d13b847a8d0a
**Evidence File**: `docs/hbtrack/evidence/AR_230/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 142a146
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_230_142a146/result.json`

### Selo Humano em 142a146
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-04T01:14:18.952482+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_230_142a146/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_230/executor_main.log`
