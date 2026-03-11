# TRAINING_SCREENS_SPEC.md — Especificação de Telas do Módulo TRAINING

Status: NORMATIVO_VIGENTE  
Versão: v1.6.0
Tipo de Documento: SSOT Normativo — Screens Spec
Módulo: TRAINING
Fase: FASE_2 + FASE_3 REAL — implementação concluída (2026-03-04). Itens pós-DONE: ver TRAINING_ROADMAP.md §POST-DONE.
Autoridade: NORMATIVO_TECNICO
Última revisão: 2026-03-05

> Changelog v1.6.0 (2026-03-09):
> - SCREEN-TRAIN-005: `overview` tab — `metadados + publish` → `metadados + agendar (schedule)`
> - SCREEN-TRAIN-020: atualizado de PARCIAL para especificação completa com ledger (Planned/Realized/Adjustments)
> - Índice: SCREEN-TRAIN-020 promovido (PARCIAL → EVIDENCIADO parcial/AR_275)
> - Versão bumped: v1.5.0 → v1.6.0 (AR_275 reconciliação léxica)

> Changelog v1.5.0 (2026-03-05):
> - SCREEN-TRAIN-014/015: PARCIAL → EVIDENCIADO (UUID gap corrigido em rankings.ts; RankingsClient + TopPerformersClient evidenciados)
> - SCREEN-TRAIN-018/019: PARCIAL → EVIDENCIADO (WellnessPreClient + WellnessPostClient evidenciados)
> - SCREEN-TRAIN-023: GAP → EVIDENCIADO (pending-queue/page.tsx + PendingQueueTable.tsx implementados)
> - Índice expandido com SCREEN-TRAIN-022..025 (FASE_3)

> Changelog v1.4.0 (2026-03-04):
> - Status: DRAFT → NORMATIVO_VIGENTE (FASE_2 + FASE_3 REAL concluídas, DONE_TRAINING_ATINGIDO)  
> - Fase atualizada: sem itens pendentes bloqueantes; features pós-DONE em TRAINING_ROADMAP.md §POST-DONE  

> Changelog v1.2.0 (2026-02-26):  
> - Adicionada Authority Matrix  
> - Adicionada convenção de Classification Tags  
> - Adicionado `decision_trace:` formal em SCREEN-TRAIN-010/011/013/015/018/019  

> Changelog v1.1.0 (2026-02-25):  
> - DEC-TRAIN-001/002: SCREEN-TRAIN-018/019 — self-only, sem seleção de atleta, mapeamento sliders  
> - DEC-TRAIN-003: SCREEN-TRAIN-015 — consome endpoint canônico CONTRACT-TRAIN-076  
> - DEC-TRAIN-004: SCREEN-TRAIN-013 — estado degradado sem worker  
> - DEC-TRAIN-EXB-*: SCREEN-TRAIN-010/011 — scope/visibility/ACL/media/copy  

Dependências (leitura):
- `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md`
- `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
- `Hb Track - Backend/docs/ssot/openapi.json`
- `Hb Track - Frontend/src/app/(admin)/training/*`
- `Hb Track - Frontend/src/app/(protected)/athlete/wellness-*/[sessionId]/*`

---

## Authority Matrix

| Aspecto | Regra |
|---|---|
| Fonte de verdade | Telas derivadas de PRD + SSOT (schema/OpenAPI) + Decisões humanas (DEC-*) |
| Escrita normativa | **Arquiteto** — criar, alterar, remover especificações de tela e regras associadas |
| Proposta UX | **Designer UX** — propõe alterações via DEC |
| Somente leitura + GAP | Executor, Testador — leitura + registrar GAP |
| Precedência em conflito | DB > Services > OpenAPI > FE > PRD |

---

## CONSUMO DO CONTRATO

As telas do módulo TRAINING devem consumir o cliente gerado a partir do contrato OpenAPI.

Cliente canônico:

`Hb Track - Frontend/src/api/generated/*`

Regras:

- telas não definem manualmente payloads de request
- telas não redefinem tipos já presentes no cliente gerado
- validações devem refletir o contrato OpenAPI

Precedência:

`FE Generated client > FE Manual adapter > Screen specification`

A especificação de tela descreve UX,
não contrato de API.

---

## Convenção de Tags (Classification)

Cada tela (SCREEN-*) neste documento é uma **unidade de afirmação testável** e recebe classificação:

| Tag | Significado |
|---|---|
| `[NORMATIVO]` | Comportamento funcional que DEVE ser respeitado. |
| `[DESCRITIVO-AS-IS]` | Observação do estado atual (evidenciado no repo). |
| `[HIPOTESE]` | Expectativa derivada do PRD/fluxos, mas não evidenciada no repo. |
| `[GAP]` | Lacuna entre normativo e estado atual. |

**Aplicação neste documento:** O campo `Estado AS-IS` na tabela de índice indica a classificação:
- `EVIDENCIADO` → `[NORMATIVO]` + `[DESCRITIVO-AS-IS]`.
- `PARCIAL` → `[NORMATIVO]` com gaps identificados.
- `HIPOTESE` → `[HIPOTESE]`.
- `BLOQUEADO` → `[NORMATIVO]` + `[GAP]` (regra existe, implementação bloqueada).

---

## RELAÇÃO COM O PIPELINE SPEC-DRIVEN

Este documento integra o pipeline spec-driven definido em:

- `_INDEX.md`
- `TEST_MATRIX_TRAINING.md`
- `TRAINING_FRONT_BACK_CONTRACT.md`

Ele não substitui a validação técnica realizada por:

- `OPENAPI_SPEC_QUALITY`
- `CONTRACT_DIFF_GATE`
- `GENERATED_CLIENT_SYNC`
- `RUNTIME CONTRACT VALIDATION`
- `TRUTH_BE`
- `TRUTH_FE`

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
| SCREEN-TRAIN-013 | Modal | `ExportPDFModal` | Coordenador | EVIDENCIADO | FLOW-TRAIN-012 |
| SCREEN-TRAIN-014 | Page | `/training/rankings` | Dirigente | EVIDENCIADO | FLOW-TRAIN-013 |
| SCREEN-TRAIN-015 | Page | `/training/top-performers/[teamId]` | Dirigente | EVIDENCIADO | FLOW-TRAIN-013 |
| SCREEN-TRAIN-016 | Page | `/training/eficacia-preventiva` | Coordenador | EVIDENCIADO | FLOW-TRAIN-014 |
| SCREEN-TRAIN-017 | Page | `/training/configuracoes` | Treinador | EVIDENCIADO | FLOW-TRAIN-010 |
| SCREEN-TRAIN-018 | Page | `/athlete/wellness-pre/[sessionId]` | Atleta | EVIDENCIADO | FLOW-TRAIN-005 |
| SCREEN-TRAIN-019 | Page | `/athlete/wellness-post/[sessionId]` | Atleta | EVIDENCIADO | FLOW-TRAIN-006 |
| SCREEN-TRAIN-020 | Page | `/training/sessions/[id]` (cockpit/detalhe) | Treinador | EVIDENCIADO (parcial — AR_275) | FLOW-TRAIN-002, FLOW-TRAIN-004 |
| SCREEN-TRAIN-021 | Page | (a definir) Central de Alertas/Sugestões | Treinador | HIPOTESE | FLOW-TRAIN-015 |
| SCREEN-TRAIN-022 | Page | `/athlete/training/[sessionId]` | Atleta | GAP | FLOW-TRAIN-016, FLOW-TRAIN-017, FLOW-TRAIN-021 |
| SCREEN-TRAIN-023 | Page | `/training/pending-queue` | Treinador | EVIDENCIADO | FLOW-TRAIN-018 |
| SCREEN-TRAIN-024 | Page | `/athlete/ai-chat/[sessionId]` | Atleta | GAP | FLOW-TRAIN-019 |
| SCREEN-TRAIN-025 | Modal | N/A (modal sobre agenda/editor) | Treinador | GAP | FLOW-TRAIN-020 |

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
- `overview`: metadados + agendar (schedule)
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
**Contratos:** `CONTRACT-TRAIN-053..062`, `CONTRACT-TRAIN-091..095`  
**decision_trace:** `[DEC-TRAIN-EXB-001, DEC-TRAIN-EXB-001B, DEC-TRAIN-EXB-002, DEC-TRAIN-EXB-RBAC-001]`

### Capacidades normativas (CRUD base, EVIDENCIADO)
- Buscar/filtrar por tags e categoria.
- Favoritar/desfavoritar exercícios.
- CRUD de exercício (somente staff).
- DnD habilitado (integração com composição de sessão).

### Capacidades normativas (scope/visibility/ACL — DEC-TRAIN-EXB-*, TO-BE)
- **Indicador de scope:** badge visual `SYSTEM` (global, somente leitura) vs `ORG` (editável) em cada card de exercício.
- **Filtro de scope:** toggle/tab para mostrar SYSTEM vs ORG vs todos.
- **Indicador de visibility:** para exercícios ORG, badge `org_wide` vs `restricted`.
- **Botão "Copiar para minha org"** em exercícios SYSTEM → aciona `CONTRACT-TRAIN-095`.
- **Indicador de mídia:** thumbnail/preview quando exercício tem `exercise_media` (INV-TRAIN-052).
- **RBAC:** Botões de edição/exclusão visíveis apenas para creator ou role "Treinador" na mesma org (DEC-TRAIN-RBAC-001).
- **Exercícios SYSTEM:** botões de editar/excluir OCULTOS para org users (INV-TRAIN-048).

### Estados de UI adicionais (TO-BE)
- `restricted_hidden`: exercício ORG restricted que o usuário não tem acesso — não aparece na listagem.
- `system_readonly`: exercício SYSTEM com ações limitadas a "ver detalhes" e "copiar para org".

Evidência:
- `Hb Track - Frontend/src/app/(admin)/training/exercise-bank/page.tsx`

---

## SCREEN-TRAIN-011 — Modais do Banco de Exercícios

**Tipo:** Modal(s)  
**Entradas:** `SCREEN-TRAIN-010`  
**Fluxo:** FLOW-TRAIN-009  
**Contratos:** `CONTRACT-TRAIN-054..061`, `CONTRACT-TRAIN-091..094` (conforme ação)  
**decision_trace:** `[DEC-TRAIN-EXB-001, DEC-TRAIN-EXB-001B]`

### Campos normativos adicionais (DEC-TRAIN-EXB-001/001B, TO-BE)
- **scope** (select): `SYSTEM` | `ORG` — visível apenas para admin global.
- **visibility_mode** (select): `org_wide` | `restricted` — visível apenas para scope=ORG.
- **Mídia:** upload area para IMAGE/VIDEO/DOCUMENT, com preview. Tipo validado (INV-TRAIN-052).

### Sub-painel: Gerenciar ACL (DEC-TRAIN-EXB-002, TO-BE)
- Acessível apenas quando `visibility_mode = restricted`.
- Listar usuários com acesso (`CONTRACT-TRAIN-092`).
- Adicionar usuário (autocomplete da mesma org, `CONTRACT-TRAIN-093`); cross-org → erro inline.
- Remover usuário (`CONTRACT-TRAIN-094`).
- Nota visual: "Você (criador) tem acesso implícito" (INV-TRAIN-EXB-ACL-005).

### Regras de visibilidade de ações (RBAC, DEC-TRAIN-RBAC-001)
- Criar exercício: qualquer staff autenticado da org.
- Editar/excluir: apenas creator OU role "Treinador" na mesma org.
- Gerenciar ACL: apenas creator OU role "Treinador" na mesma org.
- Exercício SYSTEM: nenhuma ação de edição para org users.

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
**Estado AS-IS:** EVIDENCIADO
**decision_trace:** `[DEC-TRAIN-004]`

> Promovido por Kanban+evidência: AR_180 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_180/executor_main.log

Contratos (quando reabilitado no agregador):
- `CONTRACT-TRAIN-086` (request export)
- `CONTRACT-TRAIN-087` (polling status)
- `CONTRACT-TRAIN-088` (histórico)
- `CONTRACT-TRAIN-089` (rate limit)

Regras normativas (quando habilitado):
- Consultar rate limit antes de solicitar export (INV-TRAIN-012).
- Polling por status até `completed|failed`.
- Histórico de exports por usuário.

### Estado Degradado (DEC-TRAIN-004 — normativo, TO-BE)

> Quando worker Celery/Redis NÃO estiver disponível:

- UI DEVE exibir **banner/toast de degradação**: "Export pode levar mais tempo. O sistema está processando com capacidade reduzida."
- UI NÃO DEVE bloquear — usuário pode fechar modal e continuar usando o sistema.
- Botão "Exportar" permanece habilitado; backend retorna 202 com `degraded: true`.
- Polling continua com timeout estendido.
- Se export falhar após timeout → UI mostra estado `error` com retry.

Evidência:
- `Hb Track - Frontend/src/components/training/analytics/ExportPDFModal.tsx`
- `Hb Track - Backend/app/api/v1/routers/exports.py` (router existe, mas não está incluído em `api.py`)

---

## SCREEN-TRAIN-014 — Rankings de Wellness (equipes)

**Tipo:** Page
**Rota:** `/training/rankings`
**Fluxo:** FLOW-TRAIN-013
**Estado AS-IS:** EVIDENCIADO

### Contratos
- `CONTRACT-TRAIN-073` (listar rankings)
- `CONTRACT-TRAIN-074` (recalcular — dirigente)
- `CONTRACT-TRAIN-075` (drilldown 90%+)

Evidência:
- `Hb Track - Frontend/src/app/(admin)/training/rankings/RankingsClient.tsx`
- `Hb Track - Frontend/src/lib/api/rankings.ts`

---

## SCREEN-TRAIN-015 — Top Performers (atletas 90%+)

**Tipo:** Page  
**Rota:** `/training/top-performers/[teamId]`  
**Fluxo:** FLOW-TRAIN-013  
**Estado AS-IS:** EVIDENCIADO
**decision_trace:** `[DEC-TRAIN-003]`

### Regra Canônica (DEC-TRAIN-003 — normativo)

> Esta tela DEVE consumir **`CONTRACT-TRAIN-076`** como endpoint primário (canônico).
> `CONTRACT-TRAIN-075` é apenas drilldown especializado (>90%) e NÃO DEVE ser a fonte
> da listagem principal.

### Contratos consumidos
- **Primário (listagem):** `CONTRACT-TRAIN-076` — GET `/teams/{team_id}/wellness-top-performers`
- **Drilldown (>90%):** `CONTRACT-TRAIN-075` — GET `/analytics/wellness-rankings/{team_id}/athletes-90plus`

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
**Estado AS-IS:** EVIDENCIADO
**decision_trace:** `[DEC-TRAIN-001, DEC-TRAIN-002]`

### Requisitos normativos
- Countdown de deadline (INV-TRAIN-002).
- Submit no endpoint correto (prefix `/wellness-pre/...`).
- Campos alinhados ao schema (`sleep_hours`, `sleep_quality`, `fatigue_pre`, `stress_level`, `muscle_soreness`).

### Regra Self-Only (DEC-TRAIN-001 — normativo)
- UI NÃO DEVE exibir seletor de atleta — o atleta só registra para si mesmo.
- Payload NÃO DEVE conter `athlete_id` (backend infere do JWT).
- Não deve existir dropdown/autocomplete de "atleta".

### Mapeamento FE→Payload (DEC-TRAIN-002 — normativo)
- Sliders/UI components DEVEM ser mapeados conforme tabela canônica (CONTRACT §4.4).
- Labels visuais (ex.: "Qualidade do sono") → campo payload (`sleep_quality`).
- Ranges devem respeitar schema DB (ex.: `sleep_quality` 1..5, não 0..5).

### Estados de UI adicionais (TO-BE)
- `submitted`: wellness já enviado para esta sessão → readonly com resumo.
- `deadline_expired`: após `session_at - 2h` → formulário desabilitado com mensagem.
- `permission_error`: se backend retornar 422 por tentativa de registrar para outro atleta.

Evidências:
- `Hb Track - Frontend/src/app/(protected)/athlete/wellness-pre/[sessionId]/WellnessPreClient.tsx`
- `Hb Track - Frontend/src/components/training/wellness/WellnessPreForm.tsx`

---

## SCREEN-TRAIN-019 — Wellness Pós (Atleta)

**Tipo:** Page
**Rota:** `/athlete/wellness-post/[sessionId]`
**Fluxo:** FLOW-TRAIN-006
**Estado AS-IS:** EVIDENCIADO
**decision_trace:** `[DEC-TRAIN-001]`

### Requisitos normativos
- Submit no endpoint correto (prefix `/wellness-post/...`).
- Respeitar janela de edição (INV-TRAIN-003).
- Exibir `internal_load` calculado (quando disponível).

### Regra Self-Only (DEC-TRAIN-001 — normativo)
- UI NÃO DEVE exibir seletor de atleta.
- Payload NÃO DEVE conter `athlete_id` (backend infere do JWT).
- Mesmas regras de SCREEN-TRAIN-018 aplicam-se aqui.

### Estados de UI adicionais (TO-BE)
- `submitted`: wellness já enviado para esta sessão → readonly com resumo + `internal_load`.
- `window_expired`: após 24h da sessão → formulário desabilitado.
- `permission_error`: tentativa de registrar para outro atleta.

Evidências:
- `Hb Track - Frontend/src/app/(protected)/athlete/wellness-post/[sessionId]/WellnessPostClient.tsx`
- `Hb Track - Frontend/src/components/training/wellness/WellnessPostForm.tsx`

---

## SCREEN-TRAIN-020 — Detalhe/Cockpit da Sessão (Admin)

**Tipo:** Page  
**Rota:** `/training/sessions/[id]`  
**Fluxo:** FLOW-TRAIN-002, FLOW-TRAIN-004  
**Estado AS-IS:** EVIDENCIADO (parcial — AR_275)

### Seções do Ledger (obrigatórias)

| Seção | `data-test-id` | Descrição |
|---|---|---|
| Planned | `training-session-planned-section` | Plano original da sessão (exercícios, focos, metas) — imutável após schedule |
| Realized | `training-session-realized-section` | Execução real (presenças, exercícios realizados) |
| Adjustments | `training-session-adjustments-section` | Ajustes pós-sessão (append-only) |

### Regras normativas
- Status badge exibindo exclusivamente: `draft`, `scheduled`, `in_progress`, `pending_review`, `readonly`.
- Sem botões para transições automáticas (`scheduled→in_progress`, `in_progress→pending_review`).
- Seção Planned: imutável após `schedule` (sem edição inline).
- A UI deve suportar `presence_status = present|absent|justified` e respeitar `ck_attendance_absent_reason_null`:
  - `absent` ⇒ `reason_absence = NULL`
  - `justified` ⇒ `reason_absence != NULL` (TO-BE: required no frontend)

Evidências:
- `Hb Track - Frontend/src/app/(admin)/training/sessions/[id]/page.tsx` (AR_275)
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

---

# FASE_3 — Telas v1.3.0 (Atleta Pre-Session, Pending Queue, IA Coach)

> **Cross-ref:** INV-TRAIN-063..081 • CONTRACT-TRAIN-096..105 • FLOW-TRAIN-016..021

---

## SCREEN-TRAIN-022 — Visão Pré-Treino do Atleta

**Tipo:** Page  
**Rota:** `/athlete/training/[sessionId]`  
**Fluxo:** FLOW-TRAIN-016, FLOW-TRAIN-017, FLOW-TRAIN-021  
**Estado AS-IS:** GAP  

### Estados de UI

| Estado | Condição | Elementos visíveis |
|---|---|---|
| `loading` | Carregando dados da sessão | Skeleton/spinner |
| `wellness_blocked` | `can_see_full_content == false` | Prompt wellness + info parcial (data/hora/título) |
| `data` | Wellness OK, sessão futura/em andamento | Exercícios + mídia + foco + botão pre-confirm |
| `pre_confirmed` | Atleta já pré-confirmou | Badge "Presença pré-confirmada" (não oficial) |
| `readonly` | Sessão já fechada | Dados da sessão readonly + resultado presença |
| `error` | Falha de rede/permissão | Mensagem de erro |

### Regras normativas
1. **Wellness gate (INV-TRAIN-071, INV-TRAIN-076):** Se `wellness_status.can_see_full == false`, a tela DEVE:
   - Ocultar lista de exercícios detalhada.
   - Mostrar prompt informativo (não punitivo) para preenchimento de wellness.
   - Exibir apenas: título da sessão, data/hora, local.
2. **Pre-confirm (INV-TRAIN-063):** Botão "Confirmar presença" disponível APENAS antes do fechamento.
   - Label DEVE ser "Confirmar presença" (nunca "Marcar presente").
   - Após click, exibir badge "Pré-confirmado" com nota "(não oficial)".
3. **Mídia (INV-TRAIN-069):** Exercícios devem exibir thumbnail/vídeo quando disponível.
4. **Progress gate (INV-TRAIN-078):** Se tela incluir tab de "meu progresso", compliance de wellness é requisito.

### Contratos consumidos
- `CONTRACT-TRAIN-096` (preview do treino)
- `CONTRACT-TRAIN-097` (pre-confirm)
- `CONTRACT-TRAIN-105` (wellness content gate)

### Evidências
- (a criar — AR-TRAIN-019)

---

## SCREEN-TRAIN-023 — Fila de Pendências (Admin)

**Tipo:** Page
**Rota:** `/training/pending-queue`
**Fluxo:** FLOW-TRAIN-018
**Estado AS-IS:** EVIDENCIADO

### Estados de UI

| Estado | Condição | Elementos visíveis |
|---|---|---|
| `loading` | Carregando pendências | Skeleton/spinner |
| `empty` | Nenhuma pendência aberta | Mensagem "Nenhuma pendência — ótimo!" |
| `data` | Pendências abertas existem | Lista filtrada por equipe/sessão + ações |
| `error` | Falha de rede/permissão | Mensagem de erro |

### Regras normativas
1. **Separação (INV-TRAIN-066):** Pendências são entidade separada — NÃO são attendance nor alerts.
2. **Filtros:** Por equipe, por sessão de treino, por tipo de pendência (`attendance_mismatch`, `missing_wellness`, `late_arrival`).
3. **Ações por item:**
   - "Resolver" → abre modal com resolução textual + novo status (`present|absent|justified`).
   - "Solicitar colaboração" → envia notificação ao atleta para fornecer informação (INV-TRAIN-067).
4. **RBAC:** Apenas `treinador` e `coordenador` podem resolver. Atleta pode ver e colaborar, mas não resolver (INV-TRAIN-067).

### Contratos consumidos
- `CONTRACT-TRAIN-099` (listar pendências)
- `CONTRACT-TRAIN-100` (resolver pendência)

### Evidências
- `Hb Track - Frontend/src/app/(admin)/training/pending-queue/page.tsx`
- `Hb Track - Frontend/src/components/training/PendingQueueTable.tsx`

---

## SCREEN-TRAIN-024 — Chat IA do Atleta

**Tipo:** Page  
**Rota:** `/athlete/ai-chat/[sessionId]`  
**Fluxo:** FLOW-TRAIN-019  
**Estado AS-IS:** GAP  

### Estados de UI

| Estado | Condição | Elementos visíveis |
|---|---|---|
| `loading` | Carregando contexto da sessão | Skeleton/spinner |
| `data` | Chat ativo | Input de mensagem + histórico de conversa |
| `empty` | Primeira interação | Mensagem de boas-vindas + sugestões de perguntas |
| `error` | Falha de rede/LLM indisponível | Mensagem "Assistente indisponível, tente depois" |

### Regras normativas
1. **Sugestão, não ordem (INV-TRAIN-072):** Todas as respostas da IA DEVEM usar linguagem sugestiva.
   - Exemplos OK: "Que tal...", "Uma ideia seria...", "Considere..."
   - Exemplos PROIBIDOS: "Faça...", "Você deve...", "Execute..."
2. **Privacidade (INV-TRAIN-073):** IA NÃO acessa dados wellness individuais de outros atletas.
3. **Conteúdo educacional (INV-TRAIN-074):** Conteúdo educacional (ex: técnica de arremesso) deve ser acessível independente de dados pessoais.
4. **Disclaimer:** Toda resposta tipo `"suggestion"` deve ter disclaimer visível: "Consulte seu treinador antes de adotar mudanças."
5. **Feedback imediato (INV-TRAIN-077):** Resposta deve ser gerada em ≤ 15s. Se LLM demorar, mostrar streaming ou indicador de digitação.

### Contratos consumidos
- `CONTRACT-TRAIN-103` (chat IA atleta)

### Evidências
- (a criar — AR-TRAIN-021)

---

## SCREEN-TRAIN-025 — Sugestão IA para Treinador (Draft Modal)

**Tipo:** Modal  
**Rota:** N/A (modal sobre `/training/agenda` ou `/training/sessions/[id]/edit`)  
**Fluxo:** FLOW-TRAIN-020  
**Estado AS-IS:** GAP  

### Estados de UI

| Estado | Condição | Elementos visíveis |
|---|---|---|
| `loading` | IA gerando draft | Indicador de progresso "Gerando sugestão..." |
| `data` | Draft pronto | Preview da sessão sugerida + justificativa + form de edição |
| `editing` | Treinador editando draft | Form preenchido com dados IA, editável |
| `applied` | Draft aplicado | Confirmação "Sessão criada com sucesso" |
| `error` | Falha de rede/LLM | Mensagem "Não foi possível gerar sugestão" |

### Regras normativas
1. **Draft only (INV-TRAIN-075, INV-TRAIN-080):** IA NUNCA cria sessão publicada diretamente.
   - Modal DEVE exibir preview antes de qualquer "Aplicar".
   - Botão "Aplicar" DEVE abrir editor preenchido (não criar sessão diretamente).
2. **Justificativa obrigatória (INV-TRAIN-081):** A justificativa gerada pela IA DEVE ser visível no modal.
   - Se IA não gerar justificativa, backend DEVE rejeitar o draft (422).
3. **Editar antes (INV-TRAIN-075):** O treinador DEVE conseguir editar TODOS os campos antes de aplicar.
   - FE DEVE impedir "apply" sem exibição da tela de edição (mesmo sem mudanças).
4. **Privacidade (INV-TRAIN-079):** Se sugestão menciona dados de atletas, deve ser agregado (nunca individual identificável).

### Contratos consumidos
- `CONTRACT-TRAIN-101` (gerar draft)
- `CONTRACT-TRAIN-102` (aplicar draft)
- `CONTRACT-TRAIN-104` (pedir justificativa)

### Evidências
- (a criar — AR-TRAIN-021)
