# TRAINING_FRONT_BACK_CONTRACT.md — Contratos Front-Back do Módulo TRAINING

Status: DRAFT  
Versão: v1.3.0  
Tipo de Documento: SSOT Normativo — Front-Back Contract  
Módulo: TRAINING  
Fase: PRD v2.2 (2026-02-20) + AS-IS repo (2026-02-25) + DEC-TRAIN-* (2026-02-25) + FASE_3 (2026-02-27)  
Autoridade: NORMATIVO_TECNICO  
Última revisão: 2026-02-27  

> Changelog v1.3.0 (2026-02-27):  
> - §3.5: Default `visibility_mode` alterado de `org_wide` para `restricted` (INV-TRAIN-060, AMENDA EXB-ACL-001)  
> - §5.11: Novos contratos FASE_3 — presença oficial, pending queue, wellness content gate, IA coach  
> - Shapes: Adicionados `AthleteSessionPreview`, `PendingItem`  
> - Gaps: GAP-CONTRACT-6 (presença/pending/wellness gate) e GAP-CONTRACT-7 (IA coach)  
> - Novos contracts: CONTRACT-TRAIN-096..105  

> Changelog v1.2.0 (2026-02-26):  
> - Adicionada Authority Matrix  
> - Adicionada convenção de Classification Tags  
> - Adicionada §3.5 Defaults Explícitos do Módulo  
> - Adicionada §4.6 Exemplos Canônicos (wellness self-only, top performers, ACL, export degradado)  
> - Adicionado `decision_trace:` formal nas seções impactadas por DEC-TRAIN-*  

> Changelog v1.1.0 (2026-02-25):  
> - DEC-TRAIN-001: Wellness self-only (§4.2/4.3 + regra normativa §4.5)  
> - DEC-TRAIN-002: Tabela mapeamento FE→payload canônico (§4.4)  
> - DEC-TRAIN-003: `CONTRACT-TRAIN-076` como endpoint canônico de top performers (§5.9)  
> - DEC-TRAIN-004: Estado degradado explícito de exports sem worker (§6)  
> - DEC-TRAIN-EXB-*: Banco de exercícios com scope/ACL/visibility/mídia (§5.7 expandido + §5.7b novos contratos)  

Dependências (leitura):
- `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
- `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md`
- `docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md`
- `Hb Track - Backend/docs/ssot/openapi.json`
- `Hb Track - Backend/docs/ssot/schema.sql`
- `Hb Track - Backend/app/api/v1/api.py`
- `Hb Track - Backend/app/api/v1/routers/*` (training, attendance, wellness, analytics, exports)
- `Hb Track - Frontend/src/lib/api/*` (trainings, attendance, wellness, analytics, rankings)

---

## Authority Matrix

| Aspecto | Regra |
|---|---|
| Fonte de verdade | OpenAPI SSOT (`openapi.json`) + DB schema (`schema.sql`) + Domain services |
| Escrita normativa | **Arquiteto** — regras de contrato, shapes normativos, invariantes associadas |
| Escrita de paridade (não-semântica) | **Executor** — pode corrigir paridade comprovada e não-semântica (operationId, path typo, tipo UUID/int documentado por evidência). **NÃO pode alterar comportamento normativo sob pretexto de paridade.** |
| Somente leitura / divergência | **Testador** — registra divergência/evidência, não altera regra |
| Proposta de alteração | Qualquer papel → via GAP ou DEC ao Arquiteto |
| Precedência em conflito | DB > Services > OpenAPI > FE > PRD |

---

## Convenção de Tags (Classification)

Cada contrato (CONTRACT-*), shape, ou regra neste documento é uma **unidade de afirmação testável** e recebe classificação:

| Tag | Significado |
|---|---|
| `[NORMATIVO]` | Regra/contrato que DEVE ser respeitado. Fonte: DB, Service, DEC ou PRD explícito. |
| `[DESCRITIVO-AS-IS]` | Observação do estado atual (evidenciado no repo). Pode mudar. |
| `[HIPOTESE]` | Expectativa derivada do PRD/fluxos, mas não evidenciada no repo. |
| `[GAP]` | Lacuna identificada entre o normativo e o estado atual. |

**Aplicação neste documento:**
- Contratos com `Status: EVIDENCIADO` → `[NORMATIVO]` + `[DESCRITIVO-AS-IS]` (regra + implementação existente).
- Contratos com `Status: GAP` → `[NORMATIVO]` + `[GAP]` (regra sem implementação).
- Contratos com `Status: DIVERGENTE_DO_SSOT` → `[NORMATIVO]` com nota de divergência.
- Seções "TO-BE normativo" → `[NORMATIVO]`. Seções "Gap FE↔BE" → `[GAP]`.

---

## 1) Objetivo (Normativo)

Definir o **contrato determinístico** entre Frontend e Backend do módulo **TRAINING**:
- endpoints e operationIds,
- shapes mínimos de request/response (quando OpenAPI não tipa),
- tipos canônicos (UUID vs int, datetime),
- erros e regras (mapeadas para invariantes),
- gaps de paridade FE↔BE e contrato↔schema.

Este documento é **TO-BE**: quando houver divergência, a regra é **registrar como `DIVERGENTE_DO_SSOT`** e criar ARs para convergir.

---

## 2) SSOT e precedência (normativo)

Ordem de precedência para decisões de contrato:
1. **DB schema/constraints/triggers**: `Hb Track - Backend/docs/ssot/schema.sql`
2. **Models/Services** (regras de domínio)
3. **OpenAPI SSOT**: `Hb Track - Backend/docs/ssot/openapi.json`
4. **Frontend** (UX e integrações)
5. **PRD/TRD** (referência)

Quando **OpenAPI** estiver incompleto (schema `{}`) ou divergente do DB, este contrato define o **shape mínimo normativo** e registra o gap.

---

## 3) Convenções gerais do contrato

### 3.1 Base URL
- Base: `/api/v1`
- As rotas abaixo são relativas a este prefixo.

### 3.2 Tipos canônicos
- IDs primários e FKs: **UUID string** (`format: uuid`) para `team_id`, `athlete_id`, `training_session_id`, `cycle_id`, `microcycle_id`, `template_id`, `exercise_id`, etc.
- Datas (sem hora): `YYYY-MM-DD`
- Datetimes: ISO 8601 com timezone (idealmente UTC), ex.: `2026-02-25T10:00:00Z`
- Percentuais de foco: `number` (persistência em `numeric/decimal` no DB)

### 3.3 Soft delete (sessões, ciclos, microciclos)
Regra normativa:
- Operações de delete devem exigir `reason` (query param) e registrar `deleted_at` + `deleted_reason`.  
Ref.: `INV-TRAIN-008`.

### 3.4 Enums relevantes (SSOT)
- `training_sessions.status`: `draft|scheduled|in_progress|pending_review|readonly` (INV-TRAIN-006)
- `attendance.presence_status`: `present|absent|justified`
- `attendance.participation_type`: `full|partial|adapted|did_not_train`
- `attendance.reason_absence`: `medico|escola|familiar|opcional|outro`
- `wellness_pre.menstrual_cycle_phase` (opcional): `folicular|lutea|menstruacao|nao_informa`
- `training_alerts.alert_type`: `weekly_overload|low_wellness_response`
- `training_alerts.severity`: `warning|critical`
- `training_suggestions.type`: `compensation|reduce_next_week`
- `training_suggestions.status`: `pending|applied|dismissed`

### 3.5 Defaults Explícitos do Módulo `[NORMATIVO]`

Valores padrão que o sistema DEVE aplicar quando o campo não é informado no request:

| Campo / Contexto | Default | Fonte / DEC |
|---|---|---|
| `visibility_mode` (exercício ORG) | `restricted` | DEC-TRAIN-EXB-001, INV-TRAIN-060 (AMENDADO v1.3.0: era org_wide) |
| `is_favorite` (exercício recém-criado) | `false` | INV-TRAIN-050 |
| `athlete_id` (wellness atleta) | Inferido do token JWT | DEC-TRAIN-001 |
| Worker Celery indisponível (export) | 202 estado degradado (não 500) | DEC-TRAIN-004 |
| `wellness_deadline` (deadline de submissão) | 2h antes do início da sessão | PRD v2.2 §wellness |
| `edit_window` (wellness pós) | 24h após fim da sessão | PRD v2.2 §wellness |

**Regras:**
- O FE NÃO DEVE enviar `athlete_id` no payload wellness do atleta — o backend o infere (DEC-TRAIN-001).
- Se `visibility_mode` não for informado em `ExerciseCreate`, o backend DEVE usar `restricted`.
- Export sem worker disponível DEVE retornar 202 + `{"degraded": true}`, nunca 500/503 (DEC-TRAIN-004).

---

## 4) Shapes canônicos mínimos (quando usados pelo FE)

> Nota: quando o OpenAPI já define schema tipado, ele permanece a referência.  
> Quando o OpenAPI não tipa (schema `{}`), os shapes abaixo são **normativos mínimos**.

### 4.1 Attendance (Presenças)

Regra de consistência DB (SSOT):
- `presence_status='absent'` ⇒ `reason_absence MUST be NULL`
- Ausência com motivo ⇒ usar `presence_status='justified'` (ver `ck_attendance_absent_reason_null` no model)

Shape mínimo:
```yaml
Attendance:
  id: uuid
  training_session_id: uuid
  athlete_id: uuid
  team_registration_id: uuid
  presence_status: present|absent|justified
  participation_type?: full|partial|adapted|did_not_train
  reason_absence?: medico|escola|familiar|opcional|outro
  minutes_effective?: int
  comment?: string
  source: manual|import|correction
  correction_by_user_id?: uuid
  correction_at?: datetime
```

### 4.2 Wellness Pre (Pré-treino)

> **decision_trace:** `[DEC-TRAIN-001]`

Campos exigidos pelo DB:
```yaml
WellnessPreCreate:
  # athlete_id: NÃO enviado pelo cliente atleta (DEC-TRAIN-001)
  # Backend infere athlete_id do token JWT.
  # Staff/terceiros usam endpoint separado com permissão explícita.
  sleep_hours: number  # 0..24, 1 casa decimal (numeric(4,1))
  sleep_quality: int   # 1..5
  fatigue_pre: int     # 0..10
  stress_level: int    # 0..10
  muscle_soreness: int # 0..10
  notes?: string
  readiness_score?: int # 0..10 (opcional SSOT)
  menstrual_cycle_phase?: folicular|lutea|menstruacao|nao_informa
```

> **DEC-TRAIN-001 (normativo):** O payload de wellness pré/pós do atleta NÃO DEVE conter `athlete_id`.
> O backend DEVE inferir `athlete_id` do token JWT. Caso o payload contenha `athlete_id`,
> o backend DEVE ignorá-lo ou retornar 422.

### 4.3 Wellness Post (Pós-treino)

> **decision_trace:** `[DEC-TRAIN-001]`

Campos exigidos pelo DB:
```yaml
WellnessPostCreate:
  # athlete_id: NÃO enviado pelo cliente atleta (DEC-TRAIN-001)
  # Backend infere athlete_id do token JWT.
  session_rpe: int        # 0..10
  fatigue_after: int      # 0..10
  mood_after: int         # 0..10
  muscle_soreness_after?: int # 0..10
  minutes_effective?: int
  notes?: string
```

Campo derivado:
- `internal_load` é calculado por trigger: `minutes_effective × session_rpe` (INV-TRAIN-021).

### 4.4 Tabela de Mapeamento FE→Payload Canônico (Wellness Pré) — DEC-TRAIN-002

> **decision_trace:** `[DEC-TRAIN-002]`

> Esta tabela é **normativa**: garante que components UI (sliders, selects) são traduzidos
> corretamente para o payload canônico do backend.

| Componente UI (FE) | Label UX (atleta) | Campo Payload (backend) | Tipo | Range | Semântica |
|---|---|---|---|---|---|
| Slider / Stars | "Qualidade do sono" | `sleep_quality` | int | 1..5 | 1=péssima, 5=ótima |
| Slider / Input | "Horas de sono" | `sleep_hours` | number | 0..24 (1 decimal) | Horas dormidas |
| Slider | "Fadiga" | `fatigue_pre` | int | 0..10 | 0=descansado, 10=exausto |
| Slider | "Estresse" | `stress_level` | int | 0..10 | 0=relaxado, 10=alto |
| Slider | "Dor muscular" | `muscle_soreness` | int | 0..10 | 0=nenhuma, 10=intensa |
| Slider | "Prontidão" (opcional) | `readiness_score` | int | 0..10 | 0=indisposto, 10=pronto |
| Select (opcional) | "Ciclo menstrual" | `menstrual_cycle_phase` | enum | folicular\|lutea\|menstruacao\|nao_informa | — |
| Textarea | "Observações" | `notes` | string | livre | — |

**Regras (DEC-TRAIN-002):**
- O FE DEVE mapear seus sliders/components para os campos acima antes do submit.
- Se o FE usar labels diferentes (ex.: "mood" → `stress_level`), o mapeamento DEVE estar documentado aqui.
- Tests normativos de mapeamento DEVEM verificar que cada slider produz o campo correto no payload.

### 4.5 Regra Self-Only (DEC-TRAIN-001) — Normativa

> **decision_trace:** `[DEC-TRAIN-001]`

```yaml
WellnessAthleteRule:
  rule: >
    Atleta autenticado submete wellness pré/pós SEM informar athlete_id.
    O backend DEVE inferir athlete_id do token JWT (claim user → athlete lookup).
  enforcement: BACKEND (obrigatório)
  frontend: NÃO enviar athlete_id no payload do atleta.
  staff_flow: >
    Se staff/terceiros precisarem registrar wellness de outro atleta,
    DEVE ser endpoint/escopo separado com permissão explícita e auditoria (INV-TRAIN-026).
  error_if_violated: 422 ou campo ignorado silenciosamente (backend decide; documentar).
```

### 4.6 Exemplos Canônicos (request/response) `[NORMATIVO]`

Exemplos determinísticos para os fluxos críticos. O Executor e o Testador DEVEM usar estes como referência mínima.

#### Exemplo 1 — Wellness Pré (atleta self-only) — DEC-TRAIN-001

```http
POST /api/v1/wellness-pre HTTP/1.1
Authorization: Bearer <athlete_jwt>
Content-Type: application/json

{
  "sleep_hours": 7.5,
  "sleep_quality": 4,
  "fatigue_pre": 3,
  "stress_level": 2,
  "muscle_soreness": 1,
  "readiness_score": 8,
  "notes": "Dormi bem"
}
```

```http
HTTP/1.1 201 Created

{
  "id": "uuid",
  "athlete_id": "uuid-inferred-from-jwt",
  "sleep_hours": 7.5,
  "sleep_quality": 4,
  "fatigue_pre": 3,
  "stress_level": 2,
  "muscle_soreness": 1,
  "readiness_score": 8,
  "notes": "Dormi bem",
  "created_at": "2026-02-25T08:00:00Z"
}
```

> **Anti-exemplo:** Se o payload incluir `"athlete_id": "uuid-xxx"`, o backend DEVE retornar 422 ou ignorar o campo.

#### Exemplo 2 — Top Performers (endpoint canônico) — DEC-TRAIN-003

```http
GET /api/v1/teams/{team_id}/wellness-top-performers?month=2026-02 HTTP/1.1
Authorization: Bearer <coach_jwt>
```

```http
HTTP/1.1 200 OK

{
  "month": "2026-02",
  "team_id": "uuid",
  "team_name": "Sub-16 Feminino",
  "top_performers": [
    {
      "athlete_id": "uuid",
      "athlete_name": "Maria Silva",
      "response_rate": 95.0,
      "avg_wellness_score": 7.8
    }
  ]
}
```

> **Anti-exemplo:** FE NÃO DEVE usar `CONTRACT-TRAIN-075` (`/analytics/wellness-rankings/{team_id}/athletes-90plus`) como fonte primária da listagem.

#### Exemplo 3 — Exercício ORG com ACL restricted — DEC-TRAIN-EXB-002

```http
POST /api/v1/exercises HTTP/1.1
Authorization: Bearer <coach_jwt>
Content-Type: application/json

{
  "name": "Arremesso em suspensão",
  "scope": "ORG",
  "visibility_mode": "restricted",
  "description": "Exercício técnico de arremesso",
  "tags": ["arremesso", "técnico"]
}
```

```http
HTTP/1.1 201 Created

{
  "id": "uuid-new",
  "name": "Arremesso em suspensão",
  "scope": "ORG",
  "organization_id": "uuid-org-from-jwt",
  "visibility_mode": "restricted",
  "created_by": "uuid-coach",
  "created_at": "2026-02-25T14:00:00Z"
}
```

> **Anti-exemplo (cross-org):** Se `POST /exercises/{id}/acl` com `user_id` de outra org → 422 (INV-TRAIN-EXB-ACL-003).

#### Exemplo 4 — Export sem Worker (estado degradado) — DEC-TRAIN-004

```http
POST /api/v1/analytics/export-pdf HTTP/1.1
Authorization: Bearer <coach_jwt>
Content-Type: application/json

{
  "team_id": "uuid",
  "report_type": "monthly_summary",
  "month": "2026-02"
}
```

```http
HTTP/1.1 202 Accepted

{
  "job_id": "uuid-job",
  "status": "queued",
  "degraded": true,
  "message": "Export enfileirado, processamento pode estar lento"
}
```

> **Anti-exemplo:** Retornar 500 ou 503 quando o worker não está disponível é PROIBIDO.

---

## 5) Contratos por área (CONTRACT-TRAIN-###)

### 5.1 Training Sessions — CRUD + workflow

| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-001 | GET | `/training-sessions` | `list_training_sessions_api_v1_training_sessions_get` | query filters + paginação | `TrainingSessionPaginatedResponse` | EVIDENCIADO | INV-TRAIN-006 |
| CONTRACT-TRAIN-002 | POST | `/training-sessions` | `create_training_session_api_v1_training_sessions_post` | `TrainingSessionCreate` | `TrainingSession` | EVIDENCIADO | INV-TRAIN-001, INV-TRAIN-006 |
| CONTRACT-TRAIN-003 | GET | `/training-sessions/{training_session_id}` | `get_training_session_by_id_api_v1_training_sessions__training_session_id__get` | — | `TrainingSession` | EVIDENCIADO | INV-TRAIN-006 |
| CONTRACT-TRAIN-004 | PATCH | `/training-sessions/{training_session_id}` | `update_training_session_api_v1_training_sessions__training_session_id__patch` | `TrainingSessionUpdate` | `TrainingSession` | EVIDENCIADO | INV-TRAIN-004, INV-TRAIN-005, INV-TRAIN-001 |
| CONTRACT-TRAIN-005 | DELETE | `/training-sessions/{training_session_id}?reason=` | `delete_training_session_api_v1_training_sessions__training_session_id__delete` | query `reason` | 204 | EVIDENCIADO | INV-TRAIN-008 |
| CONTRACT-TRAIN-006 | POST | `/training-sessions/{training_session_id}/publish` | `publish_training_session_api_v1_training_sessions__training_session_id__publish_post` | `{}` | `TrainingSession` | EVIDENCIADO | INV-TRAIN-006 |
| CONTRACT-TRAIN-007 | POST | `/training-sessions/{training_session_id}/close` | `close_training_session_api_v1_training_sessions__training_session_id__close_post` | `{}` | `SessionClosureResponse` | EVIDENCIADO | INV-TRAIN-006 |
| CONTRACT-TRAIN-008 | POST | `/training-sessions/{training_session_id}/duplicate` | `duplicate_training_session_api_v1_training_sessions__training_session_id__duplicate_post` | `{}` | `TrainingSession` | EVIDENCIADO | INV-TRAIN-006 |
| CONTRACT-TRAIN-009 | POST | `/training-sessions/{training_session_id}/restore` | `restore_training_session_api_v1_training_sessions__training_session_id__restore_post` | `{}` | `TrainingSession` | EVIDENCIADO | INV-TRAIN-008 |
| CONTRACT-TRAIN-010 | POST | `/training-sessions/copy-week` | `copy_week_sessions_api_v1_training_sessions_copy_week_post` | query: `team_id`, `source_week_start`, `target_week_start`, `validate_focus` | `TrainingSession[]` | EVIDENCIADO | INV-TRAIN-005, INV-TRAIN-001 |
| CONTRACT-TRAIN-011 | GET | `/training-sessions/{training_session_id}/deviation` | `get_session_deviation_api_v1_training_sessions__training_session_id__deviation_get` | — | `DeviationAnalysis` | EVIDENCIADO | INV-TRAIN-011 |
| CONTRACT-TRAIN-012 | GET | `/training-sessions/{training_session_id}/wellness-status` | `get_wellness_status_api_v1_training_sessions__training_session_id__wellness_status_get` | — | `WellnessStatusResponse` | EVIDENCIADO | INV-TRAIN-026 |

Notas:
- O endpoint `copy-week` tem regra extra de validação opcional `validate_focus=True` exigindo soma de focos = 100% (diferente de `INV-TRAIN-001` que permite até 120%). Isso deve ser refletido no FE como validação explicita no fluxo.

---

### 5.2 Training Sessions — Rotas Scoped por Team

| ID | Método | Path | operationId | Request | Response | Status | Observações |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-013 | GET | `/teams/{team_id}/trainings` | `scoped_list_training_sessions_api_v1_teams__team_id__trainings_get` | query paginação | `TrainingSessionPaginatedResponse` | EVIDENCIADO | Alternativa scoped do list |
| CONTRACT-TRAIN-014 | POST | `/teams/{team_id}/trainings` | `scoped_create_training_session_api_v1_teams__team_id__trainings_post` | `ScopedTrainingSessionCreate` | `TrainingSession` | EVIDENCIADO | `organization_id` pode ser inferido |
| CONTRACT-TRAIN-015 | GET | `/teams/{team_id}/trainings/{training_id}` | `scoped_get_training_session_api_v1_teams__team_id__trainings__training_id__get` | — | `TrainingSession` | EVIDENCIADO | Enforce team scope |
| CONTRACT-TRAIN-016 | PATCH | `/teams/{team_id}/trainings/{training_id}` | `scoped_update_training_session_api_v1_teams__team_id__trainings__training_id__patch` | `TrainingSessionUpdate` | `TrainingSession` | EVIDENCIADO | Enforce team scope |
| CONTRACT-TRAIN-017 | DELETE | `/teams/{team_id}/trainings/{training_id}?reason=` | `scoped_delete_training_session_api_v1_teams__team_id__trainings__training_id__delete` | query `reason` | 204 | EVIDENCIADO | Soft delete |
| CONTRACT-TRAIN-018 | POST | `/teams/{team_id}/trainings/{training_id}/restore` | `scoped_restore_training_session_api_v1_teams__team_id__trainings__training_id__restore_post` | `{}` | `TrainingSession` | EVIDENCIADO | Restore de soft delete |

---

### 5.3 Session Exercises (drag-and-drop)

| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-019 | GET | `/training-sessions/{session_id}/exercises` | `get_session_exercises_api_v1_training_sessions__session_id__exercises_get` | — | `SessionExerciseListResponse` | EVIDENCIADO | INV-TRAIN-045 |
| CONTRACT-TRAIN-020 | POST | `/training-sessions/{session_id}/exercises` | `add_exercise_to_session_api_v1_training_sessions__session_id__exercises_post` | `SessionExerciseCreate` | `SessionExerciseResponse` | EVIDENCIADO | INV-TRAIN-045 |
| CONTRACT-TRAIN-021 | POST | `/training-sessions/{session_id}/exercises/bulk` | `bulk_add_exercises_to_session_api_v1_training_sessions__session_id__exercises_bulk_post` | `SessionExerciseBulkCreate` | `SessionExerciseResponse[]` | EVIDENCIADO | INV-TRAIN-045 |
| CONTRACT-TRAIN-022 | PATCH | `/training-sessions/exercises/{session_exercise_id}` | `update_session_exercise_api_v1_training_sessions_exercises__session_exercise_id__patch` | `SessionExerciseUpdate` | `SessionExerciseResponse` | EVIDENCIADO | INV-TRAIN-045 |
| CONTRACT-TRAIN-023 | PATCH | `/training-sessions/{session_id}/exercises/reorder` | `reorder_session_exercises_api_v1_training_sessions__session_id__exercises_reorder_patch` | `SessionExerciseReorder` | `{success, updated_count}` | EVIDENCIADO | INV-TRAIN-045 |
| CONTRACT-TRAIN-024 | DELETE | `/training-sessions/exercises/{session_exercise_id}` | `remove_exercise_from_session_api_v1_training_sessions_exercises__session_exercise_id__delete` | — | 204 | EVIDENCIADO | INV-TRAIN-045 |

---

### 5.4 Attendance (Presenças)

> Observação de naming: attendance usa prefixo `/training_sessions` (underscore) por herança histórica.

| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-025 | GET | `/training_sessions/{training_session_id}/attendance` | `list_attendance_by_session_api_v1_training_sessions__training_session_id__attendance_get` | query opcional `athlete_id`, `status` | `Attendance[]` | EVIDENCIADO | INV-TRAIN-016 |
| CONTRACT-TRAIN-026 | POST | `/training_sessions/{training_session_id}/attendance` | `add_attendance_to_session_api_v1_training_sessions__training_session_id__attendance_post` | `AttendanceCreate` | `Attendance` | EVIDENCIADO | INV-TRAIN-030 |
| CONTRACT-TRAIN-027 | POST | `/training_sessions/{training_session_id}/attendance/batch` | `add_attendance_batch_api_v1_training_sessions__training_session_id__attendance_batch_post` | `AttendanceCreate[]` | `Attendance[]` | EVIDENCIADO | INV-TRAIN-030 |
| CONTRACT-TRAIN-028 | GET | `/training_sessions/{training_session_id}/attendance/statistics` | `get_session_attendance_statistics_api_v1_training_sessions__training_session_id__attendance_statistics_get` | — | `{total_athletes, present_count, absent_count, attendance_rate}` | EVIDENCIADO | (derivado) |

Gap FE↔DB (crítico):
- O frontend precisa aceitar `presence_status='justified'` e não enviar `reason_absence` quando `presence_status='absent'` (DB bloqueia).

---

### 5.5 Wellness Pre/Post

> Observação de naming: prefixo de router é `/wellness-pre|/wellness-post` (hífen) mas subpaths mantêm `_` (`/wellness_pre`, `/training_sessions/...`).

#### Wellness Pre

| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-029 | GET | `/wellness-pre/training_sessions/{training_session_id}/wellness_pre` | `list_wellness_pre_by_session_api_v1_wellness_pre_training_sessions__training_session_id__wellness_pre_get` | query opcional `athlete_id` | `WellnessPre[]` | EVIDENCIADO | INV-TRAIN-026 |
| CONTRACT-TRAIN-030 | POST | `/wellness-pre/training_sessions/{training_session_id}/wellness_pre` | `add_wellness_pre_to_session_api_v1_wellness_pre_training_sessions__training_session_id__wellness_pre_post` | `WellnessPreCreate` | `WellnessPre` | EVIDENCIADO | INV-TRAIN-002, INV-TRAIN-009 |
| CONTRACT-TRAIN-031 | GET | `/wellness-pre/training_sessions/{training_session_id}/wellness_pre/status` | `get_wellness_pre_status_api_v1_wellness_pre_training_sessions__training_session_id__wellness_pre_status_get` | — | `{total_athletes, responded_pre, pending[], response_rate}` | EVIDENCIADO | (derivado) |
| CONTRACT-TRAIN-032 | GET | `/wellness-pre/wellness_pre/{wellness_pre_id}` | `get_wellness_pre_by_id_api_v1_wellness_pre_wellness_pre__wellness_pre_id__get` | — | `WellnessPre` | EVIDENCIADO | INV-TRAIN-026 |
| CONTRACT-TRAIN-033 | PATCH | `/wellness-pre/wellness_pre/{wellness_pre_id}` | `update_wellness_pre_api_v1_wellness_pre_wellness_pre__wellness_pre_id__patch` | `WellnessPreUpdate` | `WellnessPre` | EVIDENCIADO | INV-TRAIN-002 |
| CONTRACT-TRAIN-034 | POST | `/wellness-pre/wellness_pre/{wellness_pre_id}/request-unlock` | `request_wellness_unlock_api_v1_wellness_pre_wellness_pre__wellness_pre_id__request_unlock_post` | `{reason?}` | `{status}` | EVIDENCIADO | (workflow) |

#### Wellness Post

| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-035 | GET | `/wellness-post/training_sessions/{training_session_id}/wellness_post` | `list_wellness_post_by_session_api_v1_wellness_post_training_sessions__training_session_id__wellness_post_get` | query opcional `athlete_id` | `WellnessPost[]` | EVIDENCIADO | INV-TRAIN-026 |
| CONTRACT-TRAIN-036 | POST | `/wellness-post/training_sessions/{training_session_id}/wellness_post` | `add_wellness_post_to_session_api_v1_wellness_post_training_sessions__training_session_id__wellness_post_post` | `WellnessPostCreate` | `WellnessPost` | EVIDENCIADO | INV-TRAIN-003, INV-TRAIN-010, INV-TRAIN-021 |
| CONTRACT-TRAIN-037 | GET | `/wellness-post/training_sessions/{training_session_id}/wellness_post/status` | `get_wellness_post_status_api_v1_wellness_post_training_sessions__training_session_id__wellness_post_status_get` | — | `{total_athletes, responded_post, pending[], response_rate}` | EVIDENCIADO | (derivado) |
| CONTRACT-TRAIN-038 | GET | `/wellness-post/wellness_post/{wellness_post_id}` | `get_wellness_post_by_id_api_v1_wellness_post_wellness_post__wellness_post_id__get` | — | `WellnessPost` | EVIDENCIADO | INV-TRAIN-026 |
| CONTRACT-TRAIN-039 | PATCH | `/wellness-post/wellness_post/{wellness_post_id}` | `update_wellness_post_api_v1_wellness_post_wellness_post__wellness_post_id__patch` | `WellnessPostUpdate` | `WellnessPost` | EVIDENCIADO | INV-TRAIN-003 |

Gap FE↔BE (crítico):
- `Hb Track - Frontend/src/lib/api/wellness.ts` não usa os paths acima; o contrato FE deve convergir para estes endpoints.

---

### 5.6 Training Cycles / Microcycles

#### Cycles
| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-040 | GET | `/training-cycles` | `list_training_cycles_api_v1_training_cycles_get` | filtros `team_id`, `cycle_type`, `status` | `TrainingCycleResponse[]` | EVIDENCIADO | INV-TRAIN-037 |
| CONTRACT-TRAIN-041 | GET | `/training-cycles/{cycle_id}` | `get_training_cycle_api_v1_training_cycles__cycle_id__get` | — | `TrainingCycleWithMicrocycles` | EVIDENCIADO | INV-TRAIN-037 |
| CONTRACT-TRAIN-042 | POST | `/training-cycles` | `create_training_cycle_api_v1_training_cycles_post` | `TrainingCycleCreate` | `TrainingCycleResponse` | EVIDENCIADO | INV-TRAIN-037 |
| CONTRACT-TRAIN-043 | PATCH | `/training-cycles/{cycle_id}` | `update_training_cycle_api_v1_training_cycles__cycle_id__patch` | `TrainingCycleUpdate` | `TrainingCycleResponse` | EVIDENCIADO | INV-TRAIN-037 |
| CONTRACT-TRAIN-044 | DELETE | `/training-cycles/{cycle_id}?reason=` | `delete_training_cycle_api_v1_training_cycles__cycle_id__delete` | query `reason` | 204 | EVIDENCIADO | INV-TRAIN-008 |
| CONTRACT-TRAIN-045 | GET | `/training-cycles/teams/{team_id}/active` | `get_active_cycles_api_v1_training_cycles_teams__team_id__active_get` | — | `TrainingCycleResponse[]` | EVIDENCIADO | (derivado) |

#### Microcycles
| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-046 | GET | `/training-microcycles` | `list_training_microcycles_api_v1_training_microcycles_get` | `team_id` obrigatório + filtros | `TrainingMicrocycleResponse[]` | EVIDENCIADO | INV-TRAIN-043 |
| CONTRACT-TRAIN-047 | GET | `/training-microcycles/{microcycle_id}` | `get_training_microcycle_api_v1_training_microcycles__microcycle_id__get` | — | `TrainingMicrocycleWithSessions` | EVIDENCIADO | INV-TRAIN-043 |
| CONTRACT-TRAIN-048 | POST | `/training-microcycles` | `create_training_microcycle_api_v1_training_microcycles_post` | `TrainingMicrocycleCreate` | `TrainingMicrocycleResponse` | EVIDENCIADO | INV-TRAIN-001, INV-TRAIN-043 |
| CONTRACT-TRAIN-049 | PATCH | `/training-microcycles/{microcycle_id}` | `update_training_microcycle_api_v1_training_microcycles__microcycle_id__patch` | `TrainingMicrocycleUpdate` | `TrainingMicrocycleResponse` | EVIDENCIADO | INV-TRAIN-043 |
| CONTRACT-TRAIN-050 | DELETE | `/training-microcycles/{microcycle_id}?reason=` | `delete_training_microcycle_api_v1_training_microcycles__microcycle_id__delete` | query `reason` | 204 | EVIDENCIADO | INV-TRAIN-008 |
| CONTRACT-TRAIN-051 | GET | `/training-microcycles/teams/{team_id}/current` | `get_current_microcycle_api_v1_training_microcycles_teams__team_id__current_get` | query opcional `at_date` | `TrainingMicrocycleResponse` | EVIDENCIADO | (derivado) |
| CONTRACT-TRAIN-052 | GET | `/training-microcycles/{microcycle_id}/summary` | `get_microcycle_summary_api_v1_training_microcycles__microcycle_id__summary_get` | — | `dict` | EVIDENCIADO | INV-TRAIN-020 |

---

### 5.7 Banco de Exercícios + Tags + Favoritos

> **decision_trace:** `[DEC-TRAIN-EXB-001, DEC-TRAIN-EXB-001B, DEC-TRAIN-EXB-002, DEC-TRAIN-EXB-RBAC-001]`

#### 5.7.1 Modelo de Scope e Visibilidade (DEC-TRAIN-EXB-001, EXB-001B)

```yaml
ExerciseScope:
  SYSTEM: >
    Exercícios de catálogo global, criados por admin.
    Imutáveis para usuários ORG (INV-TRAIN-048).
    Visíveis para todas as orgs.
  ORG: >
    Exercícios criados por um treinador dentro de uma org.
    Pertencem a exatamente uma organization_id (INV-TRAIN-049).
    Visibilidade controlada por visibility_mode.

ExerciseVisibilityMode:  # apenas para scope=ORG
  org_wide: >
    Todos os membros da organização veem o exercício.
  restricted: >
    Apenas o criador e usuários explicitamente listados na
    tabela exercise_acl podem ver/usar o exercício (INV-TRAIN-EXB-ACL-001).

ExerciseACL:  # tabela exercise_acl
  - Só existe se visibility_mode = restricted (INV-TRAIN-EXB-ACL-002)
  - user_id deve pertencer à mesma org (INV-TRAIN-EXB-ACL-003)
  - Apenas o creator pode gerenciar ACL OU role "Treinador" pode
    gerenciar exercícios da própria org (DEC-TRAIN-RBAC-001)
  - O criador tem acesso implícito sem registro na ACL (INV-TRAIN-EXB-ACL-005)
  - Unique constraint (exercise_id, user_id) (INV-TRAIN-EXB-ACL-006)
```

#### 5.7.2 Contratos existentes (CRUD exercícios + tags + favoritos)

| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-053 | GET | `/exercises` | `list_exercises_api_v1_exercises_get` | query filtros (`scope`, `organization_id`, etc.) | `ExerciseListResponse` | EVIDENCIADO | INV-TRAIN-047, INV-TRAIN-051 |
| CONTRACT-TRAIN-054 | POST | `/exercises` | `create_exercise_api_v1_exercises_post` | `ExerciseCreate` (inclui `scope`, `visibility_mode`) | `Exercise` | EVIDENCIADO | INV-TRAIN-047, INV-TRAIN-049, INV-TRAIN-EXB-ACL-001 |
| CONTRACT-TRAIN-055 | GET | `/exercises/{exercise_id}` | `get_exercise_api_v1_exercises__exercise_id__get` | — | `Exercise` | EVIDENCIADO | INV-TRAIN-048 |
| CONTRACT-TRAIN-056 | PATCH | `/exercises/{exercise_id}` | `update_exercise_api_v1_exercises__exercise_id__patch` | `ExerciseUpdate` | `Exercise` | EVIDENCIADO | INV-TRAIN-048 (SYSTEM imutável) |
| CONTRACT-TRAIN-057 | GET | `/exercise-tags` | `list_tags_api_v1_exercise_tags_get` | — | `ExerciseTag[]` | EVIDENCIADO | — |
| CONTRACT-TRAIN-058 | POST | `/exercise-tags` | `create_tag_api_v1_exercise_tags_post` | `ExerciseTagCreate` | `ExerciseTag` | EVIDENCIADO | — |
| CONTRACT-TRAIN-059 | PATCH | `/exercise-tags/{tag_id}` | `update_tag_api_v1_exercise_tags__tag_id__patch` | `ExerciseTagUpdate` | `ExerciseTag` | EVIDENCIADO | — |
| CONTRACT-TRAIN-060 | GET | `/exercise-favorites` | `list_my_favorites_api_v1_exercise_favorites_get` | — | `ExerciseFavorite[]` | EVIDENCIADO | INV-TRAIN-050 |
| CONTRACT-TRAIN-061 | POST | `/exercise-favorites` | `favorite_exercise_api_v1_exercise_favorites_post` | `{exercise_id}` | `ExerciseFavorite` | EVIDENCIADO | INV-TRAIN-050 |
| CONTRACT-TRAIN-062 | DELETE | `/exercise-favorites/{exercise_id}` | `unfavorite_exercise_api_v1_exercise_favorites__exercise_id__delete` | — | 204 | EVIDENCIADO | — |

#### 5.7.3 Novos contratos: ACL, Visibilidade, Cópia, Mídia (DEC-TRAIN-EXB-002, RBAC-001)

| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-091 | PATCH | `/exercises/{exercise_id}/visibility` | `update_exercise_visibility` | `{visibility_mode: "org_wide"\|"restricted"}` | `Exercise` | GAP | INV-TRAIN-EXB-ACL-001, INV-TRAIN-EXB-ACL-002 |
| CONTRACT-TRAIN-092 | GET | `/exercises/{exercise_id}/acl` | `list_exercise_acl` | — | `ExerciseACLEntry[]` | GAP | INV-TRAIN-EXB-ACL-002, INV-TRAIN-EXB-ACL-003 |
| CONTRACT-TRAIN-093 | POST | `/exercises/{exercise_id}/acl` | `add_exercise_acl_user` | `{user_id: uuid}` | `ExerciseACLEntry` | GAP | INV-TRAIN-EXB-ACL-003, INV-TRAIN-EXB-ACL-006 |
| CONTRACT-TRAIN-094 | DELETE | `/exercises/{exercise_id}/acl/{user_id}` | `remove_exercise_acl_user` | — | 204 | GAP | INV-TRAIN-EXB-ACL-004 |
| CONTRACT-TRAIN-095 | POST | `/exercises/{exercise_id}/copy-to-org` | `copy_exercise_to_org` | `{organization_id: uuid, visibility_mode?: str}` | `Exercise` (novo, scope=ORG) | GAP | INV-TRAIN-047, INV-TRAIN-049 |

**Regras normativas para novos contratos:**

1. **CONTRACT-TRAIN-091 (visibility toggle):**
   - Apenas scope=ORG. Se scope=SYSTEM, retornar 403.
   - Ao mudar de `restricted` → `org_wide`, ACL existente é mantida (sem purge), mas torna-se irrelevante.
   - Ao mudar de `org_wide` → `restricted`, ACL começa vazia (apenas criador tem acesso implícito).
   - Autoridade: creator do exercício OU role "Treinador" na mesma org (DEC-TRAIN-RBAC-001).

2. **CONTRACT-TRAIN-092/093/094 (ACL management):**
   - ACL só pode ser gerenciada se `visibility_mode = restricted` (INV-TRAIN-EXB-ACL-002).
   - Se `visibility_mode = org_wide`, retornar 409 Conflict ("ACL not applicable for org_wide visibility").
   - `user_id` adicionado DEVE pertencer à mesma org (INV-TRAIN-EXB-ACL-003); se não, 422.
   - Unique constraint `(exercise_id, user_id)`: POST duplicado retorna 409.
   - Autoridade: creator OU role "Treinador" (DEC-TRAIN-RBAC-001, INV-TRAIN-EXB-ACL-004).

3. **CONTRACT-TRAIN-095 (copy SYSTEM→ORG):**
   - Só funciona se o exercício fonte é scope=SYSTEM. Se ORG, retornar 422.
   - Cria um novo exercício com scope=ORG, `organization_id` do request, `created_by` do token.
   - `visibility_mode` padrão = `restricted` (pode ser overridden no request).
   - Não altera o exercício SYSTEM original.
   - Invariantes: INV-TRAIN-047 (scope válido), INV-TRAIN-049 (single org).

#### 5.7.4 Mídia de Exercício (DEC-TRAIN-EXB-001)

```yaml
ExerciseMedia:
  exercise_id: uuid (FK exercises)
  media_type: enum(IMAGE, VIDEO, DOCUMENT)  # INV-TRAIN-052
  url: string  # S3/CDN presigned URL ou path relativo
  thumbnail_url?: string
  order: int  # ordenação dentro do exercício
  created_at: datetime
```

> **Nota:** Contratos de upload de mídia (presigned URL) não estão definidos nesta fase.
> Quando materializado, adicionar CONTRACT-TRAIN-096+ para upload/delete de mídia.

#### 5.7.5 RBAC para Banco de Exercícios (DEC-TRAIN-RBAC-001)

```yaml
ExerciseRBAC:
  role_treinador: >
    O role "Treinador" (como existe no RBAC do sistema) pode:
    - Criar exercícios ORG na própria org
    - Editar exercícios ORG que criou
    - Gerenciar ACL de exercícios ORG que criou
    - Usar copy-to-org de exercícios SYSTEM
  role_admin_org: >
    Admin da org pode gerenciar todos os exercícios ORG da própria org
    (independente de quem criou).
  scope_SYSTEM: >
    Apenas admin global pode criar/editar exercícios SYSTEM.
    Treinadores/Org admins não podem modificar exercícios SYSTEM.
```

---

### 5.8 Session Templates

| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-063 | GET | `/session-templates` | `list_session_templates_api_v1_session_templates_get` | query `active_only` | `SessionTemplateListResponse` | EVIDENCIADO | INV-TRAIN-035 |
| CONTRACT-TRAIN-064 | POST | `/session-templates` | `create_session_template_api_v1_session_templates_post` | `SessionTemplateCreate` | `SessionTemplate` | EVIDENCIADO | INV-TRAIN-035, INV-TRAIN-001 |
| CONTRACT-TRAIN-065 | GET | `/session-templates/{template_id}` | `get_session_template_api_v1_session_templates__template_id__get` | — | `SessionTemplate` | EVIDENCIADO | — |
| CONTRACT-TRAIN-066 | PATCH | `/session-templates/{template_id}` | `update_session_template_api_v1_session_templates__template_id__patch` | `SessionTemplateUpdate` | `SessionTemplate` | EVIDENCIADO | INV-TRAIN-001 |
| CONTRACT-TRAIN-067 | DELETE | `/session-templates/{template_id}` | `delete_session_template_api_v1_session_templates__template_id__delete` | — | 204 | EVIDENCIADO | — |
| CONTRACT-TRAIN-068 | PATCH | `/session-templates/{template_id}/favorite` | `toggle_favorite_template_api_v1_session_templates__template_id__favorite_patch` | — | `SessionTemplate` | EVIDENCIADO | — |

---

### 5.9 Analytics (treino) + Rankings wellness + Top performers

> **decision_trace:** `[DEC-TRAIN-003]`

#### Training analytics
| ID | Método | Path | operationId | Request | Response | Status |
|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-069 | GET | `/analytics/team/{team_id}/summary` | `get_team_summary_api_v1_analytics_team__team_id__summary_get` | query `start_date`, `end_date` | `TeamSummaryResponse` | EVIDENCIADO |
| CONTRACT-TRAIN-070 | GET | `/analytics/team/{team_id}/weekly-load` | `get_weekly_load_api_v1_analytics_team__team_id__weekly_load_get` | query `weeks` | `WeeklyLoadResponse` | EVIDENCIADO |
| CONTRACT-TRAIN-071 | GET | `/analytics/team/{team_id}/deviation-analysis` | `get_deviation_analysis_api_v1_analytics_team__team_id__deviation_analysis_get` | query `start_date`, `end_date` | `DeviationAnalysisResponse` | EVIDENCIADO |
| CONTRACT-TRAIN-072 | GET | `/analytics/team/{team_id}/prevention-effectiveness` | `get_prevention_effectiveness_api_v1_analytics_team__team_id__prevention_effectiveness_get` | query `start_date`, `end_date`, `category` | `PreventionEffectivenessResponse` | EVIDENCIADO |

#### Wellness rankings (SSOT OpenAPI incompleto)
Status: **PARCIAL** (OpenAPI sem schema e service divergente do SSOT em partes).

Shape normativo mínimo (list):
```yaml
TeamWellnessRankingItem:
  team_id: uuid
  team_name: string
  response_rate_pre: number # 0..100
  response_rate_post: number # 0..100
  avg_rate: number # 0..100
  rank: int
  athletes_90plus: int
  calculated_at: datetime
```

| ID | Método | Path | operationId | Response (mínimo) | Status | Observações |
|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-073 | GET | `/analytics/wellness-rankings` | `get_wellness_rankings_api_v1_analytics_wellness_rankings_get` | `TeamWellnessRankingItem[]` | PARCIAL | response_model ausente no router |
| CONTRACT-TRAIN-074 | POST | `/analytics/wellness-rankings/calculate` | `calculate_rankings_manually_api_v1_analytics_wellness_rankings_calculate_post` | `{month_reference, teams_processed, ...}` | PARCIAL | cálculo mensal evidenciado, mas service tem trechos inconsistentes |
| CONTRACT-TRAIN-075 | GET | `/analytics/wellness-rankings/{team_id}/athletes-90plus?month=` | `get_team_athletes_90plus_api_v1_analytics_wellness_rankings__team_id__athletes_90plus_get` | `{athletes:[...], total}` | PARCIAL | implementar via `team_registrations` (SSOT) |

#### Top performers (endpoint em `/teams`)

> **DEC-TRAIN-003 (normativo):** `CONTRACT-TRAIN-076` é o **endpoint canônico** que o FE
> deve consumir para a tela principal de top performers.
> `CONTRACT-TRAIN-075` serve apenas como **drilldown especializado** (atletas >90%).
> O FE NÃO DEVE usar `CONTRACT-TRAIN-075` como fonte primária da listagem.

| ID | Método | Path | operationId | Response (mínimo) | Status | Papel (DEC-TRAIN-003) |
|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-076 | GET | `/teams/{team_id}/wellness-top-performers?month=` | `get_team_wellness_top_performers_api_v1_teams__team_id__wellness_top_performers_get` | `{month, team_id, team_name, top_performers:[...]}` | EVIDENCIADO | **CANÔNICO** (tela principal FE) |
| CONTRACT-TRAIN-075 | GET | `/analytics/wellness-rankings/{team_id}/athletes-90plus?month=` | `get_team_athletes_90plus_...` | `{athletes:[...], total}` | PARCIAL | DRILLDOWN (detalhe >90%) |

---

### 5.10 Alertas e Sugestões (Step 18)

Status: **DIVERGENTE_DO_SSOT** (tipos de IDs em rotas não batem com DB).

SSOT DB:
- `training_alerts.id` é `uuid`, mas rota usa `alert_id: int`.
- `training_suggestions.id` é `uuid`, mas rota usa `suggestion_id: int`.
- `team_id` é `uuid`, mas rotas usam `team_id: int`.

Contratos (AS-IS expostos no OpenAPI; TO-BE deve convergir para UUIDs):

| ID | Método | Path | operationId | Status |
|---|---|---|---|---|
| CONTRACT-TRAIN-077 | GET | `/training/alerts-suggestions/alerts/team/{team_id}/active` | `get_active_alerts_api_v1_training_alerts_suggestions_alerts_team__team_id__active_get` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-078 | GET | `/training/alerts-suggestions/alerts/team/{team_id}/history` | `get_alert_history_api_v1_training_alerts_suggestions_alerts_team__team_id__history_get` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-079 | GET | `/training/alerts-suggestions/alerts/team/{team_id}/stats` | `get_alert_stats_api_v1_training_alerts_suggestions_alerts_team__team_id__stats_get` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-080 | POST | `/training/alerts-suggestions/alerts/{alert_id}/dismiss` | `dismiss_alert_api_v1_training_alerts_suggestions_alerts__alert_id__dismiss_post` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-081 | GET | `/training/alerts-suggestions/suggestions/team/{team_id}/pending` | `get_pending_suggestions_api_v1_training_alerts_suggestions_suggestions_team__team_id__pending_get` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-082 | GET | `/training/alerts-suggestions/suggestions/team/{team_id}/history` | `get_suggestion_history_api_v1_training_alerts_suggestions_suggestions_team__team_id__history_get` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-083 | GET | `/training/alerts-suggestions/suggestions/team/{team_id}/stats` | `get_suggestion_stats_api_v1_training_alerts_suggestions_suggestions_team__team_id__stats_get` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-084 | POST | `/training/alerts-suggestions/suggestions/{suggestion_id}/apply` | `apply_suggestion_api_v1_training_alerts_suggestions_suggestions__suggestion_id__apply_post` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-085 | POST | `/training/alerts-suggestions/suggestions/{suggestion_id}/dismiss` | `dismiss_suggestion_api_v1_training_alerts_suggestions_suggestions__suggestion_id__dismiss_post` | DIVERGENTE_DO_SSOT |

---

### 5.11 FASE_3 — Presença Oficial, Pending Queue, Atleta Pre-Session, IA Coach (v1.3.0)

> **decision_trace:** `[INV-TRAIN-063..081]`  
> Contratos novos da FASE_3. Nenhum implementado ainda — status GAP.  
> Shapes mínimos definidos abaixo; operationIds serão materializados pelas ARs correspondentes.

#### Presença oficial e fila de pendências

| ID | Método | Path | operationId | Request shape (mínimo) | Response shape (mínimo) | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-096 | GET | `/athlete/training-sessions/{session_id}/preview` | `get_athlete_session_preview` | — | `AthleteSessionPreview` | GAP | INV-TRAIN-068, INV-TRAIN-069 |
| CONTRACT-TRAIN-097 | POST | `/training-sessions/{session_id}/pre-confirm` | `pre_confirm_attendance` | `{athlete_id?: uuid}` | `{status: "pre_confirmed", is_official: false}` | GAP | INV-TRAIN-063 |
| CONTRACT-TRAIN-098 | POST | `/training-sessions/{session_id}/close` | `close_session_with_attendance` | `{attendance: AttendanceBatch, allow_pending: bool}` | `{closed: true, pending_items: PendingItem[]}` | GAP | INV-TRAIN-064, INV-TRAIN-065 |
| CONTRACT-TRAIN-099 | GET | `/training/pending-items` | `list_pending_items` | query: `?team_id=&status=open` | `PendingItem[]` | GAP | INV-TRAIN-066 |
| CONTRACT-TRAIN-100 | PATCH | `/training/pending-items/{item_id}/resolve` | `resolve_pending_item` | `{resolution: string, new_status: present\|absent\|justified}` | `PendingItem` | GAP | INV-TRAIN-066, INV-TRAIN-067 |

#### Wellness content gate

| ID | Método | Path | operationId | Request shape | Response shape | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-105 | GET | `/athlete/wellness-content-gate/{session_id}` | `check_wellness_content_gate` | — | `{has_wellness: bool, can_see_full_content: bool, blocked_reason?: string}` | GAP | INV-TRAIN-071, INV-TRAIN-076 |

#### IA Coach (atleta + treinador)

| ID | Método | Path | operationId | Request shape | Response shape | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-101 | POST | `/ai-coach/draft-session` | `ai_draft_session` | `{team_id: uuid, context: object}` | `{draft_id: uuid, suggested_session: object, justification: string}` | GAP | INV-TRAIN-075, INV-TRAIN-080, INV-TRAIN-081 |
| CONTRACT-TRAIN-102 | PATCH | `/ai-coach/draft-session/{draft_id}/apply` | `apply_ai_draft` | `{edits?: object}` | `{training_session_id: uuid, applied: true}` | GAP | INV-TRAIN-075, INV-TRAIN-080 |
| CONTRACT-TRAIN-103 | POST | `/ai-coach/athlete-chat` | `ai_athlete_chat` | `{session_id: uuid, message: string}` | `{response: string, type: "educational"\|"motivational"\|"suggestion"}` | GAP | INV-TRAIN-072, INV-TRAIN-073, INV-TRAIN-074 |
| CONTRACT-TRAIN-104 | POST | `/ai-coach/justify-suggestion` | `ai_justify_suggestion` | `{suggestion_id: uuid}` | `{justification: string, references: string[]}` | GAP | INV-TRAIN-081 |

#### Shapes mínimos novos (FASE_3)

```yaml
AthleteSessionPreview:
  session_id: uuid
  session_date: date
  session_title: string
  focus_items: FocusItem[]
  exercises: ExercisePreviewItem[]  # só nome + duração + media_url (sem notas internas do coach)
  wellness_status: {has_pre: bool, can_see_full: bool}

PendingItem:
  id: uuid
  training_session_id: uuid
  athlete_id: uuid
  athlete_name: string
  type: "attendance_mismatch" | "missing_wellness" | "late_arrival"
  created_at: datetime
  status: "open" | "resolved"
  resolution?: string
  resolved_by?: uuid
  resolved_at?: datetime
```

> **Nota normativa (INV-TRAIN-063):** `pre-confirm` NÃO é presença oficial.  
> O FE DEVE exibir label distinto (ex: "Confirmou presença" vs "Presente ✓") para evitar ambiguidade.  
> Presença oficial é registrada APENAS em `close` (CONTRACT-TRAIN-098).

> **Nota normativa (INV-TRAIN-071, INV-TRAIN-076):** Se `wellness_status.can_see_full == false`,  
> o FE DEVE ocultar detalhes de exercícios e mostrar prompt de wellness.  
> O backend DEVE retornar shape parcial (sem `exercises` completos) quando wellness ausente.

---

## 6) Contratos desabilitados no agregador (BLOQUEADO)

> Estes contratos existem como código, mas **não estão expostos** em `Hb Track - Backend/app/api/v1/api.py` e portanto **não aparecem** no `openapi.json` atual.

### 6.1 Exports (Step 23)

> **decision_trace:** `[DEC-TRAIN-004]`

Fonte: `Hb Track - Backend/app/api/v1/routers/exports.py`

| ID | Método | Path | operationId | Status | Invariantes-chave |
|---|---|---|---|---|---|
| CONTRACT-TRAIN-086 | POST | `/analytics/export-pdf` | (não exposto no OpenAPI atual) | BLOQUEADO | INV-TRAIN-012 |
| CONTRACT-TRAIN-087 | GET | `/analytics/exports/{job_id}` | (não exposto no OpenAPI atual) | BLOQUEADO | INV-TRAIN-012 |
| CONTRACT-TRAIN-088 | GET | `/analytics/exports` | (não exposto no OpenAPI atual) | BLOQUEADO | INV-TRAIN-012 |
| CONTRACT-TRAIN-089 | GET | `/analytics/export-rate-limit` | (não exposto no OpenAPI atual) | BLOQUEADO | INV-TRAIN-012 |

#### Estado Degradado sem Worker (DEC-TRAIN-004) — Normativo

> **DEC-TRAIN-004:** Quando os contratos de export forem habilitados,
> se o worker Celery/Redis não estiver disponível, o backend DEVE:
>
> 1. Retornar **202 Accepted** com `{"status": "queued", "degraded": true, "message": "Export enfileirado, processamento pode estar lento"}`.
> 2. O FE DEVE exibir estado degradado amigável (banner/toast) — não bloquear a UI.
> 3. **NÃO retornar 500/503** — isso é falha, não degradação.
> 4. Polling via CONTRACT-TRAIN-087 continua funcionando; timeout estendido.
> 5. Rate limit (CONTRACT-TRAIN-089) DEVE ser respeitado mesmo em estado degradado.
>
> **Invariantes:** INV-TRAIN-012 (tenant isolation de exports).  
> **Tela:** SCREEN-TRAIN-013 deve mostrar indicador de degradação.

### 6.2 LGPD — Export de dados do atleta (Step 24)

Fonte: `Hb Track - Backend/app/api/v1/routers/athlete_export.py`

| ID | Método | Path | operationId | Status | Invariantes-chave |
|---|---|---|---|---|---|
| CONTRACT-TRAIN-090 | GET | `/athletes/me/export-data?format=json|csv` | (não exposto no OpenAPI atual) | BLOQUEADO | INV-TRAIN-025 |

---

## 7) Divergências e Gaps (paridade)

### GAP-CONTRACT-1 — Wellness FE aponta para endpoints errados
- FE chama `/wellness_pre` e `/wellness_post` sem prefixo `/wellness-pre|/wellness-post`.
- Contrato normativo exige `CONTRACT-TRAIN-029..039`.

### GAP-CONTRACT-2 — Rankings wellness e TopPerformers usam tipos errados no FE
- FE trata `team_id` como `number` e usa `parseInt` em rotas.
- SSOT DB define `teams.id` como UUID.

### GAP-CONTRACT-3 — Alertas/Sugestões Step 18 com IDs `int` vs DB `uuid`
- Endpoint exposto, mas incompatível com schema (team_id/alert_id/suggestion_id).
- Deve ser tratado como **bloqueante** para qualquer UI que dependa dessas rotas.

### GAP-CONTRACT-4 — OpenAPI incompleto para rankings
- Endpoints de rankings (`/analytics/wellness-rankings*`) não têm response_model, gerando schema `{}`.
- Este documento define o shape mínimo normativo até o contrato ser tipado.

### GAP-CONTRACT-5 — Exports/LGPD routers existem mas estão desabilitados
- UI existe para export PDF, invariantes existem, mas as rotas não estão incluídas no agregador v1.

### GAP-CONTRACT-6 — FASE_3: Presença oficial, pending queue, wellness content gate (v1.3.0)
- Contratos CONTRACT-TRAIN-096..100, 105 definidos normativamente na §5.11 mas **não implementados**.
- Nenhum endpoint existe ainda no backend — ARs AR-TRAIN-017/018/019 devem materializar.
- Shapes `AthleteSessionPreview` e `PendingItem` são normativos mínimos, sem âncora no SSOT DB (tabelas ainda não criadas).

### GAP-CONTRACT-7 — FASE_3: IA Coach endpoints (v1.3.0)
- Contratos CONTRACT-TRAIN-101..104 definidos normativamente na §5.11 mas **não implementados**.
- Funcionalidade de IA está marcada como P2 — endpoints serão materializados por AR-TRAIN-021.
- Shapes de request/response são provisórios — dependem da interface de LLM/agent escolhida.

---

## 8) Proposta fora do PRD — não normativa

### “Training Suggestions” (planejamento inteligente)

Há um router em `Hb Track - Backend/app/api/v1/routers/training_suggestions.py`, e chamadas no FE (`/training-suggestions`), porém:
- não está exposto no agregador v1 (não aparece no OpenAPI SSOT),
- PRD marca recomendador de treinos como futuro.

Portanto, **não** entra como contrato normativo do MCP TRAINING nesta fase.
