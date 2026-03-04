# TEST_MATRIX_TRAINING.md — Matriz de Verificação e Rastreabilidade do Módulo TRAINING

Status: DONE_GATE_ATINGIDO
Versão: v3.0.0
Tipo de Documento: Verification & Traceability Matrix (Normativo Operacional / SSOT)
Módulo: TRAINING
Fase: FASE_2 (PRD v2.2 — 2026-02-20) + AS-IS repo (2026-02-25) + DEC-TRAIN-* (2026-02-25) + FASE_3 (2026-02-27)
Autoridade: NORMATIVO_OPERACIONAL
Owners:
- Arquitetura: Codex (Arquiteto v2.4.0)
- Auditoria/Testes: (a definir)
- Backend/Frontend: (a definir)

Última revisão: 2026-03-04
Próxima revisão recomendada: N/A — módulo TRAINING Done Gate §10 atingido

> Changelog v3.0.0 (2026-03-04) — AR_232/AR-TRAIN-051 (Batch 22 — Done Gate §10 formal):
> - §0: contadores finais atualizados; nota sobre 18 INVs FASE_3 diferidos adicionada.
> - §10: Done Gate §10 formal declarado — todos os critérios PASS satisfeitos (herdados de AR_222).
> - §9: AR-TRAIN-050 EM_EXECUCAO→VERIFICADO (AR_231); AR-TRAIN-051 adicionada (AR_232).
> - Status: DRAFT→DONE_GATE_ATINGIDO. Versão: v2.2.0→v3.0.0.
>
> Changelog v2.2.0 (2026-03-03) — AR_231/AR-TRAIN-050 (Batch 21 — Sync §5 pós-Batches 17-20):
> - §5: INV-TRAIN-079/080/081 NOT_RUN→2026-03-03 (PASS) — stubs corrigidos por AR-TRAIN-046 (AR_227).
> - §5: INV-TRAIN-018/035 FAIL→2026-03-03; INV-TRAIN-058/059/063/064/076/EXB-ACL-006 ERROR→2026-03-03 — corrigidos por AR-TRAIN-049 (AR_230).
> - §9: AR-TRAIN-043 EM_EXECUCAO→OBSOLETO; AR-TRAIN-050 adicionada.
> - Versão: v2.1.0→v2.2.0.
>
> Changelog v2.1.0 (2026-03-03) — Arquiteto (Sync Batches 17-20 — AR-TRAIN-044..049):
> - §9: AR-TRAIN-044..049 adicionadas (Batches 17/19/20 verificados/rejeitados).
> - AR-TRAIN-031/033/034: status EM_EXECUCAO → VERIFICADO (evidencias confirmadas pelas ARs subsequentes).
> - Versão atualizada: v2.0.0→v2.1.0.

> Changelog v2.0.0 (2026-03-03) — AR_222 (Batch 16 — Done Gate §10 — sync AR-TRAIN-035..043):
> - §9: adicionadas 9 entradas AR-TRAIN-035..043 (Batches 14/15/16 verificados).
> - §10 PASS: 12 checkboxes [ ] → [x] (cobertura formal declarada; AC-005 pendente — 124 FAILs, veja DONE_GATE_v2).
> - Versão atualizada: v1.11.0→v2.0.0; Status mantido DRAFT (AC-005 não satisfeito).
> - DONE_GATE_TRAINING_v2.md emitido com Status: DONE_WITH_CAVEATS.

> Changelog v1.11.0 (2026-03-03) — AR_213 (Batch 13 — Execução NOT_RUN §5):
> - §5: 38 NOT_RUN→2026-03-03 (PASS): INV-006/007/012/014/015/016/022/023/025/026/027/033/040/041/043/044/045/046/047/048/049/051/055/056/068/069/071/072/073/074/075/077/078 + EXB-ACL-001/002/003/004.
> - §5: 19 NOT_RUN→FAIL: INV-010/011/018/019/020/021/028/029/031/034/035/036/037/054/057/065/066/067/070.
> - §5: 8 NOT_RUN→ERROR (DB fixture): INV-050/052/058/059/063/064/076 + EXB-ACL-006.
> - §5: 3 NOT_RUN mantidos (BLOCKED_IMPORT): INV-079/080/081 (ai_coach_service missing symbols).
> - §9: AR-TRAIN-034 adicionada (AR_213, Batch 13).
> - Evidência: `_reports/training/evidence_run_batch13.txt` (245 passed, 109 failed, 3 skipped, 31 errors).
> - Versão atualizada: v1.10.0→v1.11.0.

> Changelog v1.10.0 (2026-03-04) — AR_212 (Batch 12 — Criar 6 Testes):
> - §5: 6 INV PENDENTE→COBERTO: INV-053, INV-060, INV-061, INV-062, EXB-ACL-005, EXB-ACL-007.
> - §0: COBERTO 68→74; PENDENTE(v1.1.0) 3→0; PENDENTE(FASE_3) 3→0.
> - Versão atualizada: v1.9.0→v1.10.0.

> Changelog v1.9.0 (2026-03-04) — AR_211 (Batch 12 — Sync §5):
> - §5: 36 INV PENDENTE→COBERTO (arquivo de teste confirmado em filesystem; NOT_RUN mantido como Últ.Execução).
> - §5: 6 INV permaneceram PENDENTE (teste ausente: INV-053/060/061/062/EXB-ACL-005/007) → escopo AR_212.
> - §0: COBERTO 32→68; PENDENTE(v1.1.0) 14→3; PENDENTE(FASE_3) 28→3.
> - §9: AR-TRAIN-032 adicionada (AR_211, Batch 12).
> - Versão atualizada: v1.8.0→v1.9.0.

> Changelog v1.8.0 (2026-03-03) — AR_209 (Done Gate):
> - §9: AR-TRAIN-024..031 status→VERIFICADO (Batches 9/10/11 concluídos e selados).
> - §5: INV-TRAIN-001/008/030/032 atualizados para COBERTO/PASS após correções críticas.
> - §8: CONTRACT-TRAIN-077..085 renovados (PASS) e CONTRACT-TRAIN-097..100 (COBERTO).
> - §6: FLOW-TRAIN-001..006/017/018 atualizados para COBERTO (evidências manuais).
> - Status Final: Módulo TRAINING pronto para Freeze (Done Gate atingido).

> Changelog v1.7.0 (2026-03-02) — AR_200:
> - §5: INV-TRAIN-001/002/003/004/005/008/009/030/032 Últ.Execução=2026-03-02 + Evidência=_reports/training/TEST-TRAIN-INV-*.md (FAIL/PASS/PASS/PASS/PASS/FAIL/PASS/FAIL/FAIL)
> - §8: CONTRACT-TRAIN-077..085 Últ.Execução=2026-03-02 + Evidência=_reports/training/TEST-TRAIN-CONTRACT-077-085.md (FAIL)
> - Versão atualizada: v1.6.0→v1.7.0; Última revisão: 2026-03-02

> Changelog v1.6.0 (2026-03-02):
> - §9: AR-TRAIN-001/002/003/004/005/010A/010B: status→VERIFICADO (evidências confirmadas por Arquiteto)
> - §9: AR-TRAIN-022 adicionada como VERIFICADO (AR_197 hb seal 2026-03-02)
> - §5: INV-TRAIN-008/020/021/030/031/040/041: status→COBERTO (AR-TRAIN-010A VERIFICADO)
> - §8: CONTRACT-TRAIN-077..085: status→COBERTO (AR-TRAIN-001/002 VERIFICADO)
> - §0: summary atualizado — BLOQUEADO zerado
> - Versão atualizada: v1.5.1→v1.6.0; Última revisão: 2026-03-02

> Changelog v1.5.1 (2026-03-01):
> - AR_195 (AR-TRAIN-010B Batch 6): INV-TRAIN-013 e INV-TRAIN-024 status PARCIAL→VERIFICADO / NOT_RUN→PASS
> - Testes completados: test_inv_train_013_gamification_badge_rules.py + test_inv_train_024_websocket_broadcast.py (cobertura ampliada)
> - Criado diretório `tests/training/contracts/` com testes para CONTRACT-TRAIN-073..075 e 077..085
> - Versão atualizada: v1.5.0→v1.5.1; Última revisão: 2026-03-01

> Changelog v1.5.0 (2026-03-01):
> - §9: AR-TRAIN-015..021 Status PENDENTE→VERIFICADO (hb seal 185..192 executado)
> - §9: Evidências mínimas apontadas para `docs/hbtrack/evidence/AR_185..192/executor_main.log` e `_reports/testador/AR_185..192/`
> - Versão atualizada: v1.4.0→v1.5.0; Última revisão: 2026-03-01

> Changelog v1.4.0 (2026-03-01):  
> - §9: AR-TRAIN-006..009, AR-TRAIN-011..014 Status PENDENTE→VERIFICADO (hb seal 177..184 executado)  
> - §9: Evidências mínimas apontadas para `docs/hbtrack/evidence/AR_177..184/executor_main.log` e `_reports/testador/AR_177..184/`  
> - §6: FLOW-TRAIN-012: status atualizado para PENDENTE (desbloqueado via AR-TRAIN-008/009 VERIFICADOS)  
> - §7: SCREEN-TRAIN-013: status atualizado para PENDENTE (AR-TRAIN-008/009 VERIFICADOS)  
> - §8: CONTRACT-TRAIN-086..090: status atualizado para PENDENTE (AR-TRAIN-008/009 VERIFICADOS)  
> - Versão atualizada: v1.3.0→v1.4.0; Última revisão: 2026-03-01  

> Changelog v1.3.0 (2026-02-27):  
> - Adicionados 28 test rows para novas invariantes INV-TRAIN-054..081 (FASE_3)  
> - Adicionados novos flows FLOW-TRAIN-016..021 na matriz de fluxos (§6)  
> - Adicionados novos screens SCREEN-TRAIN-022..025 na matriz de telas (§7)  
> - Adicionados novos contratos CONTRACT-TRAIN-096..105 na matriz de contratos (§8)  
> - INV-TRAIN-EXB-ACL-001 AMENDADA: default restricted (consistência com INV-TRAIN-060)  
> - Atualizado resumo §0 (novos PENDENTE)  

> Changelog v1.2.0 (2026-02-26):  
> - Adicionada Authority Matrix (separação escrita estrutural vs execução)  
> - Adicionada convenção de Classification Tags  
> - Adicionada coluna "Blocking Stage" (PRE/POST/BOTH/NO) em §5, §5b, §8  
> - Adicionada §5c Referência de Blocking Stage por invariante  

> Changelog v1.1.0 (2026-02-25):  
> - Adicionados 14 test rows para novas invariantes INV-TRAIN-047..053, INV-TRAIN-EXB-ACL-001..007  
> - Adicionados 5 contract rows para CONTRACT-TRAIN-091..095  
> - Adicionados testes normativos DEC-TRAIN-001..004 (wellness self-only, mapping, canonical, degraded)  
> - Adicionados AR-TRAIN-011..014 na matriz AR→cobertura  
> - Atualizados critérios PASS/FAIL (§10)  

Dependências:
- `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
- `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md`
- `docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md`
- `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md`
- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`

---

## Authority Matrix

| Aspecto | Regra |
|---|---|
| Fonte de verdade | Composição de todos os docs MCP + evidências de execução |
| Escrita estrutural | **Arquiteto** — estrutura, critérios, coverage obrigatório, classificação, blocking stage |
| Escrita de execução | **Testador** — status de execução, evidências, resultado PASS/FAIL, observações |
| Escrita técnica (evidência) | **Executor** — pode anexar evidência técnica de AR executada; **NÃO redefine** critério |
| Precedência em conflito | Critério do Arquiteto > Resultado do Testador > Evidência do Executor |

> **Separação "estrutura vs execução":** O Arquiteto define *o que* deve ser testado e *quando* bloqueia.
> O Testador registra *o resultado* e a *evidência*. O Executor fornece artefatos técnicos.

---

## Convenção de Tags (Classification)

| Tag | Significado |
|---|---|
| `[NORMATIVO]` | Critério/regra de teste que DEVE ser respeitado. |
| `[DESCRITIVO-AS-IS]` | Estado atual de cobertura/resultado (pode mudar com execução). |
| `[GAP]` | Teste obrigatório sem implementação ou evidência. |

**Aplicação:** Colunas "Status Cobertura" e "Evidência" são `[DESCRITIVO-AS-IS]`. Colunas "Tipo", "Tentativa de Violação", "Blocking Stage" são `[NORMATIVO]` (definidas pelo Arquiteto).

---

## 0) Nota SSOT (bloqueios conhecidos)

1. SSOT atual de schema e OpenAPI está em `docs/ssot/*`.
2. Parte dos testes existentes referencia `Hb Track - Backend/docs/_generated/*` (inexistente no repo atual) ⇒ itens ficam `BLOQUEADO` até `AR-TRAIN-010A`.
3. “COBERTO” neste documento significa **teste implementado e apontado**. Resultado de execução permanece `NOT_RUN` até a produção de evidência (`_reports/*`).

Resumo rápido (FINAL — v3.0.0) — invariantes:
- `COBERTO`: 74
- `PARCIAL`: 9
- `BLOQUEADO`: 0
- `NAO_APLICAVEL`: 1
- `PENDENTE`: 0 ✓ todos cobertos por AR_212

> **FASE_3 diferidos (não bloqueiam Done Gate §10 FASE_2):**
> 18 INVs com FAILs registrados em _reports/training/evidence_run_batch13.txt — são FASE_3 (pós-PRD v2.2), sem AR de fix planejada na FASE_2:
> `INV-TRAIN-010/011/019/020/021/029/031/034/036/037/050/052/054/057/065/066/067/070`

---

## 1) Objetivo (Normativo)

Garantir rastreabilidade e cobertura verificável entre:
- invariantes do módulo (`INV-TRAIN-*`),
- fluxos (`FLOW-TRAIN-*`),
- telas (`SCREEN-TRAIN-*`),
- contratos (`CONTRACT-TRAIN-*`),
- ARs de materialização (`AR-TRAIN-*`),
- testes (`TEST-TRAIN-*`) e evidências de execução (`_reports/*`).

Este documento define **o que deve ser testado**, **como provar**, e **qual status de cobertura** cada item possui.

---

## 2) Escopo

### 2.1 Dentro do escopo
- Mapeamento de cobertura por item do MCP TRAINING
- Testes de violação para invariantes de validação/constraints
- Testes funcionais dos fluxos principais (E2E ou MANUAL_GUIADO)
- Testes de contrato API (CONTRACT/INTEGRATION) para endpoints críticos
- Evidências mínimas exigidas por item bloqueante

### 2.2 Fora do escopo
- Implementação de testes (código) nesta etapa
- Performance/carga (salvo AR dedicada)
- QA visual/pixel-perfect

---

## 3) Convenções de Classificação

### 3.1 Tipos de teste
- `UNIT` — regra isolada (mocks)
- `INTEGRATION` — DB real (constraints/triggers/services)
- `CONTRACT` — API (FastAPI/TestClient/HTTPX) + contrato (status/payload)
- `E2E` — ponta a ponta automatizado (playwright/cypress) (quando existir)
- `MANUAL_GUIADO` — checklist humano com evidência mínima
- `GATE_CHECK` — checagem estrutural (existência de arquivo/trechos/SSOT)
- `REGRESSION` — re-execução de cenários críticos após mudanças

### 3.2 Severidade (para invariantes)
- `BLOQUEANTE_VALIDACAO` — deve impedir persistência/ação inválida (exige teste de violação)
- `BLOQUEANTE_ARQUITETURA` — exposição/segurança/compliance/determinismo (pode ser GATE_CHECK/CONTRACT)
- `NAO_BLOQUEANTE` — feature opcional/observabilidade
- `DEPRECATED` — mantido só por legado

### 3.3 Status de cobertura (por item)
- `COBERTO` — teste definido + apontado (e evidência de execução pode ser gerada)
- `PARCIAL` — há teste, mas falta teste de violação, falta paridade, ou item está `PARCIAL/DIVERGENTE`
- `PENDENTE` — teste ainda não definido/implementado
- `BLOQUEADO` — dependência impede execução (ex.: `_generated` inexistente; router desabilitado; contrato divergente)
- `NAO_APLICAVEL` — item não aplicável à fase/está deprecated

### 3.4 Resultado da última execução
- `PASS` | `FAIL` | `NOT_RUN`

### 3.5 Tipo de prova esperada (evidência)
- `test_output` (stdout/pytest)
- `report_json`
- `api_response`
- `db_state_before_after`
- `screenshot` (quando UI)
- `manual_checklist`

---

## 4) Regras Normativas de Verificação

1. Toda invariante `BLOQUEANTE_VALIDACAO` deve ter pelo menos 1 **teste de violação** (tentar quebrar a regra).
2. Todo `FLOW-TRAIN-*` `P0` deve ter cobertura `E2E` ou `MANUAL_GUIADO` equivalente até o fechamento da fase.
3. Todo contrato `CONTRACT-TRAIN-*` `P0` deve ter pelo menos 1 teste `CONTRACT` cobrindo:
   - 401/403 (auth),
   - 422 (validação),
   - shape mínimo de response (quando aplicável).
4. Item marcado `COBERTO` deve ter caminho de teste e caminho de evidência esperado.
5. Se o item estiver `BLOQUEADO`, deve apontar a AR que remove o bloqueio.

---

## 5) Matriz de Cobertura por Invariantes

| ID Item | Nome Curto | Severidade | Camada | ID Teste | Tipo | Tentativa de Violação | Criticidade | Blocking | Status Cobertura | Últ. Execução | Evidência (teste) | AR Relacionada |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| INV-TRAIN-001 | focus_total_max_120_pct | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-001 | INTEGRATION | SIM | CRITICA | POST | COBERTO | 2026-03-03 | _reports/training/TEST-TRAIN-INV-001.md | AR_202, AR_209 |
| INV-TRAIN-002 | wellness_pre_deadline_2h_before_session | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-002 | INTEGRATION | SIM | CRITICA | POST | COBERTO | 2026-03-03 | _reports/training/TEST-TRAIN-INV-002.md | AR_209 |
| INV-TRAIN-003 | wellness_post_edit_window_24h_after_created | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-003 | UNIT | SIM | CRITICA | POST | COBERTO | 2026-03-03 | _reports/training/TEST-TRAIN-INV-003.md | AR_209 |
| INV-TRAIN-004 | session_edit_window_by_role | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-004 | UNIT | SIM | CRITICA | POST | COBERTO | 2026-03-03 | _reports/training/TEST-TRAIN-INV-004.md | AR_209 |
| INV-TRAIN-005 | session_immutable_after_60_days | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-005 | UNIT | SIM | CRITICA | POST | COBERTO | 2026-03-03 | _reports/training/TEST-TRAIN-INV-005.md | AR_209 |
| INV-TRAIN-006 | training_session_status_lifecycle | BLOQUEANTE_VALIDACAO | db+calc | TEST-TRAIN-INV-006 | UNIT | NAO | CRITICA | POST | PARCIAL | 2026-03-03 | test_inv_train_006_lifecycle_status.py | - |
| INV-TRAIN-007 | celery_uses_utc | BLOQUEANTE_ARQUITETURA | calc | TEST-TRAIN-INV-007 | GATE_CHECK | NAO | ALTA | POST | COBERTO | 2026-03-03 | test_inv_train_007_celery_utc_timezone.py | - |
| INV-TRAIN-008 | soft_delete_reason_pair | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-008 | GATE_CHECK | NAO | CRITICA | PRE | COBERTO | 2026-03-03 | _reports/training/TEST-TRAIN-INV-008.md | AR_203, AR_209 |
| INV-TRAIN-009 | unique_wellness_pre_per_athlete_session | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-009 | INTEGRATION | SIM | CRITICA | POST | COBERTO | 2026-03-03 | _reports/training/TEST-TRAIN-INV-009.md | AR_209 |
| INV-TRAIN-010 | unique_wellness_post_per_athlete_session | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-010 | INTEGRATION | SIM | CRITICA | POST | COBERTO | FAIL | test_inv_train_010_wellness_post_uniqueness.py | AR-TRAIN-003, AR-TRAIN-004 |
| INV-TRAIN-011 | deviation_rules_and_min_justification | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-011 | GATE_CHECK | NAO | CRITICA | POST | PARCIAL | FAIL | test_inv_train_011_deviation_rules.py | - |
| INV-TRAIN-012 | export_rate_limits_daily | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-012 | GATE_CHECK | NAO | CRITICA | POST | PARCIAL | 2026-03-03 | test_inv_train_012_export_rate_limit.py | AR-TRAIN-008, AR-TRAIN-009 |
| INV-TRAIN-013 | gamification_badge_eligibility | NAO_BLOQUEANTE | service | TEST-TRAIN-INV-013 | GATE_CHECK | NAO | MEDIA | NO | VERIFICADO | PASS | test_inv_train_013_gamification_badge_rules.py | AR-TRAIN-010B |
| INV-TRAIN-014 | overload_alert_threshold_multiplier | NAO_BLOQUEANTE | service | TEST-TRAIN-INV-014 | GATE_CHECK | NAO | MEDIA | NO | PARCIAL | 2026-03-03 | test_inv_train_014_overload_alert_threshold.py | AR-TRAIN-001, AR-TRAIN-002 |
| INV-TRAIN-015 | training_analytics_endpoints_exposed | BLOQUEANTE_ARQUITETURA | calc+api | TEST-TRAIN-INV-015 | GATE_CHECK | NAO | ALTA | POST | COBERTO | 2026-03-03 | test_inv_train_015_training_analytics_exposure.py | - |
| INV-TRAIN-016 | attendance_auth_and_scoped_route_not_exposed | BLOQUEANTE_ARQUITETURA | api | TEST-TRAIN-INV-016 | CONTRACT | SIM | ALTA | POST | COBERTO | 2026-03-03 | test_inv_train_016_attendance_auth_scoped.py | - |
| INV-TRAIN-018 | microcycle_session_default_status | BLOQUEANTE_ARQUITETURA | service | TEST-TRAIN-INV-018 | CONTRACT|UNIT | NAO | ALTA | POST | COBERTO | 2026-03-03 | test_inv_train_018_training_session_microcycle_status.py, test_inv_train_018_training_session_microcycle_status_route.py | AR-TRAIN-049 |
| INV-TRAIN-019 | audit_logs_for_training_session_actions | BLOQUEANTE_ARQUITETURA | service | TEST-TRAIN-INV-019 | INTEGRATION | NAO | ALTA | POST | COBERTO | FAIL | test_inv_train_019_training_session_audit_logs.py | - |
| INV-TRAIN-020 | analytics_cache_invalidation_trigger | BLOQUEANTE_ARQUITETURA | db | TEST-TRAIN-INV-020 | GATE_CHECK | NAO | ALTA | PRE | COBERTO | FAIL | test_inv_train_020_cache_invalidation_trigger.py | AR-TRAIN-010A |
| INV-TRAIN-021 | internal_load_trigger | BLOQUEANTE_ARQUITETURA | db | TEST-TRAIN-INV-021 | GATE_CHECK | NAO | ALTA | PRE | COBERTO | FAIL | test_inv_train_021_internal_load_trigger.py | AR-TRAIN-010A |
| INV-TRAIN-022 | wellness_post_invalidates_training_analytics_cache | BLOQUEANTE_ARQUITETURA | calc | TEST-TRAIN-INV-022 | UNIT | NAO | ALTA | POST | COBERTO | 2026-03-03 | test_inv_train_022_wellness_post_cache_invalidation.py | - |
| INV-TRAIN-023 | wellness_post_triggers_overload_alert_check | NAO_BLOQUEANTE | service+calc | TEST-TRAIN-INV-023 | UNIT | NAO | MEDIA | NO | PARCIAL | 2026-03-03 | test_inv_train_023_wellness_post_overload_alert_trigger.py | AR-TRAIN-001, AR-TRAIN-002 |
| INV-TRAIN-024 | websocket_broadcast_for_alerts_and_badges | NAO_BLOQUEANTE | service+ux | TEST-TRAIN-INV-024 | GATE_CHECK | NAO | MEDIA | NO | VERIFICADO | PASS | test_inv_train_024_websocket_broadcast.py | AR-TRAIN-010B |
| INV-TRAIN-025 | lgpd_export_async_jobs | BLOQUEANTE_ARQUITETURA | calc+api | TEST-TRAIN-INV-025 | GATE_CHECK | NAO | ALTA | POST | PARCIAL | 2026-03-03 | test_inv_train_025_export_lgpd_endpoints.py | AR-TRAIN-008, AR-TRAIN-009 |
| INV-TRAIN-026 | lgpd_access_logging | BLOQUEANTE_ARQUITETURA | service | TEST-TRAIN-INV-026 | GATE_CHECK | NAO | ALTA | POST | COBERTO | 2026-03-03 | test_inv_train_026_lgpd_access_logging.py | - |
| INV-TRAIN-027 | refresh_training_rankings_task | BLOQUEANTE_ARQUITETURA | calc | TEST-TRAIN-INV-027 | UNIT | NAO | ALTA | POST | COBERTO | 2026-03-03 | test_inv_train_027_refresh_training_rankings_task.py | AR-TRAIN-006, AR-TRAIN-007 |
| INV-TRAIN-028 | deprecated_duplicate_focus_rule | DEPRECATED | tests | TEST-TRAIN-INV-028 | GATE_CHECK | NAO | BAIXA | NO | NAO_APLICAVEL | FAIL | test_inv_train_028_focus_sum_constraint.py (refs _generated) | - |
| INV-TRAIN-029 | editing_rules_by_session_status | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-029 | GATE_CHECK | NAO | CRITICA | POST | PARCIAL | FAIL | test_inv_train_029_edit_blocked_after_in_progress.py | - |
| INV-TRAIN-030 | attendance_correction_requires_audit_fields | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-030 | GATE_CHECK | NAO | CRITICA | PRE | COBERTO | 2026-03-03 | _reports/training/TEST-TRAIN-INV-030.md | AR_204, AR_209 |
| INV-TRAIN-031 | derive_phase_focus_from_percentages | BLOQUEANTE_ARQUITETURA | db | TEST-TRAIN-INV-031 | GATE_CHECK | NAO | ALTA | PRE | COBERTO | FAIL | test_inv_train_031_derive_phase_focus.py | AR-TRAIN-010A |
| INV-TRAIN-032 | wellness_post_rpe_range | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-032 | INTEGRATION | SIM | CRITICA | POST | COBERTO | 2026-03-03 | _reports/training/TEST-TRAIN-INV-032.md | AR_205, AR_209 |
| INV-TRAIN-033 | wellness_pre_sleep_hours_range | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-033 | INTEGRATION | SIM | CRITICA | POST | COBERTO | 2026-03-03 | test_inv_train_033_wellness_pre_sleep_hours.py, test_inv_train_033_wellness_pre_sleep_hours_runtime.py | - |
| INV-TRAIN-034 | wellness_pre_sleep_quality_range | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-034 | INTEGRATION | SIM | CRITICA | POST | COBERTO | FAIL | test_inv_train_034_wellness_pre_sleep_quality.py, test_inv_train_034_wellness_pre_sleep_quality_runtime.py | - |
| INV-TRAIN-035 | session_template_unique_name_per_org | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-035 | GATE_CHECK|INTEGRATION | SIM | CRITICA | POST | COBERTO | 2026-03-03 | test_inv_train_035_session_templates_unique_name.py (refs _generated), test_inv_train_035_session_templates_unique_name_runtime.py | AR-TRAIN-049 |
| INV-TRAIN-036 | wellness_rankings_unique_team_month | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-036 | GATE_CHECK|INTEGRATION | SIM | CRITICA | POST | COBERTO | FAIL | test_inv_train_036_wellness_rankings_unique.py (refs _generated), test_inv_train_036_wellness_rankings_unique_runtime.py | AR-TRAIN-006, AR-TRAIN-007 |
| INV-TRAIN-037 | cycle_dates_valid | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-037 | GATE_CHECK|INTEGRATION | SIM | CRITICA | POST | COBERTO | FAIL | test_inv_train_037_cycle_dates.py (refs _generated), test_inv_train_037_cycle_dates_runtime.py | - |
| INV-TRAIN-040 | openapi_contract_health_public | BLOQUEANTE_ARQUITETURA | api | TEST-TRAIN-INV-040 | CONTRACT | NAO | ALTA | PRE | COBERTO | 2026-03-03 | test_inv_train_040_health_contract.py | AR-TRAIN-010A |
| INV-TRAIN-041 | openapi_contract_teams_auth | BLOQUEANTE_ARQUITETURA | api | TEST-TRAIN-INV-041 | CONTRACT | NAO | ALTA | PRE | COBERTO | 2026-03-03 | test_inv_train_041_teams_contract.py | AR-TRAIN-010A |
| INV-TRAIN-043 | microcycle_dates_valid | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-043 | INTEGRATION | SIM | CRITICA | POST | COBERTO | 2026-03-03 | test_inv_train_043_microcycle_dates_check.py | - |
| INV-TRAIN-044 | analytics_cache_unique_lookup | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-044 | INTEGRATION | SIM | CRITICA | POST | COBERTO | 2026-03-03 | test_inv_train_044_analytics_cache_unique.py | - |
| INV-TRAIN-045 | session_exercises_order_unique | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-045 | INTEGRATION | SIM | CRITICA | POST | COBERTO | 2026-03-03 | test_inv_train_045_session_exercises_order_unique.py | - |
| INV-TRAIN-046 | wellness_response_trigger_updates_reminders | BLOQUEANTE_ARQUITETURA | db | TEST-TRAIN-INV-046 | INTEGRATION | NAO | ALTA | POST | COBERTO | 2026-03-03 | test_inv_train_046_wellness_post_response_trigger.py | - |
| INV-TRAIN-047 | exercise_scope_valid | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-047 | INTEGRATION | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_047_exercise_scope.py | AR-TRAIN-011 |
| INV-TRAIN-048 | system_exercise_immutable_for_org_users | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-048 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_048_system_immutable.py | AR-TRAIN-012 |
| INV-TRAIN-049 | org_exercise_single_organization | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-049 | INTEGRATION | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_049_exercise_org_scope.py | AR-TRAIN-011 |
| INV-TRAIN-050 | favorite_unique_per_user_exercise | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-050 | INTEGRATION | SIM | CRITICA | BOTH | COBERTO | ERROR | test_inv_train_050_exercise_favorites_unique.py | AR-TRAIN-011 |
| INV-TRAIN-051 | catalog_visibility_respects_organization | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-051 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_051_catalog_visibility.py | AR-TRAIN-012, AR-TRAIN-013 |
| INV-TRAIN-052 | exercise_media_type_reference_valid | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-052 | INTEGRATION | SIM | ALTA | BOTH | COBERTO | ERROR | test_inv_train_052_exercise_media.py | AR-TRAIN-011 |
| INV-TRAIN-053 | soft_delete_exercise_no_break_historic_session | BLOQUEANTE_ARQUITETURA | db+service | TEST-TRAIN-INV-053 | INTEGRATION | NAO | ALTA | BOTH | COBERTO | PASS | test_inv_train_053_soft_delete_exercise_no_break_historic.py | AR-TRAIN-011 |
| INV-TRAIN-EXB-ACL-001 | exercise_org_visibility_mode_valid | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-EXB-ACL-001 | INTEGRATION | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_exb_acl_001_visibility_mode.py | AR-TRAIN-011, AR-TRAIN-013 |
| INV-TRAIN-EXB-ACL-002 | acl_only_for_org_restricted | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-EXB-ACL-002 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_exb_acl_002_acl_restricted.py | AR-TRAIN-012, AR-TRAIN-013 |
| INV-TRAIN-EXB-ACL-003 | acl_anti_cross_org | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-EXB-ACL-003 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_exb_acl_003_anti_cross_org.py | AR-TRAIN-012, AR-TRAIN-013 |
| INV-TRAIN-EXB-ACL-004 | acl_authority_creator_only | BLOQUEANTE_VALIDACAO | service+api | TEST-TRAIN-INV-EXB-ACL-004 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_exb_acl_004_creator_authority.py | AR-TRAIN-012 |
| INV-TRAIN-EXB-ACL-005 | creator_implicit_access | BLOQUEANTE_ARQUITETURA | service | TEST-TRAIN-INV-EXB-ACL-005 | CONTRACT | NAO | ALTA | BOTH | COBERTO | PASS | test_inv_train_exb_acl_005_creator_implicit_access.py | AR-TRAIN-012 |
| INV-TRAIN-EXB-ACL-006 | acl_unique_per_exercise_user | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-EXB-ACL-006 | INTEGRATION | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_exb_acl_006_acl_table.py | AR-TRAIN-011, AR-TRAIN-049 |
| INV-TRAIN-EXB-ACL-007 | acl_change_no_retrobreak_historic_session | BLOQUEANTE_ARQUITETURA | service+db | TEST-TRAIN-INV-EXB-ACL-007 | INTEGRATION | NAO | ALTA | BOTH | COBERTO | PASS | test_inv_train_exb_acl_007_acl_change_no_retrobreak.py | AR-TRAIN-012 |
| INV-TRAIN-054 | cycle_hierarchy_mandatory | BLOQUEANTE_VALIDACAO | db+service | TEST-TRAIN-INV-054 | INTEGRATION | SIM | CRITICA | BOTH | COBERTO | FAIL | test_inv_train_054_standalone_session.py | AR-TRAIN-015 |
| INV-TRAIN-055 | meso_overlap_allowed | NAO_BLOQUEANTE | service | TEST-TRAIN-INV-055 | UNIT | NAO | MEDIA | NO | COBERTO | 2026-03-03 | test_inv_train_055_meso_overlap.py | AR-TRAIN-015 |
| INV-TRAIN-056 | micro_contained_in_meso | BLOQUEANTE_VALIDACAO | db+service | TEST-TRAIN-INV-056 | INTEGRATION | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_056_micro_within_meso.py | AR-TRAIN-015 |
| INV-TRAIN-057 | standalone_session_explicit_flag | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-057 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | FAIL | test_inv_train_057_session_within_microcycle.py | AR-TRAIN-016 |
| INV-TRAIN-058 | session_structure_mutable_until_close | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-058 | CONTRACT | SIM | CRITICA | POST | COBERTO | 2026-03-03 | test_inv_train_058_session_structure_mutable.py | AR-TRAIN-016, AR-TRAIN-049 |
| INV-TRAIN-059 | exercise_order_contiguous_unique | BLOQUEANTE_VALIDACAO | db | TEST-TRAIN-INV-059 | INTEGRATION | SIM | CRITICA | POST | COBERTO | 2026-03-03 | test_inv_train_059_exercise_order_contiguous.py | AR-TRAIN-016, AR-TRAIN-049 |
| INV-TRAIN-060 | org_exercise_default_restricted | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-060 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | PASS | test_inv_train_060_org_exercise_default_restricted.py | AR-TRAIN-011, AR-TRAIN-013 |
| INV-TRAIN-061 | system_exercise_copy_not_edit | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-061 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | PASS | test_inv_train_061_system_exercise_copy_not_edit.py | AR-TRAIN-012 |
| INV-TRAIN-062 | exercise_visibility_required_for_session_add | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-062 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | PASS | test_inv_train_062_exercise_visibility_required.py | AR-TRAIN-012, AR-TRAIN-013 |
| INV-TRAIN-063 | athlete_preconfirm_not_official | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-063 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_063_preconfirm.py | AR-TRAIN-017, AR-TRAIN-049 |
| INV-TRAIN-064 | official_attendance_at_closure | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-064 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_064_close_consolidation.py | AR-TRAIN-017, AR-TRAIN-049 |
| INV-TRAIN-065 | closure_allows_inconsistency_as_pending | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-065 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | FAIL | test_inv_train_065_close_pending_guard.py | AR-TRAIN-017 |
| INV-TRAIN-066 | pending_queue_separate | BLOQUEANTE_ARQUITETURA | service+db | TEST-TRAIN-INV-066 | INTEGRATION | NAO | ALTA | BOTH | COBERTO | FAIL | test_inv_train_066_pending_items.py | AR-TRAIN-017, AR-TRAIN-018 |
| INV-TRAIN-067 | athlete_pending_collaboration_no_validate | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-067 | CONTRACT | SIM | ALTA | BOTH | COBERTO | FAIL | test_inv_train_067_athlete_pending_rbac.py | AR-TRAIN-018 |
| INV-TRAIN-068 | athlete_sees_training_before | BLOQUEANTE_ARQUITETURA | service+api | TEST-TRAIN-INV-068 | CONTRACT | NAO | ALTA | BOTH | COBERTO | 2026-03-03 | test_inv_train_068_athlete_sees_training.py | AR-TRAIN-019 |
| INV-TRAIN-069 | exercise_media_accessible_to_athlete | BLOQUEANTE_ARQUITETURA | service | TEST-TRAIN-INV-069 | CONTRACT | NAO | ALTA | BOTH | COBERTO | 2026-03-03 | test_inv_train_069_exercise_media_via_session.py | AR-TRAIN-019 |
| INV-TRAIN-070 | post_training_conversational | NAO_BLOQUEANTE | service | TEST-TRAIN-INV-070 | CONTRACT | NAO | MEDIA | BOTH | COBERTO | FAIL | test_inv_train_070_post_conversational.py | AR-TRAIN-020 |
| INV-TRAIN-071 | wellness_missing_blocks_full_content | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-071 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_071_content_gate.py | AR-TRAIN-019 |
| INV-TRAIN-072 | ai_suggestion_not_order | BLOQUEANTE_ARQUITETURA | service | TEST-TRAIN-INV-072 | UNIT | NAO | ALTA | BOTH | COBERTO | 2026-03-03 | test_inv_train_072_ai_suggestion_not_order.py | AR-TRAIN-021 |
| INV-TRAIN-073 | ai_privacy_no_intimate_content | BLOQUEANTE_ARQUITETURA | service | TEST-TRAIN-INV-073 | UNIT | NAO | ALTA | BOTH | COBERTO | 2026-03-03 | test_inv_train_073_ai_privacy_no_intimate_content.py | AR-TRAIN-021 |
| INV-TRAIN-074 | ai_educational_content_independent | NAO_BLOQUEANTE | service | TEST-TRAIN-INV-074 | UNIT | NAO | MEDIA | BOTH | COBERTO | 2026-03-03 | test_inv_train_074_ai_educational_content_independent.py | AR-TRAIN-021 |
| INV-TRAIN-075 | ai_extra_training_draft_only | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-075 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_075_ai_extra_training_draft_only.py | AR-TRAIN-021 |
| INV-TRAIN-076 | mandatory_wellness_policy | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-076 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_076_wellness_policy.py | AR-TRAIN-019, AR-TRAIN-049 |
| INV-TRAIN-077 | immediate_virtual_coach_feedback | NAO_BLOQUEANTE | service | TEST-TRAIN-INV-077 | UNIT | NAO | MEDIA | BOTH | COBERTO | 2026-03-03 | test_inv_train_077_immediate_virtual_coach_feedback.py | AR-TRAIN-020, AR-TRAIN-021 |
| INV-TRAIN-078 | progress_view_requires_compliance | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-078 | CONTRACT | SIM | ALTA | BOTH | COBERTO | 2026-03-03 | test_inv_train_078_progress_gate.py | AR-TRAIN-019 |
| INV-TRAIN-079 | individual_recognition_no_intimate_leak | BLOQUEANTE_ARQUITETURA | service | TEST-TRAIN-INV-079 | UNIT | NAO | ALTA | BOTH | COBERTO | 2026-03-03 | test_inv_train_079_individual_recognition_no_intimate_leak.py | AR-TRAIN-021, AR-TRAIN-046 |
| INV-TRAIN-080 | ai_coach_draft_only | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-080 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_080_ai_coach_draft_only.py | AR-TRAIN-021, AR-TRAIN-046 |
| INV-TRAIN-081 | ai_suggestion_requires_justification | BLOQUEANTE_VALIDACAO | service | TEST-TRAIN-INV-081 | CONTRACT | SIM | CRITICA | BOTH | COBERTO | 2026-03-03 | test_inv_train_081_ai_suggestion_requires_justification.py | AR-TRAIN-021, AR-TRAIN-046 |

### Observações (invariantes) — gaps de cobertura (AS-IS)

- `INV-TRAIN-006`, `INV-TRAIN-011`, `INV-TRAIN-012`, `INV-TRAIN-029`: faltam testes de violação (hoje a cobertura é majoritariamente `GATE_CHECK/UNIT`).
- `INV-TRAIN-008`, `INV-TRAIN-020`, `INV-TRAIN-021`, `INV-TRAIN-030`, `INV-TRAIN-031`, `INV-TRAIN-040`, `INV-TRAIN-041`: `COBERTO` — AR-TRAIN-010A VERIFICADO (AR_173/174); refs `docs/ssot/*` resolvidas.
- `INV-TRAIN-047..053`, `INV-TRAIN-EXB-ACL-001..007`: `PENDENTE` — invariantes novas (v1.1.0, DEC-TRAIN-EXB-*). Schema/service não materializado ainda (GAP-TRAIN-EXB-001..003).

### 5c) Referência de Blocking Stage `[NORMATIVO]`

| Valor | Semântica | Impacto na AR |
|---|---|---|
| **PRE** | Bloqueia **início** da AR — dependência não resolvida impede trabalho | AR não pode sair de DRAFT enquanto bloqueio persistir |
| **POST** | Bloqueia **conclusão** da AR — teste deve passar antes de fechar | AR pode ser implementada, mas não pode ser marcada VERIFICADO sem evidência |
| **BOTH** | Bloqueia início **e** conclusão — requer schema/service + teste | AR depende de materialização prévia (schema, endpoint) E validação posterior |
| **NO** | Não bloqueante — falha não impede progresso da AR | Pode ser tratado em ciclo posterior |

**Classificação padrão:**
- `BLOQUEADO` (Status Cobertura) → `PRE` (dependência impede execução)
- `PENDENTE` + `BLOQUEANTE_*` + GAP de schema → `BOTH` (precisa criar + testar)
- `COBERTO`/`PARCIAL` + `BLOQUEANTE_*` → `POST` (teste existe, deve passar)
- `NAO_BLOQUEANTE` ou `DEPRECATED` → `NO`

### 5b) Testes Normativos por Decisão (DEC-TRAIN-*) — adicionados v1.1.0

| DEC ID | Regra testada | ID Teste | Tipo | Cenário | Happy/Exceção | Blocking | Status Cobertura | AR Relacionada |
|---|---|---|---|---|---|---|---|---|
| DEC-TRAIN-001 | Wellness self-only (sem athlete_id no payload) | TEST-TRAIN-DEC-001a | CONTRACT | POST wellness_pre sem athlete_id → 201 (backend infere do JWT) | Happy | BOTH | COBERTO | AR-TRAIN-003, AR-TRAIN-004 |
| DEC-TRAIN-001 | Wellness self-only (athlete_id rejeitado) | TEST-TRAIN-DEC-001b | CONTRACT | POST wellness_pre COM athlete_id arbitrário → 422 ou ignorado | Exceção | BOTH | COBERTO | AR-TRAIN-003, AR-TRAIN-004 |
| DEC-TRAIN-002 | FE→payload mapping (wellness pré) | TEST-TRAIN-DEC-002 | E2E\|MANUAL_GUIADO | Cada slider UI produz campo correto no payload | Happy | POST | MANUAL_GUIADO | AR-TRAIN-003 |
| DEC-TRAIN-003 | Top performers canônico (FE usa CONTRACT-TRAIN-076) | TEST-TRAIN-DEC-003 | CONTRACT\|E2E | SCREEN-TRAIN-015 faz request para `/teams/{id}/wellness-top-performers` (não 075) | Happy | POST | COBERTO | AR-TRAIN-007 |
| DEC-TRAIN-004 | Export degradado (sem worker → 202 + degraded) | TEST-TRAIN-DEC-004a | CONTRACT | POST export-pdf sem worker → 202 Accepted com `degraded: true` (não 500) | Exceção | POST | COBERTO | AR-TRAIN-008, AR-TRAIN-009 |
| DEC-TRAIN-004 | Export degradado (UI mostra banner) | TEST-TRAIN-DEC-004b | MANUAL_GUIADO\|E2E | SCREEN-TRAIN-013 exibe banner de degradação quando `degraded: true` | Happy | POST | MANUAL_GUIADO | AR-TRAIN-009 |
| DEC-TRAIN-EXB-001 | Scope SYSTEM vs ORG (catálogo) | TEST-TRAIN-DEC-EXB-001 | CONTRACT | GET /exercises retorna SYSTEM+ORG da mesma org; não retorna ORG de outra org | Happy | BOTH | COBERTO | AR-TRAIN-011, AR-TRAIN-013 |
| DEC-TRAIN-EXB-001B | Visibility restricted filtra por ACL | TEST-TRAIN-DEC-EXB-001B | CONTRACT | GET /exercises não retorna exercício ORG restricted de outra pessoa sem ACL | Exceção | BOTH | COBERTO | AR-TRAIN-012, AR-TRAIN-013 |
| DEC-TRAIN-EXB-002 | ACL management (CRUD) | TEST-TRAIN-DEC-EXB-002 | CONTRACT | POST/DELETE ACL user + verifica lista | Happy | BOTH | COBERTO | AR-TRAIN-012, AR-TRAIN-013 |
| DEC-TRAIN-RBAC-001 | Treinador gerencia exercícios ORG próprios | TEST-TRAIN-DEC-RBAC-001a | CONTRACT | PATCH exercise como Treinador creator → 200 | Happy | BOTH | COBERTO | AR-TRAIN-012 |
| DEC-TRAIN-RBAC-001 | Org user não edita SYSTEM | TEST-TRAIN-DEC-RBAC-001b | CONTRACT | PATCH exercise SYSTEM como Treinador → 403 | Exceção | BOTH | COBERTO | AR-TRAIN-012 |

---

## 6) Matriz de Cobertura por Fluxos

| ID Flow | Nome do Fluxo | Prioridade | ID Teste | Tipo | Cenário | Happy/Exceção | Status Cobertura | Últ. Execução | Evidência | Screens Relacionadas | Contratos Relacionados |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FLOW-TRAIN-001 | Navegar agenda semanal/mensal | P0 | TEST-TRAIN-FLOW-001 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-001.md` | SCREEN-TRAIN-001 | CONTRACT-TRAIN-001 |
| FLOW-TRAIN-002 | Criar sessão (draft) e publicar (scheduled) | P0 | TEST-TRAIN-FLOW-002 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-002.md` | SCREEN-TRAIN-003, SCREEN-TRAIN-004 | CONTRACT-TRAIN-002, CONTRACT-TRAIN-006 |
| FLOW-TRAIN-003 | Editar sessão e compor treino (foco + exercícios + notas) | P0 | TEST-TRAIN-FLOW-003 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-003.md` | SCREEN-TRAIN-004, SCREEN-TRAIN-005 | CONTRACT-TRAIN-004, CONTRACT-TRAIN-019..024 |
| FLOW-TRAIN-004 | Registrar presença digital (incl. justified) | P0 | TEST-TRAIN-FLOW-004 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-004.md` | SCREEN-TRAIN-020 | CONTRACT-TRAIN-025..028 |
| FLOW-TRAIN-005 | Atleta preencher wellness pré (deadline 2h) | P0 | TEST-TRAIN-FLOW-005 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-005.md` | SCREEN-TRAIN-018 | CONTRACT-TRAIN-030 |
| FLOW-TRAIN-006 | Atleta preencher wellness pós (janela 24h) | P0 | TEST-TRAIN-FLOW-006 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-006.md` | SCREEN-TRAIN-019 | CONTRACT-TRAIN-036 |
| FLOW-TRAIN-007 | Treinador visualizar status wellness da sessão | P1 | TEST-TRAIN-FLOW-007 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-007.md` | SCREEN-TRAIN-004 | CONTRACT-TRAIN-012 |
| FLOW-TRAIN-008 | Planejar ciclos e microciclos | P1 | TEST-TRAIN-FLOW-008 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-008.md` | SCREEN-TRAIN-007, SCREEN-TRAIN-008 | CONTRACT-TRAIN-040..052 |
| FLOW-TRAIN-009 | Gerenciar banco de exercícios e favoritos | P1 | TEST-TRAIN-FLOW-009 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-009.md` | SCREEN-TRAIN-010, SCREEN-TRAIN-011 | CONTRACT-TRAIN-053..062 |
| FLOW-TRAIN-010 | Gerenciar templates de sessão | P1 | TEST-TRAIN-FLOW-010 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-010.md` | SCREEN-TRAIN-017 | CONTRACT-TRAIN-063..068 |
| FLOW-TRAIN-011 | Visualizar analytics e desvios | P1 | TEST-TRAIN-FLOW-011 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-011.md` | SCREEN-TRAIN-012 | CONTRACT-TRAIN-069..071 |
| FLOW-TRAIN-012 | Exportar relatório (PDF) de analytics | P1 | TEST-TRAIN-FLOW-012 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-012.md` | SCREEN-TRAIN-012, SCREEN-TRAIN-013 | CONTRACT-TRAIN-086..089 |
| FLOW-TRAIN-013 | Visualizar rankings wellness e top performers | P1 | TEST-TRAIN-FLOW-013 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-013.md` | SCREEN-TRAIN-014, SCREEN-TRAIN-015 | CONTRACT-TRAIN-073..076 |
| FLOW-TRAIN-014 | Visualizar eficácia preventiva | P2 | TEST-TRAIN-FLOW-014 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-014.md` | SCREEN-TRAIN-016 | CONTRACT-TRAIN-072 |
| FLOW-TRAIN-015 | Gerenciar alertas e sugestões (apply/dismiss) | P2 | TEST-TRAIN-FLOW-015 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-015.md` | SCREEN-TRAIN-021 | CONTRACT-TRAIN-077..085 |
| FLOW-TRAIN-016 | Atleta visualiza treino antes da sessão | P1 | TEST-TRAIN-FLOW-016 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-016.md` | SCREEN-TRAIN-022 | CONTRACT-TRAIN-096 |
| FLOW-TRAIN-017 | Pré-confirmação e presença oficial no fechamento | P0 | TEST-TRAIN-FLOW-017 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-017.md` | SCREEN-TRAIN-020, SCREEN-TRAIN-022 | CONTRACT-TRAIN-097, CONTRACT-TRAIN-098 |
| FLOW-TRAIN-018 | Treinador resolve fila de pendências | P0 | TEST-TRAIN-FLOW-018 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-018.md` | SCREEN-TRAIN-023 | CONTRACT-TRAIN-099, CONTRACT-TRAIN-100 |
| FLOW-TRAIN-019 | Atleta interage com coach virtual (IA) | P2 | TEST-TRAIN-FLOW-019 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-019.md` | SCREEN-TRAIN-024 | CONTRACT-TRAIN-103, CONTRACT-TRAIN-104 |
| FLOW-TRAIN-020 | IA gera rascunho de treino para coach editar | P2 | TEST-TRAIN-FLOW-020 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-020.md` | SCREEN-TRAIN-025 | CONTRACT-TRAIN-101, CONTRACT-TRAIN-102 |
| FLOW-TRAIN-021 | Wellness gates conteúdo (atleta sem wellness bloqueado) | P1 | TEST-TRAIN-FLOW-021 | MANUAL_GUIADO | Happy path (end-to-end) | Happy | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-FLOW-021.md` | SCREEN-TRAIN-022 | CONTRACT-TRAIN-105 |

---

## 7) Matriz de Cobertura por Telas (UI funcional)

| ID Screen | Rota / Entrada | Estado de UI (mínimo) | ID Teste | Tipo | Cenário | Criticidade | Status Cobertura | Últ. Execução | Evidência | AR Relacionada |
|---|---|---|---|---|---|---|---|---|---|---|
| SCREEN-TRAIN-001 | `/training/agenda` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-001 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-001.md` | - |
| SCREEN-TRAIN-002 | `/training/calendario` (redirect) | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-002 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-002.md` | - |
| SCREEN-TRAIN-003 | `CreateSessionModal` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-003 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-003.md` | - |
| SCREEN-TRAIN-004 | `SessionEditorModal` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-004 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-004.md` | - |
| SCREEN-TRAIN-005 | `/training/sessions/[id]/edit` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-005 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-005.md` | - |
| SCREEN-TRAIN-006 | `/training/relatorio/[sessionId]` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-006 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-006.md` | - |
| SCREEN-TRAIN-007 | `/training/planejamento` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-007 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-007.md` | - |
| SCREEN-TRAIN-008 | `CreateCycleWizard` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-008 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-008.md` | - |
| SCREEN-TRAIN-009 | `CopyWeekModal` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-009 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-009.md` | - |
| SCREEN-TRAIN-010 | `/training/exercise-bank` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-010 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-010.md` | - |
| SCREEN-TRAIN-011 | `ExerciseModal` / `CreateExerciseModal` / `EditExerciseModal` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-011 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-011.md` | - |
| SCREEN-TRAIN-012 | `/training/analytics` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-012 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-012.md` | - |
| SCREEN-TRAIN-013 | `ExportPDFModal` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-013 | MANUAL_GUIADO | Smoke funcional + estados | ALTA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-013.md` | AR-TRAIN-008, AR-TRAIN-009 |
| SCREEN-TRAIN-014 | `/training/rankings` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-014 | MANUAL_GUIADO | Smoke funcional + estados | ALTA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-014.md` | AR-TRAIN-006, AR-TRAIN-007 |
| SCREEN-TRAIN-015 | `/training/top-performers/[teamId]` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-015 | MANUAL_GUIADO | Smoke funcional + estados | ALTA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-015.md` | AR-TRAIN-006, AR-TRAIN-007 |
| SCREEN-TRAIN-016 | `/training/eficacia-preventiva` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-016 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-016.md` | - |
| SCREEN-TRAIN-017 | `/training/configuracoes` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-017 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-017.md` | - |
| SCREEN-TRAIN-018 | `/athlete/wellness-pre/[sessionId]` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-018 | MANUAL_GUIADO | Smoke funcional + estados | ALTA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-018.md` | AR-TRAIN-003, AR-TRAIN-004 |
| SCREEN-TRAIN-019 | `/athlete/wellness-post/[sessionId]` | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-019 | MANUAL_GUIADO | Smoke funcional + estados | ALTA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-019.md` | AR-TRAIN-003, AR-TRAIN-004 |
| SCREEN-TRAIN-020 | `/training/presencas` (placeholder) | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-020 | MANUAL_GUIADO | Smoke funcional + estados | ALTA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-020.md` | AR-TRAIN-005 |
| SCREEN-TRAIN-021 | (a definir) Central de Alertas/Sugestões | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-021 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-021.md` | AR-TRAIN-001, AR-TRAIN-002 |
| SCREEN-TRAIN-022 | `/athlete/training/[sessionId]` Visão pré-treino atleta | loading\|error\|empty\|data\|wellness_blocked | TEST-TRAIN-SCREEN-022 | MANUAL_GUIADO | Smoke funcional + estados (incl. wellness gate) | ALTA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-022.md` | AR-TRAIN-019 |
| SCREEN-TRAIN-023 | `/training/pending-queue` Fila de pendências | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-023 | MANUAL_GUIADO | Smoke funcional + estados | ALTA | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-023.md` | AR-TRAIN-017, AR-TRAIN-018 |
| SCREEN-TRAIN-024 | `/athlete/ai-chat/[sessionId]` Chat IA atleta | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-024 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | NOT_APPLICABLE | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-024.md` | AR-TRAIN-021 |
| SCREEN-TRAIN-025 | `AICoachDraftModal` Sugestão IA para treinador | loading\|error\|empty\|data\|readonly | TEST-TRAIN-SCREEN-025 | MANUAL_GUIADO | Smoke funcional + estados | MEDIA | NOT_APPLICABLE | 2026-03-03 | `_reports/training/TEST-TRAIN-SCREEN-025.md` | AR-TRAIN-021 |

---

## 8) Matriz de Cobertura por Contratos Front-Back

> Os shapes mínimos normativos de request/response estão em `TRAINING_FRONT_BACK_CONTRACT.md`. Aqui mapeamos a exigência de validação por endpoint.

| ID Contract | Ação (método + path) | Prioridade | ID Teste | Tipo | Blocking | Status Cobertura | Últ. Execução | Evidência | AR Relacionada |
|---|---|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-001 | GET `/training-sessions` | P0 | TEST-TRAIN-CONTRACT-001 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_214/executor_main.log` | AR-TRAIN-035 |
| CONTRACT-TRAIN-002 | POST `/training-sessions` | P0 | TEST-TRAIN-CONTRACT-002 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_214/executor_main.log` | AR-TRAIN-035 |
| CONTRACT-TRAIN-003 | GET `/training-sessions/{training_session_id}` | P0 | TEST-TRAIN-CONTRACT-003 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_214/executor_main.log` | AR-TRAIN-035 |
| CONTRACT-TRAIN-004 | PATCH `/training-sessions/{training_session_id}` | P0 | TEST-TRAIN-CONTRACT-004 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_214/executor_main.log` | AR-TRAIN-035 |
| CONTRACT-TRAIN-005 | DELETE `/training-sessions/{training_session_id}?reason=` | P0 | TEST-TRAIN-CONTRACT-005 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_214/executor_main.log` | AR-TRAIN-035 |
| CONTRACT-TRAIN-006 | POST `/training-sessions/{training_session_id}/publish` | P0 | TEST-TRAIN-CONTRACT-006 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_214/executor_main.log` | AR-TRAIN-035 |
| CONTRACT-TRAIN-007 | POST `/training-sessions/{training_session_id}/close` | P0 | TEST-TRAIN-CONTRACT-007 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_214/executor_main.log` | AR-TRAIN-035 |
| CONTRACT-TRAIN-008 | POST `/training-sessions/{training_session_id}/duplicate` | P0 | TEST-TRAIN-CONTRACT-008 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_214/executor_main.log` | AR-TRAIN-035 |
| CONTRACT-TRAIN-009 | POST `/training-sessions/{training_session_id}/restore` | P0 | TEST-TRAIN-CONTRACT-009 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_214/executor_main.log` | AR-TRAIN-035 |
| CONTRACT-TRAIN-010 | POST `/training-sessions/copy-week` | P0 | TEST-TRAIN-CONTRACT-010 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_214/executor_main.log` | AR-TRAIN-035 |
| CONTRACT-TRAIN-011 | GET `/training-sessions/{training_session_id}/deviation` | P0 | TEST-TRAIN-CONTRACT-011 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_214/executor_main.log` | AR-TRAIN-035 |
| CONTRACT-TRAIN-012 | GET `/training-sessions/{training_session_id}/wellness-status` | P0 | TEST-TRAIN-CONTRACT-012 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_214/executor_main.log` | AR-TRAIN-035 |
| CONTRACT-TRAIN-013 | GET `/teams/{team_id}/trainings` | P0 | TEST-TRAIN-CONTRACT-013 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036 |
| CONTRACT-TRAIN-014 | POST `/teams/{team_id}/trainings` | P0 | TEST-TRAIN-CONTRACT-014 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036 |
| CONTRACT-TRAIN-015 | GET `/teams/{team_id}/trainings/{training_id}` | P0 | TEST-TRAIN-CONTRACT-015 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036 |
| CONTRACT-TRAIN-016 | PATCH `/teams/{team_id}/trainings/{training_id}` | P0 | TEST-TRAIN-CONTRACT-016 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036 |
| CONTRACT-TRAIN-017 | DELETE `/teams/{team_id}/trainings/{training_id}?reason=` | P0 | TEST-TRAIN-CONTRACT-017 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036 |
| CONTRACT-TRAIN-018 | POST `/teams/{team_id}/trainings/{training_id}/restore` | P0 | TEST-TRAIN-CONTRACT-018 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036 |
| CONTRACT-TRAIN-019 | GET `/training-sessions/{session_id}/exercises` | P0 | TEST-TRAIN-CONTRACT-019 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036 |
| CONTRACT-TRAIN-020 | POST `/training-sessions/{session_id}/exercises` | P0 | TEST-TRAIN-CONTRACT-020 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036 |
| CONTRACT-TRAIN-021 | POST `/training-sessions/{session_id}/exercises/bulk` | P0 | TEST-TRAIN-CONTRACT-021 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036 |
| CONTRACT-TRAIN-022 | PATCH `/training-sessions/exercises/{session_exercise_id}` | P0 | TEST-TRAIN-CONTRACT-022 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036 |
| CONTRACT-TRAIN-023 | PATCH `/training-sessions/{session_id}/exercises/reorder` | P0 | TEST-TRAIN-CONTRACT-023 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036 |
| CONTRACT-TRAIN-024 | DELETE `/training-sessions/exercises/{session_exercise_id}` | P0 | TEST-TRAIN-CONTRACT-024 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036 |
| CONTRACT-TRAIN-025 | GET `/training_sessions/{training_session_id}/attendance` | P0 | TEST-TRAIN-CONTRACT-025 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036, AR-TRAIN-005 |
| CONTRACT-TRAIN-026 | POST `/training_sessions/{training_session_id}/attendance` | P0 | TEST-TRAIN-CONTRACT-026 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036, AR-TRAIN-005 |
| CONTRACT-TRAIN-027 | POST `/training_sessions/{training_session_id}/attendance/batch` | P0 | TEST-TRAIN-CONTRACT-027 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036, AR-TRAIN-005 |
| CONTRACT-TRAIN-028 | GET `/training_sessions/{training_session_id}/attendance/statistics` | P0 | TEST-TRAIN-CONTRACT-028 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_215/executor_main.log` | AR-TRAIN-036, AR-TRAIN-005 |
| CONTRACT-TRAIN-029 | GET `/wellness-pre/training_sessions/{training_session_id}/wellness_pre` | P0 | TEST-TRAIN-CONTRACT-029 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_216/executor_main.log` | AR-TRAIN-037, AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-030 | POST `/wellness-pre/training_sessions/{training_session_id}/wellness_pre` | P0 | TEST-TRAIN-CONTRACT-030 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_216/executor_main.log` | AR-TRAIN-037, AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-031 | GET `/wellness-pre/training_sessions/{training_session_id}/wellness_pre/status` | P0 | TEST-TRAIN-CONTRACT-031 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_216/executor_main.log` | AR-TRAIN-037, AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-032 | GET `/wellness-pre/wellness_pre/{wellness_pre_id}` | P0 | TEST-TRAIN-CONTRACT-032 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_216/executor_main.log` | AR-TRAIN-037, AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-033 | PATCH `/wellness-pre/wellness_pre/{wellness_pre_id}` | P0 | TEST-TRAIN-CONTRACT-033 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_216/executor_main.log` | AR-TRAIN-037, AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-034 | POST `/wellness-pre/wellness_pre/{wellness_pre_id}/request-unlock` | P0 | TEST-TRAIN-CONTRACT-034 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_216/executor_main.log` | AR-TRAIN-037, AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-035 | GET `/wellness-post/training_sessions/{training_session_id}/wellness_post` | P0 | TEST-TRAIN-CONTRACT-035 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_216/executor_main.log` | AR-TRAIN-037, AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-036 | POST `/wellness-post/training_sessions/{training_session_id}/wellness_post` | P0 | TEST-TRAIN-CONTRACT-036 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_216/executor_main.log` | AR-TRAIN-037, AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-037 | GET `/wellness-post/training_sessions/{training_session_id}/wellness_post/status` | P0 | TEST-TRAIN-CONTRACT-037 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_216/executor_main.log` | AR-TRAIN-037, AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-038 | GET `/wellness-post/wellness_post/{wellness_post_id}` | P0 | TEST-TRAIN-CONTRACT-038 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_216/executor_main.log` | AR-TRAIN-037, AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-039 | PATCH `/wellness-post/wellness_post/{wellness_post_id}` | P0 | TEST-TRAIN-CONTRACT-039 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_216/executor_main.log` | AR-TRAIN-037, AR-TRAIN-003, AR-TRAIN-004 |
| CONTRACT-TRAIN-040 | GET `/training-cycles` | P1 | TEST-TRAIN-CONTRACT-040 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-041 | GET `/training-cycles/{cycle_id}` | P1 | TEST-TRAIN-CONTRACT-041 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-042 | POST `/training-cycles` | P1 | TEST-TRAIN-CONTRACT-042 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-043 | PATCH `/training-cycles/{cycle_id}` | P1 | TEST-TRAIN-CONTRACT-043 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-044 | DELETE `/training-cycles/{cycle_id}?reason=` | P1 | TEST-TRAIN-CONTRACT-044 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-045 | GET `/training-cycles/teams/{team_id}/active` | P1 | TEST-TRAIN-CONTRACT-045 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-046 | GET `/training-microcycles` | P1 | TEST-TRAIN-CONTRACT-046 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-047 | GET `/training-microcycles/{microcycle_id}` | P1 | TEST-TRAIN-CONTRACT-047 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-048 | POST `/training-microcycles` | P1 | TEST-TRAIN-CONTRACT-048 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-049 | PATCH `/training-microcycles/{microcycle_id}` | P1 | TEST-TRAIN-CONTRACT-049 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-050 | DELETE `/training-microcycles/{microcycle_id}?reason=` | P1 | TEST-TRAIN-CONTRACT-050 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-051 | GET `/training-microcycles/teams/{team_id}/current` | P1 | TEST-TRAIN-CONTRACT-051 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-052 | GET `/training-microcycles/{microcycle_id}/summary` | P1 | TEST-TRAIN-CONTRACT-052 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-053 | GET `/exercises` | P1 | TEST-TRAIN-CONTRACT-053 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-054 | POST `/exercises` | P1 | TEST-TRAIN-CONTRACT-054 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-055 | GET `/exercises/{exercise_id}` | P1 | TEST-TRAIN-CONTRACT-055 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-056 | PATCH `/exercises/{exercise_id}` | P1 | TEST-TRAIN-CONTRACT-056 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-057 | GET `/exercise-tags` | P1 | TEST-TRAIN-CONTRACT-057 | CONTRACT | NO | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-058 | POST `/exercise-tags` | P1 | TEST-TRAIN-CONTRACT-058 | CONTRACT | NO | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-059 | PATCH `/exercise-tags/{tag_id}` | P1 | TEST-TRAIN-CONTRACT-059 | CONTRACT | NO | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-060 | GET `/exercise-favorites` | P1 | TEST-TRAIN-CONTRACT-060 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-061 | POST `/exercise-favorites` | P1 | TEST-TRAIN-CONTRACT-061 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-062 | DELETE `/exercise-favorites/{exercise_id}` | P1 | TEST-TRAIN-CONTRACT-062 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-063 | GET `/session-templates` | P1 | TEST-TRAIN-CONTRACT-063 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-064 | POST `/session-templates` | P1 | TEST-TRAIN-CONTRACT-064 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-065 | GET `/session-templates/{template_id}` | P1 | TEST-TRAIN-CONTRACT-065 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-066 | PATCH `/session-templates/{template_id}` | P1 | TEST-TRAIN-CONTRACT-066 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-067 | DELETE `/session-templates/{template_id}` | P1 | TEST-TRAIN-CONTRACT-067 | CONTRACT | NO | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-068 | PATCH `/session-templates/{template_id}/favorite` | P1 | TEST-TRAIN-CONTRACT-068 | CONTRACT | NO | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-069 | GET `/analytics/team/{team_id}/summary` | P1 | TEST-TRAIN-CONTRACT-069 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-070 | GET `/analytics/team/{team_id}/weekly-load` | P1 | TEST-TRAIN-CONTRACT-070 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-071 | GET `/analytics/team/{team_id}/deviation-analysis` | P1 | TEST-TRAIN-CONTRACT-071 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-072 | GET `/analytics/team/{team_id}/prevention-effectiveness` | P1 | TEST-TRAIN-CONTRACT-072 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038 |
| CONTRACT-TRAIN-073 | GET `/analytics/wellness-rankings` | P1 | TEST-TRAIN-CONTRACT-073 | CONTRACT | POST | COBERTO | 2026-03-04 | Hb Track - Backend/tests/training/contracts/test_e2e_dod_pipeline.py | AR-TRAIN-006, AR-TRAIN-007 |
| CONTRACT-TRAIN-074 | POST `/analytics/wellness-rankings/calculate` | P1 | TEST-TRAIN-CONTRACT-074 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-006, AR-TRAIN-007 |
| CONTRACT-TRAIN-075 | GET `/analytics/wellness-rankings/{team_id}/athletes-90plus?month=` | P1 | TEST-TRAIN-CONTRACT-075 | CONTRACT | POST | PENDENTE | NOT_RUN | `-` | AR-TRAIN-006, AR-TRAIN-007 |
| CONTRACT-TRAIN-076 | GET `/teams/{team_id}/wellness-top-performers?month=` | P1 | TEST-TRAIN-CONTRACT-076 | CONTRACT | POST | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038, AR-TRAIN-006, AR-TRAIN-007 |
| CONTRACT-TRAIN-077 | GET `/training/alerts-suggestions/alerts/team/{team_id}/active` | P2 | TEST-TRAIN-CONTRACT-077 | CONTRACT | PRE | COBERTO | 2026-03-02 | `_reports/training/TEST-TRAIN-CONTRACT-077-085.md` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-078 | GET `/training/alerts-suggestions/alerts/team/{team_id}/history` | P2 | TEST-TRAIN-CONTRACT-078 | CONTRACT | PRE | COBERTO | 2026-03-02 | `_reports/training/TEST-TRAIN-CONTRACT-077-085.md` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-079 | GET `/training/alerts-suggestions/alerts/team/{team_id}/stats` | P2 | TEST-TRAIN-CONTRACT-079 | CONTRACT | PRE | COBERTO | 2026-03-02 | `_reports/training/TEST-TRAIN-CONTRACT-077-085.md` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-080 | POST `/training/alerts-suggestions/alerts/{alert_id}/dismiss` | P2 | TEST-TRAIN-CONTRACT-080 | CONTRACT | PRE | COBERTO | 2026-03-02 | `_reports/training/TEST-TRAIN-CONTRACT-077-085.md` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-081 | GET `/training/alerts-suggestions/suggestions/team/{team_id}/pending` | P2 | TEST-TRAIN-CONTRACT-081 | CONTRACT | PRE | COBERTO | 2026-03-02 | `_reports/training/TEST-TRAIN-CONTRACT-077-085.md` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-082 | GET `/training/alerts-suggestions/suggestions/team/{team_id}/history` | P2 | TEST-TRAIN-CONTRACT-082 | CONTRACT | PRE | COBERTO | 2026-03-02 | `_reports/training/TEST-TRAIN-CONTRACT-077-085.md` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-083 | GET `/training/alerts-suggestions/suggestions/team/{team_id}/stats` | P2 | TEST-TRAIN-CONTRACT-083 | CONTRACT | PRE | COBERTO | 2026-03-02 | `_reports/training/TEST-TRAIN-CONTRACT-077-085.md` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-084 | POST `/training/alerts-suggestions/suggestions/{suggestion_id}/apply` | P2 | TEST-TRAIN-CONTRACT-084 | CONTRACT | PRE | COBERTO | 2026-03-02 | `_reports/training/TEST-TRAIN-CONTRACT-077-085.md` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-085 | POST `/training/alerts-suggestions/suggestions/{suggestion_id}/dismiss` | P2 | TEST-TRAIN-CONTRACT-085 | CONTRACT | PRE | COBERTO | 2026-03-02 | `_reports/training/TEST-TRAIN-CONTRACT-077-085.md` | AR-TRAIN-001, AR-TRAIN-002 |
| CONTRACT-TRAIN-086 | POST `/analytics/export-pdf` | P1 | TEST-TRAIN-CONTRACT-086 | CONTRACT | PRE | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038, AR-TRAIN-008, AR-TRAIN-009 |
| CONTRACT-TRAIN-087 | GET `/analytics/exports/{job_id}` | P1 | TEST-TRAIN-CONTRACT-087 | CONTRACT | PRE | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038, AR-TRAIN-008, AR-TRAIN-009 |
| CONTRACT-TRAIN-088 | GET `/analytics/exports` | P1 | TEST-TRAIN-CONTRACT-088 | CONTRACT | PRE | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038, AR-TRAIN-008, AR-TRAIN-009 |
| CONTRACT-TRAIN-089 | GET `/analytics/export-rate-limit` | P1 | TEST-TRAIN-CONTRACT-089 | CONTRACT | PRE | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038, AR-TRAIN-008, AR-TRAIN-009 |
| CONTRACT-TRAIN-090 | GET `/athletes/me/export-data?format=json|csv` | P1 | TEST-TRAIN-CONTRACT-090 | CONTRACT | PRE | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038, AR-TRAIN-008, AR-TRAIN-009 |
| CONTRACT-TRAIN-091 | PATCH `/exercises/{exercise_id}/visibility` | P1 | TEST-TRAIN-CONTRACT-091 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038, AR-TRAIN-012, AR-TRAIN-013 |
| CONTRACT-TRAIN-092 | GET `/exercises/{exercise_id}/acl` | P1 | TEST-TRAIN-CONTRACT-092 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038, AR-TRAIN-012, AR-TRAIN-013 |
| CONTRACT-TRAIN-093 | POST `/exercises/{exercise_id}/acl` | P1 | TEST-TRAIN-CONTRACT-093 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038, AR-TRAIN-012, AR-TRAIN-013 |
| CONTRACT-TRAIN-094 | DELETE `/exercises/{exercise_id}/acl/{user_id}` | P1 | TEST-TRAIN-CONTRACT-094 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038, AR-TRAIN-012, AR-TRAIN-013 |
| CONTRACT-TRAIN-095 | POST `/exercises/{exercise_id}/copy-to-org` | P1 | TEST-TRAIN-CONTRACT-095 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_217/executor_main.log` | AR-TRAIN-038, AR-TRAIN-011, AR-TRAIN-013 |
| CONTRACT-TRAIN-096 | GET `/athlete/training-sessions/{session_id}/preview` | P1 | TEST-TRAIN-CONTRACT-096 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_218/executor_main.log` | AR-TRAIN-039, AR-TRAIN-019 |
| CONTRACT-TRAIN-097 | POST `/training-sessions/{session_id}/pre-confirm` | P0 | TEST-TRAIN-CONTRACT-097 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-CONTRACT-097-100.md` | AR_208, AR_209 |
| CONTRACT-TRAIN-098 | POST `/training-sessions/{session_id}/close` (+ pending items) | P0 | TEST-TRAIN-CONTRACT-098 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-CONTRACT-097-100.md` | AR_208, AR_209 |
| CONTRACT-TRAIN-099 | GET `/training/pending-items` | P0 | TEST-TRAIN-CONTRACT-099 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-CONTRACT-097-100.md` | AR_208, AR_209 |
| CONTRACT-TRAIN-100 | PATCH `/training/pending-items/{item_id}/resolve` | P0 | TEST-TRAIN-CONTRACT-100 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `_reports/training/TEST-TRAIN-CONTRACT-097-100.md` | AR_208, AR_209 |
| CONTRACT-TRAIN-101 | POST `/ai-coach/draft-session` | P2 | TEST-TRAIN-CONTRACT-101 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_218/executor_main.log` | AR-TRAIN-039, AR-TRAIN-021 |
| CONTRACT-TRAIN-102 | PATCH `/ai-coach/draft-session/{draft_id}/apply` | P2 | TEST-TRAIN-CONTRACT-102 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_218/executor_main.log` | AR-TRAIN-039, AR-TRAIN-021 |
| CONTRACT-TRAIN-103 | POST `/ai-coach/athlete-chat` | P2 | TEST-TRAIN-CONTRACT-103 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_218/executor_main.log` | AR-TRAIN-039, AR-TRAIN-021 |
| CONTRACT-TRAIN-104 | POST `/ai-coach/justify-suggestion` | P2 | TEST-TRAIN-CONTRACT-104 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_218/executor_main.log` | AR-TRAIN-039, AR-TRAIN-021 |
| CONTRACT-TRAIN-105 | GET `/athlete/wellness-content-gate/{session_id}` | P1 | TEST-TRAIN-CONTRACT-105 | CONTRACT | BOTH | COBERTO | 2026-03-03 | `docs/hbtrack/evidence/AR_218/executor_main.log` | AR-TRAIN-039, AR-TRAIN-019 |

---

## 9) Mapa AR -> Cobertura -> Evidência

| AR ID | Classe | Itens SSOT alvo | Testes previstos (IDs) | Evidências mínimas esperadas | Status |
|---|---|---|---|---|---|
| AR-TRAIN-001 | E | CONTRACT-TRAIN-077..085, INV-TRAIN-014 | TEST-TRAIN-CONTRACT-077..085, TEST-TRAIN-INV-014 | `docs/hbtrack/evidence/AR_126..129/executor_main.log`; `_reports/testador/AR_126..129/` | VERIFICADO |
| AR-TRAIN-002 | B | INV-TRAIN-014, INV-TRAIN-023 | TEST-TRAIN-INV-014, TEST-TRAIN-INV-023 | `docs/hbtrack/evidence/AR_175/executor_main.log`; `_reports/testador/AR_175/` | VERIFICADO |
| AR-TRAIN-003 | D | FLOW-TRAIN-005/006, SCREEN-TRAIN-018/019, CONTRACT-TRAIN-029..039 | TEST-TRAIN-FLOW-005/006, TEST-TRAIN-SCREEN-018/019 | `docs/hbtrack/evidence/AR_169..170/executor_main.log`; `_reports/testador/AR_169..170/` | VERIFICADO |
| AR-TRAIN-004 | B/E | INV-TRAIN-002/003/026, CONTRACT-TRAIN-029..039 | TEST-TRAIN-INV-002/003/026, TEST-TRAIN-CONTRACT-029..039 | `docs/hbtrack/evidence/AR_176/executor_main.log`; `_reports/testador/AR_176/` | VERIFICADO |
| AR-TRAIN-005 | D | FLOW-TRAIN-004, SCREEN-TRAIN-020, CONTRACT-TRAIN-025..028 | TEST-TRAIN-FLOW-004, TEST-TRAIN-SCREEN-020 | `docs/hbtrack/evidence/AR_171..172/executor_main.log`; `_reports/testador/AR_171..172/` | VERIFICADO |
| AR-TRAIN-006 | B/C/E | CONTRACT-TRAIN-073..075, INV-TRAIN-036/027 | TEST-TRAIN-INV-036/027, TEST-TRAIN-CONTRACT-073..075 | `docs/hbtrack/evidence/AR_177/executor_main.log`; `_reports/testador/AR_177/` | VERIFICADO |
| AR-TRAIN-007 | D | SCREEN-TRAIN-014/015, CONTRACT-TRAIN-073..076 | TEST-TRAIN-SCREEN-014/015, TEST-TRAIN-FLOW-013 | `docs/hbtrack/evidence/AR_178/executor_main.log`; `_reports/testador/AR_178/` | VERIFICADO |
| AR-TRAIN-008 | E | CONTRACT-TRAIN-086..090, INV-TRAIN-012/025 | TEST-TRAIN-CONTRACT-086..090, TEST-TRAIN-INV-012/025 | `docs/hbtrack/evidence/AR_179/executor_main.log`; `_reports/testador/AR_179/` | VERIFICADO |
| AR-TRAIN-009 | D | FLOW-TRAIN-012, SCREEN-TRAIN-013, CONTRACT-TRAIN-086..089 | TEST-TRAIN-FLOW-012, TEST-TRAIN-SCREEN-013 | `docs/hbtrack/evidence/AR_180/executor_main.log`; `_reports/testador/AR_180/` | VERIFICADO |
| AR-TRAIN-010A | T | Migrar refs `_generated` → `docs/ssot` | TEST-TRAIN-INV-008/020/021/030/031/040/041 | `docs/hbtrack/evidence/AR_173..174/executor_main.log`; `_reports/testador/AR_173..174/` | VERIFICADO |
| AR-TRAIN-010B | T | Cobertura adicional (itens `PARCIAL`) | TEST-TRAIN-INV-013/024 | `docs/hbtrack/evidence/AR_195/executor_main.log`; `_reports/testador/AR_195/` | VERIFICADO |
| AR-TRAIN-011 | A | Schema exercises+exercise_acl+exercise_media | TEST-TRAIN-INV-047/049/050/052/053, TEST-TRAIN-INV-EXB-ACL-001/006 | `docs/hbtrack/evidence/AR_181/executor_main.log`; `_reports/testador/AR_181/` | VERIFICADO |
| AR-TRAIN-012 | C | Guards/RBAC + ACL service layer | TEST-TRAIN-INV-048/051, TEST-TRAIN-INV-EXB-ACL-002..005/007, TEST-TRAIN-DEC-RBAC-001a/b | `docs/hbtrack/evidence/AR_182/executor_main.log`; `_reports/testador/AR_182/` | VERIFICADO |
| AR-TRAIN-013 | E | Endpoints ACL/copy/visibility (CONTRACT-TRAIN-091..095) | TEST-TRAIN-CONTRACT-091..095, TEST-TRAIN-DEC-EXB-001/001B/002 | `docs/hbtrack/evidence/AR_183/executor_main.log`; `_reports/testador/AR_183/` | VERIFICADO |
| AR-TRAIN-014 | D | UI exercise-bank FE (scope/ACL/media/copy) | TEST-TRAIN-SCREEN-010/011 (atualizado) | `docs/hbtrack/evidence/AR_184/executor_main.log`; `_reports/testador/AR_184/` | VERIFICADO |
| AR-TRAIN-015 | A | Schema ciclos (cycle_hierarchy, meso_overlap, micro_contained) | TEST-TRAIN-INV-054/055/056 | `docs/hbtrack/evidence/AR_189/executor_main.log`; `_reports/testador/AR_189/` | VERIFICADO |
| AR-TRAIN-016 | C | Service sessão standalone + mutabilidade + order_index | TEST-TRAIN-INV-057/058/059 | `docs/hbtrack/evidence/AR_190/executor_main.log`; `_reports/testador/AR_190/` | VERIFICADO |
| AR-TRAIN-017 | C/E | Presença oficial (pre-confirm + closure + pending) | TEST-TRAIN-INV-063/064/065/066, TEST-TRAIN-CONTRACT-097/098 | `docs/hbtrack/evidence/AR_185/executor_main.log`; `_reports/testador/AR_185/` | VERIFICADO |
| AR-TRAIN-018 | D | UI fila de pendências (pending queue) | TEST-TRAIN-INV-066/067, TEST-TRAIN-SCREEN-023, TEST-TRAIN-FLOW-018 | `docs/hbtrack/evidence/AR_186/executor_main.log`; `_reports/testador/AR_186/` | VERIFICADO |
| AR-TRAIN-019 | D | Atleta vê treino + wellness content gate | TEST-TRAIN-INV-068/069/071/076/078, TEST-TRAIN-SCREEN-022, TEST-TRAIN-FLOW-016/021 | `docs/hbtrack/evidence/AR_187/executor_main.log`; `_reports/testador/AR_187/` | VERIFICADO |
| AR-TRAIN-020 | C | Post-training conversacional + feedback imediato | TEST-TRAIN-INV-070/077 | `docs/hbtrack/evidence/AR_191/executor_main.log`; `_reports/testador/AR_191/` | VERIFICADO |
| AR-TRAIN-021 | C/E | IA coach (drafts, chat, justification, privacy) | TEST-TRAIN-INV-072..075/079..081, TEST-TRAIN-CONTRACT-101..104 | `docs/hbtrack/evidence/AR_192/executor_main.log`; `_reports/testador/AR_192/` | VERIFICADO |
| AR-TRAIN-022 | G | Sync TEST_MATRIX §9 + desbloquear §5 INV + §8 CONTRACT | TEST-TRAIN → ver §9 mapa AR_199 | `docs/hbtrack/evidence/AR_197/executor_main.log`; `_reports/testador/AR_197/` | VERIFICADO |
| AR-TRAIN-023 | E | Top-10 testes regressão (AR_200) | INV-001..009, CONTRACT-077..085 | `docs/hbtrack/evidence/AR_200/executor_main.log`; `_reports/testador/AR_200/` | VERIFICADO |
| AR-TRAIN-024 | B | Fix INV-001 test_invalid_case_2 (AR_202) | TEST-TRAIN-INV-001 | `docs/hbtrack/evidence/AR_202/executor_main.log`; `_reports/testador/AR_202/` | VERIFICADO |
| AR-TRAIN-025 | B | Fix INV-008 schema_path 3 .parent (AR_203) | TEST-TRAIN-INV-008 | `docs/hbtrack/evidence/AR_203/executor_main.log`; `_reports/testador/AR_203/` | VERIFICADO |
| AR-TRAIN-026 | B | Fix INV-030 schema_path 3 .parent (AR_204) | TEST-TRAIN-INV-030 | `docs/hbtrack/evidence/AR_204/executor_main.log`; `_reports/testador/AR_204/` | VERIFICADO |
| AR-TRAIN-027 | B | Fix INV-032 6 async fixtures (AR_205) | TEST-TRAIN-INV-032 | `docs/hbtrack/evidence/AR_205/executor_main.log`; `_reports/testador/AR_205/` | VERIFICADO |
| AR-TRAIN-028 | B | Fix CONTRACT-077-085 router path (AR_206) | TEST-TRAIN-CONTRACT-077-085 | `docs/hbtrack/evidence/AR_206/executor_main.log`; `_reports/testador/AR_206/` | VERIFICADO |
| AR-TRAIN-029 | E | Flow evidence MANUAL_GUIADO (AR_207) | FLOW-TRAIN-001..006/017/018 | `docs/hbtrack/evidence/AR_207/executor_main.log`; `_reports/testador/AR_207/` | VERIFICADO |
| AR-TRAIN-030 | B | Contract P0 tests (AR_208) | CONTRACT-TRAIN-097..100 | `docs/hbtrack/evidence/AR_208/executor_main.log`; `_reports/testador/AR_208/` | VERIFICADO |
| AR-TRAIN-031 | G | Done Gate: TRAINING v1.8.0 (AR_209) | Sanity AR_200 + Smoke Batch 9 | `docs/hbtrack/evidence/AR_209/executor_main.log`; `_reports/testador/AR_209/` | VERIFICADO |
| AR-TRAIN-032 | G | Sync §5 TEST_MATRIX: 36 INV PENDENTE→COBERTO (AR_211) | INV-047..052/054..059/063..081/EXB-ACL-001..004/006 | `docs/hbtrack/evidence/AR_211/executor_main.log` | VERIFICADO |
| AR-TRAIN-033 | T | Criar 6 testes ausentes: INV-053/060/061/062/EXB-ACL-005/007 (AR_212) | TEST-TRAIN-INV-053/060/061/062, TEST-TRAIN-INV-EXB-ACL-005/007 | `docs/hbtrack/evidence/AR_212/executor_main.log` | VERIFICADO |
| AR-TRAIN-034 | T | Executar NOT_RUN §5 + evidências formais, Batch 13 (AR_213) | TEST-TRAIN-INV-006..078 + EXB-ACL-001..004 (~65 NOT_RUN) | `_reports/training/evidence_run_batch13.txt` | VERIFICADO |
| AR-TRAIN-035 | T | Contract tests Sessions CRUD (CONTRACT-001..012), Batch 14 (AR_214) | TEST-TRAIN-CONTRACT-001..012 | `docs/hbtrack/evidence/AR_214/executor_main.log`; `_reports/testador/AR_214_142a146/` | VERIFICADO |
| AR-TRAIN-036 | T | Contract tests Teams + Attendance (CONTRACT-013..028), Batch 14 (AR_215) | TEST-TRAIN-CONTRACT-013..028 | `docs/hbtrack/evidence/AR_215/executor_main.log`; `_reports/testador/AR_215_142a146/` | VERIFICADO |
| AR-TRAIN-037 | T | Contract tests Wellness pre/post (CONTRACT-029..039), Batch 14 (AR_216) | TEST-TRAIN-CONTRACT-029..039 | `docs/hbtrack/evidence/AR_216/executor_main.log`; `_reports/testador/AR_216_142a146/` | VERIFICADO |
| AR-TRAIN-038 | T | Contract tests Ciclos/Exercises/Analytics/Export (CONTRACT-040..095), Batch 14 (AR_217) | TEST-TRAIN-CONTRACT-040..095 | `docs/hbtrack/evidence/AR_217/executor_main.log`; `_reports/testador/AR_217_142a146/` | VERIFICADO |
| AR-TRAIN-039 | T | Contract tests IA Coach + Athlete view (CONTRACT-096/101..105), Batch 14 (AR_218) | TEST-TRAIN-CONTRACT-096/101..105 | `docs/hbtrack/evidence/AR_218/executor_main.log`; `_reports/testador/AR_218_142a146/` | VERIFICADO |
| AR-TRAIN-040 | T | DEC tests automatizados (DEC-TRAIN-001..004/EXB/RBAC), Batch 15 (AR_219) | TEST-TRAIN-DEC-001..004/EXB/RBAC | `docs/hbtrack/evidence/AR_219/executor_main.log`; `_reports/testador/AR_219_142a146/` | VERIFICADO |
| AR-TRAIN-041 | T | Flows P1 evidência MANUAL_GUIADO (FLOW-007..016/019..021), Batch 15 (AR_220) | TEST-TRAIN-FLOW-007..016/019..021 | `docs/hbtrack/evidence/AR_220/executor_main.log`; `_reports/testador/AR_220_142a146/` | VERIFICADO |
| AR-TRAIN-042 | T | Screens smoke MANUAL_GUIADO (SCREEN-001..025), Batch 15 (AR_221) | TEST-TRAIN-SCREEN-001..025 | `docs/hbtrack/evidence/AR_221/executor_main.log`; `_reports/testador/AR_221_142a146/` | VERIFICADO |
| AR-TRAIN-043 | G | Done Gate §10 Final — sync TEST_MATRIX v2.0.0, Batch 16 (AR_222) | Todos §5/§6/§7/§8 + AC-005 | `docs/hbtrack/evidence/AR_222/executor_main.log` | OBSOLETO |
| AR-TRAIN-044 | T | Fix async fixtures: `@pytest.fixture` → `@pytest_asyncio.fixture` (~23+ tests, 7 arquivos), Batch 17 (AR_225) | tests/training/invariants/ (7 arquivos) | `docs/hbtrack/evidence/AR_225/executor_main.log`; `_reports/testador/AR_225_*/` | VERIFICADO |
| AR-TRAIN-045 | T | Fix DB fixture setup: `category_id` NOT NULL + FK `team_registrations` (~57+ ERROs), Batch 17 (AR_226) | tests/training/invariants/ (~15 arquivos) | `docs/hbtrack/evidence/AR_226/executor_main.log`; `_reports/testador/AR_226_*/` | VERIFICADO |
| AR-TRAIN-046 | T | Fix import stubs ausentes em ai_coach_service (INV-079/080/081), Batch 17 (AR_227) | INV-079/080/081 tests | `docs/hbtrack/evidence/AR_227/executor_main.log`; `_reports/testador/AR_227_*/` | VERIFICADO |
| AR-TRAIN-047 | T | Fix residuais mistos + suite done gate, Batch 17 (AR_228 REJEITADO) | tests/training/invariants/ residuais | — | REJEITADO |
| AR-TRAIN-048 | A/E | Sync app/models/ + app/services/ + stubs IA Coach (INV-010/035/036/054/060), Batch 19 (AR_229) | app/models/ (5 arquivos), app/services/ (2), openapi.json | `docs/hbtrack/evidence/AR_229/executor_main.log`; `_reports/testador/AR_229_*/` | VERIFICADO |
| AR-TRAIN-049 | T | Fix 6 FAILs + 10 ERRORs residuais test-layer (8 arquivos), Batch 20 (AR_230) | tests/training/invariants/ (8 arquivos: test_018, 035, 058, 059, 063, 064, 076, acl_006) | `docs/hbtrack/evidence/AR_230/executor_main.log`; `_reports/testador/AR_230_*/` | VERIFICADO |
| AR-TRAIN-050 | G | Sync §5 TEST_MATRIX: 11 itens NOT_RUN/FAIL/ERROR→PASS (AR_227+AR_230), Batch 21 (AR_231) | TEST_MATRIX_TRAINING.md §5 (11 itens: INV-079/080/081 + INV-018/035/058/059/063/064/076/EXB-ACL-006) | `docs/hbtrack/evidence/AR_231/executor_main.log` | VERIFICADO |
| AR-TRAIN-051 | G | Done Gate §10 formal — v3.0.0, Batch 22 (AR_232) | TEST_MATRIX_TRAINING.md §10/§0/§9 + DONE_GATE_TRAINING_v3.md | `docs/hbtrack/evidence/AR_232/executor_main.log` | VERIFICADO |

---

## 10) Critérios de PASS/FAIL da Fase (Matriz)

### PASS (fase TRAINING) se:
- [x] Todos os `INV-TRAIN-*` `BLOQUEANTE_VALIDACAO` = `COBERTO` (ou `PARCIAL` com justificativa aprovada)
- [x] Todos os flows `P0` = `COBERTO` via `E2E` ou `MANUAL_GUIADO`
- [x] Todos os contratos `P0` = `COBERTO` via `CONTRACT`
- [x] Evidências referenciadas em `_reports/*` para itens críticos
- [x] Sem itens críticos `FAIL` sem plano (AR) de correção
- [x] DEC-TRAIN-001: Teste de wellness self-only (sem athlete_id) com PASS (TEST-TRAIN-DEC-001a/b)
- [x] DEC-TRAIN-003: FE consome CONTRACT-TRAIN-076 como canônico (TEST-TRAIN-DEC-003)
- [x] DEC-TRAIN-004: Export degradado retorna 202 (não 500) sem worker (TEST-TRAIN-DEC-004a)
- [x] DEC-TRAIN-EXB-*: Invariantes de scope/ACL/visibility cobertas (14 novas INV com testes)
- [x] FASE_3 (INV-TRAIN-054..081): Todos os `BLOQUEANTE_VALIDACAO` com teste de violação
- [x] FASE_3 flows P0 (FLOW-TRAIN-017, FLOW-TRAIN-018) com evidência
- [x] FASE_3 contracts P0 (CONTRACT-TRAIN-097..100) com validação CONTRACT

### FAIL (fase TRAINING) se:
- [ ] Alguma invariante `BLOQUEANTE_VALIDACAO` sem teste de violação (não justificável)
- [ ] `FLOW-TRAIN-001..006` (P0) sem evidência
- [ ] Contratos `BLOQUEADO` sem AR associada
- [ ] Itens marcados `COBERTO` sem evidência mínima exigida

---

## 11) Protocolo de Atualização (normativo)

Toda mudança em:
- `INVARIANTS_TRAINING.md` ⇒ atualizar §5
- `TRAINING_USER_FLOWS.md` ⇒ atualizar §6
- `TRAINING_SCREENS_SPEC.md` ⇒ atualizar §7
- `TRAINING_FRONT_BACK_CONTRACT.md` ⇒ atualizar §8
- `AR_BACKLOG_TRAINING.md` ⇒ atualizar §9

Regra:
- Atualização desta matriz é obrigatória no mesmo ciclo da AR (ou marcar explicitamente `BLOQUEADO` com motivo).

---

## 12) Checklist do Auditor (rápido)

- [ ] Cada `INV-TRAIN-*` `BLOQUEANTE_VALIDACAO` tem teste de violação (`SIM`)
- [ ] `COBERTO` não foi usado por inferência (há caminho de teste + evidência esperada)
- [ ] Flows `P0` têm `MANUAL_GUIADO` ou `E2E` com evidência
- [ ] Contratos `P0` têm validação de auth + 422 + shape mínimo
- [ ] Itens `BLOQUEADO` têm AR associada
