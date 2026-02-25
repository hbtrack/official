# AR_BACKLOG_TRAINING.md — Backlog de ARs (Materialização) do Módulo TRAINING

Status: DRAFT  
Versão: v1.2.0  
Tipo de Documento: AR Materialization Backlog (Normativo Operacional / SSOT)  
Módulo: TRAINING  
Fase: FASE_2 (PRD v2.2 — 2026-02-20) + DEC-TRAIN-* (2026-02-25)  
Autoridade: NORMATIVO_OPERACIONAL  
Owners:
- Arquitetura (Arquiteto): Codex (Arquiteto v2.2.0)
- Execução (Executor): (a definir)
- Auditoria/Testes: (a definir)

Última revisão: 2026-02-26  
Próxima revisão recomendada: 2026-03-04  

> Changelog v1.2.0 (2026-02-26):  
> - Adicionada Authority Matrix (separação Arquiteto/Executor/Testador)  
> - Adicionada convenção de Classification Tags  

> Changelog v1.1.0 (2026-02-25):  
> - DEC-TRAIN-001..004 movidas de PENDENTES para RESOLVIDAS  
> - Adicionadas DEC-TRAIN-EXB-001, DEC-TRAIN-EXB-001B, DEC-TRAIN-EXB-002, DEC-TRAIN-EXB-RBAC-001 como RESOLVIDAS  
> - AR-TRAIN-003/004 atualizadas com ACs de self-only e mapeamento FE→payload  
> - AR-TRAIN-007 atualizada com endpoint canônico CONTRACT-TRAIN-076  
> - AR-TRAIN-008/009 atualizadas com estado degradado sem worker  
> - Adicionadas AR-TRAIN-011..014 para Banco de Exercícios (scope/ACL/media/RBAC)  
> - Adicionados GAP-TRAIN-EXB-001..003  

Dependências:
- `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
- `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md`
- `docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md`
- `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`

---

## Authority Matrix

| Aspecto | Regra |
|---|---|
| Fonte de verdade | PRD + SSOT + Decisões humanas (DEC-*) |
| Escrita normativa | **Arquiteto** — criar, priorizar, definir escopo, ACs, dependências |
| Escrita de execução | **Executor** — atualizar status da AR em execução + evidências técnicas |
| Escrita de validação | **Testador** — atualizar status de validação/verificação da AR |
| Proposta de alteração | Qualquer papel → via GAP ou DEC ao Arquiteto |
| Precedência em conflito | Arquiteto (escopo/ACs) > Executor (implementação) > Testador (validação) |

---

## Convenção de Tags (Classification)

Cada item (AR-*, GAP-*, DEC-*, EVID-*, HIP-*) neste documento recebe classificação:

| Tag | Significado |
|---|---|
| `[NORMATIVO]` | AR/Regra aprovada que DEVE ser materializada. |
| `[DESCRITIVO-AS-IS]` | Evidência do estado atual do repo. |
| `[HIPOTESE]` | Expectativa do PRD não evidenciada. |
| `[GAP]` | Lacuna identificada. |

**Aplicação:** `EVID-*` = `[DESCRITIVO-AS-IS]`. `HIP-*` = `[HIPOTESE]`. `GAP-*` = `[GAP]`. `AR-*` com ACs aprovados = `[NORMATIVO]`. `DEC-*` = `[NORMATIVO]` quando resolvida.

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
| EVID-TRAIN-007B | Banco de exercícios (scope SYSTEM/ORG, ACL, visibilidade) | GAP | Decisões DEC-TRAIN-EXB-* aprovadas; schema/services não evidenciam scope/ACL |
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
### Gaps — Banco de Exercícios (novos, pós-decisões EXB)
- **GAP-TRAIN-EXB-001:** Schema/model de `exercises` não possui campo `scope` (SYSTEM|ORG) nem `visibility_mode` (org_wide|restricted). Decisões DEC-TRAIN-EXB-001/001B aprovadas mas não materializadas.  
  Alvos: `INV-TRAIN-047`, `INV-TRAIN-EXB-ACL-001`, `CONTRACT-TRAIN-053..056`.
- **GAP-TRAIN-EXB-002:** Tabela `exercise_acl` e tabela `exercise_media` não evidenciadas no schema atual. Necessárias para suportar ACL por usuário e mídias ricas.  
  Alvos: `INV-TRAIN-EXB-ACL-002..006`, `INV-TRAIN-052`.
- **GAP-TRAIN-EXB-003:** Service de exercícios não possui guards de escopo (`SYSTEM` imutável), visibilidade (`restricted` + ACL), nem RBAC explícito "Treinador".  
  Alvos: `INV-TRAIN-048`, `INV-TRAIN-051`, `INV-TRAIN-EXB-ACL-004`.
---

## 3) Decisões RESOLVIDAS (validação humana concluída)

### DEC-TRAIN-001 — Wellness self-only (RESOLVIDA)
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**  
- `athlete_id` DEVE ser inferido do token JWT pelo backend.  
- Cliente atleta NÃO envia `athlete_id` no payload de wellness.  
- Fluxo por staff/terceiros (se existir) DEVE ser endpoint/escopo separado com permissão explícita e auditoria (INV-TRAIN-026).  
**Impacto:** AR-TRAIN-003, AR-TRAIN-004, CONTRACT-TRAIN-029..039, FLOW-TRAIN-005/006, SCREEN-TRAIN-018/019.

### DEC-TRAIN-002 — Wellness UI (RESOLVIDA)
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**  
- Manter UX com sliders/componentes amigáveis ao atleta.  
- Mapear UI para payload canônico do backend.  
- O contrato DEVE conter tabela explícita de mapeamento FE→payload (ver TRAINING_FRONT_BACK_CONTRACT.md §4.4).  
- A matriz de testes DEVE conter testes normativos de mapeamento (ver TEST_MATRIX_TRAINING.md).  
**Impacto:** AR-TRAIN-003, CONTRACT-TRAIN-029..039, SCREEN-TRAIN-018/019, TEST_MATRIX.

### DEC-TRAIN-003 — Top performers endpoint canônico (RESOLVIDA)
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**  
- `CONTRACT-TRAIN-076` é o endpoint canônico único para consumo no frontend principal (listings).  
- `CONTRACT-TRAIN-075` permanece como endpoint especializado/derivado para drilldown analytics.  
- Frontend NÃO DEVE consumir ambos para a mesma funcionalidade; diferenciação documentada no contrato.  
**Impacto:** AR-TRAIN-007, CONTRACT-TRAIN-073..076, SCREEN-TRAIN-015, FLOW-TRAIN-013.

### DEC-TRAIN-004 — Exports worker obrigatório (RESOLVIDA)
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**  
- Fluxos assíncronos de export exigem worker/Celery ativo no ambiente.  
- Sem worker ativo, UI/contrato DEVE expor estado degradado explícito (indisponível), sem simular job funcional.  
- Polling fake (simular progresso sem worker) é PROIBIDO.  
**Impacto:** AR-TRAIN-008, AR-TRAIN-009, CONTRACT-TRAIN-086..090, SCREEN-TRAIN-013, FLOW-TRAIN-012.

### DEC-TRAIN-EXB-001 — Banco de Exercícios modelo base (RESOLVIDA)
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**  
- Banco de Exercícios do TRAINING é global por organização.  
- Exercícios possuem escopo `SYSTEM` (instalados) ou `ORG` (criados pela organização).  
- Usuários visualizam `SYSTEM` + `ORG` da própria organização (respeitando visibility/ACL).  
- Favoritos são por usuário (sem duplicar exercício).  
- Exercícios `SYSTEM` não são editáveis por usuários da organização.  
- Exercícios `ORG` podem conter fotos, vídeos, links externos (YouTube etc.).  
- Adaptar exercício `SYSTEM` → cria cópia `ORG` (não altera original).  
**Impacto:** INV-TRAIN-047..053, CONTRACT-TRAIN-053..062 + novos, FLOW-TRAIN-009, SCREEN-TRAIN-010/011.

### DEC-TRAIN-EXB-001B — Visibilidade ORG + ACL (RESOLVIDA)
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**  
- Exercícios `ORG` DEVEM suportar `visibility_mode` = `org_wide` ou `restricted`.  
- Em `restricted`, exercício visível ao criador + usuários explícitos na ACL.  
- ACL é por usuário individual (não por grupo/papel nesta fase).  
- Usuários na ACL DEVEM pertencer à mesma organização do exercício.  
- Apenas o treinador criador PODE gerenciar compartilhamento (ACL) e alterar `visibility_mode`.  
- Criador mantém acesso implícito independentemente da ACL.  
- Mudanças de ACL/visibilidade NÃO PODEM invalidar leitura de sessões históricas.  
- **Default para novos exercícios ORG: `org_wide`.**  
**Impacto:** INV-TRAIN-EXB-ACL-001..007, CONTRACT-TRAIN-091..095, SCREEN-TRAIN-010/011.

### DEC-TRAIN-EXB-002 — Capability aprovada (RESOLVIDA)
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**  
- Treinador PODE criar categorias, nomes e tags personalizadas de exercícios.  
- Exercícios `ORG` DEVEM suportar compartilhamento conforme DEC-TRAIN-EXB-001B.  
- Apenas o treinador criador PODE gerenciar ACL/visibilidade.  
- Refletir em Flows/Screens/Contracts/Testes e nas invariantes por restrições normativas.  
**Impacto:** FLOW-TRAIN-009, SCREEN-TRAIN-010/011, CONTRACT-TRAIN-053..062.

### DEC-TRAIN-EXB-RBAC-001 — Treinador como RBAC específico (RESOLVIDA)
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**  
- O termo “Treinador” DEVE ser tratado como papel RBAC específico (identificador explícito no contrato).  
- NÃO é categoria genérica inferida.  
- O MCP DEVE explicitar esse identificador RBAC nos trechos de permissão do Banco de Exercícios ORG (criar/editar/compartilhar/alterar visibilidade).  
**Impacto:** INV-TRAIN-EXB-ACL-004, CONTRACT-TRAIN-054/056/091..095, SCREEN-TRAIN-010/011.

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
7. AR-TRAIN-007 (D) — Corrigir Rankings/TopPerformers FE para UUID e endpoint canônico (`CONTRACT-TRAIN-076`)

### Lote 3 — Exports e gates (E/T/D)
8. AR-TRAIN-008 (E) — Reabilitar routers de export + atualizar OpenAPI SSOT + estado degradado sem worker
9. AR-TRAIN-009 (D) — Conectar ExportPDFModal ao backend reabilitado + estado degradado
10. AR-TRAIN-010 (T) — Ajustar testes invariants para SSOT atual e adicionar testes de contrato faltantes

### Lote 4 — Banco de Exercícios (A/B/E/D) — novo pós DEC-TRAIN-EXB-*
11. AR-TRAIN-011 (A) — Materializar schema exercises (scope, visibility_mode) + tabelas exercise_acl e exercise_media
12. AR-TRAIN-012 (B/E) — Implementar guards de escopo SYSTEM/ORG + RBAC "Treinador" + service de ACL
13. AR-TRAIN-013 (B/E) — Implementar endpoints ACL + copy SYSTEM→ORG + visibilidade
14. AR-TRAIN-014 (D) — Materializar UI scope/visibility/ACL/mídia no exercise-bank FE

---

## 7) Tabela resumo do backlog de ARs

| AR ID | Classe | Prioridade | Objetivo | Alvos SSOT | Dependências | Status |
|---|---|---|---|---|---|---|
| AR-TRAIN-001 | E | ALTA | Tipar IDs Step18 como UUID e alinhar contrato | CONTRACT-TRAIN-077..085, INV-TRAIN-014 | - | PENDENTE |
| AR-TRAIN-002 | B | ALTA | Tornar Step18 funcional com schema SSOT | INV-TRAIN-014, INV-TRAIN-023 | AR-TRAIN-001 | PENDENTE |
| AR-TRAIN-003 | D | ALTA | Corrigir Wellness FE (paths + payload schema + self-only sem athlete_id) | FLOW-TRAIN-005/006, SCREEN-TRAIN-018/019, CONTRACT-TRAIN-029..039 | - | PENDENTE |
| AR-TRAIN-004 | B/E | ALTA | Corrigir wellness self-only (athlete_id inferido do token) e payload mínimo + mapeamento FE→payload | INV-TRAIN-002/003/026, CONTRACT-TRAIN-029..039 | AR-TRAIN-003 | PENDENTE |
| AR-TRAIN-005 | D | ALTA | Materializar UI de presenças (justified + batch) | FLOW-TRAIN-004, SCREEN-TRAIN-020, CONTRACT-TRAIN-025..028 | - | PENDENTE |
| AR-TRAIN-006 | B/C/E | MEDIA | Corrigir rankings wellness (cálculo + response_model) | CONTRACT-TRAIN-073..075, INV-TRAIN-036/027 | AR-TRAIN-004 | PENDENTE |
| AR-TRAIN-007 | D | MEDIA | Corrigir Rankings/TopPerformers FE (UUID + endpoint canônico CONTRACT-TRAIN-076) | SCREEN-TRAIN-014/015, CONTRACT-TRAIN-073..076 | AR-TRAIN-006 | PENDENTE |
| AR-TRAIN-008 | E | MEDIA | Reabilitar exports + atualizar OpenAPI SSOT + estado degradado sem worker | CONTRACT-TRAIN-086..090, INV-TRAIN-012/025 | - | PENDENTE |
| AR-TRAIN-009 | D | MEDIA | Conectar ExportPDFModal (polling + history + rate limit + estado degradado) | FLOW-TRAIN-012, SCREEN-TRAIN-013, CONTRACT-TRAIN-086..089 | AR-TRAIN-008 | PENDENTE |
| AR-TRAIN-010 | T | ALTA | Corrigir testes invariants para SSOT e cobrir gaps de contrato | INV-TRAIN-040/041, TEST_MATRIX_TRAINING | AR-TRAIN-001..009 | PENDENTE |
| AR-TRAIN-011 | A | ALTA | Materializar schema exercises (scope, visibility_mode) + exercise_acl + exercise_media | INV-TRAIN-047..053, INV-TRAIN-EXB-ACL-001/006 | - | PENDENTE |
| AR-TRAIN-012 | B/E | ALTA | Guards de escopo SYSTEM/ORG + RBAC "Treinador" + service ACL + visibilidade | INV-TRAIN-048/051, INV-TRAIN-EXB-ACL-002..005/007 | AR-TRAIN-011 | PENDENTE |
| AR-TRAIN-013 | B/E | MEDIA | Endpoints ACL + copy SYSTEM→ORG + toggle visibilidade | CONTRACT-TRAIN-091..095, INV-TRAIN-EXB-ACL-001..007 | AR-TRAIN-012 | PENDENTE |
| AR-TRAIN-014 | D | MEDIA | UI scope/visibility/ACL/mídia no exercise-bank FE | SCREEN-TRAIN-010/011, FLOW-TRAIN-009 | AR-TRAIN-013 | PENDENTE |

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
**Objetivo da AR (1 frase):** Alinhar `src/lib/api/wellness.ts` e formulários athlete ao contrato SSOT (`/wellness-pre|/wellness-post`), ao payload mínimo canônico e ao modelo self-only (sem `athlete_id` no payload do atleta).

#### 8.1 Alvos SSOT
**Flows:**
- FLOW-TRAIN-005
- FLOW-TRAIN-006

**Screens:**
- SCREEN-TRAIN-018
- SCREEN-TRAIN-019

**Contracts:**
- CONTRACT-TRAIN-029..039

**Decisões incorporadas:**
- DEC-TRAIN-001 (self-only: atleta não envia `athlete_id`)
- DEC-TRAIN-002 (mapeamento UI→payload canônico)

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

##### AC-003 (DEC-TRAIN-001)
**PASS:** Form de wellness pré/pós do atleta NÃO envia `athlete_id` no payload; backend infere do token.  
**FAIL:** payload contém campo `athlete_id` enviado pelo frontend atleta.

##### AC-004 (DEC-TRAIN-002)
**PASS:** Existe tabela documentada de mapeamento FE→payload canônico (UI slider → campo DB) no contrato.  
**FAIL:** Mapeamento ausente ou incompleto.

#### 8.8 Validação
- Typecheck/build do FE (comando conforme toolchain do repo).
- Tentativa de violação: preencher após deadline deve produzir bloqueio (INV-TRAIN-002).

---

### AR-TRAIN-004 — Corrigir wellness self-only (athlete_id) e payload mínimo (backend)

**Status:** PENDENTE  
**Classe:** E  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Garantir que endpoints wellness aceitam payload mínimo (sem `organization_id/created_by_membership_id`) e que atleta opera self-only com `athlete_id` inferido do token (DEC-TRAIN-001).

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
**Objetivo da AR (1 frase):** Ajustar FE para tratar `team_id`/`athlete_id` como UUID strings e consumir endpoint canônico `CONTRACT-TRAIN-076` para top performers no FE principal (DEC-TRAIN-003).

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
**Objetivo da AR (1 frase):** Incluir routers de export no agregador v1, atualizar `docs/ssot/openapi.json` e implementar estado degradado explícito quando worker/Celery não estiver ativo (DEC-TRAIN-004).

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

##### AC-002 (DEC-TRAIN-004)
**PASS:** Endpoint de export retorna estado degradado explícito (ex.: `{"status": "unavailable", "reason": "worker_not_active"}`) quando worker/Celery não está ativo.  
**FAIL:** Endpoint aceita job sem worker e simula polling fake.

---

### AR-TRAIN-009 — Conectar ExportPDFModal (polling + history + rate limit + estado degradado)

**Status:** PENDENTE  
**Classe:** D  
**Prioridade:** MEDIA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Fazer o modal de export consumir endpoints reabilitados, apresentar evidência de job concluído e exibir estado degradado explícito quando worker indisponível (DEC-TRAIN-004).

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

### AR-TRAIN-011 — Materializar schema exercises (scope, visibility_mode) + exercise_acl + exercise_media

**Status:** PENDENTE  
**Classe:** A  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Adicionar campos `scope`, `visibility_mode`, `created_by_user_id` à tabela `exercises` e criar tabelas `exercise_acl` e `exercise_media` com constraints conforme invariantes.

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-047 (scope válido)
- INV-TRAIN-049 (ORG single org)
- INV-TRAIN-050 (favorite unique)
- INV-TRAIN-052 (media type+ref válidos)
- INV-TRAIN-EXB-ACL-001 (visibility_mode válido)
- INV-TRAIN-EXB-ACL-006 (ACL unique per exercise+user)

**Decisões incorporadas:**
- DEC-TRAIN-EXB-001
- DEC-TRAIN-EXB-001B

#### 8.4 READ
- `Hb Track - Backend/docs/ssot/schema.sql`
- `Hb Track - Backend/app/models/exercise.py`

#### 8.5 WRITE
- `Hb Track - Backend/alembic/versions/` (nova migration)
- `Hb Track - Backend/app/models/exercise.py` (acrescentar campos)
- `Hb Track - Backend/app/models/exercise_acl.py` (novo)
- `Hb Track - Backend/app/models/exercise_media.py` (novo)
- `Hb Track - Backend/docs/ssot/schema.sql` (regenerar)

#### 8.6 MUST NOT
- Não alterar schema de outras tabelas.
- Não implementar services/endpoints nesta AR (apenas schema+models).

#### 8.7 AC binário
##### AC-001
**PASS:** Migration cria `exercises.scope` (enum SYSTEM|ORG), `exercises.visibility_mode` (enum org_wide|restricted, default org_wide), `exercises.created_by_user_id` (FK).  
**FAIL:** Campos ausentes ou sem constraint.

##### AC-002
**PASS:** Tabela `exercise_acl` existe com `(exercise_id FK, user_id FK)` e constraint unique.  
**FAIL:** Tabela ausente.

##### AC-003
**PASS:** Tabela `exercise_media` existe com `(exercise_id FK, media_type, reference)` e constraints de validação.  
**FAIL:** Tabela ausente.

#### 8.8 Validação
```bash
cd "Hb Track - Backend" && alembic upgrade head && python -c "from app.models.exercise import Exercise; print('OK')"
```

---

### AR-TRAIN-012 — Guards de escopo SYSTEM/ORG + RBAC "Treinador" + service ACL + visibilidade

**Status:** PENDENTE  
**Classe:** B/E  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Implementar guards de escopo (SYSTEM imutável, ORG org-bound), filtro de visibilidade (org_wide+restricted+ACL), RBAC explícito "Treinador", e service de ACL com validação anti-cross-org.

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-048 (SYSTEM imutável)
- INV-TRAIN-051 (catálogo respeita org)
- INV-TRAIN-EXB-ACL-002 (ACL apenas em restricted)
- INV-TRAIN-EXB-ACL-003 (anti-cross-org)
- INV-TRAIN-EXB-ACL-004 (autoridade do criador + RBAC)
- INV-TRAIN-EXB-ACL-005 (criador acesso implícito)
- INV-TRAIN-EXB-ACL-007 (ACL não retroquebra sessão)

**Decisões incorporadas:**
- DEC-TRAIN-EXB-001, DEC-TRAIN-EXB-001B, DEC-TRAIN-EXB-002, DEC-TRAIN-EXB-RBAC-001

#### 8.3 Dependências
- AR-TRAIN-011

#### 8.5 WRITE
- `Hb Track - Backend/app/services/exercise_service.py` (guards scope, visibility, creator)
- `Hb Track - Backend/app/services/exercise_acl_service.py` (novo)

#### 8.7 AC binário
##### AC-001
**PASS:** PATCH/DELETE em exercício `SYSTEM` por usuário da organização retorna 403.  
**FAIL:** Edição permitida.

##### AC-002
**PASS:** Listagem de exercícios para usuário da org X retorna apenas `SYSTEM` + `ORG` da org X, respeitando `visibility_mode` e ACL.  
**FAIL:** Exercícios de org Y visíveis.

##### AC-003
**PASS:** Adicionar user de org Y à ACL de exercício org X retorna 400/422 (validação anti-cross-org).  
**FAIL:** ACL aceita user cross-org.

##### AC-004
**PASS:** Treinador B (não criador) tenta alterar `visibility_mode` ou ACL de exercício de treinador A → 403.  
**FAIL:** Alteração permitida.

##### AC-005 (RBAC)
**PASS:** Guard de criação/edição de exercício ORG verifica papel RBAC explícito "Treinador" (identificador no contrato, não inferência genérica).  
**FAIL:** Guard usa verificação genérica ou ausente.

---

### AR-TRAIN-013 — Endpoints ACL + copy SYSTEM→ORG + toggle visibilidade

**Status:** PENDENTE  
**Classe:** B/E  
**Prioridade:** MEDIA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Expor endpoints de ACL (listar/adicionar/remover), toggle de `visibility_mode`, e cópia de exercício SYSTEM→ORG no router de exercises.

#### 8.1 Alvos SSOT
**Contracts:**
- CONTRACT-TRAIN-091 (PATCH visibility)
- CONTRACT-TRAIN-092 (GET ACL)
- CONTRACT-TRAIN-093 (POST ACL)
- CONTRACT-TRAIN-094 (DELETE ACL user)
- CONTRACT-TRAIN-095 (POST copy-to-org)

**Invariantes:**
- INV-TRAIN-EXB-ACL-001..007
- INV-TRAIN-047, INV-TRAIN-048

#### 8.3 Dependências
- AR-TRAIN-012

#### 8.5 WRITE
- `Hb Track - Backend/app/api/v1/routers/exercises.py` (novos endpoints)
- `Hb Track - Backend/docs/ssot/openapi.json` (regenerar)

#### 8.7 AC binário
##### AC-001
**PASS:** `POST /exercises/{id}/copy-to-org` cria cópia ORG de exercício SYSTEM com `scope=ORG` e `created_by_user_id` do solicitante.  
**FAIL:** Cópia em exercício já ORG ou altera o original SYSTEM.

##### AC-002
**PASS:** `PATCH /exercises/{id}/visibility` aceita `org_wide|restricted` apenas para ORG por criador.  
**FAIL:** Aceita para SYSTEM ou por não-criador.

##### AC-003
**PASS:** `POST /exercises/{id}/acl` adiciona user da mesma org e retorna 201.  
**FAIL:** Aceita user cross-org ou em exercício sem `restricted`.

---

### AR-TRAIN-014 — UI scope/visibility/ACL/mídia no exercise-bank FE

**Status:** PENDENTE  
**Classe:** D  
**Prioridade:** MEDIA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Materializar no FE: indicador de escopo (SYSTEM/ORG), toggle de visibilidade, UI de ACL, ação "duplicar para ORG", preview de mídia e permissões RBAC "Treinador".

#### 8.1 Alvos SSOT
**Screens:**
- SCREEN-TRAIN-010
- SCREEN-TRAIN-011

**Flows:**
- FLOW-TRAIN-009

**Contracts:**
- CONTRACT-TRAIN-053..062, CONTRACT-TRAIN-091..095

**Decisões incorporadas:**
- DEC-TRAIN-EXB-001, DEC-TRAIN-EXB-001B, DEC-TRAIN-EXB-002, DEC-TRAIN-EXB-RBAC-001

#### 8.3 Dependências
- AR-TRAIN-013

#### 8.5 WRITE
- `Hb Track - Frontend/src/app/(admin)/training/exercise-bank/*`
- `Hb Track - Frontend/src/components/training/exercises/*`

#### 8.7 AC binário
##### AC-001
**PASS:** Card de exercício exibe badge `SYSTEM` ou `ORG` e ação "Duplicar para Meu Banco" quando SYSTEM.  
**FAIL:** Escopo não visível ou ação de duplicar ausente.

##### AC-002
**PASS:** Exercício ORG exibe toggle `org_wide|restricted` visível apenas para o criador (role Treinador).  
**FAIL:** Toggle visível para todos ou em exercício SYSTEM.

##### AC-003
**PASS:** Em modo `restricted`, UI exibe lista de ACL (usuários) + botão de compartilhar (busca de usuários da org).  
**FAIL:** ACL sem UI ou permitindo users cross-org.

##### AC-004
**PASS:** Preview de mídia (imagens, vídeos, links) funcional nos modais de detalhes.  
**FAIL:** Mídia não renderizada.

---

## 9) Critérios PASS/FAIL (fase do módulo)

### PASS se (mínimo)
- [ ] Fluxos P0 (US-001/US-002) operacionais fim-a-fim (FE↔BE) com validação de invariantes bloqueantes
- [ ] Step18 sem divergência de IDs (UUID em contrato e runtime)
- [ ] Wellness self-only com `athlete_id` inferido do token (DEC-TRAIN-001)
- [ ] Top performers consumido via `CONTRACT-TRAIN-076` canônico no FE (DEC-TRAIN-003)
- [ ] Exports exibem estado degradado sem worker (DEC-TRAIN-004)
- [ ] Banco de exercícios com scope SYSTEM/ORG e ACL por visibility_mode (DEC-TRAIN-EXB-001/001B)
- [ ] Rankings e exports com contrato tipado (ou explicitamente DEFERIDO com justificativa aprovada)
- [ ] `TEST_MATRIX_TRAINING.md` atualizado com evidências

### FAIL se
- [ ] Invariante bloqueante sem teste de violação
- [ ] Contratos críticos expostos com drift (UUID/int) sem AR de correção
- [ ] UI principal chama endpoints inexistentes (404 sistemático)

