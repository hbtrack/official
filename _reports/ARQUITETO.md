# ARQUITETO.md — Handoff para Executor

<!-- PLAN_HANDOFF -->

**Protocolo**: 1.3.0
**Branch**: dev-changes-2
**HEAD**: 142a146
**Data Planejamento**: 2026-03-04
**Status**: PLAN_HANDOFF

---

## 1. Contexto

Batch 18 concluído **parcialmente**: AR_225/226/227 ✅ VERIFICADO + sealed; AR_228 🔴 REJEITADO (AC-001 impossível — test_018_route + test_035 fora do write_scope + 10 ERRORs de conftest diferente). Batch 19 AR_229 executado mas em ⚠️ FALHA (exit=1, 6 FAILs, 10 ERRORs).

Durante execução de AR_229, foram diagnosticados **root causes definitivos** de todos os 6 FAILs + 10 ERRORs remanescentes. O Arquiteto concluiu que:

1. **AR_229 precisa de amendment**: `training_session.py` `status` server_default tem bug de triple-quote (`'''draft'''` → `'draft'`). Este fix está no write_scope de AR_229 — **Executor deve aplicá-lo e re-rodar `hb report 229`**.

2. **AR_230 (AR-TRAIN-049)** é a AR capturadora: 8 arquivos de teste com bugs puros de test-layer. Após AR_230 VERIFICADO e suite verde → re-rodar `hb report 228` e `hb report 229` para fechar ambas.

**SSOTs atualizados nesta sessão:**
- `AR_BACKLOG_TRAINING.md` → AR-TRAIN-049 adicionado (Lote 14, Batch 20; tabela-resumo; seção detalhada §8)
- `TRAINING_BATCH_PLAN_v1.md` → Batch 20 adicionado; alerta de amendment em Batch 19
- `docs/_canon/planos/ar_batch20_fix_test_layer_residuals_049.json` — **NOVO** (dry-run ✅ → AR_230)
- `Hb Track Kanban.md` → §35 Batch 18 status atualizado; §36 Batch 19 FALHA + amendment; §37 Batch 20 READY

---

## 2. Diagnóstico por Root Cause

### Amendment AR_229 — fix em `app/models/training_session.py` (dentro do write_scope de AR_229)

| Bug | Root Cause | Fix |
|---|---|---|
| test_019 FAIL após AR_229 | `status` server_default = `sa.text("'''draft'''::character varying")` → armazena `'draft'` (com aspas literais) violando `check_training_session_status` | Mudar para `sa.text("'draft'::character varying")` |

### AR_230 — 8 arquivos de teste (write_scope AR-TRAIN-049)

| Arquivo de Teste | FAILs/ERRORs | Root Cause | Fix |
|---|---|---|---|
| `test_018_..._route.py` | 1 FAIL | `Person()` sem `birth_date` (NOT NULL) | `birth_date=date(1990, 1, 1)` em Person() |
| `test_035_...runtime.py` | 4 FAILs | `SessionTemplate(organization_id=...)` — modelo usa `org_id` | Renomear kwarg `organization_id` → `org_id` |
| `test_058_...mutable.py` | 1 ERROR | `inv058_team`: `Team()` sem `category_id` NOT NULL | Add fixture `category` local + `category_id=category.id` |
| `test_059_...contiguous.py` | 1 ERROR | `inv059_team`: `Team()` sem `category_id` | Mesmo fix que test_058 |
| `test_063_preconfirm.py` | 2 ERRORs | `team_reg` usa `athlete.person_id` mas FK refs `athletes.id` (PK auto-gerada) | `str(athlete.person_id)` → `str(athlete.id)` |
| `test_064_close_consolidation.py` | 1 ERROR | Mesmo bug do test_063 na fixture `team_reg` local | Mesmo fix |
| `test_076_wellness_policy.py` | 3 ERRORs | SQL usa `status='concluída'` inválido (INVARIANTS: só 5 valores canônicos) | `'concluída'` → `'pending_review'` |
| `test_exb_acl_006_acl_table.py` | 2 ERRORs | `uuid4.__class__(exercise_id)` = `function(...)` → TypeError | `UUID(exercise_id)` + `from uuid import uuid4, UUID` |

---

## 3. Planos Materializados

| AR Físico | AR-TRAIN | Título | Batch | Plano JSON |
|---|---|---|---|---|
| **AR_229** | TRAIN-048 | Sync app/models/ + services/ + stubs IA Coach **(FALHA — amendment obrigatório)** | 19 | `docs/_canon/planos/ar_batch19_sync_app_layer_048.json` |
| **AR_230** | TRAIN-049 | Fix 6 FAILs + 10 ERRORs residuais test-layer (8 arquivos) | 20 | `docs/_canon/planos/ar_batch20_fix_test_layer_residuals_049.json` |

---

## 4. Ordem de Execução

```
[STEP 1] Amendment AR_229 → fix training_session.py (server_default) → hb report 229

[STEP 2] Materializar AR_230 → executar AR_230 → hb report 230
         (validation: pytest tests/training/ -q --tb=no → 0 failed, 0 errors)

[STEP 3 — cascata após suite verde]
         hb verify 230 → (humano: hb seal)
         hb report 228 → (deve exit=0 agora) → hb verify 228 → (humano: hb seal)
         hb report 229 → (deve exit=0 agora) → hb verify 229 → (humano: hb seal)

[STEP 4 — Done Gate]
         hb report 222 → hb verify 222 → (humano: hb seal)
```

*(AR_230 + AR_229 amendment = pré-requisitos para fechar AR_228 e AR_229. Depois AR_222.)*

---

## 5. Dry-run

```
python scripts/run/hb_cli.py plan docs/_canon/planos/ar_batch20_fix_test_layer_residuals_049.json --dry-run
→ AR_230_fix_residuais_test-layer_6_fails_+_10_errors_em_te.md (7120 bytes)  [ROLLBACK ✓]
→ 1 ARs seriam criados, 0 seriam pulados. Todas as validações passaram. ✅
```

---

## 6. Kanban atualizado

| Seção | Conteúdo | Status |
|---|---|---|
| §33 | AR_222 — Done Gate §10 | ⛔ BLOCKED_AC005 (aguarda Batch 20 + AR_229 re-verify) |
| §35 | Batch 18 (AR_225..228) | AR_225/226/227 ✅ VERIFICADO; AR_228 🔴 REJEITADO (aguarda AR_230) |
| §36 | Batch 19 (AR_229) | ⚠️ FALHA — amendment obrigatório (status server_default) |
| §37 | Batch 20 (AR_230) | 🔲 READY (dep: AR_229 amendment) |

---

## 7. Comandos para o Executor

```powershell
# STEP 1 — Amendment AR_229 (fix dentro do write_scope de AR_229)
# Arquivo: Hb Track - Backend/app/models/training_session.py
# Linha com:  server_default=sa.text("'''draft'''::character varying")
# Trocar por: server_default=sa.text("'draft'::character varying")
cd "c:\HB TRACK"
python scripts/run/hb_cli.py report 229

# STEP 2 — Materializar e executar AR_230
python scripts/run/hb_cli.py plan docs/_canon/planos/ar_batch20_fix_test_layer_residuals_049.json
python scripts/run/hb_cli.py report 230

# STEP 3 — Cascata de verificação (após suite verde)
python scripts/run/hb_cli.py verify 230
# (humano: hb seal 230)
python scripts/run/hb_cli.py report 228
python scripts/run/hb_cli.py verify 228
# (humano: hb seal 228)
python scripts/run/hb_cli.py report 229
python scripts/run/hb_cli.py verify 229
# (humano: hb seal 229)
```

**Restrições AR_230 (FORBIDDEN):**
- `app/` — zero toque (bugs são exclusivamente test-layer)
- `tests/training/invariants/conftest.py` — zero toque (fixtures base estão corretas)
- Qualquer arquivo de teste fora do write_scope de 8 arquivos
- Se necessitar de arquivo fora do write_scope → BLOCKED (reportar ao Arquiteto)

**Cuidados extras AR_230:**
- test_058/059: usar `ON CONFLICT DO NOTHING` ao criar fixture `category` (evitar colisão com id=9999)
- test_063/064: se `athlete.id` for `None` após `flush()`, adicionar `await async_db.refresh(athlete)` antes de usar `athlete.id`
- test_076: verificar se lógica do teste faz sentido semântico com `status='pending_review'`

---

*Arquiteto — 2026-03-04 — Batch 20 planejado, dry-run ✅, amendment AR_229 autorizado*

---

## 1. Contexto

Sessão anterior encerrou com Batch 17 (AR_223 + AR_224) selados. Diagnóstico confirmou 109 FAILs + 31 ERRORs residuais bloqueando AR_222 (Done Gate §10). Humano autorizou **Opção A (Batch 18)** para zerar a suite.

Nesta sessão o humano solicitou **Batch Sync Strategy** (Batch 19): sincronizar `app/` com contrato v1.3.0 + invariantes v1.5.0 via AR-TRAIN-048. A pasta `app/` foi desbloqueada explicitamente via `GOVERNED_ROOTS.yaml` (`UNLOCKED_FOR_SYNC_BATCH_19`).

**SSOTs atualizados nesta sessão:**
- `AR_BACKLOG_TRAINING.md` v2.1.0 → **v2.2.0** (AR-TRAIN-048 completa com ACs, FORBIDDEN, validation_command, rollback_plan; Lote 13; tabela-resumo)
- `TRAINING_BATCH_PLAN_v1.md` v1.2.0 → **v1.3.0** (Batch 19 adicionado com zonas de impacto, DoD, riscos)
- `docs/_canon/planos/ar_batch19_sync_app_layer_048.json` — **NOVO** (dry-run ✅)
- `Hb Track Kanban.md` — seção 36 adicionada (AR_229 🔲 READY)

---

## 2. Diagnóstico de Desalinhamento (input para AR_229)

### Zona 1 — Modelos (app/models/)
| Arquivo | Invariante | Correção |
|---|---|---|
| `athlete.py` | TRAINING_CLOSSARY.yaml | Campos `athlete_name` + `birth_date` alinhados ao Glossário |
| `exercise.py` | INV-TRAIN-060 | `visibility_mode` server_default=`restricted` |
| `training_session.py` | INV-TRAIN-010 | UniqueConstraint unicidade wellness_post |
| `attendance.py` | INV-TRAIN-036 | FK `athlete_id` com OnDelete explícito |
| `training_cycle.py` | INV-TRAIN-054 | FK hierarchy `parent_cycle_id` → self |

### Zona 2 — Serviços (app/services/)
| Arquivo | Contrato | Correção |
|---|---|---|
| `exercise_service.py` | CONTRACT-TRAIN-091..095 | Assinatura `update_exercise(self, exercise_id, data: dict, organization_id)` |
| `attendance_service.py` | GAP-CONTRACT-7 | Stub mínimo para closure de presença |

### Zona 3 — Stubs IA Coach
| Arquivo | Problema | Correção |
|---|---|---|
| `ai_coach_service.py` | ImportError nos testes 079/080/081 | Adicionar `RecognitionApproved`, `CoachSuggestionDraft`, `JustifiedSuggestion` como dataclasses |

---

## 3. Planos Materializados

| AR Físico | AR-TRAIN | Título | Batch |
|---|---|---|---|
| **AR_229** | TRAIN-048 | Sync app/models/ (INV-010/035/036/054/060) + app/services/ (contrato v1.3.0) + stubs IA Coach | 19 |

**Ordem de execução:**
```
[Batch 18] AR_225 + AR_226 + AR_227  →  AR_228  →  [Batch 19] AR_229  →  AR_222
```
*(AR_225/226/227 são pré-requisito; AR_228 depende das 3; AR_229 depende de AR_228 VERIFICADO)*

---

## 4. Dry-run

```
python scripts/run/hb_cli.py plan docs/_canon/planos/ar_batch19_sync_app_layer_048.json --dry-run
→ 1 ARs seriam criados, 0 seriam pulados. Todas as validações passaram. ✅
```

---

## 5. Kanban atualizado

| Seção | Conteúdo | Status |
|---|---|---|
| §33 | AR_222 — Done Gate §10 | ⛔ BLOCKED_AC005 (aguarda Batch 18 + Batch 19) |
| §34 | Batch 17 (AR_223 + AR_224) | ✅ SELADO |
| §35 | Batch 18 (AR_225..228) — Fix FAILs test-layer | 🔲 READY |
| §36 | Batch 19 (AR_229) — Sync app layer | 🔲 READY (dep: Batch 18) |

---

## 6. Próximos passos para o Executor

```powershell
# 1. Materializar ARs de ambos os batches
python scripts/run/hb_cli.py plan docs/_canon/planos/ar_batch18_fix_test_layer_044_047.json
python scripts/run/hb_cli.py plan docs/_canon/planos/ar_batch19_sync_app_layer_048.json

# 2. Executar Batch 18 (225/226/227 em paralelo, depois 228)
python scripts/run/hb_cli.py report 225
python scripts/run/hb_cli.py report 226
python scripts/run/hb_cli.py report 227
# Após os 3 VERIFICADO:
python scripts/run/hb_cli.py report 228

# 3. Executar Batch 19 (após AR_228 VERIFICADO)
python scripts/run/hb_cli.py report 229
```

**Restrições AR_229:**
- FORBIDDEN: `tests/` (zero toque) e qualquer `app/` não listado no write_scope
- Antes de `hb report 229`: verificar se novas Column/Constraint exigem `alembic revision --autogenerate`
- Se surgir necessidade de arquivo fora do write_scope → BLOCKED (reportar ao Arquiteto)

---

*Arquiteto — 2026-03-03 — Batch 18 + Batch 19 planejados e dry-run ✅*
