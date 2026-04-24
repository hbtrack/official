# Root Cause Consolidation — AGAUDIT v1.1

> Auditoria técnica de repositório contract-driven.
> Data: 2026-04-23
> Escopo: todos os achados de 01-contract, 02-domain-persistence, 03-architecture-reality, 04-runtime-classification, 05-adversarial, 05-adversarial/refutation
> Regras: AGAUDIT v1.1 — Prompt 7

---

## Mapa de achados → causas-raiz

| Achado original | Causa-raiz | Tipo |
|---|---|---|
| DP-001, ADV-002 | RC-001 (FSM incorreto) | bug real |
| CD-002, ADV-001 | RC-002 (wellness schema divergente) | bug real |
| CD-001, ADV-004 | RC-003 (formato de erro não RFC 7807) | bug real |
| DP-003, DP-005, ADV-011 | RC-004 (invariantes não enforced) | bug real |
| DP-002 | RC-005 (campos ORM ausentes) | bug real |
| ACHADO-007 | RC-006 (migration pendente) | bug real |
| CD-005..008, ADV-006, ADV-009, ADV-010 | RC-007 (response codes sistematicamente divergentes) | drift |
| ADV-005 | RC-008 (path param case divergente) | drift |
| DP-004, ADV-003 | RC-009 (individualizationMode ausente dos inputs de API) | drift |
| CD-004 | RC-010 (Location header ausente em 201) | drift |
| CD-003 | RC-011 (deviationJustification / status ausentes do PATCH) | drift |
| ACHADO-001, ACHADO-003, ACHADO-005 | RC-012 (hash drift — session_start.schema.json) | drift |
| ACHADO-002, ACHADO-003 | RC-013 (handoff/session_start dessincronizados) | drift |
| ACHADO-004 | RC-014 (GOVERNANCE_REGRESSION_GATE sem registro) | bug real |
| ADV-007 | RC-015 (resolve_access TODO Fase 3) | não comprovado (por design) |
| AR-001..010 | RC-016 (canon arquitetural defasado) | drift |
| CD-009 | RC-017 (runtime mais rico que contrato em attendance) | drift |
| ACHADO-008 | RC-018 (import shims em código de produção) | drift |
| ACHADO-006 | RC-019 (env var ausente no escopo de performance test) | problema de ambiente |
| ADV-008 | RC-020 (api/__init__ importa generated/ incondicionalmente) | drift |

---

## Falhas derivadas — não atacar diretamente

| Achado derivado | Causa-raiz que o resolve |
|---|---|
| ACHADO-003 (READINESS_SUMMARY_GATE) | RC-012 + RC-013 |
| ACHADO-005 (test_contract_gates_pass) | RC-012 + RC-013 + RC-014 |
| ADV-006 (createTrainingSession response codes) | RC-007 |
| ADV-009 (401 ausente em list endpoints) | RC-007 |
| ADV-010 (409 ausente em attendance) | RC-007 |

---

## Causas-raiz consolidadas

---

### RC-001 — FSM VALID_TRANSITIONS permite transições proibidas pelo STATE_MODEL

---
> ACHADO-ID: RC-001
> Categoria: Bug de domínio — FSM incorreto
> Módulo: training
> Severidade: crítica
> Estado: erro confirmado
---
> Camadas em conflito:
- documentação canônica (STATE_MODEL_TRAINING.md)
- domínio (src/training/domain/rules.py)
- runtime (src/training/api/sessions.py — publishTrainingSession, startTrainingSession)
- teste (src/training/tests/unit/test_state_machine.py)
---

**Descrição:**
`VALID_TRANSITIONS` em `domain/rules.py` permite explicitamente `DRAFT → PUBLISHED` e `SCHEDULED → IN_PROGRESS`. STATE_MODEL_TRAINING.md (canon) proíbe ambas com justificativa explícita:
- Linha 96: "DRAFT → PUBLISHED: deve passar por SCHEDULED antes de PUBLISHED"
- Linha 100: "SCHEDULED → IN_PROGRESS: deve passar por PUBLISHED antes de iniciar execução"

Agravante: `test_state_machine.py:23` — `test_draft_to_published_valid` valida ativamente a transição proibida como correta. O erro está duplicado na implementação e na suíte de testes.

**Sintomas derivados:**
- DP-001 (FSM no domínio)
- ADV-002 (FSM invocável via API — `POST /publish` e `POST /start` sem restrição)

**Evidência A:**
```python
VALID_TRANSITIONS = {
    TrainingSessionStatus.DRAFT: {SCHEDULED, PUBLISHED, CANCELLED},  # PUBLISHED: proibido
    TrainingSessionStatus.SCHEDULED: {PUBLISHED, IN_PROGRESS, CANCELLED},  # IN_PROGRESS: proibido
    ...
}
```

**Evidência B:**
```python
# test_state_machine.py:23
def test_draft_to_published_valid(self):
    assert_valid_transition(DRAFT, PUBLISHED)  # PASSA — teste errado
```

**Impacto:**
- Sessões podem pular a fase de agendamento (SCHEDULED) e ir diretamente de DRAFT para PUBLISHED
- Sessões SCHEDULED podem iniciar execução sem passar por PUBLISHED
- Quebra o modelo de negócio de aprovação/publicação de treinos
- Rastreabilidade de histórico de estados comprometida

**Correção mínima:**
Remover `PUBLISHED` de `DRAFT` no dict e `IN_PROGRESS` de `SCHEDULED`. Corrigir o teste `test_draft_to_published_valid` para assert que levanta exceção.

**Correção ideal:**
Adicionar test cases explícitos para cada transição proibida, garantindo cobertura de todas as 42 combinações de estado. Revisitar se `DRAFT → CANCELLED` também é intencional.

**Bloqueia merge?: sim**

---

### RC-002 — Schema de wellness pré diverge fundamentalmente do contrato

---
> ACHADO-ID: RC-002
> Categoria: Bug real — schema de entrada divergente em 5 camadas
> Módulo: training / wellness
> Severidade: crítica
> Estado: erro confirmado
---
> Camadas em conflito:
- contrato (source master — sleepHours required)
- schemas (SubmitWellnessPreIn — sleepHours ausente)
- runtime (handler wellness.py — sleepHours não passado ao use case)
- domínio (entidade WellnessPre — sleepHours ausente)
- persistência (ORM WellnessPreModel — sleepHours ausente)
---

**Descrição:**
O source master (`contracts/openapi/paths/training.yaml` linha 1294) declara `sleepHours` como campo **required** em `submitWellnessPre`. Em nenhuma das 5 camadas do runtime o campo existe. Adicionalmente, o runtime implementa 5 campos (`readiness`, `mood`, `fatigue`, `muscle_soreness`, `notes`) que não estão no contrato, com `additionalProperties: false` no source master.

**Sintomas derivados:**
- CD-002 (divergência de schema no contrato diff)
- ADV-001 (sleepHours ausente adversarialmente confirmado)

**Evidência A — source master (linha 1294):**
```yaml
required: [athleteId, sleepQuality, sleepHours]
```

**Evidência B — runtime:**
```python
class SubmitWellnessPreIn(Schema):
    athlete_id: uuid.UUID          # ok
    readiness: Optional[int] = None        # extra — não está no contrato
    sleep_quality: Optional[int] = None    # deveria ser required
    mood: Optional[int] = None             # extra
    fatigue: Optional[int] = None          # extra
    muscle_soreness: Optional[int] = None  # extra
    notes: Optional[str] = None            # extra
    # sleep_hours: COMPLETAMENTE AUSENTE
```

**Evidência C:** grep completo de `sleep_hours` e `sleepHours` em `src/training/` — zero matches fora de `__pycache__`.

**Impacto:**
- Clientes seguindo o contrato enviam `sleepHours` — campo silenciosamente ignorado
- Dado de sono (crítico para modelo de recuperação atlética) nunca é persistido
- O modelo de wellness produz análises sem a variável de sono — comprometendo a acurácia de recomendações

**Causa-raiz do gap:**
Decisão de design: os campos `readiness`, `mood`, `fatigue`, `muscle_soreness` representam um modelo de wellness mais completo que foi implementado no runtime mas não refletido no source master. O `sleepHours` do contrato foi esquecido durante a implementação.

**Correção mínima:**
Definir o modelo canônico. Opção A: adicionar `sleep_hours` ao runtime em todas as 5 camadas. Opção B: atualizar o source master para refletir o modelo real (adicionando `readiness`, `mood`, `fatigue`, `muscle_soreness`; tornando `sleepHours` opcional). Sem decisão de produto, ambas as opções são válidas.

**Correção ideal:**
Unificar os dois modelos — o contrato deve ter todos os campos úteis (`sleepHours`, `readiness`, `mood`, `fatigue`, `muscle_soreness`, `notes`). Implementar `sleepHours` no runtime.

**Bloqueia merge?: sim**

---

### RC-003 — Formato de erro não implementa RFC 7807 / application/problem+json

---
> ACHADO-ID: RC-003
> Categoria: Bug real — contrato de erro violado em todos os endpoints
> Módulo: training (todos os 53 endpoints)
> Severidade: crítica
> Estado: erro confirmado
---
> Camadas em conflito:
- contrato (source master — application/problem+json com required: type, title, status, traceId)
- schemas (ErrorOut = {detail: str})
- runtime (config/urls.py — _problem_response sem traceId; map_exceptions usa HttpError)
---

**Descrição:**
O source master declara todas as respostas de erro como `application/problem+json` com schema RFC 7807 (`type`, `title`, `status`, `traceId` — required). O runtime retorna `{"detail": "..."}` em `application/json`. O `traceId` — exigido pelo `contracts/openapi/components/schemas/shared/problem.yaml` com pattern UUID-like — está completamente ausente de todos os error bodies, mesmo tendo o `flow_id` disponível no contexto via `FlowIDMiddleware`.

**Sintomas derivados:**
- CD-001 (achado de contrato)
- ADV-004 (achado adversarial — traceId ausente)

**Evidência A — schema canônico:**
```yaml
# contracts/openapi/components/schemas/shared/problem.yaml
required: [type, title, status, traceId]
```

**Evidência B — runtime:**
```python
class ErrorOut(Schema):
    detail: str  # único campo

def _problem_response(status, detail):
    return {"type": "about:blank", "title": ..., "status": ..., "detail": ...}
    # traceId: AUSENTE
```

**Evidência C:** `X-Flow-ID` middleware (`FlowIDMiddleware`) está ativo e propaga `flow_id` — existe o dado, mas ele não é incluído no body de erro.

**Impacto:**
- Todos os 53 endpoints retornam formato de erro incompatível com o contrato
- Clientes que fazem parse de `application/problem+json` falharão na deserialização
- Correlação de erros por cliente impossível (sem `traceId` no body)
- Viola RFC 7807 declarado no contrato

**Correção mínima:**
Criar exception handler global no Django Ninja que:
1. Capture todas as `HttpError` e exceções de domínio
2. Produza `{type, title, status, traceId, detail}` com `Content-Type: application/problem+json`
3. Injete `flow_id` como `traceId`

Substituir `ErrorOut` por `ProblemOut` com os 4 campos required.

**Bloqueia merge?: sim**

---

### RC-004 — Invariantes de domínio declaradas no canon sem enforcement no application layer

---
> ACHADO-ID: RC-004
> Categoria: Bug real — regras de negócio declaradas mas não enforced
> Módulo: training
> Severidade: alta
> Estado: erro confirmado
---
> Camadas em conflito:
- documentação canônica (STATE_MODEL_TRAINING.md, DOMAIN_RULES_TRAINING, INV-TRAIN-086)
- domínio (domain/rules.py — sem guard de precondições)
- runtime (application/sessions/commands.py — TransitionTrainingSessionUseCase)
---

**Descrição:**
Três invariantes/regras de domínio estão declaradas no canon mas não têm implementação de guarda na camada de aplicação:

1. **INV-TRAIN-086** — precondições de publicação: `individualizationMode != null`, `sessionAt != null`, `≥1 objective`, `≥1 block`. Ausente de `TransitionTrainingSessionUseCase` (DRAFT → PUBLISHED passa sem verificação).

2. **DR-TRAIN-011** — `session_at` obrigatório para DRAFT → SCHEDULED. Ausente de qualquer guarda na transition use case.

3. **DR-TRAIN-030** — limite de carga de treino. Declarado no domínio mas ausente do contrato (schema de request não o expressa).

**Sintomas derivados:**
- DP-003 (precondições de publish)
- DP-005 (DR-TRAIN-011)
- ADV-011 (DR-TRAIN-030 no contrato)

**Impacto:**
- Sessões podem ser publicadas sem objetivos, sem blocos, sem data — estado inválido para atletas
- Sessões podem ser agendadas sem `session_at` — agendamento sem data não faz sentido de negócio

**Correção mínima:**
Adicionar guard method `_assert_publish_preconditions(session)` em `TransitionTrainingSessionUseCase` que verifica INV-TRAIN-086 antes de chamar `assert_valid_transition(DRAFT, PUBLISHED)`.
Adicionar guard `_assert_schedule_preconditions(session)` para DR-TRAIN-011.

**Bloqueia merge?: sim**

---

### RC-005 — Campos de entidade de domínio ausentes do ORM

---
> ACHADO-ID: RC-005
> Categoria: Bug real — entidade e modelo de persistência dessincronizados
> Módulo: training
> Severidade: alta
> Estado: erro confirmado
---
> Camadas em conflito:
- domínio (entidade TrainingSession — campos declarados)
- persistência (TrainingSessionModel — campos ausentes)
---

**Descrição:**
4 campos presentes na entidade de domínio `TrainingSession` estão ausentes do `TrainingSessionModel` (ORM). Confirmado após refutação (DP-002 revisado):
- `planned_content_snapshot` — snapshot do conteúdo planejado
- `post_review_completed_by_user_id` — autor da revisão pós-treino
- `post_review_deadline_at` — prazo de revisão pós-treino
- `continuity_notes` / `objective_origin` — notas de continuidade e origem de objetivos

Nota: `individualization_mode` e `post_review_completed_at` existem no ORM — não são parte deste achado.

**Sintomas derivados:**
- DP-002 (achado de domínio/persistência — revisado pós-refutação)

**Impacto:**
- Dados da entidade silenciosamente descartados na persistência
- Funcionalidades de revisão pós-treino (post_review) não persistem completamente
- Continuidade entre sessões comprometida

**Correção mínima:**
Adicionar os 4 campos ao `TrainingSessionModel` e criar migration. Verificar se a entidade já hidrata esses campos da ORM (o repository pode precisar de ajuste).

**Bloqueia merge?: não** (campos não persistidos — dado perdido, mas não bloqueio de operação)

---

### RC-006 — Migration pendente para remoção de índice em TrainingSessionModel

---
> ACHADO-ID: RC-006
> Categoria: Bug real — modelo Python e banco dessincronizados
> Módulo: training
> Severidade: alta
> Estado: erro confirmado
---
> Camadas em conflito:
- persistência (src/training/migrations/ — migration ausente)
- runtime (src/training/infrastructure/models/ — índice removido do modelo Python)
---

**Descrição:**
O índice `training_session_at_id_idx` foi removido de `TrainingSessionModel` sem a criação da migration correspondente. `makemigrations --check` confirma que a migration `0008_remove_trainingsessionmodel_training_session_at_id_idx.py` deveria existir mas não existe.

**Sintomas derivados:**
- ACHADO-007 (runtime-classification)

**Impacto:**
O banco de dados (produção/staging) mantém o índice; o modelo Python não o declara. Inconsistência entre schema real do banco e o que o Django conhece.

**Correção mínima:**
```bash
python manage.py makemigrations training
# verificar conteúdo gerado
python manage.py migrate
```

**Bloqueia merge?: sim** (model/migration out of sync é bloqueante para deploy)

---

### RC-007 — Response codes divergem sistematicamente entre contrato e handler declarations

---
> ACHADO-ID: RC-007
> Categoria: Drift — mapeamento de exceções e response dict incompletos
> Módulo: training (múltiplos handlers)
> Severidade: alta
> Estado: drift provável
---
> Camadas em conflito:
- contrato (source master — 404, 409, 500 declarados; 422 ausente)
- runtime (handlers — 422 declarado; 404/409/500 ausentes em vários)
---

**Descrição:**
Padrão sistemático em múltiplos endpoints:
1. Handlers declaram `422` (Pydantic validation) — contrato usa `400` para validation errors
2. Contrato declara `409` (conflict) — ausente do `_EXCEPTION_STATUS_MAP` em `errors.py` para alguns handlers
3. Contrato declara `500` — nunca declarado nos response dicts (framework gerencia)
4. `401` ausente da declaração de `list_session_objectives` e `list_execution_records`
5. `409` ausente de `record_session_attendance` (`AttendanceAlreadyRecorded` não mapeado)

**Sintomas derivados:**
- CD-005 (createTrainingSession)
- CD-006 (deleteTrainingSession)
- CD-007 (updateTrainingSession)
- CD-008 (500 ausente em todos — sistemático)
- ADV-006 (createTrainingSession — adversarial)
- ADV-009 (401 ausente em list endpoints)
- ADV-010 (409 ausente em attendance)

**Impacto:**
OpenAPI spec gerado pelo Ninja diverge do spec canônico. Clientes que geram código a partir do spec Ninja receberão types incorretos para respostas de erro. Regressões de breaking change não detectadas pelo `oasdiff`.

**Correção mínima:**
1. Decidir 422 vs 400 para validation — alinhar em todos os endpoints
2. Adicionar `AttendanceAlreadyRecorded → 409` ao `_EXCEPTION_STATUS_MAP`
3. Adicionar `401` ao response dict de `list_session_objectives` e `list_execution_records`
4. Adicionar 500 aos response dicts ou documentar no contrato que é framework-managed

**Bloqueia merge?: não** (comportamento funcional correto; divergência de documentação/spec)

---

### RC-008 — Path parameters com case divergente entre contrato e handlers

---
> ACHADO-ID: RC-008
> Categoria: Drift — convenção de nomenclatura inconsistente
> Módulo: training / blocks, execution
> Severidade: alta
> Estado: erro confirmado
---
> Camadas em conflito:
- contrato (source master — {blockId}, {recordId}, {athleteId} em camelCase)
- runtime (handlers — {block_id}, {record_id}, {athlete_id} em snake_case)
---

**Descrição:**
O source master declara path parameters em camelCase (ex: `{blockId}`, `{recordId}`) enquanto os handlers Django/Python usam snake_case (`{block_id}`, `{record_id}`). Django Ninja não realiza tradução automática de path parameters. Isso significa que a URL real exposta pelo servidor é diferente da URL declarada no contrato.

**Sintomas derivados:**
- ADV-005 (achado adversarial)

**Impacto:**
Clientes que seguem o contrato (`/training-sessions/{id}/blocks/{blockId}`) recebem 404 — o servidor espera `/training-sessions/{id}/blocks/{block_id}`.

**Nota:** path params em `wellness.py` usam `{athleteId}` (já camelCase no runtime) — o drift não é universal, apenas em blocks e execution.

**Correção mínima:**
Decidir convenção e alinhar. Opção A: renomear path params nos handlers Python para camelCase. Opção B: atualizar source master para snake_case. A opção A é mais alinhada com REST/OpenAPI conventions (camelCase para path params).

**Bloqueia merge?: sim** (URLs distintas entre contrato e runtime — breaking para clientes)

---

### RC-009 — individualizationMode não exposto via API de criação/atualização

---
> ACHADO-ID: RC-009
> Categoria: Drift — campo de domínio inacessível via API
> Módulo: training
> Severidade: alta
> Estado: erro confirmado
---
> Camadas em conflito:
- contrato (individualizationMode declarado como campo de sessão)
- schemas (CreateTrainingSessionIn, UpdateTrainingSessionIn — campo ausente)
---

**Descrição:**
O campo `individualizationMode` existe em:
- ORM (`individualization_mode`, linha 43, `default=""`)
- Repository (salva e carrega corretamente)
- Entidade de domínio

Mas está **ausente** de `CreateTrainingSessionIn` e `UpdateTrainingSessionIn`. Clientes não podem definir o modo de individualização ao criar ou atualizar sessões. O campo persiste com `default=""` permanentemente.

Adicionalmente, `INV-TRAIN-086` exige que `individualizationMode != null` como precondição de publicação (RC-004) — o campo nunca pode ser não-nulo se a API não o expõe.

**Sintomas derivados:**
- DP-004 (domínio/persistência)
- ADV-003 (adversarial — atenuado após refutação)

**Impacto:**
Funcionalidade de individualização de sessão (treinos personalizados vs. coletivos) é inoperável via API. Combinado com RC-004 (INV-TRAIN-086), cria dependência circular: publicar requer `individualizationMode` não-nulo, mas a API não permite setá-lo.

**Correção mínima:**
Adicionar `individualization_mode: Optional[str] = None` a `CreateTrainingSessionIn` e `UpdateTrainingSessionIn`. Validar contra enum de valores permitidos.

**Bloqueia merge?: não** (funcionalidade ausente, não bloqueio crítico)

---

### RC-010 — Location header ausente em respostas 201

---
> ACHADO-ID: RC-010
> Categoria: Drift — promessa de contrato não implementada
> Módulo: training (endpoints POST que criam recursos)
> Severidade: alta
> Estado: drift provável
---
> Camadas em conflito:
- contrato (source master — Location header declarado em 201 responses)
- runtime (handlers retornam apenas body)
---

**Descrição:**
O source master declara `Location` header nas respostas 201 de pelo menos 3 endpoints confirmados: `createTrainingSession`, `submitWellnessPre`, `submitWellnessPost`. Provável em outros endpoints POST que criam recursos. Handlers retornam apenas `(201, body)` sem setar `response.headers["Location"]`.

**Sintomas derivados:**
- CD-004 (contrato diff)

**Impacto:**
Clientes REST que usam `Location` header para descobrir URI do recurso criado não recebem o dado. Padrão REST standard (AIP-133, RFC 9110) não cumprido.

**Correção mínima:**
Em cada handler POST de criação:
```python
response.headers["Location"] = f"/api/training/training-sessions/{session.id}"
return 201, _session_to_out(session)
```

**Bloqueia merge?: não** (funcionalidade presente; REST discoverability ausente)

---

### RC-011 — deviationJustification e status ausentes do PATCH body

---
> ACHADO-ID: RC-011
> Categoria: Drift — decisão arquitetural não refletida no contrato
> Módulo: training / sessions
> Severidade: alta
> Estado: drift provável
---
> Camadas em conflito:
- contrato (source master — `deviationJustification` e `status` em updateTrainingSession)
- schemas (UpdateTrainingSessionIn — campos ausentes)
- runtime (transitions via endpoints dedicados, não via PATCH body)
---

**Descrição:**
O source master declara dois campos opcionais no PATCH `/training-sessions/{id}`:
- `deviationJustification` (string) — justificativa de desvio de plano
- `status` (enum) — transição de estado via PATCH

O runtime implementa transições via endpoints dedicados (`POST /publish`, `POST /start`, etc.) — decisão arquitetural que diverge do contrato. `deviationJustification` não existe em nenhuma camada do runtime.

**Sintomas derivados:**
- CD-003 (contrato diff)

**Impacto:**
- Clientes que enviam `status` no PATCH body têm o campo silenciosamente ignorado
- `deviationJustification` não é persistido — dado de gestão perdido

**Correção mínima:**
Decidir: se endpoints dedicados são o padrão, remover `status` do source master. Implementar `deviationJustification` no runtime (campo útil para gestão) ou remover do contrato com justificativa documentada.

**Bloqueia merge?: não**

---

### RC-012 — session_start.schema.json modificado sem re-hash

---
> ACHADO-ID: RC-012
> Categoria: Drift — artefato de contrato modificado sem pipeline de rastreabilidade
> Módulo: shared (governança)
> Severidade: alta
> Estado: drift provável
---
> Camadas em conflito:
- contrato (`contracts/schemas/shared/session_start.schema.json` — hash divergente)
- generated (manifests de rastreabilidade — 30 referências com hash stale)
---

**Descrição:**
`session_start.schema.json` foi editado diretamente sem rodar `hb artifact <path>`. Os 30 manifests distribuídos no repositório que referenciam este schema têm hash desatualizado. `DERIVED_DRIFT_GATE` falha com 30 erros — todos apontando para o mesmo arquivo.

**Sintomas derivados:**
- ACHADO-001 (drift gate)
- ACHADO-003 (READINESS_SUMMARY_GATE — derivado)
- ACHADO-005 (test_contract_gates_pass — derivado)

**Correção mínima:**
```bash
hb artifact contracts/schemas/shared/session_start.schema.json
```

**Bloqueia merge?: sim** (DERIVED_DRIFT_GATE é bloqueante)

---

### RC-013 — session_start.json e SESSION_HANDOFF.md dessincronizados

---
> ACHADO-ID: RC-013
> Categoria: Drift — metadados de sessão divergentes
> Módulo: governança
> Severidade: alta
> Estado: drift provável
---
> Camadas em conflito:
- documentação canônica (SESSION_HANDOFF.md)
- runtime (_reports/session_start.json)
---

**Descrição:**
`HANDOFF_COHERENCE_GATE` detectou 3 inconsistências entre os dois artefatos de sincronização de sessão: `module_focus` e `roadmap_phase` divergem (fase 1 no `session_start.json` vs. fase 6 no `SESSION_HANDOFF.md`). O estado real do projeto é fase 4 (confirmado por MEMORY.md), o que contradiz ambos.

**Sintomas derivados:**
- ACHADO-002 (handoff coherence)
- ACHADO-003 (READINESS_SUMMARY_GATE — derivado)

**Correção mínima:**
Sincronizar `SESSION_HANDOFF.md` com o estado real (fase 4) e regenerar `session_start.json`.

**Bloqueia merge?: sim** (HANDOFF_COHERENCE_GATE é bloqueante)

---

### RC-014 — GOVERNANCE_REGRESSION_GATE executado sem registro canônico

---
> ACHADO-ID: RC-014
> Categoria: Bug real — gate sem rastreabilidade no registry
> Módulo: governança (GATES_REGISTRY.yaml)
> Severidade: alta
> Estado: erro confirmado
---
> Camadas em conflito:
- documentação canônica (GATES_REGISTRY.yaml — gate ausente)
- runtime (validate_contracts.py — gate presente e passando)
- teste (test_executor_gates_all_in_registry — falha)
---

**Descrição:**
`GOVERNANCE_REGRESSION_GATE` foi adicionado ao executor (`validate_contracts.py`) sem a entrada correspondente no `GATES_REGISTRY.yaml`. O gate funciona e passa — o problema é exclusivamente de rastreabilidade. `test_executor_gates_all_in_registry` verifica esta paridade e falha.

**Sintomas derivados:**
- ACHADO-004 (runtime-classification)

**Correção mínima:**
Adicionar entrada `GOVERNANCE_REGRESSION_GATE` ao `GATES_REGISTRY.yaml` com os campos obrigatórios.

**Bloqueia merge?: sim** (teste de paridade de gates falha)

---

### RC-015 — resolve_access() não popula team_ids e athlete_ids (TODO Fase 3)

---
> ACHADO-ID: RC-015
> Categoria: Não comprovado como bug — implementação incompleta por design
> Módulo: training (identity_access integration)
> Severidade: alta
> Estado: não comprovado
---
> Camadas em conflito:
- runtime (src/training/api/deps.py — team_ids=(), athlete_ids=() hardcoded)
---

**Descrição:**
`resolve_access()` retorna `team_ids=()` e `athlete_ids=()` com comentário explícito `# TODO Fase 3: preencher via identity_access`. Esta é uma implementação planejada, não um bug não intencional.

Impactos reais identificados na refutação (ADV-007 atenuado):
1. **Cross-team listing:** coaches podem listar sessões de qualquer time da organização (sem filtragem por team_ids)
2. **Athlete lockout:** `GetTrainingSessionUseCase` chama `load_for_read` com `session_athlete_ids=[]` (default vazio) — athletes nunca passam no check `actor_id in athlete_ids`, ficando completamente bloqueados de ler sessões individuais

**Estado:** a integração com `identity_access` não foi implementada (Fase 3 pendente). O vetor 2 (athlete lockout) é uma regressão funcional não intencional — pode ser classificado como bug derivado da incompletude.

**Sintomas derivados:**
- ADV-007 (adversarial — atenuado)

**Correção mínima:**
Para o athlete lockout: em `get_training_session` handler, popular `session_athlete_ids` a partir dos dados da sessão carregada (antes do guard), não do AccessContext.

Para o cross-team listing: aguardar Fase 3 (integração identity_access) ou adicionar filtragem temporária.

**Bloqueia merge?: não** (TODO documentado — mas o athlete lockout é regressão funcional que deve ser avaliada)

---

### RC-016 — Canon arquitetural defasado (~6 semanas de implementação não documentada)

---
> ACHADO-ID: RC-016
> Categoria: Drift — documentação de estado atual desatualizada
> Módulo: shared (docs/_canon)
> Severidade: média
> Estado: drift provável
---
> Camadas em conflito:
- documentação canônica (RUNTIME_CURRENT_STATE.md, ARCHITECTURE.md, C4_CONTAINERS.md)
- runtime (implementação real)
---

**Descrição:**
O `RUNTIME_CURRENT_STATE.md` documenta o estado em ~2026-03-23. A implementação avançou significativamente após essa data sem atualização correspondente. 36 dos 55 elementos verificados (65%) divergem. Categorias afetadas: Celery, Django Channels, GET /health, Dockerfile/compose/nginx, FlowIDMiddleware, logging JSON, frontend completo.

**Nenhum dos 10 achados (AR-001 a AR-010) representa bug de código** — todos são drift de documentação onde o código está correto e o documento está desatualizado.

**Sintomas derivados:**
- AR-001 a AR-010 (architecture-reality)

**Correção mínima:**
Sessão de atualização de `RUNTIME_CURRENT_STATE.md` elimina 8 dos 10 achados em cascata.
Sequência: RUNTIME_CURRENT_STATE.md → ARCHITECTURE.md §1,§5 → C4_CONTAINERS.md → CODE_ARCHITECTURE.md §1,§4 → README.md.

**Bloqueia merge?: não**

---

### RC-017 — AttendanceRecordOut runtime mais rico que schema de contrato

---
> ACHADO-ID: RC-017
> Categoria: Drift — runtime evoluiu além do contrato
> Módulo: training / attendance
> Severidade: baixa
> Estado: drift provável
---
> Camadas em conflito:
- contrato (source master — 4 campos em 201 response, additionalProperties: false)
- runtime (AttendanceRecordOut — 7 campos)
---

**Descrição:**
Runtime retorna 3 campos extras (`correction_by_user_id`, `correction_at`, `justification_reason`) que não estão no source master. Com `additionalProperties: false` no schema, clientes strict-mode rejeitarão a resposta.

**Sintomas derivados:**
- CD-009 (contrato diff)

**Correção mínima:**
Atualizar source master para incluir os 3 campos opcionais no inline 201 schema de `recordSessionAttendance`.

**Bloqueia merge?: não**

---

### RC-018 — Import shims de compatibilidade em código de produção

---
> ACHADO-ID: RC-018
> Categoria: Drift — refatoração de subpacotes incompleta
> Módulo: training (múltiplos)
> Severidade: baixa
> Estado: drift provável
---
> Camadas em conflito:
- runtime (src/training/api/, application/, infrastructure/ — imports via shims)
- domínio (src/training/domain/rules.py — imports via shims)
---

**Descrição:**
~80 `DeprecationWarning` no pytest — todos do módulo training, todos sobre imports via shims de compatibilidade. Os shims cobrem os caminhos antigos de entities, models, repository, schemas e use_cases. Código de **produção** (não apenas testes) ainda usa os caminhos antigos.

**Sintomas derivados:**
- ACHADO-008 (runtime-classification)

**Risco:** quando os shims forem removidos (release N+2 declarado), o código quebrará em todos os pontos de import.

**Correção mínima:** nenhuma imediata — shims funcionam. Registrar como débito técnico.

**Correção ideal:** migrar todos os imports para subpacotes diretos em batch. Priorizar os arquivos de produção (api/, application/, infrastructure/) antes dos testes.

**Bloqueia merge?: não**

---

### RC-019 — TRAINING_CURSOR_SECRET ausente no escopo de teste de performance

---
> ACHADO-ID: RC-019
> Categoria: Problema de ambiente — env var ausente no fixture de performance
> Módulo: training / testes
> Severidade: média
> Estado: problema de ambiente
---
> Camadas em conflito:
- teste (tests/test_performance_phase4.py)
- infra (configuração de ambiente de teste)
---

**Descrição:**
`test_performance_phase4.py` falha com `RuntimeError: TRAINING_CURSOR_SECRET não definida`. O conftest.py do escopo correto não cobre este diretório. Não é bug no código de produção — `get_cursor_codec()` está corretamente defensivo.

**Sintomas derivados:**
- ACHADO-006 (runtime-classification)

**Correção mínima:**
```python
# conftest.py (escopo tests/)
import os
os.environ.setdefault("TRAINING_CURSOR_SECRET", "test-secret-for-perf")
```

**Bloqueia merge?: não** (oculta regressões de performance)

---

### RC-020 — api/__init__.py importa generated/ incondicionalmente em startup

---
> ACHADO-ID: RC-020
> Categoria: Drift — acoplamento de startup a artefato derivado
> Módulo: training
> Severidade: baixa
> Estado: drift provável
---
> Camadas em conflito:
- runtime (src/training/api/__init__.py — import incondicional de generated/)
- generated (gerado pelo pipeline; não é source soberana)
---

**Descrição:**
`src/training/api/__init__.py` importa `generated/` em startup sem condicional `if settings.DEBUG`. Se o artefato `generated/` não existir (ex: ambiente clean sem rodar pipeline), o import falha com `ImportError` em startup. O import serve como parity gate — não para servir o schema.

**Sintomas derivados:**
- ADV-008 (adversarial — atenuado após refutação)

**Severidade revisada:** BAIXA (rebaixada de MÉDIA). Risco é `ImportError` em startup em ambientes sem `generated/` — não falha funcional em runtime normal.

**Correção mínima:**
Tornar o import condicional:
```python
try:
    from generated.training import schema_parity_check  # noqa
except ImportError:
    pass  # generated/ ausente — skipa parity check
```

**Bloqueia merge?: não**

---

## Ordem recomendada de correção

### Fase 1 — Bloqueantes de merge (executar antes de qualquer PR)

| Prioridade | RC | Esforço | Resolve em cascata |
|---|---|---|---|
| 1 | RC-012 (hash drift) | `hb artifact <path>` — minutos | ACHADO-001, 003, 005 |
| 2 | RC-013 (handoff sync) | atualizar SESSION_HANDOFF + regenerar session_start.json — 30min | ACHADO-002, 003 |
| 3 | RC-014 (gate registry) | adicionar entry ao GATES_REGISTRY.yaml — 30min | ACHADO-004 |
| 4 | RC-006 (migration pendente) | `makemigrations && migrate` — 15min | ACHADO-007 |

### Fase 2 — Bugs críticos de funcionalidade

| Prioridade | RC | Esforço | Impacto |
|---|---|---|---|
| 5 | RC-001 (FSM incorreto) | Editar VALID_TRANSITIONS + corrigir 1 teste — 1h | FSM de toda a sessão |
| 6 | RC-003 (error format) | Exception handler global + ProblemOut — 2-4h | Todos os 53 endpoints |
| 7 | RC-002 (wellness schema) | Decisão de produto + alinhamento em 5 camadas — 4-8h | Módulo wellness |
| 8 | RC-004 (invariantes) | Guards em TransitionUseCase — 2-4h | Publicação de sessões |
| 9 | RC-008 (path param case) | Normalizar case em handlers ou source master — 2h | Clientes que usam blocks/execution |

### Fase 3 — Gaps de contrato (não bloqueantes, mas comprometem paridade)

| Prioridade | RC | Esforço |
|---|---|---|
| 10 | RC-007 (response codes) | Atualizar response dicts + _EXCEPTION_STATUS_MAP — 2-4h |
| 11 | RC-009 (individualizationMode API) | Adicionar campo a Create/UpdateIn — 1h |
| 12 | RC-010 (Location headers) | response.headers["Location"] em handlers POST — 1h |
| 13 | RC-011 (deviationJustification) | Decisão + implementação ou remoção do contrato — 1-2h |
| 14 | RC-005 (ORM fields) | Adicionar campos ao model + migration — 2h |

### Fase 4 — Débito técnico (planejar antes de N+2)

| Prioridade | RC | Esforço |
|---|---|---|
| 15 | RC-015 (resolve_access — Fase 3) | Integração identity_access — estimativa grande |
| 16 | RC-016 (canon arquitetural) | Sessão de atualização de docs — 4h |
| 17 | RC-017 (attendance schema) | Atualizar source master — 30min |
| 18 | RC-018 (import shims) | Migração batch de imports — 4-8h |
| 19 | RC-019 (cursor secret em test) | conftest.py — 15min |
| 20 | RC-020 (api/__init__ import) | Tornar condicional — 15min |

---

## Severidade consolidada por cluster

| Cluster | Causa-raiz | Bugs reais | Drift | Severidade máxima | Bloqueia merge? |
|---|---|---|---|---|---|
| A — Bugs de implementação | RC-001, RC-003, RC-004, RC-006, RC-014 | 5 | 0 | crítica | sim |
| B — Schema/campo divergente | RC-002, RC-005, RC-009, RC-011 | 3 | 1 | crítica | sim (RC-002) |
| C — Contrato↔runtime drift | RC-007, RC-008, RC-010, RC-017, RC-020 | 1 (RC-008) | 4 | alta | sim (RC-008) |
| D — Governança/pipeline | RC-012, RC-013 | 0 | 2 | alta | sim |
| E — Incompleto/débito | RC-015, RC-016, RC-018, RC-019 | 0 | 3 | média | não |

---

## Distribuição de severidade (consolidada pós-refutação)

| Severidade | RC IDs |
|---|---|
| Crítica | RC-001, RC-002, RC-003 |
| Alta | RC-004, RC-005, RC-006, RC-007, RC-008, RC-009, RC-010, RC-011, RC-012, RC-013, RC-014, RC-015 |
| Média | RC-016, RC-019 |
| Baixa | RC-017, RC-018, RC-020 |

**Total: 3 críticas, 12 altas, 2 médias, 3 baixas — 20 causas-raiz distintas.**
**Bloqueiam merge: RC-001 (bug real), RC-003 (bug real), RC-006 (migration), RC-008 (URL break), RC-012 (gate), RC-013 (gate), RC-014 (gate).**
Nota: RC-002 é crítico mas o merge pode ocorrer se houver waiver documentado para o módulo wellness (funcionalidade parcial — não crash).
