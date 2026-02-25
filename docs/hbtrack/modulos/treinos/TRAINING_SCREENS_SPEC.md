# TRAINING_SCREENS_SPEC.md — Especificação de Telas do Módulo TRAINING

Status: DRAFT  
Versão: v1.0.0  
Tipo de Documento: SSOT Normativo — Screens Spec  
Módulo: TRAINING  
Fase: PRD v2.2 (2026-02-20) + AS-IS repo (2026-02-25)  
Autoridade: NORMATIVO_TECNICO  
Última revisão: 2026-02-25  

Dependências (leitura):
- `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md`
- `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
- `Hb Track - Backend/docs/ssot/openapi.json`
- `Hb Track - Frontend/src/app/(admin)/training/*`
- `Hb Track - Frontend/src/app/(protected)/athlete/wellness-*/[sessionId]/*`

---

## 1) Objetivo (Normativo)

Especificar as telas (pages + modais) do módulo **TRAINING** de forma:
- rastreável (para `FLOW-*`, `CONTRACT-*`, `INV-*`),
- testável (estados mínimos de UI),
- auditável (gaps e paridade FE↔BE explicitados).

Regras:
- Este documento define **comportamento funcional**, não pixel-perfect.
- Qualquer divergência entre UI e SSOT (schema/OpenAPI/invariantes) deve ser registrada como `GAP-*` no `AR_BACKLOG_TRAINING.md`.

---

## 2) Convenções

### 2.1 Estados mínimos por tela (quando aplicável)
- `loading`
- `error`
- `empty`
- `data`
- `readonly` (quando a sessão/registro estiver bloqueado por regra)

### 2.2 Status AS-IS por tela
- `EVIDENCIADO`: existe rota/componente com comportamento funcional.
- `PARCIAL`: existe UI, mas há problemas de contrato, tipos, ou integrações.
- `HIPOTESE`: tela esperada por PRD/fluxos, mas não evidenciada.
- `BLOQUEADO`: depende de endpoints desabilitados/ausentes.

---

## 3) Índice de telas (mapa rápido)

| Screen ID | Tipo | Rota / Entrada | Atores | Estado AS-IS | Flows |
|---|---|---|---|---|---|
| SCREEN-TRAIN-001 | Page | `/training/agenda` | Treinador | EVIDENCIADO | FLOW-TRAIN-001, FLOW-TRAIN-002, FLOW-TRAIN-003 |
| SCREEN-TRAIN-002 | Page | `/training/calendario` (redirect) | Treinador | EVIDENCIADO (DEPRECATED) | FLOW-TRAIN-001 |
| SCREEN-TRAIN-003 | Modal | `CreateSessionModal` | Treinador | EVIDENCIADO | FLOW-TRAIN-002 |
| SCREEN-TRAIN-004 | Modal | `SessionEditorModal` | Treinador | EVIDENCIADO | FLOW-TRAIN-001, FLOW-TRAIN-003, FLOW-TRAIN-007 |
| SCREEN-TRAIN-005 | Page | `/training/sessions/[id]/edit` | Treinador | EVIDENCIADO | FLOW-TRAIN-003 |
| SCREEN-TRAIN-006 | Page | `/training/relatorio/[sessionId]` | Treinador | EVIDENCIADO | FLOW-TRAIN-001 |
| SCREEN-TRAIN-007 | Page | `/training/planejamento` | Treinador | EVIDENCIADO | FLOW-TRAIN-008 |
| SCREEN-TRAIN-008 | Modal | `CreateCycleWizard` | Treinador | EVIDENCIADO | FLOW-TRAIN-008 |
| SCREEN-TRAIN-009 | Modal | `CopyWeekModal` | Treinador | EVIDENCIADO | FLOW-TRAIN-008 |
| SCREEN-TRAIN-010 | Page | `/training/exercise-bank` | Treinador | EVIDENCIADO | FLOW-TRAIN-009 |
| SCREEN-TRAIN-011 | Modal | `ExerciseModal` / `CreateExerciseModal` / `EditExerciseModal` | Treinador | EVIDENCIADO | FLOW-TRAIN-009 |
| SCREEN-TRAIN-012 | Page | `/training/analytics` | Coordenador | EVIDENCIADO | FLOW-TRAIN-011 |
| SCREEN-TRAIN-013 | Modal | `ExportPDFModal` | Coordenador | BLOQUEADO | FLOW-TRAIN-012 |
| SCREEN-TRAIN-014 | Page | `/training/rankings` | Dirigente | PARCIAL | FLOW-TRAIN-013 |
| SCREEN-TRAIN-015 | Page | `/training/top-performers/[teamId]` | Dirigente | PARCIAL | FLOW-TRAIN-013 |
| SCREEN-TRAIN-016 | Page | `/training/eficacia-preventiva` | Coordenador | EVIDENCIADO | FLOW-TRAIN-014 |
| SCREEN-TRAIN-017 | Page | `/training/configuracoes` | Treinador | EVIDENCIADO | FLOW-TRAIN-010 |
| SCREEN-TRAIN-018 | Page | `/athlete/wellness-pre/[sessionId]` | Atleta | PARCIAL | FLOW-TRAIN-005 |
| SCREEN-TRAIN-019 | Page | `/athlete/wellness-post/[sessionId]` | Atleta | PARCIAL | FLOW-TRAIN-006 |
| SCREEN-TRAIN-020 | Page | `/training/presencas` (placeholder) | Treinador | PARCIAL | FLOW-TRAIN-004 |
| SCREEN-TRAIN-021 | Page | (a definir) Central de Alertas/Sugestões | Treinador | HIPOTESE | FLOW-TRAIN-015 |

---

## SCREEN-TRAIN-001 — Agenda de Treinos (Semanal/Mensal)

**Tipo:** Page  
**Rota:** `/training/agenda`  
**Query params normativos:**
- `view`: `week|month` (default `week`)
- `date`: `YYYY-MM-DD` (segunda-feira da semana corrente quando ausente)
- `teamId`: `UUID` (opcional; quando ausente, tela entra em empty-state “selecione uma equipe”)
- `q`: string (busca client-side em `main_objective|location|session_type`)

**Atores:** dirigente|coordenador|treinador  
**Fluxos:** FLOW-TRAIN-001, FLOW-TRAIN-002, FLOW-TRAIN-003  
**Contratos (mínimo):** `CONTRACT-TRAIN-001` (listar sessões)

### Estados de UI
- `loading`: skeleton/cards enquanto busca sessões.
- `empty`: sem equipe selecionada; sem sessões no período.
- `data`: lista semanal/mensal com cards por dia.
- `error`: falha ao buscar sessões.

### Ações e regras
- **Criar sessão:** abre `SCREEN-TRAIN-003`.
- **Editar sessão:** abre `SCREEN-TRAIN-004` (exceto `readonly`).
- **Relatório:** se sessão `readonly`, navegar para `SCREEN-TRAIN-006`.
- **Drag & drop entre dias:** deve atualizar `session_at` via `CONTRACT-TRAIN-004` e respeitar `INV-TRAIN-004/005`.

### Evidências AS-IS
- `Hb Track - Frontend/src/app/(admin)/training/agenda/AgendaClient.tsx`
- `Hb Track - Frontend/src/components/training/agenda/*`

---

## SCREEN-TRAIN-002 — Calendário Mensal (DEPRECATED)

**Tipo:** Page  
**Rota:** `/training/calendario`  
**Comportamento:** redirect para `/training/agenda?view=month`  
**Estado AS-IS:** EVIDENCIADO (redirect)

Evidência:
- `Hb Track - Frontend/src/app/(admin)/training/calendario/page.tsx`

---

## SCREEN-TRAIN-003 — Modal: Criar Sessão

**Tipo:** Modal (Client Component)  
**Entrada:** acionado a partir de `SCREEN-TRAIN-001`  
**Fluxo:** FLOW-TRAIN-002  
**Contrato:** `CONTRACT-TRAIN-002`

### Campos normativos (mínimo)
- `team_id` (UUID) — obrigatório
- `session_at` (datetime) — obrigatório
- `session_type` (enum) — obrigatório
- `main_objective` (texto) — opcional
- `duration_planned_minutes` (int) — opcional
- `location` (texto) — opcional

### Regras
- Validação local deve impedir submissão com payload vazio.
- Após criar, deve atualizar lista da agenda (invalidate/refetch).

Evidência:
- `Hb Track - Frontend/src/components/training/modals/CreateSessionModal.tsx`

---

## SCREEN-TRAIN-004 — Modal: Editor de Sessão

**Tipo:** Modal (Client Component)  
**Entrada:** click em card da agenda  
**Fluxos:** FLOW-TRAIN-001, FLOW-TRAIN-003, FLOW-TRAIN-007  
**Contratos:** `CONTRACT-TRAIN-003`, `CONTRACT-TRAIN-004`, `CONTRACT-TRAIN-006`, `CONTRACT-TRAIN-012`, `CONTRACT-TRAIN-019..024`

### Seções normativas (alto nível)
- Cabeçalho: status (`draft|scheduled|in_progress|pending_review|readonly`), data/hora, equipe.
- Metadados: objetivos, local, duração.
- Focos: distribuição com validação `INV-TRAIN-001`.
- Exercícios: lista e reordenação (drag-and-drop) com `INV-TRAIN-045`.
- Ações: publicar/agendar, duplicar, fechar revisão (quando aplicável), deletar (soft delete).

### Estados de UI
- `loading`: enquanto carrega sessão e exercícios.
- `readonly`: quando `INV-TRAIN-004/005/029` bloquearem edição.
- `error`: erros de validação do backend devem aparecer em banner/inline.

Evidência:
- `Hb Track - Frontend/src/components/training/modals/SessionEditorModal.tsx`

---

## SCREEN-TRAIN-005 — Editor de Sessão (página inteira)

**Tipo:** Page  
**Rota:** `/training/sessions/[id]/edit`  
**Fluxo:** FLOW-TRAIN-003  
**Contratos:** `CONTRACT-TRAIN-003`, `CONTRACT-TRAIN-004`, `CONTRACT-TRAIN-006`, `CONTRACT-TRAIN-019..024`

### Tabs internas evidenciadas
- `overview`: metadados + publish
- `focus`: editor de foco com templates
- `exercises`: banco + dropzone + reorder
- `notes`: observações e justificativas

### Regras
- “Agendar treino” deve falhar se sessão inválida ou fora da janela (INV-TRAIN-004).
- “Excluir sessão” é soft delete e exige `reason` (INV-TRAIN-008).

Evidência:
- `Hb Track - Frontend/src/app/(admin)/training/sessions/[id]/edit/SessionEditClient.tsx`

---

## SCREEN-TRAIN-006 — Relatório de Sessão (read-only)

**Tipo:** Page  
**Rota:** `/training/relatorio/[sessionId]`  
**Fluxo:** FLOW-TRAIN-001  
**Contratos:** `CONTRACT-TRAIN-003`, `CONTRACT-TRAIN-025`, `CONTRACT-TRAIN-028`, `CONTRACT-TRAIN-019`

### Conteúdo mínimo
- Identificação da sessão: data/hora, tipo, local, objetivos.
- Planejado vs realizado: duração planejada/real e outcome.
- Foco consolidado (soma e distribuição).
- Presenças + estatísticas.
- Exercícios executados/planejados (quando disponíveis).

Evidência:
- `Hb Track - Frontend/src/app/(admin)/training/relatorio/[sessionId]/RelatorioClient.tsx`

---

## SCREEN-TRAIN-007 — Planejamento (Ciclos e Microciclos)

**Tipo:** Page  
**Rota:** `/training/planejamento`  
**Fluxo:** FLOW-TRAIN-008  
**Contratos:** `CONTRACT-TRAIN-040..052`

### Estados de UI
- `empty`: sem equipe selecionada; sem ciclos/microciclos.
- `data`: timeline com macrociclos → mesociclos → microciclos.

Evidência:
- `Hb Track - Frontend/src/app/(admin)/training/planejamento/PlanejamentoClient.tsx`

---

## SCREEN-TRAIN-008 — Modal: Criar Ciclo (wizard)

**Tipo:** Modal  
**Entrada:** botão “Novo Ciclo” em `SCREEN-TRAIN-007`  
**Fluxo:** FLOW-TRAIN-008  
**Contratos:** `CONTRACT-TRAIN-042`, `CONTRACT-TRAIN-043`

Regras normativas:
- `macro` não pode ter `parent_cycle_id`; `meso` deve ter.
- Datas de `meso` devem estar contidas no `macro` pai (`INV-TRAIN-037`).

Evidência:
- `Hb Track - Frontend/src/components/training/modals/CreateCycleWizard.tsx`

---

## SCREEN-TRAIN-009 — Modal: Copiar Semana

**Tipo:** Modal  
**Entrada:** botão “Copiar Semana” em `SCREEN-TRAIN-007` (ou agenda)  
**Fluxo:** FLOW-TRAIN-008  
**Contratos:** `CONTRACT-TRAIN-010` (copy-week)

Evidência:
- `Hb Track - Frontend/src/components/training/modals/CopyWeekModal.tsx`
- `Hb Track - Backend/app/api/v1/routers/training_sessions.py` (`/copy-week`)

---

## SCREEN-TRAIN-010 — Banco de Exercícios

**Tipo:** Page  
**Rota:** `/training/exercise-bank`  
**Fluxo:** FLOW-TRAIN-009  
**Contratos:** `CONTRACT-TRAIN-053..062`

### Capacidades normativas
- Buscar/filtrar por tags e categoria.
- Favoritar/desfavoritar exercícios.
- CRUD de exercício (somente staff).
- DnD habilitado (integração com composição de sessão).

Evidência:
- `Hb Track - Frontend/src/app/(admin)/training/exercise-bank/page.tsx`

---

## SCREEN-TRAIN-011 — Modais do Banco de Exercícios

**Tipo:** Modal(s)  
**Entradas:** `SCREEN-TRAIN-010`  
**Fluxo:** FLOW-TRAIN-009  
**Contratos:** `CONTRACT-TRAIN-054..061` (conforme ação)

Evidência:
- `Hb Track - Frontend/src/components/training/exercises/ExerciseModal.tsx`
- `Hb Track - Frontend/src/components/training/exercises/CreateExerciseModal.tsx`
- `Hb Track - Frontend/src/components/training/exercises/EditExerciseModal.tsx`

---

## SCREEN-TRAIN-012 — Analytics (dashboard)

**Tipo:** Page  
**Rota:** `/training/analytics`  
**Fluxo:** FLOW-TRAIN-011  
**Contratos:** `CONTRACT-TRAIN-069..072`

### Seções normativas
- Cards: total sessões, RPE médio, carga interna, taxas wellness.
- Gráficos: carga semanal e respostas wellness (quando disponível).
- Lista: alertas de desvio (threshold).
- CTA: “Exportar PDF” → `SCREEN-TRAIN-013` (quando habilitado).

Evidência:
- `Hb Track - Frontend/src/app/(admin)/training/analytics/AnalyticsClient.tsx`

---

## SCREEN-TRAIN-013 — Modal: Exportar PDF (analytics)

**Tipo:** Modal  
**Entrada:** `SCREEN-TRAIN-012`  
**Fluxo:** FLOW-TRAIN-012  
**Estado AS-IS:** BLOQUEADO (endpoints não incluídos no agregador)

Contratos (quando reabilitado no agregador):
- `CONTRACT-TRAIN-086` (request export)
- `CONTRACT-TRAIN-087` (polling status)
- `CONTRACT-TRAIN-088` (histórico)
- `CONTRACT-TRAIN-089` (rate limit)

Regras normativas (quando habilitado):
- Consultar rate limit antes de solicitar export (INV-TRAIN-012).
- Polling por status até `completed|failed`.
- Histórico de exports por usuário.

Evidência:
- `Hb Track - Frontend/src/components/training/analytics/ExportPDFModal.tsx`
- `Hb Track - Backend/app/api/v1/routers/exports.py` (router existe, mas não está incluído em `api.py`)

---

## SCREEN-TRAIN-014 — Rankings de Wellness (equipes)

**Tipo:** Page  
**Rota:** `/training/rankings`  
**Fluxo:** FLOW-TRAIN-013  
**Estado AS-IS:** PARCIAL

### Contratos
- `CONTRACT-TRAIN-073` (listar rankings)
- `CONTRACT-TRAIN-074` (recalcular — dirigente)
- `CONTRACT-TRAIN-075` (drilldown 90%+)

### Gap crítico
- Frontend tipa `team_id` como `number`, mas SSOT usa `UUID`.

Evidência:
- `Hb Track - Frontend/src/app/(admin)/training/rankings/RankingsClient.tsx`
- `Hb Track - Frontend/src/lib/api/rankings.ts`

---

## SCREEN-TRAIN-015 — Top Performers (atletas 90%+)

**Tipo:** Page  
**Rota:** `/training/top-performers/[teamId]`  
**Fluxo:** FLOW-TRAIN-013  
**Estado AS-IS:** PARCIAL

Regra normativa:
- `teamId` deve ser tratado como `UUID` (string) e não `int`.

Evidência:
- `Hb Track - Frontend/src/app/(admin)/training/top-performers/[teamId]/TopPerformersClient.tsx`

---

## SCREEN-TRAIN-016 — Eficácia Preventiva

**Tipo:** Page  
**Rota:** `/training/eficacia-preventiva`  
**Fluxo:** FLOW-TRAIN-014  
**Contratos:** `CONTRACT-TRAIN-072`

Evidência:
- `Hb Track - Frontend/src/app/(admin)/training/eficacia-preventiva/PreventionDashboardClient.tsx`

---

## SCREEN-TRAIN-017 — Configurações (templates de sessão)

**Tipo:** Page  
**Rota:** `/training/configuracoes`  
**Fluxo:** FLOW-TRAIN-010  
**Contratos:** `CONTRACT-TRAIN-063..068`

Evidência:
- `Hb Track - Frontend/src/app/(admin)/training/configuracoes/ConfiguracoesClient.tsx`

---

## SCREEN-TRAIN-018 — Wellness Pré (Atleta)

**Tipo:** Page  
**Rota:** `/athlete/wellness-pre/[sessionId]`  
**Fluxo:** FLOW-TRAIN-005  
**Estado AS-IS:** PARCIAL

### Requisitos normativos
- Countdown de deadline (INV-TRAIN-002).
- Submit no endpoint correto (prefix `/wellness-pre/...`).
- Campos alinhados ao schema (`sleep_hours`, `sleep_quality`, `fatigue_pre`, `stress_level`, `muscle_soreness`).

Evidências:
- `Hb Track - Frontend/src/app/(protected)/athlete/wellness-pre/[sessionId]/WellnessPreClient.tsx`
- `Hb Track - Frontend/src/components/training/wellness/WellnessPreForm.tsx`

---

## SCREEN-TRAIN-019 — Wellness Pós (Atleta)

**Tipo:** Page  
**Rota:** `/athlete/wellness-post/[sessionId]`  
**Fluxo:** FLOW-TRAIN-006  
**Estado AS-IS:** PARCIAL

Requisitos normativos:
- Submit no endpoint correto (prefix `/wellness-post/...`).
- Respeitar janela de edição (INV-TRAIN-003).
- Exibir `internal_load` calculado (quando disponível).

Evidências:
- `Hb Track - Frontend/src/app/(protected)/athlete/wellness-post/[sessionId]/WellnessPostClient.tsx`
- `Hb Track - Frontend/src/components/training/wellness/WellnessPostForm.tsx`

---

## SCREEN-TRAIN-020 — Presenças (Admin)

**Tipo:** Page (ou tab no editor)  
**Rota evidenciada:** `/training/presencas` (placeholder)  
**Fluxo:** FLOW-TRAIN-004  
**Estado AS-IS:** PARCIAL

Regra normativa:
- A UI deve suportar `presence_status = present|absent|justified` e respeitar `ck_attendance_absent_reason_null`:
  - `absent` ⇒ `reason_absence = NULL`
  - `justified` ⇒ `reason_absence != NULL` (TO-BE: required no frontend)

Evidências:
- `Hb Track - Frontend/src/app/(admin)/training/presencas/page.tsx`
- `Hb Track - Frontend/src/components/training/attendance/AttendanceTab.tsx` (componente funcional, mas não integrado)

---

## SCREEN-TRAIN-021 — Central de Alertas e Sugestões (UI)

**Tipo:** Page  
**Rota:** a definir (ex.: `/training/alerts`)  
**Fluxo:** FLOW-TRAIN-015  
**Estado AS-IS:** HIPOTESE

Requisitos normativos:
- Listar alertas ativos e histórico por equipe.
- Aplicar/dismiss sugestões com registro de ação.
- Exibir severidade e categoria com filtros.

Contratos:
- `CONTRACT-TRAIN-077..085`
