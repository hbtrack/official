# TRAINING_USER_FLOWS.md — Fluxos de Usuário do Módulo TRAINING

Status: NORMATIVO_VIGENTE  
Versão: v1.5.0
Tipo de Documento: SSOT Normativo — User Flows
Módulo: TRAINING
Fase: FASE_2 + FASE_3 REAL — implementação concluída (2026-03-04). Itens pós-DONE: ver TRAINING_ROADMAP.md §POST-DONE.
Autoridade: NORMATIVO_TECNICO
Última revisão: 2026-03-05

> Changelog v1.5.0 (2026-03-05):
> - FLOW-TRAIN-018: GAP → EVIDENCIADO (pending-queue/page.tsx + PendingQueueTable.tsx + training-phase3.ts stubs)
> - FLOW-TRAIN-013: gap UUID (team_id como number) removido — corrigido em rankings.ts (team_id: string)
> - Índice expandido com FLOW-TRAIN-016..021 (FASE_3)

> Changelog v1.4.0 (2026-03-04):
> - Status: DRAFT → NORMATIVO_VIGENTE (FASE_2 + FASE_3 REAL concluídas, DONE_TRAINING_ATINGIDO)  
> - Fase atualizada: sem itens pendentes bloqueantes; HIP-TRAIN-002 RESOLVIDO por FLOW-TRAIN-016/021 + AR-TRAIN-057  

> Changelog v1.2.0 (2026-02-26):  
> - Adicionada Authority Matrix  
> - Adicionada convenção de Classification Tags  
> - Adicionado `decision_trace:` formal em FLOW-TRAIN-005/006/009/012/013  
> - Adicionados Negative Cases em fluxos críticos (005, 006, 009, 012, 013)  

> Changelog v1.1.0 (2026-02-25):  
> - DEC-TRAIN-001: FLOW-TRAIN-005/006 — regra self-only explícita, sem `athlete_id` no payload  
> - DEC-TRAIN-002: FLOW-TRAIN-005 — mapeamento FE→payload referenciado  
> - DEC-TRAIN-003: FLOW-TRAIN-013 — `CONTRACT-TRAIN-076` como canônico FE  
> - DEC-TRAIN-004: FLOW-TRAIN-012 — estado degradado sem worker  
> - DEC-TRAIN-EXB-*: FLOW-TRAIN-009 — expansão com scope/ACL/visibility/mídia/copy  

Dependências (leitura):
- `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
- `docs/hbtrack/PRD Hb Track.md`
- `Hb Track - Backend/docs/ssot/openapi.json`
- `Hb Track - Backend/docs/ssot/schema.sql`
- `Hb Track - Backend/app/api/v1/routers/*` (training/attendance/wellness/analytics)
- `Hb Track - Frontend/src/app/(admin)/training/*`
- `Hb Track - Frontend/src/app/(protected)/athlete/wellness-*/[sessionId]/*`

---

## Authority Matrix

| Aspecto | Regra |
|---|---|
| Fonte de verdade | Fluxos derivados de PRD + SSOT (schema/OpenAPI) + Decisões humanas (DEC-*) |
| Escrita normativa | **Arquiteto** — criar, alterar, remover fluxos e regras associadas |
| Proposta UX | **Designer UX** — propõe alterações via DEC |
| Somente leitura + GAP | Executor, Testador — leitura + registrar GAP |
| Precedência em conflito | DB > Services > OpenAPI > FE > PRD |

---

## RELAÇÃO COM O CONTRATO

Este documento descreve fluxos de interação do usuário.

Ele não define:

- endpoints
- request schemas
- response schemas
- tipos canônicos

Esses elementos são definidos exclusivamente em:

- `TRAINING_FRONT_BACK_CONTRACT.md`
- OpenAPI materializado (`Hb Track - Backend/docs/ssot/openapi.json`)

Regra:

Se um fluxo exigir alteração de contrato,
a mudança deve ocorrer primeiro no contrato e na spec OpenAPI.

---

## Convenção de Tags (Classification)

Cada fluxo (FLOW-*) neste documento é uma **unidade de afirmação testável** e recebe classificação:

| Tag | Significado |
|---|---|
| `[NORMATIVO]` | Fluxo/regra que DEVE ser respeitado. Fonte: DB, Service, DEC ou PRD explícito. |
| `[DESCRITIVO-AS-IS]` | Observação do estado atual (evidenciado no repo). Pode mudar. |
| `[HIPOTESE]` | Expectativa derivada do PRD/fluxos, mas não evidenciada no repo. |
| `[GAP]` | Lacuna identificada entre o normativo e o estado atual. |

**Aplicação neste documento:**
- Seções "Passos (TO-BE normativo)" → `[NORMATIVO]`.
- Seções "Gaps AS-IS" → `[GAP]` + `[DESCRITIVO-AS-IS]`.
- Seções "Exceções normativas" → `[NORMATIVO]`.
- Fluxos com `estado_asis: HIPOTESE` → `[HIPOTESE]`.

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

Definir os **fluxos canônicos** do módulo **TRAINING**, com rastreabilidade explícita para:
- Requisitos do PRD (RF/US),
- Invariantes (`INV-TRAIN-*`),
- Telas (`SCREEN-TRAIN-*`),
- Contratos front-back (`CONTRACT-TRAIN-*`).

Este documento é **TO-BE normativo** (o que o módulo deve suportar), e marca o estado atual como:
- `EVIDENCIADO` (há evidência objetiva no repo/SSOT),
- `PARCIAL` (há partes implementadas, mas há gaps de paridade FE↔BE ou contrato↔código),
- `HIPOTESE` (apenas PRD/expectativa; não evidenciado no repo),
- `BLOQUEADO` (dependência/decisão impede materialização completa).

---

## 2) Escopo

### 2.1 Dentro do escopo (TRAINING)
- Agenda semanal/mensal de treinos
- Sessões de treino (criar/editar/publicar/fechar/relatório)
- Presença (attendance) e estatísticas
- Wellness pré e pós-treino (submissão, deadlines, status)
- Planejamento: ciclos e microciclos
- Banco de exercícios + tags + favoritos
- Templates de sessão
- Analytics de treino (carga semanal, desvios, taxas de resposta)
- Rankings de wellness e top performers
- Alertas e sugestões (sobrecarga, baixa resposta, eficácia preventiva)

### 2.2 Fora do escopo (dependências)
- COMPETITIONS/SCOUT (partidas, eventos, scout em jogo)
- Auth “core” e gestão de usuários (exceto uso de permissões por fluxo)
- Modo offline (PRD menciona, mas não está materializado no repo atual)
- IA tática (recomendador de treinos) — PRD marca como futuro

---

## 3) Papéis (atores) e autorização (alto nível)

Papéis relevantes (PRD v2.2):
- **Dirigente**, **Coordenador**, **Treinador**: gerenciam treinos, analytics, planejamento e relatórios.
- **Atleta**: preenche wellness pré/pós (self-only) e consome rotas de atleta.
- **Super Admin**: bypass/escopo especial (não detalhado aqui).

Regra normativa:
- O enforcement de RBAC/escopo deve ocorrer em **contrato + backend** (dependente de `permission_dep/require_role`).
- Quando houver divergência FE↔BE sobre role/permission keys, registrar como `GAP` e materializar via AR de classe `E` (contrato) + `D` (UX).

---

## 4) Índice de fluxos (mapa de rastreabilidade)

| Flow ID | Nome | Ator Primário | Prioridade | Estado AS-IS | Telas | Contratos | Invariantes | PRD |
|---|---|---:|---:|---|---|---|---|---|
| FLOW-TRAIN-001 | Navegar agenda semanal/mensal | Treinador | P0 | EVIDENCIADO | SCREEN-TRAIN-001 | CONTRACT-TRAIN-001 | INV-TRAIN-006 | RF-003 |
| FLOW-TRAIN-002 | Criar sessão (draft) e publicar (scheduled) | Treinador | P0 | EVIDENCIADO | SCREEN-TRAIN-003, SCREEN-TRAIN-004 | CONTRACT-TRAIN-002, CONTRACT-TRAIN-006 | INV-TRAIN-001, INV-TRAIN-006 | US-001 |
| FLOW-TRAIN-003 | Editar sessão e compor treino (foco + exercícios + notas) | Treinador | P0 | EVIDENCIADO | SCREEN-TRAIN-004, SCREEN-TRAIN-005 | CONTRACT-TRAIN-004, CONTRACT-TRAIN-019..024 | INV-TRAIN-001, INV-TRAIN-004, INV-TRAIN-005 | RF-003 |
| FLOW-TRAIN-004 | Registrar presença digital (incl. justified) | Treinador | P0 | EVIDENCIADO | SCREEN-TRAIN-020 | CONTRACT-TRAIN-025..028 | INV-TRAIN-030, INV-TRAIN-016 | US-001 |
| FLOW-TRAIN-005 | Atleta preencher wellness pré (deadline 2h) | Atleta | P0 | EVIDENCIADO | SCREEN-TRAIN-018 | CONTRACT-TRAIN-030 | INV-TRAIN-002, INV-TRAIN-009 | US-002 |
| FLOW-TRAIN-006 | Atleta preencher wellness pós (janela 24h) | Atleta | P0 | EVIDENCIADO | SCREEN-TRAIN-019 | CONTRACT-TRAIN-036 | INV-TRAIN-003, INV-TRAIN-010, INV-TRAIN-021 | RF-004 |
| FLOW-TRAIN-007 | Treinador visualizar status wellness da sessão | Treinador | P1 | EVIDENCIADO | SCREEN-TRAIN-004 | CONTRACT-TRAIN-012 | INV-TRAIN-022, INV-TRAIN-026 | RF-004 |
| FLOW-TRAIN-008 | Planejar ciclos e microciclos | Treinador | P1 | EVIDENCIADO | SCREEN-TRAIN-007, SCREEN-TRAIN-008 | CONTRACT-TRAIN-040..052 | INV-TRAIN-037, INV-TRAIN-043 | RF-011 |
| FLOW-TRAIN-009 | Gerenciar banco de exercícios e favoritos | Treinador | P1 | EVIDENCIADO | SCREEN-TRAIN-010, SCREEN-TRAIN-011 | CONTRACT-TRAIN-053..062, 091..095 | INV-TRAIN-045, INV-TRAIN-047..053, INV-TRAIN-EXB-ACL-001..007 | (PRD: In Scope V1) |
| FLOW-TRAIN-010 | Gerenciar templates de sessão | Treinador | P1 | EVIDENCIADO | SCREEN-TRAIN-017 | CONTRACT-TRAIN-063..068 | INV-TRAIN-035 | (PRD: suporte operacional) |
| FLOW-TRAIN-011 | Visualizar analytics e desvios | Coordenador | P1 | EVIDENCIADO | SCREEN-TRAIN-012 | CONTRACT-TRAIN-069..071 | INV-TRAIN-020, INV-TRAIN-015 | US-003 |
| FLOW-TRAIN-012 | Exportar relatório (PDF) de analytics | Coordenador | P1 | EVIDENCIADO | SCREEN-TRAIN-012, SCREEN-TRAIN-013 | CONTRACT-TRAIN-086..089 | INV-TRAIN-012 | US-003, RF-012 |
| FLOW-TRAIN-013 | Visualizar rankings wellness e top performers | Dirigente | P1 | EVIDENCIADO | SCREEN-TRAIN-014, SCREEN-TRAIN-015 | CONTRACT-TRAIN-073..076 | INV-TRAIN-036, INV-TRAIN-027 | RF-008 |
| FLOW-TRAIN-014 | Visualizar eficácia preventiva | Coordenador | P2 | EVIDENCIADO | SCREEN-TRAIN-016 | CONTRACT-TRAIN-072 | INV-TRAIN-014, INV-TRAIN-023 | RF-008 |
| FLOW-TRAIN-015 | Gerenciar alertas e sugestões (apply/dismiss) | Coordenador | P2 | HIPOTESE | SCREEN-TRAIN-021 | CONTRACT-TRAIN-077..085 | INV-TRAIN-014, INV-TRAIN-023 | RF-013 |
| FLOW-TRAIN-016 | Atleta visualiza treino antes da sessão | Atleta | P1 | GAP | SCREEN-TRAIN-022 | CONTRACT-TRAIN-096, 105 | INV-TRAIN-068, 069, 071, 076 | — |
| FLOW-TRAIN-017 | Pré-confirmação de presença e presença oficial | Atleta/Treinador | P0 | GAP | SCREEN-TRAIN-022, 020 | CONTRACT-TRAIN-097, 098 | INV-TRAIN-063..065 | — |
| FLOW-TRAIN-018 | Treinador resolve fila de pendências | Treinador | P0 | EVIDENCIADO | SCREEN-TRAIN-023 | CONTRACT-TRAIN-099, 100 | INV-TRAIN-066, 067 | — |
| FLOW-TRAIN-019 | Atleta interage com coach virtual (IA) | Atleta | P2 | GAP | SCREEN-TRAIN-024 | CONTRACT-TRAIN-103 | INV-TRAIN-072..074, 077 | — |
| FLOW-TRAIN-020 | IA gera rascunho de treino para treinador editar | Treinador | P2 | GAP | SCREEN-TRAIN-025 | CONTRACT-TRAIN-101, 102, 104 | INV-TRAIN-075, 080, 081 | — |
| FLOW-TRAIN-021 | Wellness gate bloqueia conteúdo (atleta sem wellness) | Atleta | P1 | GAP | SCREEN-TRAIN-022 | CONTRACT-TRAIN-105 | INV-TRAIN-071, 076, 078 | — |

Notas:
- `FLOW-TRAIN-012` estava `BLOQUEADO`: routers de export existem, **habilitados** após AR_179+AR_180 (evidenciado) (ver `Hb Track - Backend/app/api/v1/api.py`).

---

## FLOW-TRAIN-001 — Navegar agenda semanal/mensal

```yaml
id: FLOW-TRAIN-001
atores:
  primario: treinador|coordenador
prioridade: P0
estado_asis: EVIDENCIADO
telas:
  - SCREEN-TRAIN-001  # /training/agenda (week|month via querystring)
contratos:
  - CONTRACT-TRAIN-001 # GET /training-sessions (lista/paginado)
invariantes_chave:
  - INV-TRAIN-006 # lifecycle status
evidencias:
  - Hb Track - Frontend/src/app/(admin)/training/agenda/AgendaClient.tsx
  - Hb Track - Frontend/src/lib/hooks/useSessions.ts
  - Hb Track - Backend/app/api/v1/routers/training_sessions.py
```

### Passos (happy path)
1. Usuário acessa `SCREEN-TRAIN-001` (`/training/agenda`).
2. Seleciona equipe (team selector) e o sistema atualiza a URL (`teamId=`) e busca sessões via `CONTRACT-TRAIN-001`.
3. Alterna `view=week|month` (estado de UI) mantendo o time selecionado.
4. Usuário clica em uma sessão:
   - se status = `readonly` → navega para `SCREEN-TRAIN-006` (relatório),
   - caso contrário → abre `SCREEN-TRAIN-004` (editor modal).

### Exceções mínimas
- Sem sessão de auth → redirect para `/signin` (guard server-side).
- Time não selecionado → UI deve guiar seleção (não bloquear rota).

---

## FLOW-TRAIN-002 — Criar sessão (draft) e publicar (scheduled)

```yaml
id: FLOW-TRAIN-002
atores:
  primario: treinador|coordenador
prioridade: P0
estado_asis: EVIDENCIADO
telas:
  - SCREEN-TRAIN-003 # CreateSessionModal
  - SCREEN-TRAIN-004 # SessionEditorModal
contratos:
  - CONTRACT-TRAIN-002 # POST /training-sessions
  - CONTRACT-TRAIN-006 # POST /training-sessions/{id}/publish
invariantes_chave:
  - INV-TRAIN-001 # focos somam <= 120
  - INV-TRAIN-006 # status lifecycle
evidencias:
  - Hb Track - Frontend/src/components/training/modals/CreateSessionModal.tsx
  - Hb Track - Backend/app/api/v1/routers/training_sessions.py
```

### Passos (happy path)
1. Em `SCREEN-TRAIN-001`, usuário aciona “Criar sessão”.
2. Em `SCREEN-TRAIN-003`, preenche: equipe (`team_id`), data/hora (`session_at`), tipo (`session_type`), objetivo, duração/local (quando aplicável).
3. O sistema cria sessão via `CONTRACT-TRAIN-002` com status `draft`.
4. Usuário abre a sessão e, ao concluir, executa “Agendar treino” → `CONTRACT-TRAIN-006` (transição para `scheduled`).

### Exceções mínimas
- Soma de focos > 120% → bloqueio (422/validation_error) conforme `INV-TRAIN-001`.
- Temporada bloqueada/interrompida → bloqueio (regra PRD RF5.2; checar enforcement no service).

---

## FLOW-TRAIN-003 — Editar sessão e compor treino (foco + exercícios + notas)

```yaml
id: FLOW-TRAIN-003
atores:
  primario: treinador|coordenador
prioridade: P0
estado_asis: EVIDENCIADO
telas:
  - SCREEN-TRAIN-004 # Editor modal
  - SCREEN-TRAIN-005 # Editor full page (/training/sessions/[id]/edit)
contratos:
  - CONTRACT-TRAIN-004 # PATCH /training-sessions/{id}
  - CONTRACT-TRAIN-019 # GET /training-sessions/{id}/exercises
  - CONTRACT-TRAIN-020 # POST /training-sessions/{id}/exercises
  - CONTRACT-TRAIN-021 # POST /training-sessions/{id}/exercises/bulk
  - CONTRACT-TRAIN-022 # PATCH /training-sessions/exercises/{session_exercise_id}
  - CONTRACT-TRAIN-023 # PATCH /training-sessions/{id}/exercises/reorder
  - CONTRACT-TRAIN-024 # DELETE /training-sessions/exercises/{session_exercise_id}
invariantes_chave:
  - INV-TRAIN-004 # janela de edição por papel/estado
  - INV-TRAIN-005 # imutabilidade 60 dias
  - INV-TRAIN-001 # focos <= 120
  - INV-TRAIN-045 # order_index unique em session_exercises
evidencias:
  - Hb Track - Frontend/src/app/(admin)/training/sessions/[id]/edit/SessionEditClient.tsx
  - Hb Track - Backend/app/api/v1/routers/session_exercises.py
  - Hb Track - Backend/app/services/training_session_service.py
```

### Passos (happy path)
1. Usuário abre editor (modal ou página) de uma sessão `draft|scheduled`.
2. Ajusta metadados (objetivo, local, duração), salva via `CONTRACT-TRAIN-004`.
3. Define distribuição de focos (validação local) e salva via `CONTRACT-TRAIN-004`.
4. Adiciona exercícios (drag-and-drop) via `CONTRACT-TRAIN-020`/`021`, reordena via `CONTRACT-TRAIN-023`.

### Exceções mínimas
- Sessão em `in_progress|pending_review|readonly` → edição deve ser bloqueada conforme `INV-TRAIN-029` e `INV-TRAIN-006`.
- Sessão `scheduled` após `session_at - 10min` → bloqueio para autor (ver `INV-TRAIN-004`).

---

## FLOW-TRAIN-004 — Registrar presença digital (incl. justified)

```yaml
id: FLOW-TRAIN-004
atores:
  primario: treinador|coordenador
prioridade: P0
estado_asis: EVIDENCIADO
telas:
  - SCREEN-TRAIN-020 # Presenças (placeholder) ou tab de presença no editor
contratos:
  - CONTRACT-TRAIN-025 # GET /training_sessions/{id}/attendance
  - CONTRACT-TRAIN-027 # POST /training_sessions/{id}/attendance/batch
  - CONTRACT-TRAIN-028 # GET /training_sessions/{id}/attendance/statistics
invariantes_chave:
  - INV-TRAIN-016 # auth + rota scoped não exposta
  - INV-TRAIN-030 # correction fields quando source=correction
evidencias:
  - Hb Track - Backend/app/api/v1/routers/attendance.py
  - Hb Track - Frontend/src/components/training/attendance/AttendanceTab.tsx (não integrado)
  - Hb Track - Frontend/src/app/(admin)/training/presencas/page.tsx (placeholder)
```

> Promovido por Kanban+evidência: AR_176 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_176/executor_main.log

### Passos (TO-BE normativo)
1. Usuário abre a sessão e acessa “Presenças”.
2. O sistema carrega roster (team_registrations ativos) e presenças já marcadas via `CONTRACT-TRAIN-025`.
3. Usuário marca status por atleta:
   - `present`,
   - `absent`,
   - `justified` (exige `reason_absence`).
4. Usuário salva em batch via `CONTRACT-TRAIN-027`; UI atualiza estatísticas via `CONTRACT-TRAIN-028`.

### Gaps AS-IS (bloqueantes)
- UI de presenças não materializada na navegação principal (há placeholder; `AttendanceTab` existe mas não está em uso).
- Frontend tipa `PresenceStatus` sem `justified` e envia `reason_absence` com `absent`, o que viola constraint DB (`ck_attendance_absent_reason_null`).

---

## FLOW-TRAIN-005 — Atleta preencher wellness pré (deadline 2h)

```yaml
id: FLOW-TRAIN-005
atores:
  primario: atleta
prioridade: P0
estado_asis: EVIDENCIADO
decision_trace: [DEC-TRAIN-001, DEC-TRAIN-002]
telas:
  - SCREEN-TRAIN-018 # /athlete/wellness-pre/[sessionId]
contratos:
  - CONTRACT-TRAIN-030 # POST /wellness-pre/training_sessions/{id}/wellness_pre
invariantes_chave:
  - INV-TRAIN-002 # deadline 2h antes
  - INV-TRAIN-009 # UNIQUE athlete×session
evidencias:
  - Hb Track - Frontend/src/app/(protected)/athlete/wellness-pre/[sessionId]/WellnessPreClient.tsx
  - Hb Track - Frontend/src/components/training/wellness/WellnessPreForm.tsx
  - Hb Track - Backend/app/api/v1/routers/wellness_pre.py
```

> Promovido por Kanban+evidência: AR_171 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_171/executor_main.log

### Passos (TO-BE normativo)

> **DEC-TRAIN-001 (normativo):** O payload de wellness pré do atleta NÃO DEVE conter
> `athlete_id`. Backend infere do token JWT. Ver CONTRACT §4.5.

1. Atleta acessa `SCREEN-TRAIN-018` via link para uma sessão agendada.
2. Sistema exibe resumo da sessão e countdown de deadline (até `session_at - 2h`).
3. Atleta preenche campos do **schema real** (PRD US-002):
   - `stress_level` (0–10; semântica inversa do PRD: 0=ótimo),
   - `sleep_quality` (1–5),
   - `sleep_hours` (0–24, decimal),
   - `fatigue_pre` (0–10),
   - `muscle_soreness` (0–10),
   - opcionais SSOT: `readiness_score`, `menstrual_cycle_phase`, `notes`.
4. **FE NÃO inclui `athlete_id` no payload** (DEC-TRAIN-001).
5. FE mapeia sliders/UI components conforme tabela canônica (CONTRACT §4.4, DEC-TRAIN-002).
6. Submete via `CONTRACT-TRAIN-030`.

### Exceções normativas (DEC-TRAIN-001)
- Se FE enviar `athlete_id` no payload → backend DEVE ignorar ou retornar 422.
- Staff/terceiros registrando wellness de outro atleta → endpoint/escopo separado com auditoria (INV-TRAIN-026).

### Gaps AS-IS (bloqueantes)
- Frontend chama endpoints inexistentes/errados (`/wellness_pre`, `/wellness_pre/sessions/...`) em `Hb Track - Frontend/src/lib/api/wellness.ts` (esperado: prefix `/wellness-pre/...`).
- UI coleta campos não alinhados ao schema (`fatigue_level`, `mood`, `readiness`) e não coleta `sleep_hours`.

### Casos Negativos (anti-exemplos) `[NORMATIVO]`

| # | Cenário negativo | Resultado esperado | DEC/INV |
|---|---|---|---|
| NEG-005-1 | Atleta envia payload com `athlete_id` explícito (tentativa de impersonação) | Backend retorna **422** ou ignora o campo; NUNCA usa o valor enviado | DEC-TRAIN-001 |
| NEG-005-2 | Atleta submete wellness pré **após** deadline (session_at - 2h) | Backend retorna **403/422** com mensagem de deadline expirado | INV-TRAIN-002 |
| NEG-005-3 | Atleta submete wellness pré **duplicado** (mesma sessão) | Backend retorna **409 Conflict** (unique constraint athlete×session) | INV-TRAIN-009 |
| NEG-005-4 | FE mapeia slider "mood" para campo inexistente no schema | Validação falha **422** — campo não reconhecido | DEC-TRAIN-002 |

---

## FLOW-TRAIN-006 — Atleta preencher wellness pós (janela 24h)

```yaml
id: FLOW-TRAIN-006
atores:
  primario: atleta
prioridade: P0
estado_asis: EVIDENCIADO
decision_trace: [DEC-TRAIN-001]
telas:
  - SCREEN-TRAIN-019 # /athlete/wellness-post/[sessionId]
contratos:
  - CONTRACT-TRAIN-036 # POST /wellness-post/training_sessions/{id}/wellness_post
invariantes_chave:
  - INV-TRAIN-003 # edit window 24h
  - INV-TRAIN-010 # UNIQUE athlete×session
  - INV-TRAIN-021 # internal_load trigger (minutes_effective × rpe)
evidencias:
  - Hb Track - Frontend/src/app/(protected)/athlete/wellness-post/[sessionId]/WellnessPostClient.tsx
  - Hb Track - Frontend/src/components/training/wellness/WellnessPostForm.tsx
  - Hb Track - Backend/app/api/v1/routers/wellness_post.py
```

> Promovido por Kanban+evidência: AR_187 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_187/executor_main.log

### Passos (TO-BE normativo)

> **DEC-TRAIN-001 (normativo):** O payload de wellness pós do atleta NÃO DEVE conter
> `athlete_id`. Backend infere do token JWT. Ver CONTRACT §4.5.

1. Atleta acessa `SCREEN-TRAIN-019` após o treino.
2. Preenche: `session_rpe`, `fatigue_after`, `mood_after`, `muscle_soreness_after` (opcional), `minutes_effective` (quando aplicável), `notes` (opcional).
3. **FE NÃO inclui `athlete_id` no payload** (DEC-TRAIN-001).
4. Submete via `CONTRACT-TRAIN-036`.
5. Sistema calcula `internal_load` automaticamente (trigger) e invalida caches de analytics quando aplicável.

### Exceções normativas (DEC-TRAIN-001)
- Se FE enviar `athlete_id` no payload → backend DEVE ignorar ou retornar 422.
- Staff registrando wellness de outro atleta → endpoint separado com RBAC e auditoria.

### Gaps AS-IS (bloqueantes)
- Mesmo problema de endpoint base do módulo wellness no frontend (`/wellness_post` vs `/wellness-post/...`).
- Badge/progresso mensal na UI está hardcoded (não evidenciado como contrato consumido).

### Casos Negativos (anti-exemplos) `[NORMATIVO]`

| # | Cenário negativo | Resultado esperado | DEC/INV |
|---|---|---|---|
| NEG-006-1 | Atleta envia payload com `athlete_id` explícito | Backend retorna **422** ou ignora o campo | DEC-TRAIN-001 |
| NEG-006-2 | Atleta submete wellness pós **após** janela de 24h | Backend retorna **403/422** — edição fora da janela | INV-TRAIN-003 |
| NEG-006-3 | Atleta submete wellness pós **duplicado** (mesma sessão) | Backend retorna **409 Conflict** (unique athlete×session) | INV-TRAIN-010 |

---

## FLOW-TRAIN-007 — Treinador visualizar status wellness da sessão

```yaml
id: FLOW-TRAIN-007
atores:
  primario: treinador|coordenador
prioridade: P1
estado_asis: EVIDENCIADO
telas:
  - SCREEN-TRAIN-004 # editor modal (ponto de entrada natural)
contratos:
  - CONTRACT-TRAIN-012 # GET /training-sessions/{id}/wellness-status
invariantes_chave:
  - INV-TRAIN-022 # cache invalidation wellness_post
  - INV-TRAIN-026 # LGPD access logging (staff lendo dados)
evidencias:
  - Hb Track - Backend/app/api/v1/routers/training_sessions.py (wellness-status)
```

> Promovido por Kanban+evidência: AR_177 + AR_178 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_177/executor_main.log, docs/hbtrack/evidence/AR_178/executor_main.log

### Passos (TO-BE normativo)
1. Treinador abre detalhes da sessão.
2. Sistema consulta `CONTRACT-TRAIN-012` para obter por atleta: status (pre/post/ausente), sinais críticos e agregados.
3. UI destaca pendências e possíveis alertas.

### Gap AS-IS
- Não há tela/tab evidenciada consumindo esse endpoint no frontend atual.

---

## FLOW-TRAIN-008 — Planejar ciclos e microciclos

```yaml
id: FLOW-TRAIN-008
atores:
  primario: treinador|coordenador
prioridade: P1
estado_asis: EVIDENCIADO
telas:
  - SCREEN-TRAIN-007 # /training/planejamento
  - SCREEN-TRAIN-008 # CreateCycleWizard, CopyWeekModal
contratos:
  - CONTRACT-TRAIN-040..045 # training-cycles
  - CONTRACT-TRAIN-046..052 # training-microcycles
  - CONTRACT-TRAIN-010 # POST /training-sessions/copy-week
invariantes_chave:
  - INV-TRAIN-037 # cycle dates constraints
  - INV-TRAIN-043 # microcycle date check
  - INV-TRAIN-001 # focos <= 120 (planejado também)
evidencias:
  - Hb Track - Frontend/src/app/(admin)/training/planejamento/PlanejamentoClient.tsx
  - Hb Track - Backend/app/api/v1/routers/training_cycles.py
  - Hb Track - Backend/app/api/v1/routers/training_microcycles.py
```

### Passos (happy path)
1. Usuário seleciona equipe e acessa planejamento.
2. Cria macrociclo/mesociclo via wizard (datas e hierarquia validadas) → `CONTRACT-TRAIN-042`.
3. Cria microciclos semanais (datas, focos planejados) → `CONTRACT-TRAIN-048`.
4. Associa sessões a microciclo (via criação/edição de sessão).
5. (Opcional) Copia sessões de uma semana para outra via `CONTRACT-TRAIN-010`.

---

## FLOW-TRAIN-009 — Gerenciar banco de exercícios e favoritos

```yaml
id: FLOW-TRAIN-009
atores:
  primario: treinador|coordenador
prioridade: P1
estado_asis: EVIDENCIADO (CRUD base) / GAP (scope/ACL/media/copy)
decision_trace: [DEC-TRAIN-EXB-001, DEC-TRAIN-EXB-001B, DEC-TRAIN-EXB-002, DEC-TRAIN-EXB-RBAC-001]
telas:
  - SCREEN-TRAIN-010 # /training/exercise-bank
  - SCREEN-TRAIN-011 # modais create/edit/details
contratos:
  - CONTRACT-TRAIN-053..062 # exercises + tags + favorites (existentes)
  - CONTRACT-TRAIN-091..095 # ACL + visibility + copy (novos, GAP)
invariantes_chave:
  - INV-TRAIN-045 # order_index unique em session_exercises
  - INV-TRAIN-047 # exercise scope (SYSTEM|ORG)
  - INV-TRAIN-048 # SYSTEM imutável para org users
  - INV-TRAIN-049 # ORG exercise single org
  - INV-TRAIN-050 # favorite unique per user×exercise
  - INV-TRAIN-051 # catalog visibility scoped
  - INV-TRAIN-052 # exercise media valid type
  - INV-TRAIN-053 # soft-delete no break historic
  - INV-TRAIN-EXB-ACL-001..007 # ACL invariants
evidencias:
  - Hb Track - Frontend/src/app/(admin)/training/exercise-bank/page.tsx
  - Hb Track - Backend/app/api/v1/routers/exercises.py
```

### Passos (happy path — CRUD base, EVIDENCIADO)
1. Usuário acessa banco de exercícios e filtra por busca/tags/categoria/favoritos.
2. Staff cria/edita exercícios e tags; marca favoritos.
3. Usuário arrasta exercícios para compor sessão (integra com `FLOW-TRAIN-003`).

### Passos (scope + visibility + ACL — DEC-TRAIN-EXB-001/001B, TO-BE normativo)
4. Ao listar (`CONTRACT-TRAIN-053`), o catálogo exibe:
   - Exercícios SYSTEM (visíveis para todos, imutáveis para org users).
   - Exercícios ORG da própria organização com `visibility_mode = org_wide`.
   - Exercícios ORG da própria org com `visibility_mode = restricted` **apenas se o usuário é creator ou está na ACL**.
5. Ao criar exercício (`CONTRACT-TRAIN-054`):
   - Staff de org cria com scope=ORG (padrão), `organization_id` inferido do token.
   - Admin global pode criar com scope=SYSTEM.
   - `visibility_mode` padrão = `restricted` (pode ser alterado para `org_wide`).
6. Ao editar exercício ORG (`CONTRACT-TRAIN-056`):
   - Apenas creator ou role "Treinador" da mesma org (DEC-TRAIN-RBAC-001).
   - Exercícios SYSTEM → 403 para org users (INV-TRAIN-048).

### Passos (ACL management — DEC-TRAIN-EXB-002, TO-BE normativo)
7. Creator de exercício ORG com `restricted` acessa painel de ACL via UI:
   - Lista usuários com acesso (`CONTRACT-TRAIN-092`).
   - Adiciona usuário da mesma org (`CONTRACT-TRAIN-093`); cross-org → 422.
   - Remove usuário (`CONTRACT-TRAIN-094`).
8. Ao alterar `visibility_mode` (`CONTRACT-TRAIN-091`):
   - `restricted → org_wide`: todos da org veem; ACL mantida mas irrelevante.
   - `org_wide → restricted`: apenas creator e ACL explícita veem.

### Passos (copy SYSTEM→ORG — DEC-TRAIN-EXB-001, TO-BE normativo)
9. Usuário visualiza exercício SYSTEM e aciona "Copiar para minha org" (`CONTRACT-TRAIN-095`).
10. Sistema cria cópia como scope=ORG, `created_by` do token, `visibility_mode` padrão = `restricted`.
11. Exercício SYSTEM original permanece inalterado.

### Passos (mídia — DEC-TRAIN-EXB-001, TO-BE normativo)
12. Ao criar/editar exercício, usuário pode anexar mídia (imagem, vídeo, documento).
13. Tipo de mídia validado: IMAGE|VIDEO|DOCUMENT (INV-TRAIN-052).
14. UI exibe preview/thumbnail quando disponível.

### Passos (favoritos — existente)
15. Usuário marca/desmarca favorito (CONTRACT-TRAIN-061/062).
16. Unique constraint `(user_id, exercise_id)` → duplicata retorna 409 (INV-TRAIN-050).

### Passos (soft-delete — DEC-TRAIN-EXB-001, TO-BE normativo)
17. Ao excluir exercício ORG, soft-delete com reason pair.
18. Sessões históricas que referenciavam esse exercício continuam legíveis (INV-TRAIN-053, INV-TRAIN-EXB-ACL-007).

### Casos Negativos (anti-exemplos) `[NORMATIVO]`

| # | Cenário negativo | Resultado esperado | DEC/INV |
|---|---|---|---|
| NEG-009-1 | Usuário fora da ACL tenta acessar exercício ORG restricted | Exercício **não aparece** no catálogo; acesso direto retorna **403** | DEC-TRAIN-EXB-001B, INV-TRAIN-EXB-ACL-001 |
| NEG-009-2 | Usuário tenta adicionar à ACL um `user_id` de **outra org** | Backend retorna **422** (cross-org bloqueado) | INV-TRAIN-EXB-ACL-003 |
| NEG-009-3 | Org user tenta editar exercício SYSTEM | Backend retorna **403** (SYSTEM imutável para org users) | INV-TRAIN-048, DEC-TRAIN-RBAC-001 |
| NEG-009-4 | Usuário tenta gerenciar ACL em exercício com `visibility_mode = org_wide` | Backend retorna **409 Conflict** ("ACL not applicable for org_wide") | INV-TRAIN-EXB-ACL-002 |
| NEG-009-5 | Duplicata de favorito `(user_id, exercise_id)` | Backend retorna **409 Conflict** | INV-TRAIN-050 |

---

## FLOW-TRAIN-010 — Gerenciar templates de sessão

```yaml
id: FLOW-TRAIN-010
atores:
  primario: treinador|coordenador
prioridade: P1
estado_asis: EVIDENCIADO
telas:
  - SCREEN-TRAIN-017 # /training/configuracoes
contratos:
  - CONTRACT-TRAIN-063..068
invariantes_chave:
  - INV-TRAIN-035 # unique name por org + limite 50
evidencias:
  - Hb Track - Frontend/src/app/(admin)/training/configuracoes/ConfiguracoesClient.tsx
  - Hb Track - Backend/app/api/v1/routers/session_templates.py
```

---

## FLOW-TRAIN-011 — Visualizar analytics e desvios

```yaml
id: FLOW-TRAIN-011
atores:
  primario: coordenador|dirigente|treinador
prioridade: P1
estado_asis: EVIDENCIADO
telas:
  - SCREEN-TRAIN-012 # /training/analytics
contratos:
  - CONTRACT-TRAIN-069..071
invariantes_chave:
  - INV-TRAIN-015 # exposure analytics endpoints
  - INV-TRAIN-020 # cache invalidation triggers
evidencias:
  - Hb Track - Frontend/src/app/(admin)/training/analytics/AnalyticsClient.tsx
  - Hb Track - Backend/app/api/v1/routers/training_analytics.py
```

---

## FLOW-TRAIN-012 — Exportar relatório (PDF) de analytics

```yaml
id: FLOW-TRAIN-012
atores:
  primario: coordenador|dirigente
prioridade: P1
estado_asis: EVIDENCIADO
decision_trace: [DEC-TRAIN-004]
telas:
  - SCREEN-TRAIN-012 # /training/analytics (entrada)
  - SCREEN-TRAIN-013 # ExportPDFModal
contratos:
  - CONTRACT-TRAIN-086 # POST /analytics/export-pdf
  - CONTRACT-TRAIN-087 # GET /analytics/exports/{job_id}
  - CONTRACT-TRAIN-088 # GET /analytics/exports
  - CONTRACT-TRAIN-089 # GET /analytics/export-rate-limit
invariantes_chave:
  - INV-TRAIN-012 # rate limit export
evidencias:
  - Hb Track - Frontend/src/components/training/analytics/ExportPDFModal.tsx
  - Hb Track - Backend/app/api/v1/api.py (exports desabilitado)
```

> Promovido por Kanban+evidência: AR_179 + AR_180 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_179/executor_main.log, docs/hbtrack/evidence/AR_180/executor_main.log

Regra normativa:
- O fluxo só pode ser marcado como `EVIDENCIADO` quando o contrato de export e o job assíncrono estiverem expostos e testados.

### Estado Degradado (DEC-TRAIN-004 — normativo)

> Quando os contratos forem habilitados e o worker Celery/Redis NÃO estiver disponível:

1. Backend retorna **202 Accepted** com `{"status": "queued", "degraded": true}` (não 500/503).
2. FE exibe **banner/toast de degradação** em SCREEN-TRAIN-013 ("Export pode levar mais tempo").
3. FE NÃO bloqueia a UI — usuário pode continuar navegando.
4. Polling via `CONTRACT-TRAIN-087` continua com timeout estendido.
5. Rate limit (`CONTRACT-TRAIN-089`) DEVE ser respeitado mesmo em estado degradado.

**Invariantes:** INV-TRAIN-012.  
**Tela:** SCREEN-TRAIN-013 deve mostrar indicador de degradação.

### Casos Negativos (anti-exemplos) `[NORMATIVO]`

| # | Cenário negativo | Resultado esperado | DEC/INV |
|---|---|---|---|
| NEG-012-1 | Worker Celery/Redis **indisponível** e backend retorna 500/503 | **PROIBIDO** — deve retornar **202 Accepted** + `{"degraded": true}` | DEC-TRAIN-004 |
| NEG-012-2 | FE bloqueia UI completamente quando recebe `degraded: true` | **PROIBIDO** — FE deve exibir banner amigável, manter navegação | DEC-TRAIN-004 |
| NEG-012-3 | Usuário excede rate limit de export diário | Backend retorna **429 Too Many Requests** | INV-TRAIN-012 |

---

## FLOW-TRAIN-013 — Visualizar rankings wellness e top performers

```yaml
id: FLOW-TRAIN-013
atores:
  primario: dirigente|coordenador|treinador
prioridade: P1
estado_asis: EVIDENCIADO
decision_trace: [DEC-TRAIN-003]
telas:
  - SCREEN-TRAIN-014 # /training/rankings
  - SCREEN-TRAIN-015 # /training/top-performers/[teamId]
contratos:
  - CONTRACT-TRAIN-073..076
invariantes_chave:
  - INV-TRAIN-036 # unique ranking (team_id, month_reference)
  - INV-TRAIN-027 # refresh rankings task
evidencias:
  - Hb Track - Frontend/src/app/(admin)/training/rankings/RankingsClient.tsx
  - Hb Track - Frontend/src/app/(admin)/training/top-performers/[teamId]/TopPerformersClient.tsx
  - Hb Track - Backend/app/api/v1/routers/analytics.py
  - Hb Track - Backend/app/api/v1/routers/teams.py (/wellness-top-performers)
```

> Promovido por Kanban+evidência: AR_181 + AR_182 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_181/executor_main.log, docs/hbtrack/evidence/AR_182/executor_main.log

### Regra Canônica (DEC-TRAIN-003 — normativo)

> **`CONTRACT-TRAIN-076`** é o **endpoint canônico** que o FE deve consumir para a **tela principal
> de top performers** (SCREEN-TRAIN-015).
>
> **`CONTRACT-TRAIN-075`** serve apenas como **drilldown especializado** (atletas com >90% de
> taxa de resposta). O FE NÃO DEVE usar `CONTRACT-TRAIN-075` como fonte primária da listagem.

### Passos (TO-BE normativo)
1. Usuário acessa SCREEN-TRAIN-014 (rankings) e seleciona equipe/mês.
2. Ranking listado via `CONTRACT-TRAIN-073` (GET wellness-rankings).
3. Usuário clica em equipe para ver top performers → SCREEN-TRAIN-015.
4. **FE consome `CONTRACT-TRAIN-076`** (canônico) para montar a listagem principal.
5. (Opcional) Usuário aciona drilldown >90% → `CONTRACT-TRAIN-075`.

### Casos Negativos (anti-exemplos) `[NORMATIVO]`

| # | Cenário negativo | Resultado esperado | DEC/INV |
|---|---|---|---|
| NEG-013-1 | FE usa `CONTRACT-TRAIN-075` (`/athletes-90plus`) como **fonte primária** da listagem top performers | **PROIBIDO** — FE DEVE usar `CONTRACT-TRAIN-076` (canônico) | DEC-TRAIN-003 |
| NEG-013-2 | FE usa `team_id` como `number`/`parseInt` em vez de UUID | Request falha ou retorna dados errados — DEVE usar UUID string | GAP-CONTRACT-2 |

---

## FLOW-TRAIN-014 — Visualizar eficácia preventiva

```yaml
id: FLOW-TRAIN-014
atores:
  primario: coordenador|treinador
prioridade: P2
estado_asis: EVIDENCIADO
telas:
  - SCREEN-TRAIN-016 # /training/eficacia-preventiva
contratos:
  - CONTRACT-TRAIN-072 # GET /analytics/team/{team_id}/prevention-effectiveness
invariantes_chave:
  - INV-TRAIN-014 # threshold multiplier
  - INV-TRAIN-023 # overload alert trigger (observável via dados)
evidencias:
  - Hb Track - Frontend/src/app/(admin)/training/eficacia-preventiva/PreventionDashboardClient.tsx
  - Hb Track - Backend/app/api/v1/routers/training_analytics.py
```

---

## FLOW-TRAIN-015 — Gerenciar alertas e sugestões (apply/dismiss)

```yaml
id: FLOW-TRAIN-015
atores:
  primario: coordenador|treinador
prioridade: P2
estado_asis: HIPOTESE
telas:
  - SCREEN-TRAIN-021 # (a definir) Central de alertas/sugestões
contratos:
  - CONTRACT-TRAIN-077..085
invariantes_chave:
  - INV-TRAIN-014 # threshold multiplier
  - INV-TRAIN-023 # overload alerts on wellness_post
evidencias:
  - Hb Track - Backend/app/api/v1/routers/training_alerts_step18.py
```

Regra normativa:
- Este fluxo só pode ser marcado como `EVIDENCIADO` quando houver UI consumindo os endpoints de alertas/sugestões com RBAC correto e rastreabilidade de ação (apply/dismiss).

---

# FASE_3 — Fluxos v1.3.0 (Presença Oficial, Atleta Pre-Session, Pending Queue, IA Coach, Wellness Gate)

> **Cross-ref:** INV-TRAIN-063..081 • CONTRACT-TRAIN-096..105

---

## FLOW-TRAIN-016 — Atleta visualiza treino antes da sessão

```yaml
id: FLOW-TRAIN-016
atores:
  primario: atleta
prioridade: P1
estado_asis: GAP
telas:
  - SCREEN-TRAIN-022 # /athlete/training/[sessionId]
contratos:
  - CONTRACT-TRAIN-096 # GET /athlete/training-sessions/{session_id}/preview
  - CONTRACT-TRAIN-105 # GET /athlete/wellness-content-gate/{session_id}
invariantes_chave:
  - INV-TRAIN-068 # atleta vê treino antes
  - INV-TRAIN-069 # mídia acessível ao atleta
  - INV-TRAIN-071 # wellness missing bloqueia conteúdo completo
  - INV-TRAIN-076 # wellness obrigatório
evidencias: []
```

### Passos (happy path)
1. Atleta abre tela do treino agendado (SCREEN-TRAIN-022).
2. FE chama `CONTRACT-TRAIN-105` (wellness content gate) para verificar se atleta tem wellness pré preenchido.
3. **Se `has_wellness == true`**: FE chama `CONTRACT-TRAIN-096` (preview completo) → exibe exercícios, mídia, foco.
4. **Se `has_wellness == false`**: FE mostra conteúdo parcial + prompt "Preencha seu wellness para ver o treino completo" (INV-TRAIN-071).
5. Atleta pode navegar para preenchimento de wellness (FLOW-TRAIN-005).

### Casos Negativos (anti-exemplos) `[NORMATIVO]`

| # | Cenário negativo | Resultado esperado | DEC/INV |
|---|---|---|---|
| NEG-016-1 | Atleta sem wellness tenta ver exercícios detalhados | Conteúdo bloqueado — FE mostra prompt de wellness | INV-TRAIN-071 |
| NEG-016-2 | Atleta de outra equipe tenta acessar preview | 403 Forbidden | INV-TRAIN-016 |

---

## FLOW-TRAIN-017 — Pré-confirmação de presença e presença oficial no fechamento

```yaml
id: FLOW-TRAIN-017
atores:
  primario: atleta (pre-confirm)
  secundario: treinador (presença oficial)
prioridade: P0
estado_asis: GAP
telas:
  - SCREEN-TRAIN-022 # /athlete/training/[sessionId] (botão pre-confirm)
  - SCREEN-TRAIN-020 # /training/presencas (presença oficial pelo coach)
contratos:
  - CONTRACT-TRAIN-097 # POST /training-sessions/{session_id}/pre-confirm
  - CONTRACT-TRAIN-098 # POST /training-sessions/{session_id}/close (com attendance batch)
invariantes_chave:
  - INV-TRAIN-063 # pre-confirm não é oficial
  - INV-TRAIN-064 # presença oficial só no fechamento
  - INV-TRAIN-065 # fechamento permite inconsistência como pendência
evidencias: []
```

### Passos (happy path)
1. Atleta abre treino agendado e clica "Confirmar presença" (pre-confirm).
2. FE chama `CONTRACT-TRAIN-097` → backend registra `pre_confirmed = true`, **sem marcar como presente oficialmente**.
3. FE exibe label "Presença confirmada (não oficial)" — nunca "✓ Presente".
4. Treinador abre SCREEN-TRAIN-020 para fechar a sessão.
5. Treinador revisa lista de atletas:
   - Pré-confirmados aparecem com sugestão "presente" (mas editável).
   - Atletas sem pré-confirmação aparecem como "ausente" (editável).
6. Treinador ajusta conforme realidade e clica "Fechar sessão".
7. FE chama `CONTRACT-TRAIN-098` com batch de attendance + `allow_pending: true`.
8. Backend registra presenças oficiais e gera `PendingItem` para inconsistências (INV-TRAIN-065).

### Casos Negativos (anti-exemplos) `[NORMATIVO]`

| # | Cenário negativo | Resultado esperado | DEC/INV |
|---|---|---|---|
| NEG-017-1 | FE trata pre-confirm como presença oficial | **PROIBIDO** — pre-confirm nunca é oficial | INV-TRAIN-063 |
| NEG-017-2 | Backend permite presença oficial sem sessão fechada | **PROIBIDO** — presença oficial só no `close` | INV-TRAIN-064 |
| NEG-017-3 | Treinador fecha sessão com atleta ausente+justificado e ambos | Backend gera PendingItem para resolver | INV-TRAIN-065 |

---

## FLOW-TRAIN-018 — Treinador resolve fila de pendências

```yaml
id: FLOW-TRAIN-018
atores:
  primario: treinador|coordenador
  secundario: atleta (colaboração opcional)
prioridade: P0
estado_asis: EVIDENCIADO
telas:
  - SCREEN-TRAIN-023 # /training/pending-queue
contratos:
  - CONTRACT-TRAIN-099 # GET /training/pending-items
  - CONTRACT-TRAIN-100 # PATCH /training/pending-items/{item_id}/resolve
invariantes_chave:
  - INV-TRAIN-066 # pending queue separada
  - INV-TRAIN-067 # atleta colabora mas não valida
evidencias:
  - Hb Track - Frontend/src/app/(admin)/training/pending-queue/page.tsx
  - Hb Track - Frontend/src/components/training/PendingQueueTable.tsx
  - Hb Track - Frontend/src/lib/api/training-phase3.ts (getPendingItems, resolveTrainingPendingItem)
```

### Passos (happy path)
1. Treinador acessa SCREEN-TRAIN-023 (fila de pendências).
2. FE chama `CONTRACT-TRAIN-099` → lista PendingItems `status=open`.
3. Para cada item, treinador pode:
   a. Resolver diretamente (ex: marcar como "present" após verificação).
   b. Solicitar colaboração do atleta (ex: pedir justificativa — INV-TRAIN-067).
4. Treinador clica "Resolver" → FE chama `CONTRACT-TRAIN-100` com resolução.
5. Backend atualiza PendingItem e ajusta attendance conforme resolução.

### Nota sobre colaboração do atleta (INV-TRAIN-067)
- Atleta PODE fornecer informação (ex: justificativa, horário real de chegada).
- Atleta NÃO PODE validar/resolver a pendência — apenas o treinador ou coordenador.

### Casos Negativos (anti-exemplos) `[NORMATIVO]`

| # | Cenário negativo | Resultado esperado | DEC/INV |
|---|---|---|---|
| NEG-018-1 | Atleta tenta resolver pendência própria via API | 403 Forbidden — só treinador/coordenador pode | INV-TRAIN-067 |
| NEG-018-2 | Pendência resolvida sem `resolution` text | 422 — resolução requer texto | INV-TRAIN-066 |

---

## FLOW-TRAIN-019 — Atleta interage com coach virtual (IA)

```yaml
id: FLOW-TRAIN-019
atores:
  primario: atleta
prioridade: P2
estado_asis: GAP
telas:
  - SCREEN-TRAIN-024 # /athlete/ai-chat/[sessionId]
contratos:
  - CONTRACT-TRAIN-103 # POST /ai-coach/athlete-chat
invariantes_chave:
  - INV-TRAIN-072 # sugestão, não ordem
  - INV-TRAIN-073 # privacidade (sem conteúdo íntimo)
  - INV-TRAIN-074 # conteúdo educacional independente
  - INV-TRAIN-077 # feedback imediato do virtual coach
evidencias: []
```

### Passos (happy path)
1. Atleta abre chat IA pós-treino (SCREEN-TRAIN-024).
2. Atleta digita mensagem (ex: "como posso melhorar meu arremesso?").
3. FE chama `CONTRACT-TRAIN-103` → backend processa via LLM com contexto da sessão.
4. Backend retorna resposta com `type: "educational"` ou `"suggestion"` ou `"motivational"`.
5. FE exibe resposta. Se `type == "suggestion"`, FE exibe disclaimer: "Isto é uma sugestão — consulte seu treinador."

### Casos Negativos (anti-exemplos) `[NORMATIVO]`

| # | Cenário negativo | Resultado esperado | DEC/INV |
|---|---|---|---|
| NEG-019-1 | IA sugere como se fosse ordem ("faça 50 flexões agora") | **PROIBIDO** — IA deve usar linguagem de sugestão | INV-TRAIN-072 |
| NEG-019-2 | IA acessa dados íntimos do atleta (wellness individual detalhado) | **PROIBIDO** — IA opera em dados agregados/públicos | INV-TRAIN-073 |
| NEG-019-3 | IA condiciona conteúdo educacional a dados pessoais | **PROIBIDO** — educacional deve ser acessível sem expor dados | INV-TRAIN-074 |

---

## FLOW-TRAIN-020 — IA gera rascunho de treino para treinador editar

```yaml
id: FLOW-TRAIN-020
atores:
  primario: treinador
prioridade: P2
estado_asis: GAP
telas:
  - SCREEN-TRAIN-025 # AICoachDraftModal
contratos:
  - CONTRACT-TRAIN-101 # POST /ai-coach/draft-session
  - CONTRACT-TRAIN-102 # PATCH /ai-coach/draft-session/{draft_id}/apply
  - CONTRACT-TRAIN-104 # POST /ai-coach/justify-suggestion
invariantes_chave:
  - INV-TRAIN-075 # treino extra gerado por IA é rascunho
  - INV-TRAIN-080 # IA coach gera apenas draft, humano materializa
  - INV-TRAIN-081 # sugestão requer justificativa
evidencias: []
```

### Passos (happy path)
1. Treinador abre SCREEN-TRAIN-025 (modal de sugestão IA).
2. FE chama `CONTRACT-TRAIN-101` com contexto do time e período.
3. Backend retorna `draft_id` + sessão sugerida + justificativa textual (INV-TRAIN-081).
4. Treinador DEVE revisar e pode editar qualquer campo do rascunho.
5. Treinador clica "Aplicar" → FE chama `CONTRACT-TRAIN-102` com edits opcionais.
6. Backend cria a sessão de treino REAL a partir do draft + edits. Draft é marcado como `applied`.

### Nota normativa (INV-TRAIN-080)
- IA NUNCA cria sessão real diretamente. Sempre passa por `draft` → revisão humana → `apply`.
- FE DEVE impedir "apply" sem que o treinador veja a tela de edição (mesmo que não edite).

### Casos Negativos (anti-exemplos) `[NORMATIVO]`

| # | Cenário negativo | Resultado esperado | DEC/INV |
|---|---|---|---|
| NEG-020-1 | IA cria sessão publicada diretamente (sem draft) | **PROIBIDO** — IA só gera drafts | INV-TRAIN-080 |
| NEG-020-2 | Draft aplicado sem justificativa | **PROIBIDO** — toda sugestão IA requer justificativa | INV-TRAIN-081 |
| NEG-020-3 | FE permite "apply" sem exibir tela de edição | **PROIBIDO** — treinador deve ver/editar antes de aplicar | INV-TRAIN-075 |

---

## FLOW-TRAIN-021 — Wellness gates conteúdo (atleta sem wellness bloqueado)

```yaml
id: FLOW-TRAIN-021
atores:
  primario: atleta
prioridade: P1
estado_asis: GAP
telas:
  - SCREEN-TRAIN-022 # /athlete/training/[sessionId]
contratos:
  - CONTRACT-TRAIN-105 # GET /athlete/wellness-content-gate/{session_id}
invariantes_chave:
  - INV-TRAIN-071 # wellness missing bloqueia conteúdo completo
  - INV-TRAIN-076 # wellness obrigatório como política
  - INV-TRAIN-078 # progress view requer compliance
evidencias: []
```

### Passos (happy path)
1. Atleta tenta acessar visualização de treino ou progresso.
2. FE chama `CONTRACT-TRAIN-105` → backend verifica se atleta tem `wellness_pre` preenchido para a sessão.
3. **Se `can_see_full_content == true`**: FE libera visualização completa.
4. **Se `can_see_full_content == false`**: FE bloqueia conteúdo detalhado e exibe:
   - Mensagem: "Preencha seu wellness para acessar o conteúdo completo do treino."
   - Link para FLOW-TRAIN-005 (preenchimento wellness pré).
5. Após preenchimento, atleta retorna e FE re-verifica → libera conteúdo.

### Nota sobre progresso (INV-TRAIN-078)
- Visualização de progresso individual (ex: gráficos de evolução) também é bloqueada sem compliance de wellness.
- O bloqueio é informativo ("preencha para ver"), não punitivo (sem mensagem negativa).

### Casos Negativos (anti-exemplos) `[NORMATIVO]`

| # | Cenário negativo | Resultado esperado | DEC/INV |
|---|---|---|---|
| NEG-021-1 | Atleta sem wellness vê exercícios detalhados | **PROIBIDO** — conteúdo bloqueado até wellness | INV-TRAIN-071 |
| NEG-021-2 | Atleta sem compliance vê gráficos de progresso | **PROIBIDO** — progress view requer compliance | INV-TRAIN-078 |
| NEG-021-3 | FE mostra mensagem punitiva ("você foi penalizado") | **PROIBIDO** — tom deve ser informativo/motivacional | INV-TRAIN-076 |
