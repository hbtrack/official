# AR_BACKLOG_TRAINING.md — Backlog de ARs (Materialização) do Módulo TRAINING

Status: DRAFT  
Versão: v1.0.0  
Tipo de Documento: AR Materialization Backlog (Normativo Operacional / SSOT)  
Módulo: TRAINING  
Fase: FASE_2 (PRD v2.2 — 2026-02-20)  
Autoridade: NORMATIVO_OPERACIONAL  
Owners:
- Arquitetura (Arquiteto): Codex (Arquiteto v2.2.0)
- Execução (Executor): (a definir)
- Auditoria/Testes: (a definir)

Última revisão: 2026-02-25  
Próxima revisão recomendada: 2026-03-04  

Dependências:
- `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
- `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md`
- `docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md`
- `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`

---

## 0) Auditoria AS-IS (Resumo) — 2026-02-25

### 0.1 O que está evidenciado (alto nível)
- **Training sessions**: CRUD + workflow (publish/close/duplicate/restore) exposto via `/api/v1/training-sessions/*` e rotas scoped `/api/v1/teams/{team_id}/trainings/*`.
- **Session exercises**: add/bulk/reorder/update/remove exposto sob `/api/v1/training-sessions/*/exercises*` (suporta DnD).
- **Attendance**: endpoints expostos sob `/api/v1/training_sessions/{id}/attendance*` (underscore).
- **Wellness pré/pós**: endpoints expostos sob `/api/v1/wellness-pre/*` e `/api/v1/wellness-post/*` (com subpaths underscore).
- **Ciclos/microciclos**: endpoints expostos sob `/api/v1/training-cycles/*` e `/api/v1/training-microcycles/*`.
- **Analytics**: endpoints expostos sob `/api/v1/analytics/team/{team_id}/*` e prevenção `/prevention-effectiveness`.
- **Banco de exercícios**: endpoints expostos sob `/api/v1/exercises`, `/exercise-tags`, `/exercise-favorites`.
- **Templates de sessão**: endpoints expostos sob `/api/v1/session-templates/*`.
- **Frontend admin training**: `/training/agenda`, `/planejamento`, `/exercise-bank`, `/analytics`, `/rankings`, `/eficacia-preventiva`, `/configuracoes`, `/relatorio/[sessionId]`, `/sessions/[id]/edit`.

### 0.2 O que está parcial/bloqueado (alto nível)
- **Presenças (UI)**: `/training/presencas` é placeholder; componente `AttendanceTab` existe mas não está integrado.
- **Wellness (FE)**: `src/lib/api/wellness.ts` aponta para endpoints incorretos; formulário não está alinhado ao schema (faltam campos e tipos).
- **Rankings (FE/BE)**: FE tipa `team_id`/`athlete_id` como `number`; BE tem endpoints com response_model ausente e services com trechos legados.
- **Alertas/Sugestões Step 18**: endpoints expostos, mas **IDs em path tipados como int** conflitam com DB `uuid` (alert_id, suggestion_id, team_id).
- **Exports/LGPD export**: routers existem (`exports.py`, `athlete_export.py`) mas estão **desabilitados** no agregador v1 ⇒ não aparecem no OpenAPI SSOT e bloqueiam o fluxo de export.
- **Testes invariants**: parte referencia `docs/_generated/*` (inexistente); SSOT atual está em `Hb Track - Backend/docs/ssot/*`.

---

## 1) Mapa: Evidência vs Hipótese

| Item | Descrição | Status | Evidência mínima |
|---|---|---|---|
| EVID-TRAIN-001 | Sessões de treino CRUD+workflow | EVIDENCIADO | `app/api/v1/routers/training_sessions.py`, `openapi.json` |
| EVID-TRAIN-002 | Presença (endpoints) | EVIDENCIADO | `app/api/v1/routers/attendance.py`, `openapi.json` |
| EVID-TRAIN-003 | Presença (UI) | PARCIAL | `AttendanceTab.tsx` existe; `/training/presencas` placeholder |
| EVID-TRAIN-004 | Wellness pré/pós (endpoints) | EVIDENCIADO | `routers/wellness_pre.py`, `routers/wellness_post.py` |
| EVID-TRAIN-005 | Wellness pré/pós (athlete UX) | PARCIAL | páginas existem, API FE divergente |
| EVID-TRAIN-006 | Planejamento ciclos/microciclos | EVIDENCIADO | `PlanejamentoClient.tsx` + routers cycles/microcycles |
| EVID-TRAIN-007 | Banco de exercícios + favoritos | EVIDENCIADO | `/training/exercise-bank` + routers exercises |
| EVID-TRAIN-008 | Templates de sessão | EVIDENCIADO | `/training/configuracoes` + `/session-templates` |
| EVID-TRAIN-009 | Analytics (team summary/load/deviation) | EVIDENCIADO | `routers/training_analytics.py` + FE analytics |
| EVID-TRAIN-010 | Rankings wellness (endpoints) | PARCIAL | endpoints expostos, mas sem schema e services legados |
| EVID-TRAIN-011 | Alertas/Sugestões Step 18 | DIVERGENTE_DO_SSOT | endpoints expostos com IDs int vs DB uuid |
| EVID-TRAIN-012 | Export PDF analytics | BLOQUEADO | FE modal existe; router existe mas desabilitado |
| HIP-TRAIN-001 | Central UI de alertas/sugestões | HIPOTESE | não evidenciado no FE |
| HIP-TRAIN-002 | Lista “treinos de hoje” para atleta (US-002) | HIPOTESE | não evidenciado no FE (`/athlete/dashboard` não existe) |

---

## 2) Gaps (com severidade)

### Bloqueantes (P0)
- **GAP-TRAIN-001:** IDs `int` em Step18 (`team_id`, `alert_id`, `suggestion_id`) divergem do DB `uuid` e impedem UI confiável.  
  Alvos: `CONTRACT-TRAIN-077..085`, `INV-TRAIN-014`.
- **GAP-TRAIN-002:** Wellness FE chama endpoints errados e formulário pré não está alinhado ao schema (sem `sleep_hours`, campos divergentes).  
  Alvos: `SCREEN-TRAIN-018`, `CONTRACT-TRAIN-029..034`, `INV-TRAIN-002`.
- **GAP-TRAIN-003:** Serviços wellness para atleta dependem de resolução de `athlete_id` (há evidência de query por coluna inexistente em `Athlete`).  
  Alvos: `INV-TRAIN-026`, `FLOW-TRAIN-005/006`.
- **GAP-TRAIN-004:** UI de presenças não materializada; falta suporte a `justified` e semântica de `reason_absence` (DB).  
  Alvos: `SCREEN-TRAIN-020`, `CONTRACT-TRAIN-025..028`, `INV-TRAIN-030`.

### Não-bloqueantes (P1/P2)
- **GAP-TRAIN-005:** Rankings FE usa `team_id:number` e `parseInt`, mas SSOT é UUID; endpoints de drilldown têm response_model ausente.  
  Alvos: `SCREEN-TRAIN-014/015`, `CONTRACT-TRAIN-073..076`, `INV-TRAIN-036`.
- **GAP-TRAIN-006:** Exports/LGPD export routers existem mas estão desabilitados no agregador v1, bloqueando US-003 “Export PDF”.  
  Alvos: `CONTRACT-TRAIN-086..090`, `INV-TRAIN-012`, `INV-TRAIN-025`.
- **GAP-TRAIN-007:** Testes invariants referenciam `docs/_generated/*` ao invés do SSOT atual `docs/ssot/*`.  
  Alvos: `INV-TRAIN-040/041`, gates T.

---

## 3) Decisões pendentes (validação humana)

- **DEC-TRAIN-001:** Wellness (atleta): `athlete_id` deve ser inferido do token (recomendado) ou enviado no payload?  
  Impacto: simplifica FE e reduz risco de acesso indevido.
- **DEC-TRAIN-002:** Wellness pré UI: manter sliders atuais e mapear para campos do DB (ex.: `fatigue_level→fatigue_pre`, `mood/readiness→(stress_level/readiness_score)`), ou alterar UI para o schema “puro”?  
  Impacto: compatibilidade UX vs SSOT.
- **DEC-TRAIN-003:** Top performers: padronizar consumo em `CONTRACT-TRAIN-076` (teams) ou em `CONTRACT-TRAIN-075` (analytics drilldown)?  
  Impacto: duplicidade de endpoints e consistência.
- **DEC-TRAIN-004:** Reintroduzir exports no agregador exige Celery/worker ativo no ambiente alvo?  
  Impacto: UX/ops (polling vs job stuck).

---

## 4) Objetivo (Normativo)

Decompor a materialização do módulo TRAINING em ARs pequenas, rastreáveis, testáveis e auditáveis, com:
- alvos SSOT explícitos (`INV/FLOW/SCREEN/CONTRACT`),
- ACs binários,
- estratégia de validação (incluindo tentativa de violação para invariantes bloqueantes),
- ordem e dependências.

---

## 5) Classes de AR (Padrão)

- **A** — Banco/Persistência
- **B** — Regras de Domínio/Services
- **C** — Cálculo/Derivados/Determinismo
- **D** — Frontend/UX
- **E** — Contrato Front-Back / integração
- **T** — Testes/Gates/Paridade

---

## 6) Ordem sugerida (lotes)

### Lote 1 — Núcleo bloqueante (E/B/T)
1. AR-TRAIN-001 (E) — Convergir IDs UUID em Step18
2. AR-TRAIN-002 (B) — Corrigir implementação Step18 (alerts/suggestions)
3. AR-TRAIN-003 (D) — Corrigir Wellness FE (endpoints + payload)
4. AR-TRAIN-004 (B/E) — Corrigir wellness self-only (athlete_id) e simplificar payload
5. AR-TRAIN-005 (D) — Materializar presenças (justified + batch)

### Lote 2 — Paridade analytics/rankings (B/E/D)
6. AR-TRAIN-006 (B/C) — Corrigir cálculo e contratos de rankings wellness
7. AR-TRAIN-007 (D) — Corrigir Rankings/TopPerformers FE para UUID e endpoint canônico

### Lote 3 — Exports e gates (E/T/D)
8. AR-TRAIN-008 (E) — Reabilitar routers de export + atualizar OpenAPI SSOT
9. AR-TRAIN-009 (D) — Conectar ExportPDFModal ao backend reabilitado
10. AR-TRAIN-010 (T) — Ajustar testes invariants para SSOT atual e adicionar testes de contrato faltantes

---

## 7) Tabela resumo do backlog de ARs

| AR ID | Classe | Prioridade | Objetivo | Alvos SSOT | Dependências | Status |
|---|---|---|---|---|---|---|
| AR-TRAIN-001 | E | ALTA | Tipar IDs Step18 como UUID e alinhar contrato | CONTRACT-TRAIN-077..085, INV-TRAIN-014 | - | PENDENTE |
| AR-TRAIN-002 | B | ALTA | Tornar Step18 funcional com schema SSOT | INV-TRAIN-014, INV-TRAIN-023 | AR-TRAIN-001 | PENDENTE |
| AR-TRAIN-003 | D | ALTA | Corrigir Wellness FE (paths + payload schema) | FLOW-TRAIN-005/006, SCREEN-TRAIN-018/019, CONTRACT-TRAIN-029..039 | - | PENDENTE |
| AR-TRAIN-004 | B/E | ALTA | Corrigir wellness self-only (athlete_id) e payload mínimo | INV-TRAIN-002/003/026, CONTRACT-TRAIN-029..039 | AR-TRAIN-003 | PENDENTE |
| AR-TRAIN-005 | D | ALTA | Materializar UI de presenças (justified + batch) | FLOW-TRAIN-004, SCREEN-TRAIN-020, CONTRACT-TRAIN-025..028 | - | PENDENTE |
| AR-TRAIN-006 | B/C/E | MEDIA | Corrigir rankings wellness (cálculo + response_model) | CONTRACT-TRAIN-073..075, INV-TRAIN-036/027 | AR-TRAIN-004 | PENDENTE |
| AR-TRAIN-007 | D | MEDIA | Corrigir Rankings/TopPerformers FE (UUID + endpoint canônico) | SCREEN-TRAIN-014/015, CONTRACT-TRAIN-073..076 | AR-TRAIN-006 | PENDENTE |
| AR-TRAIN-008 | E | MEDIA | Reabilitar exports + atualizar OpenAPI SSOT | CONTRACT-TRAIN-086..090, INV-TRAIN-012/025 | - | PENDENTE |
| AR-TRAIN-009 | D | MEDIA | Conectar ExportPDFModal (polling + history + rate limit) | FLOW-TRAIN-012, SCREEN-TRAIN-013, CONTRACT-TRAIN-086..089 | AR-TRAIN-008 | PENDENTE |
| AR-TRAIN-010 | T | ALTA | Corrigir testes invariants para SSOT e cobrir gaps de contrato | INV-TRAIN-040/041, TEST_MATRIX_TRAINING | AR-TRAIN-001..009 | PENDENTE |

---

## 8) Template completo por AR (obrigatório)

> Abaixo, cada AR já vem pré-preenchida para execução por agentes (Executor/Testador).

### AR-TRAIN-001 — Convergir IDs UUID em Step18 (alerts/suggestions)

**Status:** PENDENTE  
**Classe:** E  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Tornar o contrato Step18 coerente com o DB SSOT, trocando IDs em path para UUID (team_id/alert_id/suggestion_id) e atualizando OpenAPI SSOT.

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-014

**Flows:**
- FLOW-TRAIN-015

**Screens:**
- SCREEN-TRAIN-021

**Contracts:**
- CONTRACT-TRAIN-077..085

#### 8.2 Tipo de mudança esperada
- [ ] API / Contrato
- [ ] Documentação MCP (ajuste)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** -

#### 8.4 Escopo de leitura (READ)
- `Hb Track - Backend/docs/ssot/schema.sql`
- `Hb Track - Backend/docs/ssot/openapi.json`
- `Hb Track - Backend/app/api/v1/routers/training_alerts_step18.py`
- `Hb Track - Backend/app/models/training_alert.py`
- `Hb Track - Backend/app/models/training_suggestion.py`

#### 8.5 Escopo de escrita (WRITE)
- `Hb Track - Backend/app/api/v1/routers/training_alerts_step18.py`
- `Hb Track - Backend/docs/ssot/openapi.json` (regenerar/atualizar)
- `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md` (ajuste se necessário)

#### 8.6 Fora do escopo / MUST NOT
- Não alterar schema do banco nesta AR.
- Não implementar UI.

#### 8.7 Acceptance Criteria (AC)
##### AC-001
**PASS:** OpenAPI SSOT define `team_id`, `alert_id`, `suggestion_id` como `string(uuid)` nas rotas Step18.  
**FAIL:** Qualquer um permanecer como `integer`.

##### AC-002
**PASS:** Rotas Step18 aceitam UUID em runtime (sem erro de validação do FastAPI).  
**FAIL:** 422 por tipo inválido ao passar UUID.

#### 8.8 Estratégia de validação
**validation_command (preferencial):**
```bash
cd "Hb Track - Backend" && pytest -q tests/training/invariants/test_inv_train_014_overload_alert_threshold.py
```

**Tentativa de violação:**
- Chamar endpoint Step18 com UUID em path; esperado: não falhar por parse/type.

#### 8.9 Evidências esperadas
- [ ] diff de router + OpenAPI SSOT atualizado
- [ ] output de teste/validação

---

### AR-TRAIN-002 — Corrigir Step18 (services/queries) para SSOT atual

**Status:** PENDENTE  
**Classe:** B  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Fazer Step18 (alerts/suggestions) operar sobre `training_alerts`/`training_suggestions` (UUID) e produzir listagens e ações apply/dismiss funcionais.

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-014
- INV-TRAIN-023

**Contracts:**
- CONTRACT-TRAIN-077..085

#### 8.3 Dependências
- AR-TRAIN-001

#### 8.7 AC binário
##### AC-001
**PASS:** `dismiss` de alert/suggestion atualiza `dismissed_at/applied_at` no registro correto (UUID).  
**FAIL:** 404 indevido ou update em registro incorreto.

##### AC-002
**PASS:** `GET active/pending` retorna lista vazia ou itens válidos sem erro SQL.  
**FAIL:** exceção por mismatch de tipo (UUID/int) ou consulta em coluna inexistente.

#### 8.8 Validação
```bash
cd "Hb Track - Backend" && pytest -q tests/training/invariants/test_inv_train_023_wellness_post_overload_alert_trigger.py
```

---

### AR-TRAIN-003 — Corrigir Wellness FE (paths + payload)

**Status:** PENDENTE  
**Classe:** D  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Alinhar `src/lib/api/wellness.ts` e formulários athlete ao contrato SSOT (`/wellness-pre|/wellness-post`) e ao payload mínimo canônico.

#### 8.1 Alvos SSOT
**Flows:**
- FLOW-TRAIN-005
- FLOW-TRAIN-006

**Screens:**
- SCREEN-TRAIN-018
- SCREEN-TRAIN-019

**Contracts:**
- CONTRACT-TRAIN-029..039

#### 8.4 READ
- `Hb Track - Frontend/src/lib/api/wellness.ts`
- `Hb Track - Frontend/src/components/training/wellness/*`
- `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md`

#### 8.5 WRITE
- `Hb Track - Frontend/src/lib/api/wellness.ts`
- `Hb Track - Frontend/src/components/training/wellness/WellnessPreForm.tsx`
- `Hb Track - Frontend/src/components/training/wellness/WellnessPostForm.tsx`

#### 8.7 AC binário
##### AC-001
**PASS:** `submitWellnessPre(sessionId, data)` faz POST em `/api/v1/wellness-pre/training_sessions/{sessionId}/wellness_pre`.  
**FAIL:** POST para `/wellness_pre` ou 404 por path incorreto.

##### AC-002
**PASS:** Form de wellness pré coleta `sleep_hours` e envia payload compatível com DB (`fatigue_pre`/`stress_level` etc).  
**FAIL:** payload sem `sleep_hours` ou com campos incompatíveis sem mapeamento.

#### 8.8 Validação
- Typecheck/build do FE (comando conforme toolchain do repo).
- Tentativa de violação: preencher após deadline deve produzir bloqueio (INV-TRAIN-002).

---

### AR-TRAIN-004 — Corrigir wellness self-only (athlete_id) e payload mínimo (backend)

**Status:** PENDENTE  
**Classe:** E  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Garantir que endpoints wellness aceitam payload mínimo (sem `organization_id/created_by_membership_id`) e que atleta consegue operar self-only de forma determinística.

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-002
- INV-TRAIN-003
- INV-TRAIN-026

**Contracts:**
- CONTRACT-TRAIN-029..039

#### 8.3 Dependências
- AR-TRAIN-003

#### 8.7 AC binário
##### AC-001
**PASS:** Atleta autenticado consegue submeter wellness sem informar `organization_id` e sem escolher `athlete_id` de terceiros.  
**FAIL:** 422 exigindo campos que o server pode inferir, ou permissões allow indevido.

##### AC-002
**PASS:** Staff lendo wellness de outros atletas registra `data_access_logs` (LGPD).  
**FAIL:** ausência de log em acesso staff.

#### 8.8 Validação
```bash
cd "Hb Track - Backend" && pytest -q tests/training/invariants/test_inv_train_026_lgpd_access_logging.py
```

---

### AR-TRAIN-005 — Materializar presenças (UI) com `justified`

**Status:** PENDENTE  
**Classe:** D  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Integrar UI de presenças ao módulo training (tab no editor ou página) suportando `present|absent|justified` e batch save.

#### 8.1 Alvos SSOT
**Flows:**
- FLOW-TRAIN-004

**Screens:**
- SCREEN-TRAIN-020

**Contracts:**
- CONTRACT-TRAIN-025..028

**Invariantes:**
- INV-TRAIN-030

#### 8.7 AC binário
##### AC-001
**PASS:** UI permite marcar `justified` e exigir `reason_absence` (UX), sem violar `ck_attendance_absent_reason_null`.  
**FAIL:** UI envia `reason_absence` com `absent` ou não permite `justified`.

##### AC-002
**PASS:** Batch save envia payload válido e atualiza estatísticas.  
**FAIL:** erro 409/422 por payload inválido.

---

### AR-TRAIN-006 — Corrigir rankings wellness (backend) + tipar response_model

**Status:** PENDENTE  
**Classe:** B  
**Prioridade:** MEDIA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Tornar `/analytics/wellness-rankings*` determinístico no schema SSOT (UUIDs, team_registrations, attendance.presence_status) e com response_model no OpenAPI.

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-036
- INV-TRAIN-027

**Contracts:**
- CONTRACT-TRAIN-073..075

#### 8.7 AC binário
##### AC-001
**PASS:** Endpoint retorna `team_id` UUID e taxas coerentes com `attendance(present|justified)` (definir regra) e `wellness_pre/post`.  
**FAIL:** uso de campos/tabelas legadas (`Attendance.present`, `Athlete.active`, `TeamMembership` para atletas).

---

### AR-TRAIN-007 — Corrigir Rankings/TopPerformers FE para UUID + endpoint canônico

**Status:** PENDENTE  
**Classe:** D  
**Prioridade:** MEDIA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Ajustar FE para tratar `team_id`/`athlete_id` como UUID strings e consumir endpoints canônicos.

#### 8.1 Alvos SSOT
**Screens:**
- SCREEN-TRAIN-014
- SCREEN-TRAIN-015

**Contracts:**
- CONTRACT-TRAIN-073..076

#### 8.7 AC binário
##### AC-001
**PASS:** `TopPerformersClient` não usa `parseInt` e funciona com UUID.  
**FAIL:** erro por `NaN`/type mismatch.

---

### AR-TRAIN-008 — Reabilitar exports + atualizar OpenAPI SSOT

**Status:** PENDENTE  
**Classe:** E  
**Prioridade:** MEDIA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Incluir routers de export no agregador v1 e atualizar `docs/ssot/openapi.json`.

#### 8.1 Alvos SSOT
**Contracts:**
- CONTRACT-TRAIN-086..090

**Invariantes:**
- INV-TRAIN-012
- INV-TRAIN-025

#### 8.7 AC binário
##### AC-001
**PASS:** OpenAPI SSOT passa a conter `/analytics/export-pdf`, `/analytics/exports*` e `/athletes/me/export-data`.  
**FAIL:** rotas continuam ausentes após reabilitar include_router.

---

### AR-TRAIN-009 — Conectar ExportPDFModal (polling + history + rate limit)

**Status:** PENDENTE  
**Classe:** D  
**Prioridade:** MEDIA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Fazer o modal de export consumir endpoints reabilitados e apresentar evidência de job concluído.

#### 8.1 Alvos SSOT
**Screen:**
- SCREEN-TRAIN-013

**Contracts:**
- CONTRACT-TRAIN-086..089

**Invariantes:**
- INV-TRAIN-012

---

### AR-TRAIN-010 — Testes/Gates: SSOT path + contratos críticos

**Status:** PENDENTE  
**Classe:** T  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Ajustar testes para SSOT atual (`docs/ssot`) e cobrir contratos críticos sem schema no OpenAPI.

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-040
- INV-TRAIN-041

**Contracts:**
- CONTRACT-TRAIN-073..075
- CONTRACT-TRAIN-077..085

#### 8.7 AC binário
##### AC-001
**PASS:** suite `Hb Track - Backend/tests/training/invariants/*` não depende de `docs/_generated/*`.  
**FAIL:** testes falham por arquivo inexistente.

---

## 9) Critérios PASS/FAIL (fase do módulo)

### PASS se (mínimo)
- [ ] Fluxos P0 (US-001/US-002) operacionais fim-a-fim (FE↔BE) com validação de invariantes bloqueantes
- [ ] Step18 sem divergência de IDs (UUID em contrato e runtime)
- [ ] Rankings e exports com contrato tipado (ou explicitamente DEFERIDO com justificativa aprovada)
- [ ] `TEST_MATRIX_TRAINING.md` atualizado com evidências

### FAIL se
- [ ] Invariante bloqueante sem teste de violação
- [ ] Contratos críticos expostos com drift (UUID/int) sem AR de correção
- [ ] UI principal chama endpoints inexistentes (404 sistemático)

