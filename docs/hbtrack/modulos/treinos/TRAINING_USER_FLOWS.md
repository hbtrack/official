# TRAINING_USER_FLOWS.md — Fluxos de Usuário do Módulo TRAINING

Status: DRAFT  
Versão: v1.0.0  
Tipo de Documento: SSOT Normativo — User Flows  
Módulo: TRAINING  
Fase: PRD v2.2 (2026-02-20) + AS-IS repo (2026-02-25)  
Autoridade: NORMATIVO_TECNICO  
Última revisão: 2026-02-25  

Dependências (leitura):
- `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
- `docs/hbtrack/PRD Hb Track.md`
- `Hb Track - Backend/docs/ssot/openapi.json`
- `Hb Track - Backend/docs/ssot/schema.sql`
- `Hb Track - Backend/app/api/v1/routers/*` (training/attendance/wellness/analytics)
- `Hb Track - Frontend/src/app/(admin)/training/*`
- `Hb Track - Frontend/src/app/(protected)/athlete/wellness-*/[sessionId]/*`

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
| FLOW-TRAIN-004 | Registrar presença digital (incl. justified) | Treinador | P0 | PARCIAL | SCREEN-TRAIN-020 | CONTRACT-TRAIN-025..028 | INV-TRAIN-030, INV-TRAIN-016 | US-001 |
| FLOW-TRAIN-005 | Atleta preencher wellness pré (deadline 2h) | Atleta | P0 | PARCIAL | SCREEN-TRAIN-018 | CONTRACT-TRAIN-030 | INV-TRAIN-002, INV-TRAIN-009 | US-002 |
| FLOW-TRAIN-006 | Atleta preencher wellness pós (janela 24h) | Atleta | P0 | PARCIAL | SCREEN-TRAIN-019 | CONTRACT-TRAIN-036 | INV-TRAIN-003, INV-TRAIN-010, INV-TRAIN-021 | RF-004 |
| FLOW-TRAIN-007 | Treinador visualizar status wellness da sessão | Treinador | P1 | PARCIAL | SCREEN-TRAIN-004 | CONTRACT-TRAIN-012 | INV-TRAIN-022, INV-TRAIN-026 | RF-004 |
| FLOW-TRAIN-008 | Planejar ciclos e microciclos | Treinador | P1 | EVIDENCIADO | SCREEN-TRAIN-007, SCREEN-TRAIN-008 | CONTRACT-TRAIN-040..052 | INV-TRAIN-037, INV-TRAIN-043 | RF-011 |
| FLOW-TRAIN-009 | Gerenciar banco de exercícios e favoritos | Treinador | P1 | EVIDENCIADO | SCREEN-TRAIN-010, SCREEN-TRAIN-011 | CONTRACT-TRAIN-053..062 | INV-TRAIN-045 | (PRD: In Scope V1) |
| FLOW-TRAIN-010 | Gerenciar templates de sessão | Treinador | P1 | EVIDENCIADO | SCREEN-TRAIN-017 | CONTRACT-TRAIN-063..068 | INV-TRAIN-035 | (PRD: suporte operacional) |
| FLOW-TRAIN-011 | Visualizar analytics e desvios | Coordenador | P1 | EVIDENCIADO | SCREEN-TRAIN-012 | CONTRACT-TRAIN-069..071 | INV-TRAIN-020, INV-TRAIN-015 | US-003 |
| FLOW-TRAIN-012 | Exportar relatório (PDF) de analytics | Coordenador | P1 | BLOQUEADO | SCREEN-TRAIN-012, SCREEN-TRAIN-013 | CONTRACT-TRAIN-086..089 | INV-TRAIN-012 | US-003, RF-012 |
| FLOW-TRAIN-013 | Visualizar rankings wellness e top performers | Dirigente | P1 | PARCIAL | SCREEN-TRAIN-014, SCREEN-TRAIN-015 | CONTRACT-TRAIN-073..076 | INV-TRAIN-036, INV-TRAIN-027 | RF-008 |
| FLOW-TRAIN-014 | Visualizar eficácia preventiva | Coordenador | P2 | EVIDENCIADO | SCREEN-TRAIN-016 | CONTRACT-TRAIN-072 | INV-TRAIN-014, INV-TRAIN-023 | RF-008 |
| FLOW-TRAIN-015 | Gerenciar alertas e sugestões (apply/dismiss) | Coordenador | P2 | HIPOTESE | SCREEN-TRAIN-021 | CONTRACT-TRAIN-077..085 | INV-TRAIN-014, INV-TRAIN-023 | RF-013 |

Notas:
- `FLOW-TRAIN-012` está `BLOQUEADO`: routers de export existem, mas estão **desabilitados** no agregador atual (ver `Hb Track - Backend/app/api/v1/api.py`).

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
estado_asis: PARCIAL
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
estado_asis: PARCIAL
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

### Passos (TO-BE normativo)
1. Atleta acessa `SCREEN-TRAIN-018` via link para uma sessão agendada.
2. Sistema exibe resumo da sessão e countdown de deadline (até `session_at - 2h`).
3. Atleta preenche campos do **schema real** (PRD US-002):
   - `stress_level` (0–10; semântica inversa do PRD: 0=ótimo),
   - `sleep_quality` (1–5),
   - `sleep_hours` (0–24, decimal),
   - `fatigue_pre` (0–10),
   - `muscle_soreness` (0–10),
   - opcionais SSOT: `readiness_score`, `menstrual_cycle_phase`, `notes`.
4. Submete via `CONTRACT-TRAIN-030`.

### Gaps AS-IS (bloqueantes)
- Frontend chama endpoints inexistentes/errados (`/wellness_pre`, `/wellness_pre/sessions/...`) em `Hb Track - Frontend/src/lib/api/wellness.ts` (esperado: prefix `/wellness-pre/...`).
- UI coleta campos não alinhados ao schema (`fatigue_level`, `mood`, `readiness`) e não coleta `sleep_hours`.

---

## FLOW-TRAIN-006 — Atleta preencher wellness pós (janela 24h)

```yaml
id: FLOW-TRAIN-006
atores:
  primario: atleta
prioridade: P0
estado_asis: PARCIAL
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

### Passos (TO-BE normativo)
1. Atleta acessa `SCREEN-TRAIN-019` após o treino.
2. Preenche: `session_rpe`, `fatigue_after`, `mood_after`, `muscle_soreness_after` (opcional), `minutes_effective` (quando aplicável), `notes` (opcional).
3. Submete via `CONTRACT-TRAIN-036`.
4. Sistema calcula `internal_load` automaticamente (trigger) e invalida caches de analytics quando aplicável.

### Gaps AS-IS (bloqueantes)
- Mesmo problema de endpoint base do módulo wellness no frontend (`/wellness_post` vs `/wellness-post/...`).
- Badge/progresso mensal na UI está hardcoded (não evidenciado como contrato consumido).

---

## FLOW-TRAIN-007 — Treinador visualizar status wellness da sessão

```yaml
id: FLOW-TRAIN-007
atores:
  primario: treinador|coordenador
prioridade: P1
estado_asis: PARCIAL
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
estado_asis: EVIDENCIADO
telas:
  - SCREEN-TRAIN-010 # /training/exercise-bank
  - SCREEN-TRAIN-011 # modais create/edit/details
contratos:
  - CONTRACT-TRAIN-053..062 # exercises + tags + favorites
invariantes_chave:
  - INV-TRAIN-045 # order_index unique em session_exercises (impacto indireto)
evidencias:
  - Hb Track - Frontend/src/app/(admin)/training/exercise-bank/page.tsx
  - Hb Track - Backend/app/api/v1/routers/exercises.py
```

### Passos (happy path)
1. Usuário acessa banco de exercícios e filtra por busca/tags/categoria/favoritos.
2. Staff cria/edita exercícios e tags; marca favoritos.
3. Usuário arrasta exercícios para compor sessão (integra com `FLOW-TRAIN-003`).

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
estado_asis: BLOQUEADO
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

Regra normativa:
- O fluxo só pode ser marcado como `EVIDENCIADO` quando o contrato de export e o job assíncrono estiverem expostos e testados.

---

## FLOW-TRAIN-013 — Visualizar rankings wellness e top performers

```yaml
id: FLOW-TRAIN-013
atores:
  primario: dirigente|coordenador|treinador
prioridade: P1
estado_asis: PARCIAL
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

### Gaps AS-IS
- Frontend trata `team_id` como `number` (parseInt) e backend/schema usam `UUID`.
- Endpoint `/analytics/wellness-rankings/{team_id}/athletes-90plus` usa tipagem/implementação inconsistente (service com campos antigos).

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
