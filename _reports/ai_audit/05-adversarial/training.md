# Adversarial Scan — Módulo Training

> Auditoria técnica de repositório contract-driven.
> Data: 2026-04-23
> Escopo: módulo `training` — adversarial scan de contrato, schema, runtime e domínio
> Regras aplicadas: AGAUDIT v1.1 — Prompt 5

---

## Resumo executivo

| Métrica | Valor |
|---|---|
| Arquivos analisados | 12 (api/*, schemas/*, domain/rules.py, contract/paths/training.yaml) |
| Achados totais | 11 |
| Erros confirmados | 8 |
| Drifts prováveis | 3 |
| Severidade CRÍTICA | 2 |
| Severidade ALTA | 5 |
| Severidade MÉDIA | 3 |
| Severidade BAIXA | 1 |

**Veredicto:** O scan adversarial encontrou dois achados críticos que testes regulares não capturam: (1) `sleepHours` desaparecido em 5 camadas simultaneamente sem nenhum erro em runtime e (2) o FSM permite caminhos de estado proibidos que podem ser invocados diretamente por qualquer ator autenticado. Os achados de response code e schema divergente são sistêmicos — afetam múltiplos endpoints pelo mesmo padrão.

---

## Achados

---

### ACHADO-ADV-001

```
ACHADO-ID: ACHADO-ADV-001
Categoria: Schema soberano mais rico que runtime — sleepHours ausente em 5 camadas
Módulo: training / wellness
Severidade: crítica
Estado: erro confirmado
```

**Camadas em conflito:**
- contrato (`contracts/openapi/paths/training.yaml`)
- runtime (`src/training/schemas/wellness.py`)
- runtime (`src/training/api/wellness.py`)
- runtime (`src/training/api/mappers.py`)
- domínio (entidade WellnessPre)

**Descrição:**

O campo `sleepHours` é declarado no contrato como campo **required** no request body de `submitWellnessPre` e presente em `updateWellnessPre`. Ele desapareceu simultaneamente de todas as camadas do runtime sem gerar nenhum erro — teste, gate ou compilação.

**Evidência A — contrato (`contracts/openapi/paths/training.yaml:1292-1306`):**
```yaml
required:
  - athleteId
  - sleepHours          # ← campo obrigatório segundo o contrato
  ...
properties:
  sleepHours:
    type: integer
    minimum: 0
    maximum: 24
```

**Evidência B — runtime (`src/training/schemas/wellness.py:28-36`):**
```python
class SubmitWellnessPreIn(Schema):
    athlete_id: uuid.UUID
    readiness: Optional[int] = None
    sleep_quality: Optional[int] = None
    mood: Optional[int] = None
    fatigue: Optional[int] = None
    muscle_soreness: Optional[int] = None
    notes: Optional[str] = None
    # sleep_hours: ausente — o campo não existe aqui
```

**Evidência C — handler (`src/training/api/wellness.py:59-72`):**
`submit_wellness_pre` não passa `sleep_hours` para `SubmitWellnessPreInput`.

**Evidência D — output schema (`WellnessPreOut`):**
`WellnessPreOut` também não tem `sleep_hours` — portanto, mesmo que o dado existisse na entidade, não seria serializado na resposta.

**Evidência E — mapper (`src/training/api/mappers.py:101-114`):**
`_wellness_pre_to_out` não inclui `sleep_hours` na construção do `WellnessPreOut`.

**Impacto:**

Clientes que enviam `sleepHours` (como requerido pelo contrato) recebem 201 Created sem erro — mas o campo é silenciosamente ignorado e nunca persiste. Clientes que leem `sleepHours` na resposta nunca o recebem. O contrato promete o campo; o runtime descarta sem aviso.

**Correção mínima:**
1. Adicionar `sleep_hours: Optional[int] = None` ao `SubmitWellnessPreIn` e `UpdateWellnessPreIn`
2. Adicionar `sleep_hours: Optional[int] = None` ao `WellnessPreOut`
3. Propagar o campo no handler, use case input, entidade de domínio e ORM
4. Criar migration para adicionar coluna `sleep_hours` ao modelo ORM

**Correção ideal:**
Adicionar teste de contrato que verifica campo-a-campo entre o schema OpenAPI e o schema Python de cada operação.

**Bloqueia merge?:** sim — campo required no contrato não existe no runtime

---

### ACHADO-ADV-002

```
ACHADO-ID: ACHADO-ADV-002
Categoria: FSM divergente — transições proibidas invocáveis diretamente via API
Módulo: training / domínio / api
Severidade: crítica
Estado: erro confirmado
```

**Camadas em conflito:**
- documentação canônica (`STATE_MODEL_TRAINING.md`)
- domínio (`src/training/domain/rules.py:136-161`)
- runtime (`src/training/api/sessions.py:215-270`)

**Descrição:**

O scan adversarial confirma o achado de domínio (ACHADO-DP-001) sob a perspectiva de exploração via API: qualquer ator com role `coach`, `coordinator` ou `admin` pode invocar diretamente os endpoints de transição para mover uma sessão em caminhos canonicamente proibidos.

Os endpoints de transição são:
- `POST /training-sessions/{id}/publish` → alvo: `PUBLISHED`
- `POST /training-sessions/{id}/start` → alvo: `IN_PROGRESS`

O path adversarial viável:
1. Criar sessão em DRAFT
2. Chamar `POST .../publish` → move DRAFT→PUBLISHED (canonicamente proibido, runtime permite)
3. Chamar `POST .../start` → tenta IN_PROGRESS mas PUBLISHED→IN_PROGRESS é válido, então OK

Ou:
1. Criar sessão em DRAFT
2. Mover para SCHEDULED (`POST .../unpublish` não, `POST .../publish` não é unpublish)

Mais precisamente: DRAFT→PUBLISHED está explicitamente em `VALID_TRANSITIONS[DRAFT]`. Um coach pode:
- Criar sessão (→ DRAFT)
- Publicar imediatamente (POST .../publish → DRAFT→PUBLISHED) — sem passar por SCHEDULED, sem notificações de planejamento, sem pre-condições de publicação

E SCHEDULED→IN_PROGRESS: um coach pode:
- Criar sessão (DRAFT) → mover para SCHEDULED → iniciar diretamente (POST .../start → SCHEDULED→IN_PROGRESS) sem passar por PUBLISHED, sem snapshot de conteúdo imutabilizado.

**Evidência A — `VALID_TRANSITIONS` (`src/training/domain/rules.py:136-144`):**
```python
TrainingSessionStatus.DRAFT: {
    TrainingSessionStatus.SCHEDULED,
    TrainingSessionStatus.PUBLISHED,   # ← proibido pelo canon
    TrainingSessionStatus.CANCELLED,
},
TrainingSessionStatus.SCHEDULED: {
    TrainingSessionStatus.PUBLISHED,
    TrainingSessionStatus.IN_PROGRESS, # ← proibido pelo canon
    TrainingSessionStatus.CANCELLED,
},
```

**Evidência B — handler (`src/training/api/sessions.py:237-250`):**
```python
@router.post("/training-sessions/{id}/publish", response=_TRANSITION_RESPONSE)
@map_exceptions
def publish_training_session(request, id: uuid.UUID):
    return 200, _do_transition(request, id, TrainingSessionStatus.PUBLISHED)

@router.post("/training-sessions/{id}/start", response=_TRANSITION_RESPONSE)
@map_exceptions
def start_training_session(request, id: uuid.UUID):
    return 200, _do_transition(request, id, TrainingSessionStatus.IN_PROGRESS)
```

**Impacto:**

Bypass completo do grafo de lifecycle. Sessões podem ser publicadas sem passar por SCHEDULED (notificações de planejamento ignoradas) e sem satisfazer as pré-condições de INV-TRAIN-086. Sessões podem ser iniciadas sem ter sido publicadas (atletas nunca viram o conteúdo planejado).

**Correção mínima:**

Remover `PUBLISHED` de `VALID_TRANSITIONS[DRAFT]` e `IN_PROGRESS` de `VALID_TRANSITIONS[SCHEDULED]` em `src/training/domain/rules.py`.

**Bloqueia merge?:** sim — exploração direta via API

---

### ACHADO-ADV-003

```
ACHADO-ID: ACHADO-ADV-003
Categoria: Promessa sem enforcement — individualizationMode inatingível pela API
Módulo: training / api / domínio
Severidade: alta
Estado: erro confirmado
```

**Camadas em conflito:**
- documentação canônica (`DOMAIN_RULES_TRAINING.md` — DR-TRAIN-030)
- contrato (`contracts/openapi/paths/training.yaml` — createTrainingSession sem o campo)
- runtime (`src/training/schemas/sessions.py` — ausente de CreateTrainingSessionIn e UpdateTrainingSessionIn)

**Descrição:**

DR-TRAIN-030 define: "individualizationMode é obrigatório para criação de sessão". O scan adversarial detecta que o campo é **impossível de definir via API** — não existe em nenhuma operação de escrita:

| Schema | `individualizationMode`? |
|---|---|
| `CreateTrainingSessionIn` (runtime) | ausente |
| `UpdateTrainingSessionIn` (runtime) | ausente |
| `createTrainingSession` request body (contrato) | ausente |

O campo existe em:
- `TrainingSessionOut` (saída, leitura) — sempre `null`
- `_session_to_out` mapper — serializa `s.individualization_mode` → sempre `null`

**Evidência A — `CreateTrainingSessionIn` (`src/training/schemas/sessions.py:56-82`):**
O schema de input não declara `individualization_mode`. O campo não é enviado pelo cliente e não é recebido pelo handler.

**Evidência B — contrato (`contracts/openapi/paths/training.yaml:120-275`):**
A seção `properties` de `createTrainingSession` request body não inclui `individualizationMode`. O campo está ausente do contrato de criação.

**Evidência C — contrato (`contracts/openapi/paths/training.yaml:3224`):**
```yaml
Requires individualizationMode, sessionAt, and at least one session_objective
```
O contrato de `publishTrainingSession` exige `individualizationMode` como pré-condição — mas o campo nunca foi settable.

**Impacto:**

Toda sessão criada tem `individualization_mode = null`. A pré-condição de publicação (INV-TRAIN-086) que exige o campo definido é inalcançável — qualquer tentativa de publish sempre falharia (se o guard fosse implementado, o que não é). O sistema está em estado de deadlock silencioso: regra exige campo, API não expõe campo, guard não existe.

**Correção mínima:**
1. Adicionar `individualization_mode: str` (com enum de valores válidos) ao `CreateTrainingSessionIn`
2. Adicionar ao contrato `createTrainingSession` request body
3. Propagar no handler e use case

**Bloqueia merge?:** sim — deadlock de regra de negócio

---

### ACHADO-ADV-004

```
ACHADO-ID: ACHADO-ADV-004
Categoria: Envelope de erro divergente — ErrorOut declarado, problem+json entregue
Módulo: training / api / config
Severidade: alta
Estado: erro confirmado
```

**Camadas em conflito:**
- contrato (`contracts/openapi/paths/training.yaml` — declara `application/problem+json` com schema `problem.yaml`)
- runtime (handlers declaram `ErrorOut = {detail: str}` nos `response={}`)
- runtime (`config/urls.py` — global handler retorna `application/problem+json`)

**Descrição:**

Todos os handlers do módulo `training` declaram erros como `ErrorOut`:
```python
response={201: TrainingSessionOut, 400: ErrorOut, 401: ErrorOut, ...}
```

Onde `ErrorOut = Schema(detail: str)`.

O contrato canônico declara erros como `application/problem+json` com schema `problem.yaml` que exige `{type, title, status, traceId}` (+ opcional `detail`).

O global exception handler em `config/urls.py:62-84` retorna **de fato** `application/problem+json`:
```python
def _problem_response(status: int, detail: str) -> HttpResponse:
    body = json.dumps({"type": "about:blank", "title": title, "status": status, "detail": detail})
    return HttpResponse(body, content_type="application/problem+json", status=status)
```

**Resultado:** O schema OpenAPI gerado pelo Django Ninja documenta `{detail: str}` mas o runtime retorna `{type, title, status, detail}` com Content-Type diferente (`application/problem+json` vs `application/json`). Clientes que confiem no spec gerado terão deserialização incorreta.

Nota adversarial adicional: o `problem_response` não inclui `traceId` — que é **required** em `problem.yaml` (`contracts/openapi/components/schemas/shared/problem.yaml:18-19: required: - type - title - status - traceId`). Portanto, o handler global também não produz um `problem.yaml`-compliant response.

**Evidência A — `problem.yaml` (required fields):**
```yaml
required:
- type
- title
- status
- traceId     # ← obrigatório pelo schema canônico
```

**Evidência B — `_problem_response` (`config/urls.py:51-59`):**
```python
body = json.dumps({
    "type": "about:blank",
    "title": title,
    "status": status,
    "detail": detail,
    # traceId: AUSENTE
})
```

**Impacto:** Dupla divergência: (1) spec documenta `ErrorOut` mas runtime entrega `problem+json`; (2) o `problem+json` entregue viola `problem.yaml` por ausência de `traceId`.

**Correção mínima:**
1. Criar `ProblemOut` schema alinhado a `problem.yaml`
2. Substituir `ErrorOut` em todos os `response={}` por `ProblemOut`
3. Adicionar `traceId` (X-Flow-ID) ao `_problem_response` em `config/urls.py`

**Bloqueia merge?:** sim — clientes não conseguem consumir erros conforme contrato

---

### ACHADO-ADV-005

```
ACHADO-ID: ACHADO-ADV-005
Categoria: Path param camelCase/snake_case drift — contrato vs handler
Módulo: training / api / contrato
Severidade: alta
Estado: erro confirmado
```

**Camadas em conflito:**
- contrato (`contracts/openapi/paths/training.yaml`)
- runtime (`src/training/api/blocks.py`, `src/training/api/execution.py`)

**Descrição:**

O contrato canônico usa **camelCase** em path parameters de sub-recursos:

| Path no contrato | Param name |
|---|---|
| `/training-sessions/{id}/blocks/{blockId}` | `{blockId}` |
| `/training-sessions/{id}/execution-records/{recordId}` | `{recordId}` |

Os handlers Python usam **snake_case**:

| Handler | Param name |
|---|---|
| `blocks.py:get_session_block` | `{block_id}` |
| `execution.py:get_execution_record` | `{record_id}` |

O Django Ninja gera a documentação OpenAPI a partir da assinatura Python — portanto o spec gerado terá `{block_id}` e `{record_id}`. O canonical contract tem `{blockId}` e `{recordId}`.

**Evidência A — contrato (`contracts/openapi/paths/training.yaml:514`):**
```
/training/training-sessions/{id}/blocks/{blockId}:
```

**Evidência B — handler (`src/training/api/blocks.py:90-101`):**
```python
@router.get("/training-sessions/{id}/blocks/{block_id}", ...)
def get_session_block(request, id: uuid.UUID, block_id: uuid.UUID):
```

Nota: `{athleteId}` é consistente — contrato e handler usam `athleteId`.

**Impacto:**

Divergência na documentação OpenAPI gerada vs canonical contract. Ferramentas que consomem o contrato canônico (ex: geração de SDK, Schemathesis) usarão `{blockId}`; o spec gerado do Django Ninja usará `{block_id}`. Em HTTP, o roteamento é posicional então funciona em runtime, mas a documentação publicada estará incorreta.

**Correção mínima:**

Opção A: renomear os parâmetros Python para `blockId` e `recordId` (consistente com `athleteId`).
Opção B: atualizar o contrato canônico para usar `{block_id}` e `{record_id}`.

Escolher uma e aplicar consistentemente.

**Bloqueia merge?:** não (funcional), mas gera spec divergente publicado

---

### ACHADO-ADV-006

```
ACHADO-ID: ACHADO-ADV-006
Categoria: Response codes divergentes — createTrainingSession
Módulo: training / api
Severidade: alta
Estado: erro confirmado
```

**Camadas em conflito:**
- contrato (`contracts/openapi/paths/training.yaml:215-275`)
- runtime (`src/training/api/sessions.py:86-96`)

**Descrição:**

O contrato declara 7 response codes para `createTrainingSession`:
```
201, 400, 401, 403, 404, 409, 500
```

O handler runtime declara 5:
```python
response={
    201: TrainingSessionOut,
    400: ErrorOut,
    401: ErrorOut,
    403: ErrorOut,
    422: ErrorOut,   # ← não está no contrato
    # 404 ausente — referência a teamId/seasonId/microcycleId não encontrada
    # 409 ausente — conflito
    # 500 ausente
}
```

Divergências:
- **404 ausente no handler**: se `team_id` ou `season_id` não existir, `NotFoundError` → 404 via `map_exceptions`, mas não está declarado no `response={}`. Django Ninja não incluirá 404 no spec gerado para esta operação.
- **409 ausente no handler**: `ConflictError` vai para 409 via fallback, mas não declarado.
- **500 ausente no handler**: o spec gerado não documenta 500.
- **422 no handler mas ausente no contrato**: o contrato usa 400 para validação; o handler declara 422 para `DomainValidationError`. Divergência semântica (400 vs 422 para erros de validação de negócio).

**Evidência A — contrato (`contracts/openapi/paths/training.yaml:232-274`):**
```yaml
responses:
  "201": Created
  "400": Validation error
  "401": Unauthenticated
  "403": Forbidden
  "404": Referenced resource not found
  "409": Conflict
  "500": Internal server error
```

**Evidência B — handler (`src/training/api/sessions.py:87-96`):**
```python
response={201: ..., 400: ErrorOut, 401: ErrorOut, 403: ErrorOut, 422: ErrorOut}
```

**Impacto:**

O spec gerado pelo Django Ninja para `createTrainingSession` documenta responses diferentes dos declarados no contrato canônico. Clientes que leem o spec gerado não saberão tratar 404 e 409. A divergência 400 vs 422 pode causar bugs em clientes que fazem switch por status code.

**Correção mínima:**

Atualizar `response={}` do handler para incluir 404 e 409. Alinhar 422→400 ou atualizar o contrato para aceitar 422.

**Bloqueia merge?:** não imediatamente (runtime funciona), mas quebra contratos de clientes

---

### ACHADO-ADV-007

```
ACHADO-ID: ACHADO-ADV-007
Categoria: Promessa sem enforcement — resolve_access Fase 3 incompleto (BOLA latente)
Módulo: training / api / identity_access
Severidade: alta
Estado: drift provável
```

**Camadas em conflito:**
- runtime (`src/training/api/deps.py:38-59`)
- domínio (`src/training/domain/rules.py:234-252` — `assert_can_read_session`)
- documentação canônica (ADR-008 — RBAC, OWASP API1 BOLA)

**Descrição:**

`resolve_access()` em `src/training/api/deps.py` é responsável por construir o `AccessContext` do ator autenticado. A implementação atual tem um `TODO Fase 3` explícito:

```python
# TODO Fase 3: preencher team_ids e athlete_ids via identity_access
return AccessContext(
    actor_id=actor_id,
    role=role,
    organization_id=organization_id,
    team_ids=(),       # ← sempre vazio
    athlete_ids=(),    # ← sempre vazio
)
```

O `AccessContext` é usado por `list_training_sessions` mas os campos `team_ids` e `athlete_ids` nunca são preenchidos. Se algum use case de listing usar `athlete_ids` para filtrar quais sessões um atleta pode ver, o filtro seria aplicado sobre uma lista vazia — resultando em acesso a zero sessões (falso negativo) **ou** o filtro pode ser implementado como "se vazio, não filtrar" — resultando em acesso não restrito (BOLA).

**Evidência A — `deps.py:52-58`:**
```python
return AccessContext(
    actor_id=actor_id,
    role=role,
    organization_id=organization_id,
    team_ids=(),    # EMPTY — never populated
    athlete_ids=(), # EMPTY — never populated
)
```

**Evidência B — `sessions.py:65-70` (list handler):**
```python
access = resolve_access(request)
...
ListTrainingSessionsInput(
    actor_role=access.role,
    actor_id=access.actor_id,
    organization_id=organization_id,
    # team_ids e athlete_ids NÃO são passados para o use case
)
```

**Nota de contenção:** A BOLA check por acesso a sessão individual (`assert_can_read_session`) usa `actor_id not in session_athlete_ids` — isso vem dos dados da sessão, não do AccessContext, e não é afetado por este bug. O risco é para o listing onde filtros baseados em `team_ids` do ator nunca são aplicados.

**Impacto:**

Se o use case de listing não filtrar por `actor_id` para o role `ATHLETE`, qualquer atleta poderia listar sessões de outros atletas via `GET /training-sessions`. A profundidade do impacto requer leitura do `ListTrainingSessionsUseCase` (não lido nesta análise).

**Correção mínima:**

Implementar a integração com `identity_access` para preencher `team_ids` e `athlete_ids` no `AccessContext`. Enquanto a Fase 3 não está completa, documentar explicitamente que o listing de sessões não aplica filtro por time/atleta e verificar se o use case tem filtro alternativo.

**Bloqueia merge?:** não comprovado sem leitura do use case, mas representa risco de BOLA latente

---

### ACHADO-ADV-008

```
ACHADO-ID: ACHADO-ADV-008
Categoria: Acoplamento escondido — production API importa generated/ em startup
Módulo: training / api / generated
Severidade: média
Estado: erro confirmado
```

**Camadas em conflito:**
- runtime (`src/training/api/__init__.py:14-15`)
- canon (princípio: `generated/` nunca é fonte de verdade)

**Descrição:**

O `api/__init__.py` importa diretamente de `generated/` em startup do módulo:

```python
# CODEGEN CUTOVER — side-effect imports
from ..generated.application import use_cases as _gen_use_cases   # noqa: F401
from ..generated.infrastructure import repository as _gen_repository  # noqa: F401
```

O comentário explica o motivo: `test_training_codegen_parity.py` verifica que `generated/` é importável junto com `api/`. O problema adversarial é que **se `generated/` tiver um erro de sintaxe, import error ou drift incompatível, o módulo inteiro `training.api` falha ao importar** — causando 500 em todos os endpoints de training em produção.

O `generated/` é um artefato derivado que não deve influenciar a disponibilidade do serviço em produção. A dependência de import cria um coupling oculto que viola o princípio de que `generated/` é apenas output de codegen, nunca runtime crítico.

**Evidência A — `src/training/api/__init__.py:14-15`:**
```python
from ..generated.application import use_cases as _gen_use_cases  # noqa: F401
from ..generated.infrastructure import repository as _gen_repository  # noqa: F401
```

**Evidência B — comentário explícito:**
"NÃO remover: test_training_codegen_parity.py verifica que generated/ é importável junto com api/"

**Impacto:**

Falha no `generated/` = falha de import em `training.api` = 500 em todos os endpoints de training em produção. O gate de paridade de codegen está correto em sua intenção, mas a implementação via import no módulo de produção é o mecanismo errado.

**Correção mínima:**

Mover a verificação de importabilidade do `generated/` para o próprio teste (`test_training_codegen_parity.py`), que deve importar `generated/` diretamente sem passar pelo módulo de produção. Remover os imports de `api/__init__.py`.

**Correção ideal:**

O gate de paridade deve verificar importabilidade de `generated/` em isolamento, não através do caminho de produção.

**Bloqueia merge?:** não em condições normais, mas cria ponto único de falha silencioso

---

### ACHADO-ADV-009

```
ACHADO-ID: ACHADO-ADV-009
Categoria: Response code divergente — 401 ausente em endpoints de leitura autenticados
Módulo: training / api / execution / objectives
Severidade: média
Estado: erro confirmado
```

**Camadas em conflito:**
- contrato (`contracts/openapi/paths/training.yaml` — declara 401 em endpoints autenticados)
- runtime (`src/training/api/execution.py:44-53, 105-115`)

**Descrição:**

Os handlers `list_execution_records` e `list_session_objectives` não declaram 401 em seus `response={}`:

```python
# list_execution_records
response={200: ExecutionRecordListOut, 403: ErrorOut, 404: ErrorOut}
# sem 401 ← se _get_actor_role falhar, HttpError(401) é lançado via global handler,
# mas não está documentado no spec gerado

# list_session_objectives
response={200: SessionObjectiveListOut, 403: ErrorOut, 404: ErrorOut}
# idem
```

O 401 é lançado via `_get_actor_id` → `HttpError(401, "Unauthenticated")` quando o request não tem JWT válido. O global handler captura e retorna `problem+json` com status 401. Mas o Django Ninja não incluirá 401 no spec gerado para esses endpoints.

**Evidência A:** handlers em `execution.py:44,105` não incluem `401: ErrorOut`.

**Evidência B:** `_get_actor_id` em `deps.py:31-35` pode lançar `HttpError(401)`.

**Impacto:**

Spec gerado para esses endpoints não documenta 401. Clientes que consultam o spec para entender erros possíveis podem não implementar tratamento de 401 nesses paths específicos.

**Correção mínima:**

Adicionar `401: ErrorOut` aos `response={}` de `list_execution_records` e `list_session_objectives`.

**Bloqueia merge?:** não

---

### ACHADO-ADV-010

```
ACHADO-ID: ACHADO-ADV-010
Categoria: Response code divergente — 409 ausente em record_session_attendance
Módulo: training / api / attendance
Severidade: média
Estado: erro confirmado
```

**Camadas em conflito:**
- contrato (`contracts/openapi/paths/training.yaml:1255` — declara 409)
- runtime (`src/training/api/attendance.py:48-50`)

**Descrição:**

O contrato declara 409 para `recordSessionAttendance` (presença duplicada para o mesmo atleta). O handler não declara 409:

```python
@router.post(
    "/training-sessions/{id}/attendance",
    response={201: AttendanceRecordOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut},
    # sem 409 ← se houver duplicata, ConflictError → 409 via fallback, mas não declarado
)
```

**Evidência A — contrato (`contracts/openapi/paths/training.yaml:1255`):**
```yaml
"409":
  description: Attendance already recorded for this athlete in this session
```

**Evidência B — handler (`src/training/api/attendance.py:48-51`):**
```python
response={201: AttendanceRecordOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut}
# 409 ausente
```

**Impacto:**

Se um atleta tentar registrar presença duplicada, `ConflictError` é lançada, capturada pelo fallback de `map_exceptions`, e retorna 409 — mas o spec não documenta isso.

**Correção mínima:**

Adicionar `409: ErrorOut` ao `response={}` de `record_session_attendance`.

**Bloqueia merge?:** não

---

### ACHADO-ADV-011

```
ACHADO-ID: ACHADO-ADV-011
Categoria: Regra de domínio sem suporte no contrato — DR-TRAIN-030 incoerente entre canon e contrato
Módulo: training / contrato / domínio
Severidade: baixa
Estado: drift provável
```

**Camadas em conflito:**
- documentação canônica (`DOMAIN_RULES_TRAINING.md` — DR-TRAIN-030)
- contrato (`contracts/openapi/paths/training.yaml` — createTrainingSession sem o campo)

**Descrição:**

DR-TRAIN-030 declara: "individualizationMode é obrigatório para criação de sessão". O contrato de `createTrainingSession` não inclui `individualizationMode` no request body. Portanto, o canon de domínio e o canon de contrato estão em conflito entre si — sem intervenção do runtime.

Isso é diferente do ACHADO-ADV-003 (que trata da ausência no runtime): aqui o problema é que a regra de domínio não foi traduzida para o contrato OpenAPI, e portanto o contrato não pode enforcer a regra mesmo que o runtime seja corrigido.

**Impacto:**

Baixo em isolamento, mas cria ambiguidade: qual canon prevalece? O domínio diz "obrigatório"; o contrato diz "não existe". A correção do ACHADO-ADV-003 no runtime ainda não alinharia o contrato com o domínio.

**Correção mínima:**

Adicionar `individualizationMode` (com enum de valores válidos) ao contrato `createTrainingSession` request body — e marcá-lo como obrigatório conforme DR-TRAIN-030.

**Bloqueia merge?:** não

---

## Agrupamento por categoria adversarial

### Categoria 1 — Schema soberano vs runtime (campo desaparecido)

| Achado | Campo | Camadas afetadas |
|---|---|---|
| ACHADO-ADV-001 | `sleepHours` | contrato, schema input, handler, use case, schema output, mapper — 5 camadas |
| ACHADO-ADV-003 | `individualizationMode` | domínio, contrato, schema input, handler |

### Categoria 2 — FSM e transições proibidas via API

| Achado | Transição | Vetor |
|---|---|---|
| ACHADO-ADV-002 | DRAFT→PUBLISHED, SCHEDULED→IN_PROGRESS | POST /publish e /start direto sem pré-condições |

### Categoria 3 — Envelope de erro sistêmico

| Achado | Divergência | Impacto |
|---|---|---|
| ACHADO-ADV-004 | `ErrorOut` declarado vs `problem+json` entregue + `traceId` ausente | todos os endpoints de training |

### Categoria 4 — Response codes divergentes (sistêmico)

| Achado | Endpoint | Código ausente |
|---|---|---|
| ACHADO-ADV-005 | blocks/{blockId}, execution-records/{recordId} | path param naming |
| ACHADO-ADV-006 | createTrainingSession | 404, 409, 500 no handler |
| ACHADO-ADV-009 | listExecutionRecords, listSessionObjectives | 401 |
| ACHADO-ADV-010 | recordSessionAttendance | 409 |

### Categoria 5 — Promessas sem enforcement / acoplamento oculto

| Achado | Promessa | Estado |
|---|---|---|
| ACHADO-ADV-007 | AccessContext Fase 3 — team_ids/athlete_ids | TODO não implementado |
| ACHADO-ADV-008 | generated/ como artefato derivado | import em produção |

---

## Prioridade de correção

| Prioridade | Achado | Motivo |
|---|---|---|
| 1 | ACHADO-ADV-002 | Exploração direta via API sem requisito especial |
| 2 | ACHADO-ADV-001 | Campo required no contrato ignorado silenciosamente |
| 3 | ACHADO-ADV-004 | Todos os erros violam o schema de erro canônico |
| 4 | ACHADO-ADV-003 | Campo de negócio inatingível cria deadlock na publicação |
| 5 | ACHADO-ADV-006 | Response codes incompletos no endpoint de criação |
| 6 | ACHADO-ADV-007 | Risco de BOLA latente em listing (requires use case audit) |
| 7 | ACHADO-ADV-005 | Path param naming divergente gera spec incorreto |
| 8 | ACHADO-ADV-008 | Ponto único de falha via generated/ em produção |
| 9 | ACHADO-ADV-009 | 401 ausente em 2 endpoints |
| 10 | ACHADO-ADV-010 | 409 ausente em attendance |
| 11 | ACHADO-ADV-011 | Canon de domínio vs canon de contrato em conflito |
