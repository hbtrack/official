# TRAINING ROADMAP — Módulo TRAINING

**Tipo:** ROADMAP (Features futuras, gaps e decisões arquiteturais)  
**Versão:** v1.2.1 (2026-03-06) — Emenda DEC-TRAIN-EXB-001B (default `visibility_mode` = `restricted`) + higiene spec-driven  
**Módulo:** TRAINING  
**Fase atual:** FASE_2 + FASE_3 REAL concluídas — `DONE_TRAINING_ATINGIDO = TRUE`  
**Documentos relacionados:**
- [_INDEX.md](_INDEX.md) — autoridade e protocolo do módulo
- [AR_BACKLOG_TRAINING.md](AR_BACKLOG_TRAINING.md) — backlog de ARs
- [TEST_MATRIX_TRAINING.md](TEST_MATRIX_TRAINING.md) — política de evidência, TRUTH_BE e roteamento de impacto

---

## Auditoria AS-IS — 2026-02-25

### O que está evidenciado

- **Training sessions**: CRUD + workflow (publish/close/duplicate/restore) exposto via `/api/v1/training-sessions/*` e rotas scoped `/api/v1/teams/{team_id}/trainings/*`.
- **Session exercises**: add/bulk/reorder/update/remove exposto sob `/api/v1/training-sessions/*/exercises*` (suporta DnD).
- **Attendance**: endpoints expostos sob `/api/v1/training_sessions/{id}/attendance*` (underscore).
- **Wellness pré/pós**: endpoints expostos sob `/api/v1/wellness-pre/*` e `/api/v1/wellness-post/*` (com subpaths underscore).
- **Ciclos/microciclos**: endpoints expostos sob `/api/v1/training-cycles/*` e `/api/v1/training-microcycles/*`.
- **Analytics**: endpoints expostos sob `/api/v1/analytics/team/{team_id}/*` e prevenção `/prevention-effectiveness`.
- **Banco de exercícios**: endpoints expostos sob `/api/v1/exercises`, `/exercise-tags`, `/exercise-favorites`.
- **Templates de sessão**: endpoints expostos sob `/api/v1/session-templates/*`.
- **Frontend admin training**: `/training/agenda`, `/planejamento`, `/exercise-bank`, `/analytics`, `/rankings`, `/eficacia-preventiva`, `/configuracoes`, `/relatorio/[sessionId]`, `/sessions/[id]/edit`.

### O que estava parcial/bloqueado (baseline 2026-02-25)

- **Presenças (UI)**: `/training/presencas` era placeholder; componente `AttendanceTab` existia mas não integrado. → **Resolvido em AR-TRAIN-005/017/018.**
- **Wellness (FE)**: `src/lib/api/wellness.ts` apontava para endpoints incorretos; formulário não alinhado ao schema. → **Resolvido em AR-TRAIN-003/004.**
- **Rankings (FE/BE)**: FE tipava `team_id`/`athlete_id` como `number`; BE sem response_model, services legados. → **Resolvido em AR-TRAIN-006/007.**
- **Alertas/Sugestões Step 18**: IDs em path tipados como int conflitavam com DB `uuid`. → **Resolvido em AR-TRAIN-001/002.**
- **Exports/LGPD**: routers desabilitados no agregador v1. → **Resolvido em AR-TRAIN-008/009.**
- **Testes invariants**: referenciavam `docs/_generated/*` ao invés do SSOT atual. → **Resolvido em AR-TRAIN-010A.**

---

## Mapa: Evidência vs Hipótese

| Item | Descrição | Status (baseline 2026-02-25) | Evidência mínima |
|---|---|---|---|
| EVID-TRAIN-001 | Sessões de treino CRUD+workflow | EVIDENCIADO | `app/api/v1/routers/training_sessions.py`, `openapi.json` |
| EVID-TRAIN-002 | Presença (endpoints) | EVIDENCIADO | `app/api/v1/routers/attendance.py`, `openapi.json` |
| EVID-TRAIN-003 | Presença (UI) | PARCIAL → RESOLVIDO (AR-TRAIN-005/017/018) | `AttendanceTab.tsx` + FASE_3 endpoints |
| EVID-TRAIN-004 | Wellness pré/pós (endpoints) | EVIDENCIADO | `routers/wellness_pre.py`, `routers/wellness_post.py` |
| EVID-TRAIN-005 | Wellness pré/pós (athlete UX) | PARCIAL → RESOLVIDO (AR-TRAIN-003/004) | payload canônico + self-only |
| EVID-TRAIN-006 | Planejamento ciclos/microciclos | EVIDENCIADO | `PlanejamentoClient.tsx` + routers cycles/microcycles |
| EVID-TRAIN-007 | Banco de exercícios + favoritos | EVIDENCIADO | `/training/exercise-bank` + routers exercises |
| EVID-TRAIN-007B | Banco de exercícios (scope SYSTEM/ORG, ACL) | GAP → RESOLVIDO (AR-TRAIN-011..014) | schema/services/endpoints materializados |
| EVID-TRAIN-008 | Templates de sessão | EVIDENCIADO | `/training/configuracoes` + `/session-templates` |
| EVID-TRAIN-009 | Analytics (team summary/load/deviation) | EVIDENCIADO | `routers/training_analytics.py` + FE analytics |
| EVID-TRAIN-010 | Rankings wellness (endpoints) | PARCIAL → RESOLVIDO (AR-TRAIN-006) | response_model + cálculo correto |
| EVID-TRAIN-011 | Alertas/Sugestões Step 18 | DIVERGENTE_DO_SSOT → RESOLVIDO (AR-TRAIN-001/002) | UUID alinhado |
| EVID-TRAIN-012 | Export PDF analytics | BLOQUEADO → RESOLVIDO (AR-TRAIN-008/009) | router reabilitado + estado degradado |
| HIP-TRAIN-001 | Central UI de alertas/sugestões | HIPOTESE — FASE_4 / fora do escopo atual | não priorizado |
| HIP-TRAIN-002 | Lista “treinos de hoje” para atleta (US-002) | RESOLVIDO (FASE_3 REAL) — AR-TRAIN-019 implementou visão pré-treino atleta + wellness content gate | `GET /athlete/wellness-content-gate/{session_id}` (AR-TRAIN-057) |

---

## Gaps

### Status dos Gaps FASE_2 (todos resolvidos)

| Gap | Resolução |
|---|---|
| GAP-TRAIN-001: IDs int em Step18 | **Resolvido**: AR-TRAIN-001/002 (AR_126/AR_175) |
| GAP-TRAIN-002: Wellness FE endpoints errados | **Resolvido**: AR-TRAIN-003/004 (AR_177/AR_178) |
| GAP-TRAIN-003: athlete_id por coluna inexistente | **Resolvido**: AR-TRAIN-004 (AR_178) |
| GAP-TRAIN-004: UI presenças não materializada | **Resolvido**: AR-TRAIN-005/017/018 |
| GAP-TRAIN-005: Rankings FE UUID/int + response_model | **Resolvido**: AR-TRAIN-006/007 (AR_180/AR_183) |
| GAP-TRAIN-006: Exports desabilitados | **Resolvido**: AR-TRAIN-008/009 (AR_185/AR_186) |
| GAP-TRAIN-007: Testes refs `_generated` | **Resolvido**: AR-TRAIN-010A (AR_187) |
| GAP-TRAIN-EXB-001: schema sem scope/visibility_mode | **Resolvido**: AR-TRAIN-011 (AR_189) |
| GAP-TRAIN-EXB-002: exercise_acl + exercise_media ausentes | **Resolvido**: AR-TRAIN-011 (AR_189) |
| GAP-TRAIN-EXB-003: guards SYSTEM/ORG + RBAC ausentes | **Resolvido**: AR-TRAIN-012/013 (AR_190/AR_191) |

### Gaps FASE_3 — Status atualizado (v1.1.0)

| Gap | Status |
|---|---|
| GAP-FASE3-001: Central UI de alertas/sugestões (HIP-TRAIN-001) | **ABERTO** — não priorizado em FASE_3. Candidato a FASE_4. |
| GAP-FASE3-002: Dashboard atleta com lista "treinos de hoje" (HIP-TRAIN-002) | **RESOLVIDO** — AR-TRAIN-019 implementou visão pré-treino atleta + AR-TRAIN-057 implementou GET /athlete/wellness-content-gate. |

---

## Decisões Arquiteturais Resolvidas

### DEC-TRAIN-001 — Wellness self-only
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**
- `athlete_id` DEVE ser inferido do token JWT pelo backend.
- Cliente atleta NÃO envia `athlete_id` no payload de wellness.
- Fluxo por staff/terceiros DEVE ser endpoint/escopo separado com permissão explícita e auditoria (INV-TRAIN-026).

**Impacto:** AR-TRAIN-003, AR-TRAIN-004, CONTRACT-TRAIN-029..039, FLOW-TRAIN-005/006, SCREEN-TRAIN-018/019.

---

### DEC-TRAIN-002 — Wellness UI
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**
- Manter UX com sliders/componentes amigáveis ao atleta.
- Mapear UI para payload canônico do backend.
- O contrato DEVE conter tabela explícita de mapeamento FE→payload (ver TRAINING_FRONT_BACK_CONTRACT.md §4.4).
- A matriz de testes DEVE conter testes normativos de mapeamento (ver TEST_MATRIX_TRAINING.md).

**Impacto:** AR-TRAIN-003, CONTRACT-TRAIN-029..039, SCREEN-TRAIN-018/019, TEST_MATRIX.

---

### DEC-TRAIN-003 — Top performers endpoint canônico
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**
- `CONTRACT-TRAIN-076` é o endpoint canônico único para consumo no frontend principal (listings).
- `CONTRACT-TRAIN-075` permanece como endpoint especializado/derivado para drilldown analytics.
- Frontend NÃO DEVE consumir ambos para a mesma funcionalidade.

**Impacto:** AR-TRAIN-007, CONTRACT-TRAIN-073..076, SCREEN-TRAIN-015, FLOW-TRAIN-013.

---

### DEC-TRAIN-004 — Exports worker obrigatório
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**
- Fluxos assíncronos de export exigem worker/Celery ativo no ambiente.
- Sem worker ativo, UI/contrato DEVE expor estado degradado explícito (indisponível), sem simular job funcional.
- Polling fake (simular progresso sem worker) é **PROIBIDO**.

**Impacto:** AR-TRAIN-008, AR-TRAIN-009, CONTRACT-TRAIN-086..090, SCREEN-TRAIN-013, FLOW-TRAIN-012.

---

### DEC-TRAIN-EXB-001 — Banco de Exercícios modelo base
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

---

### DEC-TRAIN-EXB-001B — Visibilidade ORG + ACL
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**
- Exercícios `ORG` DEVEM suportar `visibility_mode` = `org_wide` ou `restricted`.
- Em `restricted`, exercício visível ao criador + usuários explícitos na ACL.
- ACL é por usuário individual (não por grupo/papel nesta fase).
- Usuários na ACL DEVEM pertencer à mesma organização do exercício.
- Apenas o treinador criador PODE gerenciar compartilhamento (ACL) e alterar `visibility_mode`.
- Criador mantém acesso implícito independentemente da ACL.
- Mudanças de ACL/visibilidade NÃO PODEM invalidar leitura de sessões históricas.
- **Default para novos exercícios ORG: `restricted`.** *(AMENDADO: era `org_wide` em 2026-02-25; ver INV-TRAIN-060 e INV-TRAIN-EXB-ACL-001.)*

**Impacto:** INV-TRAIN-EXB-ACL-001..007, CONTRACT-TRAIN-091..095, SCREEN-TRAIN-010/011.

---

### DEC-TRAIN-EXB-002 — Capability aprovada
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**
- Treinador PODE criar categorias, nomes e tags personalizadas de exercícios.
- Exercícios `ORG` DEVEM suportar compartilhamento conforme DEC-TRAIN-EXB-001B.
- Apenas o treinador criador PODE gerenciar ACL/visibilidade.

**Impacto:** FLOW-TRAIN-009, SCREEN-TRAIN-010/011, CONTRACT-TRAIN-053..062.

---

### DEC-TRAIN-EXB-RBAC-001 — Treinador como RBAC específico
**Status:** RESOLVIDA (2026-02-25)  
**Texto normativo final:**
- O termo "Treinador" DEVE ser tratado como papel RBAC específico (identificador explícito no contrato).
- NÃO é categoria genérica inferida.
- O MCP DEVE explicitar esse identificador RBAC nos trechos de permissão do Banco de Exercícios ORG.

**Impacto:** INV-TRAIN-EXB-ACL-004, CONTRACT-TRAIN-054/056/091..095, SCREEN-TRAIN-010/011.

---

### DEC-INV-065 — Encerramento permite pendências
**Status:** RESOLVIDA (2026-02-26)  
**Contexto:** AR_154 item 3 solicitou guard que BLOQUEIA `close_session()` se houver pending items. Executor identificou contradição com INV-TRAIN-065 canônica: "sistema DEVE PERMITIR encerrar. Itens inconsistentes viram pendências (INV-066), NÃO bloqueiam."  
**Texto normativo final:**
- INV-TRAIN-065 é AUTORITATIVA: encerramento de sessão DEVE ser permitido independentemente de pending items.
- Dados inconsistentes/não resolvidos viram fila de pendências (`training_pending_items` via INV-066).
- Guard de bloqueio por pending items é **PROIBIDO** — violaria invariante canônica.
- AR_154 item 3 CANCELADO. AR_155 implementa pending queue service (INV-066).

**Impacto:** AR_154 (item 3 cancelado), AR_155 (pending queue), INV-TRAIN-065/066, FLOW-TRAIN-017.

---

## POST-DONE Backlog

> Esta seção cataloga itens identificados **após o DONE_TRAINING_ATINGIDO**.  
> Nenhum deles constitui pendência bloqueante. São candidatos a batches futuros com autorização do PO.
> Classificação: **UX Polish** (pequ. melhorias dentro de capabilities já existentes) vs **Nova Capability** (novo escopo funcional).

### UX Polish (melhorias em capabilities existentes)

> Não exigem nova autorização de escopo. Podem ser executados como ARs do tipo D/E/M.

| ID | Descrição | Origem |
|---|---|---|
| POLISH-001 | Central UI de alertas IA com filtros e histórico de sugestões aplicadas/descartadas | HIP-TRAIN-001 |
| POLISH-002 | Dashboard atleta com sumário "treinos de hoje" e informações de ciclo ativo | HIP-TRAIN-002 (complemento ao FLOW-TRAIN-016 já implementado) |
| POLISH-003 | Estado degradado de export com estimativa de disponibilidade do worker | DEC-TRAIN-004 (melhoria de UX sobre implementação atual) |
| POLISH-004 | Notificação push para atleta quando presença pendente expira | INV-TRAIN-066/067 (UX adicional) |
| POLISH-005 | Filtro e exportação de histórico de wellness pós-treino por período | FLOW-TRAIN-006 (extensão) |

### Novas Capabilities (novo escopo funcional)

> Exigem autorização PO explícita e ARs de Arquiteto antes da execução.

| ID | Descrição | Referência |
|---|---|---|
| CAP-001 | Training Suggestions (recomendador de planos) | `training_suggestions.py` router inativo; PRD marca como futuro |
| CAP-002 | Planner automático de ciclos via IA (propostas geradas, revisão humana) | Extensão do DEC-TRAIN-EXB-002 + IA Coach (AR-TRAIN-021) |
| CAP-003 | Load management automático (alerta de sobrecarga com modelo preditivo) | GAP-FASE3-001 (HIP-TRAIN-001); nova integração de analytics |
| CAP-004 | Integração wearables (import de dados de esforço externo) | Fora do PRD v2.2; nova capability |
| CAP-005 | Multi-tenant coaching (treinador gerencia múltiplas equipes com visão consolidada) | Fora do PRD v2.2 |
