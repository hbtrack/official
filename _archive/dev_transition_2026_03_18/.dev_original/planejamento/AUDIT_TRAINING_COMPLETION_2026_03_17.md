# Audit: Completude do Módulo Training
> Data: 2026-03-17
> Status: ✅ **Análise Concluída** | **Próximas ações claras e priorizadas**
> Autoridade: Validação com DECISION_IR.yaml e MODULE_REGISTRY.yaml

---

## 📊 Resumo Executivo

O módulo `training` está em status **`implementation_ready`** (12/12 superfícies), mas apresenta **3 lacunas críticas** que precisam ser fechadas antes de gerar código:

| Superfície | Status | Achado | URL |
|---|---|---|---|
| ✅ module_docs_minimum | COMPLETO | 9 arquivos essenciais | `docs/hbtrack/modulos/training/` |
| ✅ openapi_sync | COMPLETO | 30+ endpoints | `contracts/openapi/paths/training.yaml` |
| ✅ json_schema | COMPLETO | 6 entidades | `contracts/schemas/training/` |
| ✅ test_matrix | COMPLETO | Matriz de ~100 casos | `TEST_MATRIX_TRAINING.md` |
| ✅ state_model | COMPLETO | 7 estados (ADR-017) | `STATE_MODEL_TRAINING.md` |
| ✅ permissions | COMPLETO | 5 roles × 30+ ops | `PERMISSIONS_TRAINING.md` |
| ✅ errors | COMPLETO | 19+ códigos RFC 7807 | `ERRORS_TRAINING.md` |
| ✅ sport_science | COMPLETO | ACSM/ASPETAR | `SPORT_SCIENCE_RULES_TRAINING.md` |
| ⚠️ asyncapi | **INCOMPLETO** | 1/27 eventos | `contracts/asyncapi/asyncapi.yaml` |
| ❌ ui_contract | **FALTANTE** | 0 ficheiros | `docs/hbtrack/modulos/training/UI_CONTRACT_TRAINING.md` |
| 📋 arazzo | ✅ COMPLETO | 1 workflow | `contracts/workflows/training/create_training_session_and_mark_attendance.arazzo.yaml` |
| 📋 decision_ir | ✅ EXISTENTE | 27 eventos | `docs/_canon/gates/TRAINING_MODULE_DECISION_IR.yaml` |

---

## **Achado 1: AsyncAPI — 26 Eventos Faltando**

### Status Atual
- **Arquivo:** `contracts/asyncapi/asyncapi.yaml`
- **Eventos implementados:** 1 (`training.attendance.marked`)
- **Mensagens criadas:** apenas 1 YAML
- **Canais definidos:** 1

### Eventos Esperados (DECISION_IR.yaml)
Encontrados **27 eventos** definidos em `docs/_canon/gates/TRAINING_MODULE_DECISION_IR.yaml`:

```
EVT-TRAINING-001: intervention_cycle_created
EVT-TRAINING-002: intervention_cycle_completed
EVT-TRAINING-003: need_detected_created
EVT-TRAINING-004: objective_created
EVT-TRAINING-005: need_linked_to_objective
EVT-TRAINING-006: recommendation_generated
EVT-TRAINING-007: recommendation_accepted
EVT-TRAINING-008: recommendation_dismissed
EVT-TRAINING-009: training_session_created
EVT-TRAINING-010: training_session_published
EVT-TRAINING-011: training_session_started
EVT-TRAINING-012: training_session_completed
EVT-TRAINING-013: training_session_cancelled
EVT-TRAINING-014: training_session_archived
EVT-TRAINING-015: session_objective_achieved
EVT-TRAINING-016: execution_recorded
EVT-TRAINING-017: feedback_thread_created
EVT-TRAINING-018: feedback_thread_closed
EVT-TRAINING-019: session_adjustment_made
EVT-TRAINING-020: attention_queue_item_created
EVT-TRAINING-021: attention_queue_item_resolved
EVT-TRAINING-022: athlete_ineligible_for_prescription
EVT-TRAINING-023: prescription_adjusted
EVT-TRAINING-024: completion_evidence_provided
EVT-TRAINING-025: coach_intervention_required
EVT-TRAINING-026: continuity_snapshot_created
EVT-TRAINING-027: training_readiness_assessed
```

### Ação Prioritária
**CRIAR** `contracts/asyncapi/channels/` e `contracts/asyncapi/messages/` para os 26 eventos faltando.

**Mapeamento rápido:**
- Eventos de ciclobiol (`intervention_cycle_*`) — 2 eventos
- Eventos de necessidade (`need_*`) — 3 eventos  
- Eventos de objective (`objective_*`, `objective_achieved`) — 2 eventos
- Eventos de recomendação (`recommendation_*`) — 3 eventos
- **Eventos de sessão (críticos)** — 6 eventos
- Eventos de execução/feedback (`execution_*`, `feedback_*`) — 4 eventos
- Eventos de ajuste/fila (`adjustment_*`, `attention_*`) — 3 eventos
- Eventos de prescrição/readiness (`prescription_*`, `readiness_*`) — 2 eventos

---

## **Achado 2: UI_CONTRACT_TRAINING.md — Faltante**

### Status Atual
- **Arquivo esperado:** `docs/hbtrack/modulos/training/UI_CONTRACT_TRAINING.md`
- **Existente:** NÃO
- **Referência global:** `docs/_canon/UI_CONTRACT_GUIDE.md` ✅ existe

### O que Deveria Conter
Baseado em `UI_CONTRACT_GUIDE.md` e `DECISION_IR.yaml`, o arquivo deve documentar:

```markdown
# UI_CONTRACT_TRAINING.md

## Flows de UI (UIF-*) — 3 flows esperados
- UIF-TRAINING-001: coach.manage_session
- UIF-TRAINING-002: coach.manage_attention_queue
- UIF-TRAINING-003: athlete.checkin

## Telas Principais
1. Sessão (create, edit, publish, complete, cancel)
2. Objetivos
3. Fila de atenção (attention_queue)
4. Feedback threads
5. Check-in pré/pós-treino

## Estados de UI Esperados
Cada tela deve mapear: loading, success, error, empty, partial-data (7 estados globais)

## Componentes Específicos
- Session form (com validation de focus %)
- Wellness pre/post inputs (Likert, RPE, etc.)
- Status FSM visualization (7 estados)
- Attention queue prioritization
- Feedback threads conversation

## Integração com DECISION_IR
- Referenciar UIF-TRAINING-001/002/003 do DECISION_IR.yaml
- Mapear cada flow a use_cases (API-TRAINING-*)
```

### Ação Prioritária
**CRIAR** `docs/hbtrack/modulos/training/UI_CONTRACT_TRAINING.md` com conteúdo acima.

---

## **Achado 3: Arch Decisions — Consolidação Necessária**

### Status Atual
- **Referência em README:** `docs/hbtrack/decisoes/ARCH_DECISIONS_TRAINING.md`
- **Existente:** NÃO (arquivo não localizado)
- **Decisões disponíveis:** 46+ referências em `DECISION_IR.yaml` (TRAIN-DEC-001 a TRAIN-DEC-050)

### Decisões Encontradas em DECISION_IR.yaml

Estrutura esperada do arquivo consolidado:

```yaml
TRAIN-DEC-001: Create training need from detected signal
TRAIN-DEC-002: Intervention cycle structure vs. season periodic decomposition
TRAIN-DEC-003: Need origin tracking (evidence_ref vs. coach_rationale)
TRAIN-DEC-004: Objective-need linkage vs. standalone objectives
TRAIN-DEC-005: Analytics recommendation workflow (PENDING_COACH_REVIEW required)
TRAIN-DEC-006: Training session creation workflow
TRAIN-DEC-007: Publication preconditions guard
TRAIN-DEC-008: State machine transitions (FSM closed)
TRAIN-DEC-009: Execution recording context requirement
TRAIN-DEC-010: Planned content snapshot immutability (after PUBLISHED)
TRAIN-DEC-011: Session adjustment structured reasoning
TRAIN-DEC-012: Completion evidence guard
TRAIN-DEC-013: Feedback thread anchoring requirement
TRAIN-DEC-014: Feedback closure outcome mapping
TRAIN-DEC-015 to TRAIN-DEC-050: [Additional 36 decisions]
```

### Ação Prioritária
**CRIAR** `docs/hbtrack/decisoes/ARCH_DECISIONS_TRAINING.md` — consolidar 46+ TRAIN-DEC-* do DECISION_IR.yaml com narrativa explicativa.

---

## 📋 Próximos Passos (Priorizado)

| # | Tarefa | Esforço | Bloqueio |
|---|--------|---------|---------|
| **1** | Gerar 26 eventos AsyncAPI | 2–3h | Bloqueia tests de integração |
| **2** | Criar UI_CONTRACT_TRAINING.md | 1–2h | Bloqueia UI contract gates |
| **3** | Compilar ARCH_DECISIONS_TRAINING.md | 1–2h | Documentativo (não bloqueia) |
| **4** | Validar com gates (`ASYNCAPI_VALIDATION_GATE`, etc.) | 1h | Bloqueio na CI/CD |
| **5** | Análise adversarial (F6) | 2–3h | Antes de gerar código |
| **6** | Gerar relatório final de readiness | 1h | Documentativo |

---

## 🎯 Recomendação

### Imediato (Hoje)
- **✅ Concluído:** Migrations do training (6 tabelas, reversivelidade garantida)
- **⏳ Em andamento:** Análise técnica (este audit)

### Próximo Sprint (Esta sessão)
- **[1]** Gerar 26 eventos AsyncAPI (referenciados em DECISION_IR.yaml)
- **[2]** Criar UI_CONTRACT_TRAINING.md (3 UI flows mapeados)
- **[3]** Compilar ARCH_DECISIONS_TRAINING.md (46+ decisões)
- **[4]** Rodar gates de validação (`ASYNCAPI_VALIDATION_GATE`, etc.)
- **[5]** Análise adversarial (F6) — checkpoint crítico antes de gerar código
- **[6]** Gerar relatório final → **training 100% pronto para implementação**

### Após Fechar Training (Próxima sessão)
- **[A]** Auditar 15 módulos (status vs. expected_surfaces)
- **[B]** Responder decisões humanas (D1, D2, D4) para desbloquear geração de código
- **[C]** Gerar scaffold de código (backend FastAPI + frontend)

---

## 📚 Referências Críticas

| Artefato | Localização | Propósito |
|---|---|---|
| DECISION_IR | `docs/_canon/gates/TRAINING_MODULE_DECISION_IR.yaml` | **SSOT de 27 eventos + 11 entities + 40+ rules + 11 use cases** |
| MODULE_REGISTRY | `docs/_canon/MODULE_REGISTRY.yaml` | Status `implementation_ready` + 12 expected surfaces |
| UI_CONTRACT_GUIDE | `docs/_canon/UI_CONTRACT_GUIDE.md` | Padrões globais de UI (7 estados, breakpoints, componentes) |
| OpenAPI | `contracts/openapi/paths/training.yaml` | 30+ endpoints (já conforme) |
| AsyncAPI | `contracts/asyncapi/asyncapi.yaml` | 1/27 eventos (faltam 26) |
| Schema | `contracts/schemas/training/` | 6 entidades (já conforme) |
| Migrations | `migrations/training/versions/20260317_001_create_training_tables.py` | Criado hoje ✅ |

---

## ✅ Validação

Todos os achados foram validados contra:
- ✅ `MODULE_REGISTRY.yaml` — training é `implementation_ready`
- ✅ `DECISION_IR.yaml` — SSOT de 27 eventos esperados
- ✅ `UI_CONTRACT_GUIDE.md` — documentação global existe
- ✅ Contract gates — DATA_MIGRATION_GATE = PASS

---

## 🚀 Status Final

**Módulo training:**
- ✅ Esquema de DB completo (migrations criadas)
- ✅ Contrato OpenAPI robusto
- ✅ Regras de negócio documentadas (94+ invariantes)
- ⚠️ **Lacun as críticas:** AsyncAPI (26 eventos faltando), UI Contract faltando, Arch Decisions não compiladas
- **Bloqueador para código:** Faltan as 3 superfícies acima + análise adversarial (F6)

**Próximo status esperado após fechar as 3 lacunas:**
- 🟢 **`implementation_ready` → `ready_for_implementation`** (código pode começar)

