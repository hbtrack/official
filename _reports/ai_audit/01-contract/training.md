# Contract Diff Max — Módulo: training

> Auditoria técnica de repositório contract-driven — modo Contract Diff Max
> Data: 2026-04-23
> Módulo: training
> Regras: AGAUDIT v1.1

---

## Fontes auditadas (por ordem de autoridade)

| Camada | Arquivo | Linha base |
|---|---|---|
| Source master | `docs/hbtrack/modulos/training/graph/openapi_paths.yaml` | 4423 linhas |
| Generated | `generated/contracts/openapi/paths/training.yaml` | 4416 linhas |
| Contract | `contracts/openapi/paths/training.yaml` | 4416 linhas |
| Runtime API | `src/training/api/*.py` | 14 handlers |
| Runtime schemas | `src/training/schemas/*.py` | 9 arquivos |

**Paridade entre camadas de contrato:**
- Diff `source master ↔ generated`: apenas cabeçalho de comentários — conteúdo **idêntico** ✓
- Diff `generated ↔ contracts`: **idêntico** ✓
- Contagem de operationIds: **53 em todas as três camadas** ✓

**Conclusão preliminar:** não existe drift de derivação/compilação. As 3 camadas de contrato são equivalentes. Todos os desvios encontrados são entre contrato (fonte) e runtime (implementação).

---

## Mapa operationId → handler

| operationId | Handler | Arquivo | Método |
|---|---|---|---|
| listTrainingSessions | `list_training_sessions` | sessions.py | GET |
| createTrainingSession | `create_training_session` | sessions.py | POST |
| getTrainingSessionById | `get_training_session` | sessions.py | GET |
| updateTrainingSession | `update_training_session` | sessions.py | PATCH |
| deleteTrainingSession | `delete_training_session` | sessions.py | DELETE |
| publishTrainingSession | `publish_training_session` | sessions.py | POST |
| unpublishTrainingSession | `unpublish_training_session` | sessions.py | POST |
| startTrainingSession | `start_training_session` | sessions.py | POST |
| completeTrainingSession | `complete_training_session` | sessions.py | POST |
| cancelTrainingSession | `cancel_training_session` | sessions.py | POST |
| archiveTrainingSession | `archive_training_session` | sessions.py | POST |
| listSessionBlocks | `list_session_blocks` | blocks.py | GET |
| addSessionBlock | `add_session_block` | blocks.py | POST |
| getSessionBlock | `get_session_block` | blocks.py | GET |
| updateSessionBlock | `update_session_block` | blocks.py | PATCH |
| deleteSessionBlock | `delete_session_block` | blocks.py | DELETE |
| reorderSessionBlocks | `reorder_session_blocks` | blocks.py | POST |
| listSessionAttendance | `list_session_attendance` | attendance.py | GET |
| recordSessionAttendance | `record_session_attendance` | attendance.py | POST |
| submitWellnessPre | `submit_wellness_pre` | wellness.py | POST |
| getWellnessPre | `get_wellness_pre` | wellness.py | GET |
| updateWellnessPre | `update_wellness_pre` | wellness.py | PATCH |
| submitWellnessPost | `submit_wellness_post` | wellness.py | POST |
| getWellnessPost | `get_wellness_post` | wellness.py | GET |
| updateWellnessPost | `update_wellness_post` | wellness.py | PATCH |
| listMesocycles | `list_mesocycles` | planning.py | GET |
| createMesocycle | `create_mesocycle` | planning.py | POST |
| getMesocycleById | `get_mesocycle` | planning.py | GET |
| updateMesocycle | `update_mesocycle` | planning.py | PATCH |
| listMicrocycles | `list_microcycles` | planning.py | GET |
| createMicrocycle | `create_microcycle` | planning.py | POST |
| getMicrocycleById | `get_microcycle` | planning.py | GET |
| updateMicrocycle | `update_microcycle` | planning.py | PATCH |
| listExecutionRecords | `list_execution_records` | execution.py | GET |
| createExecutionRecord | `create_execution_record` | execution.py | POST |
| getExecutionRecord | `get_execution_record` | execution.py | GET |
| listSessionObjectives | `list_session_objectives` | execution.py | GET |
| createSessionObjective | `create_session_objective` | execution.py | POST |
| listFeedbackThreads | `list_feedback_threads` | feedback.py | GET |
| createFeedbackThread | `create_feedback_thread` | feedback.py | POST |
| closeFeedbackThread | `close_feedback_thread` | feedback.py | POST |
| listAttentionQueueItems | `list_attention_queue_items` | attention.py | GET |
| resolveAttentionQueueItem | `resolve_attention_queue_item` | attention.py | POST |
| dismissAttentionQueueItem | `dismiss_attention_queue_item` | attention.py | POST |
| escalateAttentionQueueItem | `escalate_attention_queue_item` | attention.py | POST |
| listRecommendations | `list_recommendations` | recommendations.py | GET |
| acceptRecommendation | `accept_recommendation` | recommendations.py | POST |
| dismissRecommendation | `dismiss_recommendation` | recommendations.py | POST |
| getIneligibilityStatus | `get_ineligibility_status` | eligibility.py | GET |
| submitIneligibilityDeclaration | `submit_ineligibility_declaration` | eligibility.py | POST |
| getLoadChart | `get_load_chart` | analytics.py | GET |
| listChatMessages | `list_chat_messages` | chat.py | GET |
| submitTrainingSuggestion | `submit_training_suggestion` | chat.py | POST |

**Resultado:** 53/53 operationIds com handler correspondente. Zero operationIds órfãos. Zero handlers sem contrato.

---

## Achados

---

### ACHADO-CD-001

```
ACHADO-ID: ACHADO-CD-001
Categoria: Formato de resposta de erro — problem+json vs ErrorOut plano
Módulo: training (todos os 53 endpoints)
Severidade: crítica
Estado: erro confirmado
```

**Camadas em conflito:**
- contrato (source master declara `application/problem+json`)
- runtime (retorna `application/json` com `{"detail": str}`)
- schemas (ErrorOut = `{detail: str}`)

**Descrição:**
O source master declara todas as respostas de erro como `application/problem+json` com `$ref: ../components/schemas/shared/problem.yaml`. O schema `problem.yaml` é RFC 7807 com os campos **required**: `type`, `title`, `status`, `traceId`. O runtime retorna o schema `ErrorOut` que contém apenas `{"detail": "..."}` em `application/json`.

**Evidência A — problem.yaml (contrato):**
```yaml
required: [type, title, status, traceId]
additionalProperties: false
properties:
  type: string (minLength: 1)
  title: string (minLength: 1)
  status: integer [100–599]
  detail: string
  traceId: string (pattern: ^[A-Za-z0-9][...])
```

**Evidência B — runtime schemas/sessions.py:**
```python
class ErrorOut(Schema):
    detail: str
```

**Causa-raiz:**
O `ErrorOut` foi implementado como schema simplificado. O decorator `@map_exceptions` usa `HttpError(code, str(exc))` cujo output padrão do Django Ninja é `{"detail": "..."}` — sem `type`, `title`, `status`, `traceId`. Nenhum middleware de transformação para problem+json foi implementado.

**Impacto:**
Clientes que parseiam respostas de erro como `application/problem+json` (esperando `type`, `title`, `status`, `traceId`) receberão erro de deserialização. O `traceId` que seria usado para correlação de logs pelo cliente está ausente. Viola RFC 7807 e o invariante declarado no contrato.

**Afeta:** todos os 53 endpoints — qualquer resposta 400, 401, 403, 404, 409, 422 retorna formato incorreto.

**Correção mínima:**
Adicionar middleware ou exception handler global no Django Ninja que converta `HttpError` para o envelope RFC 7807:
```python
{"type": "...", "title": "...", "status": code, "traceId": flow_id, "detail": str(exc)}
```
e sete `Content-Type: application/problem+json`.

**Correção ideal:**
Substituir `ErrorOut` por `ProblemOut` com os 4 campos required. Integrar `flow_id` (já presente nos logs de erro como `"flow_id"`) como `traceId`.

**Bloqueia merge?:** sim

**Classificação:** erro confirmado (bug real — todos os error envelopes divergem do contrato)

---

### ACHADO-CD-002

```
ACHADO-ID: ACHADO-CD-002
Categoria: Request schema completamente divergente — submitWellnessPre
Módulo: training / wellness
Severidade: crítica
Estado: erro confirmado
```

**Camadas em conflito:**
- contrato (source master — submitWellnessPre requestBody)
- runtime (SubmitWellnessPreIn schema)
- schemas (src/training/schemas/wellness.py)

**Descrição:**
O source master e o runtime descrevem APIs de submissão de wellness pré completamente diferentes. O contrato define um modelo centrado em `sleepQuality` e `sleepHours` como campos obrigatórios, com `additionalProperties: false`. O runtime implementa um modelo diferente centrado em `readiness`, `sleep_quality`, `mood`, `fatigue`, `muscle_soreness` — e não tem `sleepHours`.

**Evidência A — source master (linhas 1296–1317):**
```yaml
requestBody:
  schema:
    additionalProperties: false
    required: [athleteId, sleepQuality, sleepHours]
    properties:
      athleteId: {type: string, format: uuid}
      sleepQuality: {type: integer, minimum: 1, maximum: 5}
      sleepHours: {type: number, minimum: 0, maximum: 24}
```

**Evidência B — runtime (src/training/schemas/wellness.py:28-35):**
```python
class SubmitWellnessPreIn(Schema):
    athlete_id: uuid.UUID          # → athleteId ✓
    readiness: Optional[int] = None        # NÃO está no contrato
    sleep_quality: Optional[int] = None    # → sleepQuality, mas Optional no runtime vs required no contrato
    mood: Optional[int] = None             # NÃO está no contrato
    fatigue: Optional[int] = None          # NÃO está no contrato
    muscle_soreness: Optional[int] = None  # NÃO está no contrato
    notes: Optional[str] = None            # NÃO está no contrato
```

**Divergências exatas:**

| Campo contrato | No runtime? | Obrigatoriedade |
|---|---|---|
| `athleteId` (required) | sim (`athlete_id`) | required ✓ |
| `sleepQuality` (required) | sim (`sleep_quality`), mas **Optional** | diverge — required no contrato, opcional no runtime |
| `sleepHours` (required) | **AUSENTE** | required no contrato, **inexiste** no runtime |
| `readiness` | **não está no contrato** | extra no runtime |
| `mood` | **não está no contrato** | extra no runtime |
| `fatigue` | **não está no contrato** | extra no runtime |
| `muscle_soreness` | **não está no contrato** | extra no runtime |
| `notes` | **não está no contrato** | extra no runtime |

**Impacto:**
- Cliente que segue o contrato: envia `{athleteId, sleepQuality, sleepHours}` → runtime aceita `athleteId` e `sleepQuality` (mapeado para `sleep_quality`), ignora `sleepHours`, não valida que foi enviado.
- Cliente que usa a API real (runtime): envia `{athleteId, readiness, mood, ...}` → funciona, mas viola `additionalProperties: false` do contrato.
- O campo `sleepHours` — central no modelo de wellness do contrato — não existe no runtime.

**Correção mínima:**
Adicionar `sleep_hours: Optional[float] = None` ao `SubmitWellnessPreIn` E ao modelo de domínio/banco correspondente.

**Correção ideal:**
Definir qual é o modelo canônico de wellness (o contrato ou o runtime?) e alinhar o outro. Se `readiness`, `mood`, `fatigue`, `muscle_soreness` são campos reais do produto, adicionar ao source master. Se `sleepHours` é o modelo canônico, o runtime precisa ser atualizado.

**Bloqueia merge?:** sim

**Classificação:** erro confirmado (schema soberano e runtime descrevem APIs de wellness diferentes — ausência de `sleepHours` no runtime é a evidência mais grave)

---

### ACHADO-CD-003

```
ACHADO-ID: ACHADO-CD-003
Categoria: Request schema divergente — updateTrainingSession (campos extras no contrato)
Módulo: training / sessions
Severidade: alta
Estado: drift provável
```

**Camadas em conflito:**
- contrato (source master — updateTrainingSession requestBody)
- runtime (UpdateTrainingSessionIn schema)
- schemas (src/training/schemas/sessions.py)

**Descrição:**
O source master declara dois campos opcionais no PATCH `/training-sessions/{id}` que não existem no `UpdateTrainingSessionIn` runtime:
- `deviationJustification` (string) — justificativa de desvio de plano
- `status` (enum) — transição de estado via PATCH

**Evidência A — source master (linhas 918–934):**
```yaml
properties:
  ...
  notes: {type: string}
  deviationJustification: {type: string}
  status:
    type: string
    enum: [DRAFT, SCHEDULED, PUBLISHED, IN_PROGRESS, COMPLETED, CANCELLED]
    description: "Transition to canonical state (ADR-017). ARCHIVED is set by system automation only."
```

**Evidência B — runtime (src/training/schemas/sessions.py:84-106):**
```python
class UpdateTrainingSessionIn(Schema):
    session_at: Optional[datetime] = None
    session_type: Optional[str] = None
    ...
    notes: Optional[str] = None
    # ← deviationJustification: AUSENTE
    # ← status: AUSENTE
```

**Análise:**
O runtime implementa transições de estado via endpoints dedicados (`POST /publish`, `POST /start`, etc.) em vez de aceitar `status` no PATCH body. Isso é uma decisão arquitetural que diverge do contrato, mas pode ser intencional. O `deviationJustification` não existe em nenhuma camada do runtime (handler, schema, use case, domain).

**Impacto:**
- Um cliente que envia `status` no PATCH body (seguindo o contrato) terá o campo silenciosamente ignorado — a transição não acontece.
- `deviationJustification` é silenciosamente descartado se enviado.

**Correção mínima:**
Documentar no contrato que `status` transitions are via dedicated endpoints (adicionar note ou remover o campo `status` do PATCH body se os endpoints dedicados são o padrão). Verificar se `deviationJustification` foi descartado intencionalmente.

**Bloqueia merge?:** não (comportamento de ignorar campos extras é previsível, mas representa promessa não cumprida)

**Classificação:** drift provável (decision arquitetural não refletida no source master)

---

### ACHADO-CD-004

```
ACHADO-ID: ACHADO-CD-004
Categoria: Location header ausente em respostas 201
Módulo: training / sessions, wellness
Severidade: alta
Estado: drift provável
```

**Camadas em conflito:**
- contrato (source master — Location header em 201)
- runtime (handlers não setam Location header)

**Descrição:**
O source master declara explicitamente um `Location` header nas respostas 201 de pelo menos dois grupos de endpoints. O runtime retorna apenas o body, sem o header `Location`.

**Evidência A — source master createTrainingSession (linhas 230–237):**
```yaml
"201":
  description: Created
  headers:
    Location:
      description: URI of the created resource
      schema:
        type: string
        format: uri
```

**Evidência B — runtime sessions.py:130:**
```python
return 201, _session_to_out(session)
# ← nenhum header Location setado
```

**Evidência C — source master submitWellnessPre (linhas 1319–1326):**
```yaml
"201":
  headers:
    Location:
      description: URI of the created resource
```

**Evidência D — runtime wellness.py:73:**
```python
return 201, _wellness_pre_to_out(wellness)
# ← nenhum header Location setado
```

**Endpoints afetados (confirmados):** createTrainingSession, submitWellnessPre, submitWellnessPost.
**Endpoints prováveis (não verificados individualmente):** createMesocycle, createMicrocycle, createExecutionRecord, createSessionObjective, createFeedbackThread, recordSessionAttendance, submitIneligibilityDeclaration.

**Impacto:**
Clientes que usam `Location` header para redirecionar ou derivar a URI do recurso criado (REST REST pattern padrão) não recebem o dado. Viola Google AIP-133 (Create methods return Location).

**Correção mínima:**
Adicionar `Location` header nas responses 201 de cada handler. Para Django Ninja, usar `response.headers["Location"] = f"/api/training/training-sessions/{session.id}"`.

**Bloqueia merge?:** não (funcionalidade presente, REST discoverability ausente)

**Classificação:** drift provável (promessa do contrato não implementada — não é falha de comportamento, é ausência de header)

---

### ACHADO-CD-005

```
ACHADO-ID: ACHADO-CD-005
Categoria: Response codes divergentes — createTrainingSession
Módulo: training / sessions
Severidade: média
Estado: drift provável
```

**Camadas em conflito:**
- contrato (source master)
- runtime (handler response dict)

**Path/Method:** POST `/training/training-sessions`
**operationId:** createTrainingSession

**Evidência:**

| Code | Contrato | Handler | Observação |
|---|---|---|---|
| 201 | ✓ | ✓ | ✓ |
| 400 | ✓ (validation) | ✓ | ✓ |
| 401 | ✓ | ✓ | ✓ |
| 403 | ✓ | ✓ | ✓ |
| 404 | ✓ (resource not found) | **AUSENTE** | map_exceptions pode gerar 404 mas não está no response dict |
| 409 | ✓ (conflict) | **AUSENTE** | map_exceptions pode gerar 409 mas não está no response dict |
| 422 | **AUSENTE** | ✓ | runtime declara 422 para validação; contrato usa 400 |
| 500 | ✓ | **AUSENTE** | framework gerencia, mas spec gerado pelo Ninja omitirá |

**Descrição:**
O handler declara 422 (Unprocessable Entity) para erros de validação onde o contrato declara 400. A escolha de 422 vs 400 para erros de validação é uma divergência real — o contrato usa 400 para "validation error", o Django Ninja/Pydantic usa 422 como padrão para erros de schema. O `map_exceptions` também pode retornar 404 e 409 em runtime (quando `microcycle_id`, `team_id`, `season_id` não existem, ou por IntegrityError), mas esses códigos não estão no response dict.

**Correção mínima:**
Adicionar 404 e 409 ao response dict do handler. Alinhar 422 vs 400 no contrato ou no handler.

**Bloqueia merge?:** não (comportamento funcional presente, divergência de documentação/spec)

**Classificação:** drift provável

---

### ACHADO-CD-006

```
ACHADO-ID: ACHADO-CD-006
Categoria: Response codes divergentes — deleteTrainingSession
Módulo: training / sessions
Severidade: média
Estado: drift provável
```

**Camadas em conflito:**
- contrato
- runtime (handler response dict)

**Path/Method:** DELETE `/training/training-sessions/{id}`
**operationId:** deleteTrainingSession

**Evidência:**

| Code | Contrato | Handler |
|---|---|---|
| 204 | ✓ | ✓ |
| 401 | ✓ | ✓ |
| 403 | ✓ | ✓ |
| 404 | ✓ | ✓ |
| 409 | ✓ | **AUSENTE** |
| 422 | **AUSENTE** | ✓ |
| 500 | ✓ | **AUSENTE** |

O handler tem 422 (não documentado no contrato para DELETE) e não tem 409 (documentado no contrato). `map_exceptions` pode gerar ambos em runtime.

**Classificação:** drift provável

**Bloqueia merge?:** não

---

### ACHADO-CD-007

```
ACHADO-ID: ACHADO-CD-007
Categoria: Response codes divergentes — updateTrainingSession
Módulo: training / sessions
Severidade: média
Estado: drift provável
```

**Camadas em conflito:**
- contrato
- runtime (handler response dict)

**Path/Method:** PATCH `/training/training-sessions/{id}`
**operationId:** updateTrainingSession

**Evidência:**

| Code | Contrato | Handler |
|---|---|---|
| 200 | ✓ | ✓ |
| 400 | ✓ | **AUSENTE** |
| 401 | ✓ | ✓ |
| 403 | ✓ | ✓ |
| 404 | ✓ | ✓ |
| 409 | ✓ | **AUSENTE** |
| 422 | **AUSENTE** | ✓ |
| 500 | ✓ | **AUSENTE** |

**Classificação:** drift provável

**Bloqueia merge?:** não

---

### ACHADO-CD-008

```
ACHADO-ID: ACHADO-CD-008
Categoria: 500 ausente em todos os handlers
Módulo: training (todos os endpoints)
Severidade: baixa
Estado: drift provável
```

**Camadas em conflito:**
- contrato (source master — 500 declarado em todas as operações com security)
- runtime (handlers não declaram 500 em response dict)

**Descrição:**
O source master declara `"500"` response para todos os endpoints que têm `security: HTTPBearer`. Os handlers do Django Ninja nunca declaram 500 em seus `response` dicts — o framework gerencia 500s internamente. Isso significa que o OpenAPI spec gerado automaticamente pelo Ninja não incluirá 500, enquanto o spec manual (source master) sim.

Este é um gap entre o spec gerado pelo framework e o spec canônico à mão. O comportamento runtime está correto (500s acontecem quando há exceções não tratadas). A divergência é de documentação.

**Nota:** este drift é conhecido e sistemático. Não é um achado pontual de um endpoint específico.

**Classificação:** drift provável (gap de documentação entre spec manual e spec Ninja-gerado)

**Bloqueia merge?:** não

---

### ACHADO-CD-009

```
ACHADO-ID: ACHADO-CD-009
Categoria: Runtime mais rico que contrato — recordSessionAttendance 201 response
Módulo: training / attendance
Severidade: baixa
Estado: drift provável
```

**Camadas em conflito:**
- contrato (source master — 201 response inline schema)
- runtime (AttendanceRecordOut schema)

**Path/Method:** POST `/training/training-sessions/{id}/attendance`
**operationId:** recordSessionAttendance

**Evidência A — source master 201 response (linhas 1212–1231):**
```yaml
schema:
  type: object
  additionalProperties: false
  required: [athleteId, status, recordedAt]
  properties:
    athleteId: ...
    status: ...
    recordedAt: ...
    source: ...
```
4 propriedades, `additionalProperties: false`.

**Evidência B — runtime (src/training/schemas/attendance.py:14-21):**
```python
class AttendanceRecordOut(Schema):
    athlete_id: uuid.UUID
    status: str
    recorded_at: datetime
    source: str
    correction_by_user_id: Optional[uuid.UUID] = None
    correction_at: Optional[datetime] = None
    justification_reason: Optional[str] = None
```
7 campos — 3 extras: `correction_by_user_id`, `correction_at`, `justification_reason`.

**Impacto:**
Runtime retorna mais campos que o contrato promete. Clientes com `additionalProperties: false` no parser rejeitarão a resposta. Os campos extras (`correctionByUserId`, `correctionAt`, `justificationReason`) são semanticamente relevantes para source=correction, e deveriam estar no contrato.

**Classificação:** drift provável (runtime mais rico que schema soberano — schema soberano precisa ser atualizado para refletir o runtime real)

**Bloqueia merge?:** não

---

## Resumo por operationId

| operationId | Request OK | Response codes OK | Response shape OK | Achados |
|---|---|---|---|---|
| listTrainingSessions | ✓ | parcial (sem 500 no handler) | ✓ | CD-008 |
| createTrainingSession | ✓ | parcial (404,409,500 ausentes; 422 extra) | parcial (sem Location header) | CD-004, CD-005, CD-008 |
| getTrainingSessionById | ✓ | parcial (sem 500) | ✓ | CD-008 |
| updateTrainingSession | parcial (deviationJustification, status ausentes) | parcial (400,409,500 ausentes; 422 extra) | ✓ | CD-003, CD-007, CD-008 |
| deleteTrainingSession | ✓ | parcial (409,500 ausentes; 422 extra) | ✓ | CD-006, CD-008 |
| publishTrainingSession | ✓ | ✓ | ✓ | CD-008 |
| unpublishTrainingSession | ✓ | ✓ | ✓ | CD-008 |
| startTrainingSession | ✓ | ✓ | ✓ | CD-008 |
| completeTrainingSession | ✓ | ✓ | ✓ | CD-008 |
| cancelTrainingSession | ✓ | ✓ | ✓ | CD-008 |
| archiveTrainingSession | ✓ | ✓ | ✓ | CD-008 |
| listSessionBlocks | ✓ | parcial (sem 500) | ✓ (data envelope ok) | CD-008 |
| addSessionBlock | ✓ | ✓ | ✓ | CD-008 |
| getSessionBlock | ✓ | ✓ | ✓ | CD-008 |
| updateSessionBlock | ✓ | ✓ | ✓ | CD-008 |
| deleteSessionBlock | ✓ | ✓ | ✓ | CD-008 |
| reorderSessionBlocks | ✓ | ✓ | ✓ (data envelope ok) | CD-008 |
| listSessionAttendance | ✓ | ✓ | ✓ | CD-008 |
| recordSessionAttendance | ✓ | parcial (409,500 ausentes) | parcial (runtime mais rico) | CD-008, CD-009 |
| submitWellnessPre | **divergente** | parcial (sem 500) | **verificar wellness_pre.yaml** | CD-002, CD-004(parcial), CD-008 |
| getWellnessPre | ✓ (athleteId em path ok) | ✓ | verificar | CD-008 |
| updateWellnessPre | parcial (sleepHours ausente) | ✓ | verificar | CD-002(parcial), CD-008 |
| submitWellnessPost | verificar | ✓ | verificar | CD-008 |
| getWellnessPost | ✓ | ✓ | verificar | CD-008 |
| updateWellnessPost | verificar | ✓ | verificar | CD-008 |
| listMesocycles | ✓ | ✓ | ✓ | CD-008 |
| createMesocycle | ✓ | verificar (Location header) | ✓ | CD-004(provável), CD-008 |
| getMesocycleById | ✓ | ✓ | ✓ | CD-008 |
| updateMesocycle | ✓ | ✓ | ✓ | CD-008 |
| listMicrocycles | ✓ | ✓ | ✓ | CD-008 |
| createMicrocycle | ✓ | verificar (Location header) | ✓ | CD-004(provável), CD-008 |
| getMicrocycleById | ✓ | ✓ | ✓ | CD-008 |
| updateMicrocycle | ✓ | ✓ | ✓ | CD-008 |
| listExecutionRecords | ✓ | ✓ | ✓ | CD-008 |
| createExecutionRecord | ✓ | verificar | verificar | CD-008 |
| getExecutionRecord | ✓ | ✓ | ✓ | CD-008 |
| listSessionObjectives | ✓ | ✓ | ✓ | CD-008 |
| createSessionObjective | ✓ | verificar | verificar | CD-008 |
| listFeedbackThreads | ✓ | ✓ | ✓ | CD-008 |
| createFeedbackThread | ✓ | verificar | verificar | CD-008 |
| closeFeedbackThread | ✓ | ✓ | ✓ | CD-008 |
| listAttentionQueueItems | ✓ | ✓ | ✓ | CD-008 |
| resolveAttentionQueueItem | ✓ | ✓ | ✓ | CD-008 |
| dismissAttentionQueueItem | ✓ | ✓ | ✓ | CD-008 |
| escalateAttentionQueueItem | ✓ | ✓ | ✓ | CD-008 |
| listRecommendations | ✓ | ✓ | ✓ | CD-008 |
| acceptRecommendation | ✓ | ✓ | ✓ | CD-008 |
| dismissRecommendation | ✓ | ✓ | ✓ | CD-008 |
| getIneligibilityStatus | ✓ | ✓ | ✓ | CD-008 |
| submitIneligibilityDeclaration | ✓ | verificar | verificar | CD-008 |
| getLoadChart | ✓ | ✓ | ✓ | CD-008 |
| listChatMessages | ✓ | ✓ | ✓ | CD-008 |
| submitTrainingSuggestion | ✓ | ✓ | ✓ | CD-008 |

---

## Consolidação por causa-raiz

### CR-CD-001 — Formato de erro não é RFC 7807

**Achados:** CD-001 (direto)
**Severidade:** crítica
**Prioridade:** 1
**Escopo:** todos os 53 endpoints
**Ação:** implementar exception handler global que produza `{type, title, status, traceId, detail}` com `Content-Type: application/problem+json`

### CR-CD-002 — Schema de wellness pré diverge fundamentalmente do contrato

**Achados:** CD-002 (direto)
**Severidade:** crítica
**Prioridade:** 2
**Escopo:** submitWellnessPre, getWellnessPre, updateWellnessPre (model compartilhado)
**Ação:** definir qual é o modelo canônico (sleepHours do contrato ou readiness/mood/fatigue do runtime) e alinhar

### CR-CD-003 — Location headers não implementados

**Achados:** CD-004 (direto)
**Severidade:** alta
**Prioridade:** 3
**Escopo:** todos os endpoints que retornam 201
**Ação:** adicionar `response.headers["Location"]` nos handlers POST que criam recursos

### CR-CD-004 — Response codes divergentes sistematicamente entre contrato e handler declarations

**Achados:** CD-005, CD-006, CD-007 (diretos), CD-008 (sistemático)
**Severidade:** média
**Prioridade:** 4
**Escopo:** sessions.py principalmente, mas padrão se repete
**Ação:** alinhar response dicts dos handlers com os códigos do contrato; resolver 422 vs 400; adicionar 500

### CR-CD-005 — deviationJustification e status no PATCH não implementados

**Achados:** CD-003 (direto)
**Severidade:** alta
**Prioridade:** 5
**Escopo:** updateTrainingSession
**Ação:** implementar `deviationJustification` no domain + schema, ou remover do contrato com justificativa

### CR-CD-006 — Runtime mais rico que contrato no response de recordSessionAttendance

**Achados:** CD-009 (direto)
**Severidade:** baixa
**Prioridade:** 6
**Ação:** atualizar source master para incluir correctionByUserId, correctionAt, justificationReason no inline 201 schema

---

## Itens verificados e OK

- Paridade source master ↔ generated ↔ contracts: **sem drift de compilação**
- Cobertura de handlers: **53/53 operationIds com handler** — zero órfãos
- Path parameter camelCase (`athleteId`) no wellness: **consistente entre contrato e runtime**
- Envelope `{data: [...]}` em listSessionBlocks e reorderSessionBlocks: **correto**
- Envelope `{items: [...]}` em listTrainingSessions e listSessionAttendance: **correto**
- Query params camelCase (organizationId, teamId, etc.): **correto** (Django Ninja converte snake→camel)
- Transições de estado via endpoints dedicados: **OK** (implementação correta, contrato pode estar desatualizado com o campo `status` no PATCH)
- `observedAt` em recordSessionAttendance: **presente em contrato e runtime** ✓
