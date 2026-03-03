# ARQUITETO.md — Handoff para executor (Batch 9)

| Campo | Valor |
|---|---|
| **Protocolo** | v1.3.0 |
| **Branch** | dev-changes-2 |
| **HEAD** | b123a58 |
| **Data** | 2026-03-03 |
| **Status** | PLAN_HANDOFF — Re-execução Batch 9 (AR_202..206) |
| **gen_docs_ssot.py** | OpenAPI FAILED (backend offline, pré-existente) / Schema SQL ✅ / Alembic ✅ / Manifest ✅ |

---

## Contexto

**AR_210 (Fix sistêmico compute_behavior_hash)** ✅ VERIFICADO.

Anteriormente, o Batch 9 foi rejeitado pelo Testador devido ao `FLAKY_OUTPUT` causado por timings variáveis do pytest no `stdout`. O fix sistêmico implementado em AR_210 normaliza timings (`\b\d+\.\d+s\b` → `X.Xs`) antes de gerar o hash, tornando o processo determinístico.

**Missão atual:** Realizar a verificação oficial (triple-run) das ARs do Batch 9. Como o código das ARs 202..206 já foi reportado e está staged, o próximo passo é estritamente a verificação via Testador.

---

## Ordem de Execução

Ao invés de passar para o Executor (que já concluiu seu trabalho para este batch), o fluxo segue para o **Testador** para re-validar as ARs com a nova infraestrutura de hash.

```
AR_202 → AR_203 → AR_204 → AR_205 → AR_206
```

---

## Diagnóstico por AR

*Nota: Todas as ARs abaixo já foram reportadas. O Testador deve apenas executar `hb verify <id>`.*

### AR_202 .. AR_206

**Estado**: `EM_EXECUCAO` (Reported, staged evidence).
**validation_command**: (Original, inalterado).
**Mudança esperada**: O hash gerado por `hb_cli.py verify` agora deve ser idêntico nos 3 runs devido à normalização implementada em AR_210.

---

## Instrução ao Testador

```
PLAN_HANDOFF — Testador deve:
1. Executar triple-run de verificação para as ARs do Batch 9:
   python scripts/run/hb_cli.py verify 202
   python scripts/run/hb_cli.py verify 203
   python scripts/run/hb_cli.py verify 204
   python scripts/run/hb_cli.py verify 205
   python scripts/run/hb_cli.py verify 206
2. Confirmar que Consistency = OK (3/3 hashes idênticos).
3. Após aprovação de todas, notificar para hb seal humano.
```

_gerado pelo Arquiteto — 2026-03-03_


---

## Contexto

Ciclo anterior (AR_200 + AR_201) ✅ VERIFICADO. Kanban §24/§25 = ✅ VERIFICADO.

Este ciclo planeja o caminho completo para o **Done Gate do módulo TRAINING** (§10 TEST_MATRIX_TRAINING.md):

1. **Batch 9** (AR_202..206): Eliminar 5 FAILs críticos — todos test-layer, zero mudança de produto.
2. **Batch 10** (AR_207..208): Cobrir evidências P0 restantes — 8 flows MANUAL_GUIADO + 4 contracts P0 com teste automatizado.
3. **Batch 11** (AR_209): Done Gate — sync TEST_MATRIX v1.8.0 + FASE-1 smoke 5 Batch9 + FASE-2 sanity AR_200 full (11 arquivos) + declaração DONE.

Root cause analysis concluída pelo Arquiteto:
- **INV-001**: `test_invalid_case_2__negative_focus` espera `ck_training_sessions_focus_total_sum` mas valor negativo (`focus_attack_positional_pct=-5`) dispara `ck_training_sessions_focus_attack_positional_range` primeiro.
- **INV-008**: `Path(__file__).parent.parent.parent / "docs/ssot/schema.sql"` resolve para `tests/docs/ssot/schema.sql` (inexistente); fix = adicionar `.parent` → aponta para `Hb Track - Backend/docs/ssot/schema.sql`.
- **INV-030**: Mesma causa raiz do INV-008.
- **INV-032**: 6 fixtures `async def` decoradas com `@pytest.fixture` (linhas 40/54/66/81/94/110) em vez de `@pytest_asyncio.fixture`.
- **CONTRACT-077-085**: `ROUTER_PATH = Path(__file__).parent.parent.parent / "app/..."` resolve para `tests/app/...` (inexistente); fix = adicionar `.parent`.

---

## Planos Materializados

| AR | AR-TRAIN | Plano JSON | Dependência | Dry-run |
|---|---|---|---|---|
| AR_202 | AR-TRAIN-024 | `docs/_canon/planos/ar_batch9_fix_fails_202_206.json` (task 202) | nenhuma | ✅ PASS |
| AR_203 | AR-TRAIN-025 | `docs/_canon/planos/ar_batch9_fix_fails_202_206.json` (task 203) | nenhuma | ✅ PASS |
| AR_204 | AR-TRAIN-026 | `docs/_canon/planos/ar_batch9_fix_fails_202_206.json` (task 204) | nenhuma | ✅ PASS |
| AR_205 | AR-TRAIN-027 | `docs/_canon/planos/ar_batch9_fix_fails_202_206.json` (task 205) | nenhuma | ✅ PASS |
| AR_206 | AR-TRAIN-028 | `docs/_canon/planos/ar_batch9_fix_fails_202_206.json` (task 206) | nenhuma | ✅ PASS |
| AR_207 | AR-TRAIN-029 | `docs/_canon/planos/ar_batch10_flows_contracts_207_208.json` (task 207) | AR_202..206 VERIFICADO | ✅ PASS |
| AR_208 | AR-TRAIN-030 | `docs/_canon/planos/ar_batch10_flows_contracts_207_208.json` (task 208) | AR_202..206 VERIFICADO | ✅ PASS |
| AR_209 | AR-TRAIN-031 | `docs/_canon/planos/ar_209_done_gate_training.json` (task 209) | AR_202..208 VERIFICADO | ✅ PASS |

---

## Ordem de Execução

```
Batch 9 (paralelas entre si — sem deps): AR_202 → AR_203 → AR_204 → AR_205 → AR_206
  (todos os 5 são independentes; podem ser executados em sequência rápida)

Batch 10 (após Batch 9 VERIFICADO): AR_207 → AR_208
  (AR_207 e AR_208 podem ser paralelas)

Batch 11 (após Batches 9+10 VERIFICADOS): AR_209
```

---

## Diagnóstico por AR

### AR_202 — Fix INV-001: expected constraint name errado

**write_scope:**
- `Hb Track - Backend/tests/training/invariants/test_inv_train_001_focus_sum_constraint.py`

**Fix exato:** Na função `test_invalid_case_2__negative_focus`, linha ~220-223: mudar a string esperada de `"ck_training_sessions_focus_total_sum"` para `"ck_training_sessions_focus_attack_positional_range"` na chamada `assert_pg_constraint_violation`.

**validation_command:**
```
cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_001_focus_sum_constraint.py -v --tb=short 2>&1 | tail -20
```

**AC-001:** pytest = 0 FAILs, 0 ERRORs.
**Risco:** Verificar outros test cases que possam esperar `ck_training_sessions_focus_total_sum` com valores negativos.

---

### AR_203 — Fix INV-008: schema_path 3 .parent → 4 .parent

**write_scope:**
- `Hb Track - Backend/tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py`

**Fix exato:** `Path(__file__).parent.parent.parent / "docs" / "ssot" / "schema.sql"` → `Path(__file__).parent.parent.parent.parent / "docs" / "ssot" / "schema.sql"`. Arquivo em `tests/training/invariants/` → 4 parents = `Hb Track - Backend/` → schema existe.

**validation_command:**
```
cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py -v --tb=short 2>&1 | tail -20
```

**AC-001:** pytest = 0 FAILs, 0 ERRORs.

---

### AR_204 — Fix INV-030: schema_path 3 .parent → 4 .parent (mesma causa INV-008)

**write_scope:**
- `Hb Track - Backend/tests/training/invariants/test_inv_train_030_attendance_correction_fields.py`

**Fix exato:** Mesmo fix de AR_203 — adicionar `.parent` extra na definição de `schema_path`.

**validation_command:**
```
cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_030_attendance_correction_fields.py -v --tb=short 2>&1 | tail -20
```

**AC-001:** pytest = 0 FAILs, 0 ERRORs.

---

### AR_205 — Fix INV-032: 6 async fixtures @pytest.fixture → @pytest_asyncio.fixture

**write_scope:**
- `Hb Track - Backend/tests/training/invariants/test_inv_train_032_wellness_post_rpe.py`

**Fix exato:**
1. Adicionar `import pytest_asyncio` no bloco de imports.
2. Linhas 40, 54, 66, 81, 94, 110: `@pytest.fixture` → `@pytest_asyncio.fixture` **somente** nas `async def` fixtures (não tocar fixtures síncronas).

**validation_command:**
```
cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_032_wellness_post_rpe.py -v --tb=short 2>&1 | tail -20
```

**AC-001:** pytest = 0 FAILs, 0 ERRORs, sem `PytestUnraisableExceptionWarning` de async.
**Risco:** Verificar `pytest.ini` asyncio_mode — se `strict`, `@pytest_asyncio.fixture` é obrigatório (já é o caso).

---

### AR_206 — Fix CONTRACT-077-085: ROUTER_PATH 3 .parent → 4 .parent

**write_scope:**
- `Hb Track - Backend/tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py`

**Fix exato:** Definição de `ROUTER_PATH` (~linha 27-31): `Path(__file__).parent.parent.parent / "app" / ...` → `Path(__file__).parent.parent.parent.parent / "app" / ...`. Router `training_alerts_step18.py` existe em `Hb Track - Backend/app/api/v1/routers/`.

**validation_command:**
```
cd "Hb Track - Backend" && pytest tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py -v --tb=short 2>&1 | tail -20
```

**AC-001:** pytest = 0 FAILs, 0 ERRORs.

---

### AR_207 — Flow P0 evidence: FLOW-TRAIN-001..006 + 017 + 018 (MANUAL_GUIADO)

**write_scope (governed):**
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` (§6: Status/Últ.Execução/Evidência para 8 flows)

**Deliverables adicionais (criados pelo Executor, fora governed roots):**
- `_reports/training/TEST-TRAIN-FLOW-001.md` a `_reports/training/TEST-TRAIN-FLOW-006.md`
- `_reports/training/TEST-TRAIN-FLOW-017.md`, `_reports/training/TEST-TRAIN-FLOW-018.md`

Cada arquivo: situação inicial, passos executados, resultado observado, critério de PASS.

**validation_command:**
```
python -c "import os,sys; files=['_reports/training/TEST-TRAIN-FLOW-001.md','_reports/training/TEST-TRAIN-FLOW-002.md','_reports/training/TEST-TRAIN-FLOW-003.md','_reports/training/TEST-TRAIN-FLOW-004.md','_reports/training/TEST-TRAIN-FLOW-005.md','_reports/training/TEST-TRAIN-FLOW-006.md','_reports/training/TEST-TRAIN-FLOW-017.md','_reports/training/TEST-TRAIN-FLOW-018.md']; missing=[f for f in files if not os.path.exists(f)]; print('PASS' if not missing else 'MISSING: '+str(missing)); sys.exit(0 if not missing else 1)"
```

**AC-001:** 8 arquivos de evidência existem com conteúdo MANUAL_GUIADO.
**AC-002:** TEST_MATRIX §6: FLOW-TRAIN-001..006/017/018 = COBERTO.

---

### AR_208 — Contract P0 tests: CONTRACT-TRAIN-097..100

**write_scope (governed):**
- `Hb Track - Backend/tests/training/contracts/test_contract_train_097_100_presence_pending.py` (novo)
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` (§8: CONTRACT-097..100 COBERTO)

Endpoints (implementados por AR-TRAIN-017/018 VERIFICADOS):
- `CONTRACT-097`: `POST /training-sessions/{id}/pre-confirm`
- `CONTRACT-098`: `POST /training-sessions/{id}/close`
- `CONTRACT-099`: `GET /training/pending-items`
- `CONTRACT-100`: `PATCH /training/pending-items/{id}/resolve`

**validation_command:**
```
cd "Hb Track - Backend" && pytest tests/training/contracts/test_contract_train_097_100_presence_pending.py -v --tb=short 2>&1 | tail -20
```

**AC-001:** pytest = 0 FAILs, 0 ERRORs.
**AC-002:** TEST_MATRIX §8: CONTRACT-097..100 = COBERTO.
**Risco:** Se DB offline, usar testes de contrato estático (import + schema inspection).

---

### AR_209 — Done Gate: sync TEST_MATRIX v1.8.0 + smoke Batch9 (5) + sanity AR_200 full (11) + DONE_GATE_TRAINING.md

**write_scope (governed):**
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` (v1.7.0 → v1.8.0; §9 + §5 + §6 + §8 + §0)

**Deliverables adicionais (fora governed roots):**
- `_reports/training/DONE_GATE_TRAINING.md`

**validation_command (2 fases encadeadas):**
```
cd "Hb Track - Backend" && echo '=== FASE-1: SMOKE Batch9 fixes (5 arquivos) ===' && pytest tests/training/invariants/test_inv_train_001_focus_sum_constraint.py tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py tests/training/invariants/test_inv_train_030_attendance_correction_fields.py tests/training/invariants/test_inv_train_032_wellness_post_rpe.py tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py -v --tb=short 2>&1 && echo '=== FASE-2: SANITY AR_200 full rerun (11 arquivos) ===' && pytest tests/training/invariants/test_inv_train_001_focus_sum_constraint.py tests/training/invariants/test_inv_train_002_wellness_pre_deadline.py tests/training/invariants/test_inv_train_003_wellness_post_deadline.py tests/training/invariants/test_inv_train_004_edit_window_constants_runtime.py tests/training/invariants/test_inv_train_004_edit_window_time.py tests/training/invariants/test_inv_train_005_immutability_60_days.py tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py tests/training/invariants/test_inv_train_009_wellness_pre_uniqueness.py tests/training/invariants/test_inv_train_030_attendance_correction_fields.py tests/training/invariants/test_inv_train_032_wellness_post_rpe.py tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py -v --tb=short 2>&1 | tail -40
```

**AC-001:** TEST_MATRIX versão = v1.8.0.
**AC-002:** §9 contém entries para AR-TRAIN-024..031.
**AC-003:** `_reports/training/DONE_GATE_TRAINING.md` existe com critérios §10 satisfeitos.
**AC-004:** FASE-1 smoke (5 arquivos fixados Batch9, incl. CONTRACT-077-085) = 0 FAILs.
**AC-005:** FASE-2 sanity AR_200 full (11 arquivos: INV-001/002/003/004a/004b/005/008/009/030/032 + CONTRACT-077-085) = 0 FAILs — prova que o DONE não é artefato de 'fix import/path'.
**Risco:** Bloquear se algum AR de Batch 9/10 não estiver VERIFICADO ao iniciar esta AR.

---

## Kanban

| Seção | AR | Atualização |
|---|---|---|
| §26 | AR_202..206 | Adicionado — Batch 9 🔲 READY |
| §27 | AR_207..208 | Adicionado — Batch 10 🔲 READY (dep: Batch 9) |
| §28 | AR_209 | Adicionado — Batch 11 🔲 READY (dep: Batches 9+10) |

---

## SSOTs Atualizados Neste Ciclo

| Arquivo | Mudança |
|---|---|
| `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md` | AR-TRAIN-024..031 adicionadas (8 novas entradas) |
| `docs/hbtrack/modulos/treinos/TRAINING_BATCH_PLAN_v1.md` | v1.0.4 → v1.0.5; Batches 9/10/11 adicionados |
| `docs/hbtrack/Hb Track Kanban.md` | §26/§27/§28 adicionados |
| `docs/_canon/planos/ar_batch9_fix_fails_202_206.json` | criado; dry-run ✅ PASS (5 ARs) |
| `docs/_canon/planos/ar_batch10_flows_contracts_207_208.json` | criado; dry-run ✅ PASS (2 ARs) |
| `docs/_canon/planos/ar_209_done_gate_training.json` | criado; dry-run ✅ PASS (1 AR) |

---

## Instrução ao Executor

```
PLAN_HANDOFF — Executor deve:
1. Ler este handoff e os 3 planos JSON listados acima.
2. Executar Batch 9 (AR_202..206) — sem dependências entre si.
   Para cada AR: hb plan <json> → implementar fix → hb report <N> → aguardar Testador → hb seal <N>.
3. Após Batch 9 VERIFICADO (todos os 5 ARs), executar Batch 10 (AR_207..208).
4. Após Batches 9+10 VERIFICADOS, executar Batch 11 (AR_209 Done Gate).
NÃO alterar Backend/Frontend app/ — todos os fixes Batch 9 são test-layer.
NÃO criar novas ARs — apenas executar as listadas.
```

_gerado pelo Arquiteto — 2026-03-02_