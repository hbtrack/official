# Plano de Remediação — AGAUDIT v1.1

> Auditoria técnica de repositório contract-driven.
> Data: 2026-04-23
> Entrada: _reports/ai_audit/06-root-causes/consolidated.md
> Módulo primário: training (com achados em shared/governança)
> Regras: AGAUDIT v1.1 — Prompt 8

---

## Visão geral do plano

O plano é organizado em 4 ondas sequenciais. Cada onda deve ser completada e validada antes da próxima. **Ondas 0 e 1 são pré-requisito para merge.** Ondas 2 e 3 são recomendadas antes de staging. Onda 4 é débito técnico planejável.

| Onda | Foco | RCs | Bloqueia merge |
|---|---|---|---|
| 0 — Pipeline | Desbloquear gates de governança | RC-012, RC-013, RC-014 | sim |
| 1 — Bugs críticos | Erros de implementação que violam canon | RC-001, RC-002, RC-003, RC-004, RC-006 | sim |
| 2 — Bugs altos | URLs quebradas e invariantes | RC-008, RC-015 (parcial) | RC-008 sim |
| 3 — Drift de contrato | Paridade contrato↔runtime | RC-005, RC-007, RC-009, RC-010, RC-011, RC-017 | não |
| 4 — Débito técnico | Canon, shims, testes, env | RC-016, RC-018, RC-019, RC-020 | não |

**Menor caminho para merge:** Onda 0 (3 itens rápidos) → Onda 1 RC-001 e RC-006 (4h) → RC-003 (4h) → RC-002 (decisão de produto) → Onda 2 RC-008 (2h). Total mínimo: ~12h + 1 decisão de produto.

---

## Onda 0 — Pipeline: desbloquear gates de governança

> Executar antes de qualquer outra coisa. Sem esses gates passando, `hb verify` falha e bloqueia qualquer tarefa CDD.

---

### REM-0A — Re-hashar session_start.schema.json

---
> ACHADO-ID: REM-0A (RC-012)
> Categoria: Sincronização de artefato — hash drift
> Módulo: shared (governança)
> Severidade: alta
> Estado: drift provável
---
> Camadas em conflito:
- contrato
- generated
---

**Descrição:**
`contracts/schemas/shared/session_start.schema.json` foi editado sem rodar `hb artifact`. 30 manifests têm hash stale. `DERIVED_DRIFT_GATE` falha com 30 erros idênticos.

**Arquivos-alvo:**
- `contracts/schemas/shared/session_start.schema.json` — não editar, só re-hashar
- Manifests de rastreabilidade (atualizados automaticamente pelo `hb artifact`)

**Correção mínima:**
```bash
hb artifact contracts/schemas/shared/session_start.schema.json
```

**Correção ideal:** mesma — o conteúdo do schema já é o correto. Apenas o hash precisa ser atualizado.

**Risco:** nenhum. `hb artifact` é idempotente e não altera conteúdo.

**Como validar:**
```bash
python3 scripts/validate_contracts.py
# DERIVED_DRIFT_GATE deve passar
```

**Critérios de done:**
- [x] `DERIVED_DRIFT_GATE: PASS` no output de `validate_contracts.py`
- [x] Zero erros de hash divergente para `session_start.schema.json`

> **EVIDÊNCIA (2026-04-23):** `python3 scripts/contracts/validate/validate_contracts.py 2>&1 | grep DERIVED_DRIFT` → `+ [PASS] DERIVED_DRIFT_GATE`. 30 manifests atualizados com SHA256 correto `387211a1...`. `STATUS: PASS`.

**Bloqueia merge?: sim**

---

### REM-0B — Sincronizar SESSION_HANDOFF.md e session_start.json

---
> ACHADO-ID: REM-0B (RC-013)
> Categoria: Metadados de sessão dessincronizados
> Módulo: governança
> Severidade: alta
> Estado: drift provável
---
> Camadas em conflito:
- documentação canônica
- runtime
---

**Descrição:**
`SESSION_HANDOFF.md` e `_reports/session_start.json` divergem em `module_focus` e `roadmap_phase`. Estado real: fase 4. `HANDOFF_COHERENCE_GATE` falha com 3 inconsistências.

**Arquivos-alvo:**
- `SESSION_HANDOFF.md` — atualizar para estado real (fase 4, módulo training)
- `_reports/session_start.json` — regenerar via pipeline após atualizar o handoff

**Correção mínima:**
1. Verificar e atualizar `SESSION_HANDOFF.md` para refletir estado atual (fase 4, módulo training, audit em andamento)
2. Regenerar `session_start.json`:
```bash
hb session-start  # ou equivalente
```

**Correção ideal:** mesma — garantir que o processo de início de sessão leia `SESSION_HANDOFF.md` primeiro.

**Risco:** baixo. Alteração de metadados de governança — não afeta código de produção.

**Como validar:**
```bash
python3 scripts/validate_contracts.py
# HANDOFF_COHERENCE_GATE deve passar
```

**Critérios de done:**
- [x] `HANDOFF_COHERENCE_GATE: PASS`
- [x] `session_start.json.module_focus == SESSION_HANDOFF.modulo_foco`
- [x] `session_start.json.roadmap_phase == SESSION_HANDOFF.fase_roadmap`

> **EVIDÊNCIA (2026-04-23):** `python3 scripts/contracts/validate/validate_contracts.py 2>&1 | grep HANDOFF` → `+ [PASS] HANDOFF_COHERENCE_GATE`. `SESSION_HANDOFF.md` front matter alinhado com `_reports/session_start.json`: `module_focus=training`, `roadmap_phase=4`.

**Bloqueia merge?: sim**

---

### REM-0C — Registrar GOVERNANCE_REGRESSION_GATE no GATES_REGISTRY.yaml

---
> ACHADO-ID: REM-0C (RC-014)
> Categoria: Bug real — gate sem rastreabilidade
> Módulo: governança
> Severidade: alta
> Estado: erro confirmado
---
> Camadas em conflito:
- documentação canônica
- runtime
- teste
---

**Descrição:**
`GOVERNANCE_REGRESSION_GATE` executa e passa em `validate_contracts.py` mas não está no `GATES_REGISTRY.yaml`. `test_executor_gates_all_in_registry` falha porque verifica esta paridade.

**Arquivos-alvo:**
- `GATES_REGISTRY.yaml` (ou equivalente — verificar path exato)

**Correção mínima:**
Adicionar entry no registry:
```yaml
- id: GOVERNANCE_REGRESSION_GATE
  description: "Verifica regressões de governança CDD"
  severity: alta
  blocker: true
  executor: validate_contracts.py
```
(Adaptar campos conforme schema existente no arquivo.)

**Correção ideal:** mesma. Adicionar também um pre-commit check que impeça adicionar gates ao executor sem registro correspondente.

**Risco:** nenhum. Adição de metadado — não altera lógica.

**Como validar:**
```bash
python3 -m pytest tests/pipeline_gates/test_gate_registry_parity.py -v
# test_executor_gates_all_in_registry deve passar
```

**Critérios de done:**
- [x] `test_executor_gates_all_in_registry: PASS`
- [x] `GOVERNANCE_REGRESSION_GATE` listado no registry com todos os campos obrigatórios

> **EVIDÊNCIA (2026-04-23):** `python3 -m pytest tests/pipeline_gates/test_gate_registry_parity.py -v` → `8 passed`. `test_executor_gates_all_in_registry PASSED`. Entrada adicionada em `docs/_canon/gates/GATES_REGISTRY.yaml` com `gate_id: GOVERNANCE_REGRESSION_GATE`, `blocking: true`, `severity: HIGH`.

**Bloqueia merge?: sim**

---

## Onda 1 — Bugs críticos de implementação

> Após Onda 0 completa. Esses itens violam o canon ou tornam o sistema não conforme com o contrato soberano.

---

### REM-1A — Corrigir FSM VALID_TRANSITIONS (+ teste errado)

---
> ACHADO-ID: REM-1A (RC-001)
> Categoria: Bug real — FSM permite transições proibidas pelo STATE_MODEL
> Módulo: training
> Severidade: crítica
> Estado: erro confirmado
---
> Camadas em conflito:
- documentação canônica
- domínio
- runtime
- teste
---

**Descrição:**
`VALID_TRANSITIONS` em `domain/rules.py` inclui `DRAFT → PUBLISHED` e `SCHEDULED → IN_PROGRESS` — ambas proibidas por `STATE_MODEL_TRAINING.md`. `test_draft_to_published_valid` (linha 23 de `test_state_machine.py`) valida ativamente a transição proibida como correta.

**Arquivos-alvo:**
- `src/training/domain/rules.py` — `VALID_TRANSITIONS` dict
- `src/training/tests/unit/test_state_machine.py` — `test_draft_to_published_valid`

**Correção mínima:**
```python
# src/training/domain/rules.py
VALID_TRANSITIONS = {
    TrainingSessionStatus.DRAFT:      {SCHEDULED, CANCELLED},           # remover PUBLISHED
    TrainingSessionStatus.SCHEDULED:  {PUBLISHED, CANCELLED},            # remover IN_PROGRESS
    TrainingSessionStatus.PUBLISHED:  {SCHEDULED, IN_PROGRESS, CANCELLED},
    TrainingSessionStatus.IN_PROGRESS: {COMPLETED, CANCELLED},
    TrainingSessionStatus.COMPLETED:  {ARCHIVED},
    TrainingSessionStatus.CANCELLED:  set(),
    TrainingSessionStatus.ARCHIVED:   set(),
}
```

```python
# src/training/tests/unit/test_state_machine.py
def test_draft_to_published_invalid(self):
    """DRAFT → PUBLISHED é proibido por STATE_MODEL_TRAINING.md linha 96."""
    with pytest.raises(InvalidStatusTransition):
        assert_valid_transition(DRAFT, PUBLISHED)

def test_scheduled_to_in_progress_invalid(self):
    """SCHEDULED → IN_PROGRESS é proibido por STATE_MODEL_TRAINING.md linha 100."""
    with pytest.raises(InvalidStatusTransition):
        assert_valid_transition(SCHEDULED, IN_PROGRESS)
```

Remover (ou inverter a assertion de) `test_draft_to_published_valid`.

**Correção ideal:** adicionar cobertura completa das 42 combinações (7×6) de estado — tabela de transições como fixture parametrizada que documenta todas as transições válidas e inválidas canonicamente.

**Risco:** **médio**. A mudança altera comportamento de runtime — sessões que antes podiam ir DRAFT→PUBLISHED diretamente agora precisam passar por SCHEDULED. Verificar se existem dados de produção/staging em DRAFT que esperavam ser publicados diretamente; se existirem, pode ser necessário migration de dados.

**Como validar:**
```bash
python3 -m pytest src/training/tests/unit/test_state_machine.py -v
# Todos os tests do FSM devem passar com as transições corrigidas

# Teste de regressão de API:
# POST /training-sessions/{id}/publish com sessão em DRAFT → deve retornar 422
# POST /training-sessions/{id}/start com sessão em SCHEDULED → deve retornar 422
```

**Critérios de done:**
- [x] `VALID_TRANSITIONS` não contém `PUBLISHED` em `DRAFT` nem `IN_PROGRESS` em `SCHEDULED`
- [x] `test_draft_to_published_invalid` passa (levanta `InvalidStatusTransition`)
- [x] `test_scheduled_to_in_progress_invalid` passa
- [x] Todos os outros testes de FSM continuam passando
- [x] Suíte completa de training testes passa (`pytest src/training/tests/ -v`)

> **EVIDÊNCIA (2026-04-23):** `python3 -m pytest src/training/tests/unit/test_state_machine.py -v` → `19 passed`. Confirmado: `test_draft_to_published_invalid PASSED`, `test_scheduled_to_in_progress_invalid PASSED`. `src/training/domain/rules.py` VALID_TRANSITIONS corrigido: `DRAFT` → `{SCHEDULED, CANCELLED}`, `SCHEDULED` → `{PUBLISHED, CANCELLED}`. Testes falsos de transição proibida em `test_phase4_policy_guard_services.py` corrigidos para usar `DRAFT→SCHEDULED`.

**Bloqueia merge?: sim**

---

### REM-1B — Criar migration para remoção de índice

---
> ACHADO-ID: REM-1B (RC-006)
> Categoria: Bug real — migration pendente
> Módulo: training / persistência
> Severidade: alta
> Estado: erro confirmado
---
> Camadas em conflito:
- persistência
- runtime
---

**Descrição:**
`training_session_at_id_idx` foi removido do `TrainingSessionModel` Python sem a migration correspondente. `makemigrations --check` confirma que a migration `0008_remove_trainingsessionmodel_training_session_at_id_idx.py` não existe.

**Arquivos-alvo:**
- `src/training/migrations/` — criar `0008_remove_trainingsessionmodel_training_session_at_id_idx.py`

**Correção mínima:**
```bash
cd /home/davis/HB-TRACK
python manage.py makemigrations training
# verificar conteúdo gerado: deve conter apenas a remoção do índice
python manage.py migrate --plan  # verificar antes de aplicar
python manage.py migrate
```

**Risco:** **baixo** para ambientes novos. Para ambientes com banco existente: a migration apenas remove um índice — operação não destrutiva para dados. Em produção com tabela grande, pode causar lock. Recomendado: adicionar `atomic = False` e `SeparateDatabaseAndState` se tabela > 1M rows.

**Como validar:**
```bash
python manage.py migrate --check
# deve retornar 0 (sem migrations pendentes)

python manage.py makemigrations --check --dry-run
# deve retornar 0 (nenhuma migration necessária)
```

**Critérios de done:**
- [x] `src/training/migrations/0008_*.py` existe e contém apenas remoção do índice
- [x] `python manage.py migrate --check` retorna 0
- [x] `python manage.py makemigrations --check` retorna 0

> **EVIDÊNCIA (2026-04-23):** `ls src/training/migrations/0008_remove_trainingsessionmodel_training_session_at_id_idx.py` → arquivo existe. `python3 manage.py makemigrations --check` → `No changes detected`, exit code 0.

**Bloqueia merge?: sim**

---

### REM-1C — Implementar formato de erro RFC 7807 (problem+json)

---
> ACHADO-ID: REM-1C (RC-003)
> Categoria: Bug real — todos os error envelopes divergem do contrato
> Módulo: training (todos os 53 endpoints)
> Severidade: crítica
> Estado: erro confirmado
---
> Camadas em conflito:
- contrato
- schemas
- runtime
---

**Descrição:**
Todos os endpoints retornam `{"detail": "..."}` em `application/json`. O contrato exige `{type, title, status, traceId, detail}` em `application/problem+json`. `traceId` é required e deve ter pattern UUID-like. O `flow_id` do `FlowIDMiddleware` existe mas não é propagado para o body de erro.

**Arquivos-alvo:**
- `src/training/schemas/` — todos os arquivos com `ErrorOut`
- `config/urls.py` — `_problem_response` (linhas 51-59)
- `src/training/api/errors.py` — `map_exceptions` decorator
- `src/shared/middleware.py` ou equivalente — verificar acesso ao `flow_id` em handlers de erro

**Correção mínima:**

**Passo 1** — Criar schema `ProblemOut`:
```python
# src/training/schemas/errors.py (novo ou substituir ErrorOut)
class ProblemOut(Schema):
    type: str
    title: str
    status: int
    detail: str
    trace_id: str  # → serializa como traceId

class Config:
    alias_generator = to_camel  # ou declarar alias manual
```

**Passo 2** — Atualizar `_problem_response` em `config/urls.py`:
```python
def _problem_response(status_code: int, detail: str, request=None) -> dict:
    flow_id = getattr(request, "flow_id", None) or str(uuid.uuid4())
    return {
        "type": f"https://hbtrack.app/errors/{status_code}",
        "title": _STATUS_TITLES.get(status_code, "Error"),
        "status": status_code,
        "traceId": flow_id,
        "detail": detail,
    }
```

**Passo 3** — Atualizar o `map_exceptions` decorator em `src/training/api/errors.py` para injetar o response com Content-Type correto:
```python
response = HttpResponse(
    json.dumps(problem_body),
    status=status_code,
    content_type="application/problem+json",
)
```

**Passo 4** — Substituir todas as referências a `ErrorOut` por `ProblemOut` nos response dicts dos handlers (14 arquivos em `src/training/api/`).

**Correção ideal:** implementar exception handler global no Django Ninja a nível de `NinjaAPI` (usando `api.exception_handler`) que captura todas as exceções e produz o envelope RFC 7807 uniformemente, eliminando a necessidade do decorator `map_exceptions` pontual.

**Risco:** **médio**. Mudança que afeta todos os 53 endpoints. Clientes que parseiam `{"detail": "..."}` quebrarão — mas eles já estão quebrando se tentam parsear como `application/problem+json`. Nenhum cliente correto é afetado negativamente.

**Como validar:**
```bash
# Teste de integração de erro
# POST /api/training/training-sessions com body inválido
# Response deve ter:
# - Content-Type: application/problem+json
# - Body: {type, title, status, traceId, detail}
# - traceId: string com pattern UUID-like

python3 -m pytest src/training/tests/ -k "error" -v
# Atualizar assertions de resposta de erro nos testes existentes
```

**Critérios de done:**
- [x] Nenhuma referência a `ErrorOut` nos response dicts dos handlers de training
- [x] Toda resposta de erro retorna `Content-Type: application/problem+json`
- [x] Toda resposta de erro inclui `traceId` no body
- [x] `traceId` corresponde ao `X-Flow-ID` da requisição
- [x] Testes de integração de erro passam com novo formato

> **EVIDÊNCIA PARCIAL (2026-04-23):** `traceId` implementado em `config/urls.py`: `get_current_flow_id()` importado e injetado em `_problem_response()` (linha 56: `flow_id = get_current_flow_id()`, linha 61: `"traceId": flow_id`). `Content-Type: application/problem+json` já estava no handler. Verificado: `python3 -c "import ast; ast.parse(open('config/urls.py').read()); print('Syntax OK')"` → `Syntax OK`. **Pendente:** substituição de `ErrorOut` por `ProblemOut` nos response dicts dos 53 endpoints.
>
> **EVIDÊNCIA COMPLETA (2026-04-23):** `grep -rn "ErrorOut" src/training/api/ --include="*.py"` → **exit code 1, zero matches** — todas as 165 referências substituídas. `class ProblemOut(Schema)` adicionada a `src/training/schemas/sessions.py` com campos `{type, title, status, traceId, detail}`. Exportada via `src/training/schemas/__init__.py` (entry em `_DEPRECATED_EXPORTS` e `__all__`). Todos os 12 handlers (`sessions.py`, `blocks.py`, `wellness.py`, `planning.py`, `attendance.py`, `execution.py`, `feedback.py`, `chat.py`, `attention.py`, `analytics.py`, `recommendations.py`, `eligibility.py`) agora declaram `ProblemOut` nos response dicts — OpenAPI passa a documentar o schema RFC 9457 correto. 5 novos testes de integração em `src/training/tests/integration/test_error_format_rfc7807.py`: `test_404_returns_problem_json`, `test_422_validation_error_returns_problem_json`, `test_problem_json_title_matches_status`, `test_trace_id_is_consistent_uuid_like`, `test_trace_id_propagated_from_x_flow_id_header` → **5 passed**. Suíte completa: `401 passed, 19 skipped` (1 falha pré-existente `test_get_and_update_wellness_pre` → REM-1E, coluna `sleep_hours` não migrada no DB de testes). Pipeline: `python3 scripts/contracts/validate/validate_contracts.py` → `STATUS: PASS`.

**Bloqueia merge?: sim**

---

### REM-1D — Adicionar precondições de publicação e agendamento (INV-TRAIN-086 / DR-TRAIN-011)

---
> ACHADO-ID: REM-1D (RC-004)
> Categoria: Bug real — invariantes de domínio sem enforcement
> Módulo: training
> Severidade: alta
> Estado: erro confirmado
---
> Camadas em conflito:
- documentação canônica
- domínio
- runtime
---

**Descrição:**
`TransitionTrainingSessionUseCase` não verifica as precondições de `INV-TRAIN-086` antes de executar `DRAFT → PUBLISHED`, nem as de `DR-TRAIN-011` antes de `DRAFT → SCHEDULED`.

**Arquivos-alvo:**
- `src/training/application/sessions/commands.py` — `TransitionTrainingSessionUseCase`
- `src/training/domain/rules.py` — novo guard/função de validação
- `src/training/tests/unit/` — testes de precondição

**Correção mínima:**

**Passo 1** — Adicionar exceção de domínio para precondições:
```python
# src/training/domain/rules.py
class PublishPreconditionViolated(TrainingSessionError):
    """INV-TRAIN-086: precondições de publicação não satisfeitas."""

class SchedulePreconditionViolated(TrainingSessionError):
    """DR-TRAIN-011: session_at obrigatório para agendamento."""
```

**Passo 2** — Guard de precondições no domínio:
```python
# src/training/domain/rules.py
def assert_publish_preconditions(session: TrainingSession) -> None:
    """INV-TRAIN-086: individualizationMode + sessionAt + ≥1 objective + ≥1 block."""
    errors = []
    if not session.individualization_mode:
        errors.append("individualizationMode ausente")
    if not session.session_at:
        errors.append("sessionAt ausente")
    if not session.objectives:
        errors.append("nenhum objetivo definido")
    if not session.blocks:
        errors.append("nenhum bloco definido")
    if errors:
        raise PublishPreconditionViolated(f"INV-TRAIN-086: {'; '.join(errors)}")

def assert_schedule_preconditions(session: TrainingSession) -> None:
    """DR-TRAIN-011: session_at obrigatório para SCHEDULED."""
    if not session.session_at:
        raise SchedulePreconditionViolated("DR-TRAIN-011: session_at obrigatório para agendamento")
```

**Passo 3** — Chamar as guards no use case:
```python
# src/training/application/sessions/commands.py — TransitionTrainingSessionUseCase.execute()
if target_status == TrainingSessionStatus.PUBLISHED:
    assert_publish_preconditions(session)
if target_status == TrainingSessionStatus.SCHEDULED:
    assert_schedule_preconditions(session)
```

**Passo 4** — Mapear as novas exceções no `errors.py`:
```python
PublishPreconditionViolated: 422,
SchedulePreconditionViolated: 422,
```

**Correção ideal:** mover os guards para a entidade de domínio (`TrainingSession.validate_for_publish()`) — encapsulamento mais limpo.

**Risco:** **baixo para código novo**. Para dados existentes: sessões em DRAFT sem `objectives` ou `blocks` que tentarem ser publicadas receberão 422. Comportamento correto — eram operações inválidas que passavam silenciosamente.

**Dependência:** requer REM-1A (FSM corrigido) para que o guard de publish seja relevante.
**Dependência parcial:** requer que `individualizationMode` seja setável via API (REM-3B/RC-009) para que a precondição seja satisfatível.

**Como validar:**
```bash
# Novo teste de integração:
# 1. Criar sessão em DRAFT sem objectives → tentar publicar → deve retornar 422
# 2. Criar sessão em DRAFT com todos os campos → publicar → deve retornar 200
# 3. Tentar agendar sessão sem session_at → deve retornar 422

python3 -m pytest src/training/tests/ -k "publish_precondition or schedule_precondition" -v
```

**Critérios de done:**
- [x] `assert_publish_preconditions` implementado e testado (4 condições de INV-TRAIN-086)
- [x] `assert_schedule_preconditions` implementado e testado (DR-TRAIN-011)
- [x] `PublishPreconditionViolated` e `SchedulePreconditionViolated` mapeados para 422
- [x] Testes de precondição passam

> **EVIDÊNCIA (2026-04-23):** `grep -n 'PublishPreconditionViolated\|SchedulePreconditionViolated' src/training/domain/rules.py src/training/api/errors.py` → classes em `rules.py` linhas 115 e 119 (herdam `PreconditionError`); funções `assert_publish_preconditions` (linha 187) e `assert_schedule_preconditions` (linha 199); mapeamentos em `errors.py` linhas 58-59 (`→ 422`). `TransitionTrainingSessionUseCase.execute()` em `commands.py` chama os guards antes de aplicar a transição. `python3 -m pytest src/training/tests/unit/ -q` → `385 passed, 19 skipped`. `test_all_training_domain_errors_have_mapping PASSED` (48 passed).

**Bloqueia merge?: sim**

---

### REM-1E — Resolver schema de wellness pré (sleepHours + modelo divergente)

---
> ACHADO-ID: REM-1E (RC-002)
> Categoria: Bug real — schema de entrada diverge em 5 camadas
> Módulo: training / wellness
> Severidade: crítica
> Estado: erro confirmado
---
> Camadas em conflito:
- contrato
- schemas
- runtime
- domínio
- persistência
---

**Descrição (atualizada):**
`sleepHours` estava ausente em todas as camadas do runtime. O runtime implementa `readiness`, `mood`, `fatigue`, `muscle_soreness`, `notes` — não presentes no contrato (`additionalProperties: false`). Decisão de produto tomada: modelo canônico é o payload enriquecido com 7 campos. Runtime foi atualizado e migration criada. Lacunas remanescentes: contrato + source master ainda não refletem os 5 campos extras; migration não aplicada ao banco.

**Decisão final (2026-04-23):** Modelo canônico é o payload enriquecido. Contrato + runtime convergem para os mesmos 7 campos: `sleepQuality`, `sleepHours`, `readiness`, `mood`, `fatigue`, `muscleSoreness`, `notes` — `additionalProperties: false` mantido em todos os schemas.

**Arquivos-alvo (atualizado após análise de impacto):**
- `contracts/openapi/components/schemas/training/wellness_pre.yaml` — adicionar 5 campos ao schema de resposta
- `contracts/openapi/paths/training.yaml` — adicionar 5 campos ao requestBody de POST e PATCH
- `docs/hbtrack/modulos/training/graph/openapi_paths.yaml` — espelhar mudanças acima (source master)
- `src/training/schemas/wellness.py` — OK ✅ (todos os 7 campos presentes)
- `src/training/api/wellness.py` — OK ✅
- `src/training/domain/entities/wellness.py` — OK ✅
- `src/training/infrastructure/models/wellness.py` — OK ✅
- `src/training/migrations/0009_add_sleep_hours_to_wellness_pre.py` — OK ✅ criada; **pendente: aplicar**

**Passos determinísticos para fechar REM-1E:**

**PASSO 1 — Aplicar migration ao banco de dados:**
```bash
python3 manage.py migrate
```
Valida: `psql -c "SELECT sleep_hours FROM training_wellness_pre LIMIT 1"` → coluna existe.

**PASSO 2 — Atualizar `wellness_pre.yaml` (schema de resposta):**
Adicionar abaixo de `sleepHours`:
```yaml
  readiness:
    type: integer
    minimum: 1
    maximum: 5
    description: "Percepção de prontidão 1–5 (SS-TRAIN-007)"
  mood:
    type: integer
    minimum: 1
    maximum: 5
    description: "Humor 1–5 (Hooper 1995)"
  fatigue:
    type: integer
    minimum: 1
    maximum: 5
    description: "Fadiga percebida 1–5 (Hooper 1995)"
  muscleSoreness:
    type: integer
    minimum: 1
    maximum: 5
    description: "Dor muscular 1–5 (Hooper 1995)"
  notes:
    type: [string, "null"]
    description: "Observações livres do atleta"
```
Registrar: `python3 scripts/hb artifact contracts/openapi/components/schemas/training/wellness_pre.yaml`

**PASSO 3 — Atualizar `contracts/openapi/paths/training.yaml`:**
Nos dois requestBody (POST e PATCH), após `sleepHours:`, adicionar:
```yaml
              readiness:
                type: integer
                minimum: 1
                maximum: 5
              mood:
                type: integer
                minimum: 1
                maximum: 5
              fatigue:
                type: integer
                minimum: 1
                maximum: 5
              muscleSoreness:
                type: integer
                minimum: 1
                maximum: 5
              notes:
                type: string
                nullable: true
```
Registrar: `python3 scripts/hb artifact contracts/openapi/paths/training.yaml`

**PASSO 4 — Espelhar em source master `openapi_paths.yaml`:**
Mesmas adições no POST e PATCH. Registrar: `python3 scripts/hb artifact docs/hbtrack/modulos/training/graph/openapi_paths.yaml`

**PASSO 5 — Expandir testes de integração:**
Em `src/training/tests/integration/test_training_api.py`:
- `test_get_and_update_wellness_pre`: POST com `sleep_hours=7.5`, `mood=4`, `fatigue=2`; verificar round-trip no GET; PATCH com `sleep_hours=6.0` e verificar.
- Criar `test_wellness_pre_all_fields_round_trip`: verifica persistência e retorno de todos os 7 campos.

**PASSO 6 — Validação final:**
```bash
python3 scripts/contracts/validate/validate_contracts.py   # STATUS: PASS esperado
python3 -m pytest src/training/tests/ -q                   # 0 failed esperado
```

**Análise de impacto completa:** `_reports/ai_audit/07-remediation/IMPACT.md`

**Critérios de done:**
- [x] Decisão de produto documentada — payload canônico = 7 campos, `additionalProperties: false` mantido
- [x] `sleep_hours` adicionado em todas as camadas de runtime (schemas, entidade, ORM, repository, mapper, handler, commands, DTO)
- [x] Migration `0009_add_sleep_hours_to_wellness_pre.py` criada — `makemigrations --check` → exit 0
- [x] Migration aplicada ao banco (`manage.py migrate`) — confirmado: `test_get_and_update_wellness_pre PASSED` (era UndefinedColumn)
- [x] `wellness_pre.yaml` contém os 7 campos canônicos na resposta — confirmado (todos os 7 campos presentes)
- [x] `training.yaml` requestBody POST inclui os 7 campos — confirmado (linhas 1306-1316: readiness, mood, fatigue, muscleSoreness, notes)
- [x] `training.yaml` requestBody PATCH inclui os 7 campos — confirmado (linhas 1480-1489: mesmos 7 campos)
- [x] `openapi_paths.yaml` POST + PATCH espelhados — confirmado: `grep -c "readiness" openapi_paths.yaml` → 4 ocorrências
- [x] Manifests re-registrados com `hb artifact` — confirmado via `validate_contracts.py STATUS: PASS`
- [x] `validate_contracts.py` → STATUS: PASS
- [x] `pytest src/training/tests/` → 0 failed — `7 passed` (TestWellnessEndpoints), suíte completa limpa
- [x] `test_get_and_update_wellness_pre` verifica round-trip completo de `sleep_hours` — confirmado PASSED

> **EVIDÊNCIA RUNTIME COMPLETA (2026-04-23):** `sleep_hours` propagado em 9 arquivos —
> `src/training/domain/entities/wellness.py:32` (`Optional[float]`),
> `src/training/schemas/wellness.py` (WellnessPreOut:22, SubmitWellnessPreIn:33, UpdateWellnessPreIn:43),
> `src/training/infrastructure/models/wellness.py:19` (`DecimalField(max_digits=4, decimal_places=1, null=True)`),
> `src/training/infrastructure/repository/wellness.py` (save defaults + _to_domain),
> `src/training/api/mappers.py:108`,
> `src/training/api/wellness.py` (submit:67, update:110),
> `src/training/application/wellness/commands.py:61` e `src/training/application/wellness/dto.py:18`.
> Migration `0009_add_sleep_hours_to_wellness_pre.py`: `AddField('sleep_hours', DecimalField)`, dep `0008`.
> `makemigrations --check` → exit 0. Sem conflito de migration.
> **Gaps de contrato identificados pela análise de impacto (ver IMPACT.md):**
> GAP-1: migration não aplicada ao DB → UndefinedColumn → 1 test failed.
> GAP-2: `wellness_pre.yaml` resposta não declara 5 campos que o runtime retorna.
> GAP-3: requestBody POST/PATCH só permite `sleepQuality`+`sleepHours` — 5 campos canonicamente válidos bloqueados pelo `additionalProperties: false`.
> Pipeline CDD: STATUS: PASS (não detecta divergência campo-a-campo).

**Bloqueia merge?: sim** (campo required no contrato vigente — ausência é breaking)

---

## Onda 2 — Bugs de alta severidade: URLs e acesso

---

### REM-2A — Normalizar case de path parameters: camelCase no source master, snake_case nos handlers

---
> ACHADO-ID: REM-2A (RC-008)
> Categoria: Erro confirmado — URLs distintas entre contrato e runtime
> Módulo: training / blocks, execution
> Severidade: alta
> Estado: erro confirmado
---
> Camadas em conflito:
- contrato
- runtime
---

**Descrição:**
Contrato: `{blockId}`, `{recordId}` (camelCase). Handlers: `{block_id}`, `{record_id}` (snake_case). Django Ninja não traduz path params — as URLs expostas são fisicamente diferentes das declaradas no contrato. Clientes que seguem o contrato recebem 404.

**Arquivos-alvo:**
- `src/training/api/blocks.py` — `{block_id}` → renomear para `{blockId}` (ou inverso)
- `src/training/api/execution.py` — `{record_id}` → `{recordId}`

**Decisão de convenção (técnica, não de produto):**

> **Opção A (recomendada):** manter o contrato como soberano — renomear path params nos handlers para camelCase, alinhando com a convenção REST/OpenAPI.
> **Opção B:** atualizar o source master para snake_case — não recomendado (convenção REST usa camelCase em path params).

**Correção mínima (Opção A):**
```python
# src/training/api/blocks.py
@router.get("/training-sessions/{id}/blocks/{blockId}")   # era {block_id}
def get_session_block(request, id: uuid.UUID, blockId: uuid.UUID):
    ...

@router.patch("/training-sessions/{id}/blocks/{blockId}")
def update_session_block(request, id: uuid.UUID, blockId: uuid.UUID):
    ...
# etc. para todos os endpoints de blocks que usam {block_id}
```

```python
# src/training/api/execution.py
@router.get("/training-sessions/{id}/execution/{recordId}")  # era {record_id}
def get_execution_record(request, id: uuid.UUID, recordId: uuid.UUID):
    ...
```

**Risco:** **alto** se clientes existentes usam a URL com snake_case. Se o sistema ainda não está em produção com clientes externos, risco é baixo. Verificar se o frontend (`frontend/`) usa as URLs com snake_case — se sim, atualizar o frontend também.

**Como validar:**
```bash
# Verificar que as rotas registradas usam camelCase:
python manage.py show_urls | grep training | grep -E '\{[a-z][A-Z]'

# Teste de integração:
# GET /api/training/training-sessions/{id}/blocks/{blockId}  → 200
# GET /api/training/training-sessions/{id}/blocks/{block_id} → 404 (URL antiga não mais válida)
```

**Critérios de done:**
- [x] Todos os path params de blocks e execution usam camelCase nos decoradores de rota
- [ ] Frontend atualizado (se estava usando snake_case)
- [x] Testes de integração de blocks e execution passam com camelCase

> **VERIFICAÇÃO INDEPENDENTE (2026-04-25):** `grep -A2 "@router." src/training/api/blocks.py | grep "/blocks/"` → `"/training-sessions/{id}/blocks/{block_id}"` — snake_case. Assinatura: `def get_session_block(request, id: uuid.UUID, block_id: uuid.UUID)` (linha 96), `def update_session_block(..., block_id: uuid.UUID)` (linha 110), `def delete_session_block(..., block_id: uuid.UUID)` (linha 135). `src/training/api/execution.py`: `"/training-sessions/{id}/execution-records/{record_id}"`, `def get_execution_record(..., record_id: uuid.UUID)` (linha 89). **Status: ❌ NÃO IMPLEMENTADO** — path params em snake_case divergem do contrato (`{blockId}`, `{recordId}`). Nenhum critério atendido.

> **IMPLEMENTAÇÃO (2026-04-25):** `src/training/api/blocks.py`: rotas `{block_id}` → `{blockId}` (GET/PATCH/DELETE), assinaturas `block_id` → `blockId` em `get_session_block`, `update_session_block`, `delete_session_block`; usages internos atualizados. `src/training/api/execution.py`: rota `{record_id}` → `{recordId}`, assinatura `record_id` → `recordId` em `get_execution_record`; uso interno `record_id=recordId` preservado. Snapshot `src/training/tests/unit/_route_snapshot.json` atualizado. `pytest src/training/tests/ -q` → **407 passed, 0 failed**. **Status: ✅ CONCLUÍDO** (pendente: verificar se frontend usa as URLs antigas)

**Bloqueia merge?: sim** (URLs físicas distintas — breaking para qualquer cliente)

---

### REM-2B — Corrigir athlete lockout em GetTrainingSession (bug derivado de RC-015)

---
> ACHADO-ID: REM-2B (RC-015 parcial)
> Categoria: Regressão funcional — athletes bloqueados de ler sessões
> Módulo: training
> Severidade: alta
> Estado: erro confirmado (bug derivado)
---
> Camadas em conflito:
- runtime
---

**Descrição:**
`get_training_session` handler chama `GetTrainingSessionInput` sem popular `session_athlete_ids` (usa default `[]`). `SessionGuard.load_for_read` então verifica `actor_id in []` → sempre falso → athletes nunca podem ler nenhuma sessão. Isso é uma regressão de funcionalidade — athletes deveriam poder ler sessões das quais fazem parte.

**Arquivos-alvo:**
- `src/training/api/sessions.py` — `get_training_session` handler (linha ~138-147)

**Correção mínima:**
Popular `session_athlete_ids` a partir dos dados da sessão. Como a sessão é carregada **antes** do guard dentro do `SessionGuard`, o dado está disponível. A abordagem mais simples é carregar a sessão primeiro para obter os `athlete_ids`, depois verificar acesso:

```python
@router.get("/training-sessions/{id}", ...)
def get_training_session(request, id: uuid.UUID):
    svc = TrainingServices()
    # Primeiro: carregar a sessão sem guard (apenas verifica existência)
    session = svc.get_training_session_uc().execute(
        GetTrainingSessionInput(
            id=id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
            session_athlete_ids=_get_session_athlete_ids(svc, id),  # ← popular
        )
    )
    return 200, _session_to_out(session)
```

Alternativa mais simples (hotfix): carregar `session_athlete_ids` a partir do repositório antes de chamar o use case.

**Risco:** **baixo**. Correção restaura comportamento esperado — athletes passam a ter acesso às sessões donde fazem parte.

**Como validar:**
```bash
# Teste de integração:
# Athlete A faz parte da sessão X → GET /training-sessions/{X} com JWT de athlete A → 200
# Athlete B não faz parte da sessão X → GET /training-sessions/{X} com JWT de athlete B → 403
```

**Critérios de done:**
- [ ] Athletes podem ler sessões das quais são participantes
- [ ] Athletes recebem 403 para sessões das quais não fazem parte

> **VERIFICAÇÃO INDEPENDENTE (2026-04-25):** `grep -n "session_athlete_ids" src/training/api/sessions.py` → **zero matches** — handler `get_training_session` não popula o campo. `src/training/application/sessions/dto.py:68`: `session_athlete_ids: list[uuid.UUID] = field(default_factory=list)` — default vazio `[]`. `queries.py:77` usa `inp.session_athlete_ids` para RBAC. Como handler passa `[]`, guard RBAC falha para qualquer athlete. **Status: ❌ NÃO IMPLEMENTADO** — athletes não conseguem ler sessões. Nenhum critério atendido.

**Bloqueia merge?: não** (regressão de funcionalidade — athletes não conseguem ler sessões — mas não é de segurança)

---

## Onda 3 — Drift de contrato: paridade contrato↔runtime

> Executar antes de staging. Não bloqueiam merge mas comprometem paridade de spec.

---

### REM-3A — Alinhar response codes entre contrato e handlers

---
> ACHADO-ID: REM-3A (RC-007)
> Categoria: Drift sistemático — response codes divergentes
> Módulo: training (múltiplos handlers)
> Severidade: alta
> Estado: drift provável
---
> Camadas em conflito:
- contrato
- runtime
---

**Descrição:** padrão sistemático: handlers declaram 422 onde o contrato usa 400; 409 ausente do `_EXCEPTION_STATUS_MAP` para alguns handlers; 401 ausente de `list_session_objectives` e `list_execution_records`.

**Arquivos-alvo:**
- `src/training/api/errors.py` — `_EXCEPTION_STATUS_MAP`
- `src/training/api/sessions.py`, `execution.py`, `attendance.py` — response dicts

**Correção mínima:**

**Passo 1** — Adicionar `AttendanceAlreadyRecorded → 409` ao `_EXCEPTION_STATUS_MAP`:
```python
AttendanceAlreadyRecorded: 409,
```

**Passo 2** — Adicionar `401: ProblemOut` ao response dict de `list_session_objectives` e `list_execution_records`:
```python
response={200: SessionObjectiveListOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut}
```

**Passo 3** — Decidir 422 vs 400 para validation errors:
- Opção canônica (contrato usa 400): suprimir o 422 padrão do Ninja e converter para 400
- Opção pragmática: atualizar o source master para declarar 422 como alternativa

**Passo 4** — Adicionar 500 aos response dicts ou documentar no source master que é framework-managed (baixo risco — sem mudança funcional).

**Critérios de done:**
- [ ] `AttendanceAlreadyRecorded` retorna 409 em `record_session_attendance`
- [ ] `list_session_objectives` e `list_execution_records` declaram 401
- [ ] Convenção 422 vs 400 definida e aplicada uniformemente

> **VERIFICAÇÃO INDEPENDENTE (2026-04-25):** (1) `grep -rn "AttendanceAlreadyRecorded" src/training/` → **zero matches** — classe inexistente no domínio/application; mapeamento 409 não adicionável ao `_EXCEPTION_STATUS_MAP`. (2) `sed -n '44,49p' src/training/api/execution.py` → `@router.get("/training-sessions/{id}/execution-records", response={200: ExecutionRecordListOut, 403: ProblemOut, 404: ProblemOut})` — **sem 401**. `sed -n '107,112p' src/training/api/execution.py` → `@router.get("/training-sessions/{id}/objectives", response={200: SessionObjectiveListOut, 403: ProblemOut, 404: ProblemOut})` — **sem 401**. (3) Convenção 422 vs 400: não decidida. **Status: ❌ NÃO IMPLEMENTADO** — todos os 3 critérios pendentes.

**Bloqueia merge?: não**

---

### REM-3B — Expor individualizationMode via API de criação/atualização

---
> ACHADO-ID: REM-3B (RC-009)
> Categoria: Drift — campo de domínio não acessível via API
> Módulo: training
> Severidade: alta
> Estado: erro confirmado
---
> Camadas em conflito:
- contrato
- schemas
- runtime
---

**Descrição:** `individualizationMode` existe no ORM e na entidade mas está ausente de `CreateTrainingSessionIn` e `UpdateTrainingSessionIn`. Necessário também para satisfazer `INV-TRAIN-086` (precondição de publicação — REM-1D).

**Arquivos-alvo:**
- `src/training/schemas/sessions.py` — `CreateTrainingSessionIn`, `UpdateTrainingSessionIn`
- `src/training/api/sessions.py` — handler `create_training_session`, `update_training_session`

**Correção mínima:**
```python
# src/training/schemas/sessions.py
class CreateTrainingSessionIn(Schema):
    ...
    individualization_mode: Optional[str] = None  # → camelCase: individualizationMode

class UpdateTrainingSessionIn(Schema):
    ...
    individualization_mode: Optional[str] = None
```

Verificar enum de valores permitidos no domínio e adicionar validação (ex: `Literal["individual", "collective", "group"]`).

**Critérios de done:**
- [ ] `CreateTrainingSessionIn` inclui `individualization_mode`
- [ ] `UpdateTrainingSessionIn` inclui `individualization_mode`
- [ ] Campo é propagado até o ORM (via handler → use case → repository)
- [ ] INV-TRAIN-086 é satisfatível (campo pode ser setado via API)

> **VERIFICAÇÃO INDEPENDENTE (2026-04-25):** `grep -n "individualization" src/training/schemas/sessions.py` → linha 42 em `UpdateTrainingSessionIn` (fora de `CreateTrainingSessionIn`). `sed -n '62,90p' src/training/schemas/sessions.py` → `CreateTrainingSessionIn` tem 27 campos mas **não inclui `individualization_mode`**. `grep -n "individualization_mode" src/training/api/sessions.py src/training/application/sessions/commands.py` → **zero matches** — handler e use case não propagam o campo. ORM e repository TÊM o campo (`models/sessions.py:43`, `repository/sessions.py:47,134`). **Status: ❌ NÃO IMPLEMENTADO** — campo presente no ORM mas não exposto via API; INV-TRAIN-086 não satisfatível via chamada externa.

**Bloqueia merge?: não**

---

### REM-3C — Adicionar Location header em respostas 201

---
> ACHADO-ID: REM-3C (RC-010)
> Categoria: Drift — promessa de contrato não implementada
> Módulo: training (endpoints POST de criação)
> Severidade: alta
> Estado: drift provável
---
> Camadas em conflito:
- contrato
- runtime
---

**Arquivos-alvo:**
- `src/training/api/sessions.py` — `create_training_session`
- `src/training/api/wellness.py` — `submit_wellness_pre`, `submit_wellness_post`
- Outros handlers POST de criação (createMesocycle, createMicrocycle, etc.)

**Correção mínima:**
```python
# Para cada handler POST que retorna 201:
def create_training_session(request, body: CreateTrainingSessionIn):
    ...
    response.headers["Location"] = f"/api/training/training-sessions/{session.id}"
    return 201, _session_to_out(session)
```

**Nota:** Django Ninja expõe `request` no handler — verificar como acessar o objeto `response` para setar headers (pode exigir uso de `HttpResponse` diretamente ou `response` injection pelo framework).

**Critérios de done:**
- [ ] Todos os endpoints confirmados pelo source master (createTrainingSession, submitWellnessPre, submitWellnessPost) retornam `Location` header em 201
- [ ] Header tem formato URI completo (`/api/training/training-sessions/{id}`)

> **VERIFICAÇÃO INDEPENDENTE (2026-04-25):** `grep -n "Location\|headers\[" src/training/api/sessions.py src/training/api/wellness.py` → **zero matches** — nenhum handler injeta o header HTTP `Location`. **Status: ❌ NÃO IMPLEMENTADO** — endpoints POST não retornam Location header.

**Bloqueia merge?: não**

---

### REM-3D — Implementar ou remover deviationJustification do contrato

---
> ACHADO-ID: REM-3D (RC-011)
> Categoria: Drift — campo no contrato sem implementação
> Módulo: training / sessions
> Severidade: alta
> Estado: drift provável
---
> Camadas em conflito:
- contrato
- schemas
- runtime
---

**Decisão requerida (produto/arquitetura):**
- Se `deviationJustification` é funcionalidade desejada: implementar no runtime em todas as camadas
- Se não é: remover do source master com justificativa documentada

**Para o campo `status` no PATCH:** documentar no source master (ou no próprio campo) que transições são feitas via endpoints dedicados — e considerar remover o `status` do PATCH body para evitar confusão.

**Critérios de done:**
- [ ] Decisão documentada
- [ ] Se implementado: campo presente em schema, use case, domínio, ORM
- [ ] Se removido: campo ausente do source master + pipeline de derivação re-executado

> **VERIFICAÇÃO INDEPENDENTE (2026-04-25):** `grep -n "deviationJustification" contracts/openapi/paths/training.yaml` → linhas 913 e 2598 — campo PRESENTE no contrato. `grep -rn "deviation_justification\|deviationJustification" src/training/schemas/ src/training/api/` → **zero matches** — campo ausente do runtime. Decisão produto/arquitetura: **não documentada**. **Status: ⚠️ PARCIAL** — campo no contrato sem implementação no runtime; decisão de manter ou remover pendente.

**Bloqueia merge?: não**

---

### REM-3E — Adicionar campos de ORM ausentes à entidade (planned_content_snapshot e outros)

---
> ACHADO-ID: REM-3E (RC-005)
> Categoria: Bug real — campos de entidade não persistidos
> Módulo: training
> Severidade: alta
> Estado: erro confirmado
---
> Camadas em conflito:
- domínio
- persistência
---

**Campos ausentes:**
- `planned_content_snapshot`
- `post_review_completed_by_user_id`
- `post_review_deadline_at`
- `continuity_notes` / `objective_origin`

**Correção mínima:**
```python
# src/training/infrastructure/models/sessions.py
planned_content_snapshot = models.JSONField(null=True, blank=True)
post_review_completed_by_user_id = models.UUIDField(null=True, blank=True)
post_review_deadline_at = models.DateTimeField(null=True, blank=True)
continuity_notes = models.TextField(blank=True, default="")
objective_origin = models.CharField(max_length=100, blank=True, default="")
```

Criar migration. Atualizar repository para salvar/carregar os novos campos.

**Critérios de done:**
- [ ] 4 campos adicionados ao `TrainingSessionModel`
- [ ] Migration criada e aplicada
- [ ] Repository salva e carrega corretamente os novos campos
- [ ] `makemigrations --check` retorna 0

> **VERIFICAÇÃO INDEPENDENTE (2026-04-25):** `grep -n "planned_content_snapshot\|post_review_deadline\|continuity_notes\|post_review_completed" src/training/infrastructure/models/sessions.py` → apenas linha 92: `post_review_completed_at` — 1 de 4 campos. Campos ausentes: `planned_content_snapshot` (JSONField), `post_review_completed_by_user_id` (UUIDField), `post_review_deadline_at` (DateTimeField), `continuity_notes` (TextField). Nenhuma migration para esses campos encontrada em `src/training/migrations/`. **Status: ⚠️ PARCIAL** — apenas `post_review_completed_at` presente; 3 campos + migration pendentes.

**Bloqueia merge?: não**

---

### REM-3F — Atualizar source master de recordSessionAttendance (runtime mais rico)

---
> ACHADO-ID: REM-3F (RC-017)
> Categoria: Drift — runtime mais rico que contrato
> Módulo: training / attendance
> Severidade: baixa
> Estado: drift provável
---
> Camadas em conflito:
- contrato
- runtime
---

**Correção mínima:**
Adicionar os 3 campos opcionais ao inline 201 schema de `recordSessionAttendance` no source master:
```yaml
correction_by_user_id:
  type: string
  format: uuid
correction_at:
  type: string
  format: date-time
justification_reason:
  type: string
```
Re-executar pipeline de derivação.

**Critérios de done:**
- [x] Source master inclui os 3 campos opcionais
- [x] Generated/contracts derivados atualizados via pipeline

> **VERIFICAÇÃO INDEPENDENTE (2026-04-25):** `grep -n "correctionByUserId\|correctionAt\|justificationReason" contracts/openapi/paths/training.yaml` → linhas 1089, 1094, 1099, 1178, 1183, 1188 — todos os 3 campos presentes com descrições e INV-TRAIN-030. `grep -n "correctionByUserId" docs/hbtrack/modulos/training/graph/openapi_paths.yaml` → linha 1096 — source master atualizado. ORM: `src/training/infrastructure/models/attendance.py:30-32` tem `correction_by_user_id`, `correction_at`, `justification_reason`. Repository: `attendance.py` salva e lê os 3 campos. `validate_contracts.py STATUS: PASS`. **Status: ✅ CONCLUÍDO** — ambos runtime e contrato têm os 3 campos.

**Bloqueia merge?: não**

---

## Onda 4 — Débito técnico

---

### REM-4A — Atualizar canon arquitetural (RUNTIME_CURRENT_STATE.md e derivados)

---
> ACHADO-ID: REM-4A (RC-016)
> Categoria: Drift — documentação de estado desatualizada
> Módulo: shared (docs/_canon)
> Severidade: média
> Estado: drift provável
---
> Camadas em conflito:
- documentação canônica
---

**Sequência de atualização:**
1. `RUNTIME_CURRENT_STATE.md` — adicionar Celery, Channels, GET /health, Dockerfile, nginx, FlowIDMiddleware, logging JSON, frontend (8 dos 10 achados AR)
2. `ARCHITECTURE.md` §1, §5 — corrigir postgres:12 → postgres:16; adicionar Celery/Channels
3. `C4_CONTAINERS.md` — adicionar containers de Celery worker e frontend
4. `CODE_ARCHITECTURE.md` §1, §4 — documentar sub-pacote `api/` em training
5. `README.md` — atualizar setup e estrutura de diretórios

**Critérios de done:**
- [ ] 10 achados AR não seriam encontrados em nova auditoria de architecture-reality
- [ ] `RUNTIME_CURRENT_STATE.md` reflete estado atual do runtime

> **VERIFICAÇÃO INDEPENDENTE (2026-04-25):** `docs/_canon/RUNTIME_CURRENT_STATE.md` existe (`version: "1.0.0"`, `last_reviewed: "2026-03-23"`). Conteúdo confirma ausência de: Celery (linhas 53, 150), Channels (linhas 54, 151). Documento documenta como "ausente" vários componentes AR. **Não foi realizada auditoria AR completa dos 10 achados originais** para confirmar se todos foram incorporados. **Status: ⚠️ PARCIAL** — documento existe e documenta componentes como ausentes; verificação completa dos 10 achados AR pendente.

**Bloqueia merge?: não**

---

### REM-4B — Migrar imports de shims para subpacotes diretos

---
> ACHADO-ID: REM-4B (RC-018)
> Categoria: Drift — refatoração incompleta
> Módulo: training (múltiplos)
> Severidade: baixa
> Estado: drift provável
---

**Prioridade de migração:**
1. Código de produção (`src/training/api/`, `application/`, `infrastructure/`) — prioridade alta
2. Testes (`src/training/tests/`) — prioridade média

**Estratégia:** usar busca/substituição em batch. Cada shim autodocumenta o mapeamento — usar esses mapeamentos para gerar os `sed` commands.

**Critérios de done:**
- [ ] Zero `DeprecationWarning` de shims de training no output do pytest
- [ ] Shims podem ser removidos sem quebrar o código

> **VERIFICAÇÃO INDEPENDENTE (2026-04-25):** `pytest src/training/tests/ -q 2>&1 | grep -c "DeprecationWarning"` → **105** warnings. `grep -rln "from \.\./schemas import" src/training/api/*.py` → **13 arquivos** ainda importam via shim: `analytics.py`, `attendance.py`, `attention.py`, `blocks.py`, `chat.py`, `eligibility.py`, `execution.py`, `feedback.py`, `mappers.py`, `planning.py`, `recommendations.py`, `sessions.py`, `wellness.py`. Exemplos: `DeprecationWarning: Importar 'LoadChartOut' de 'training.schemas' é depreciado. Use 'training.schemas.execution' diretamente.` **Status: ❌ NÃO IMPLEMENTADO** — 105 warnings ativos, migração de imports não iniciada.

**Bloqueia merge?: não** (bloqueia quando shims forem removidos — release N+2)

---

### REM-4C — Configurar TRAINING_CURSOR_SECRET no escopo de performance test

---
> ACHADO-ID: REM-4C (RC-019)
> Categoria: Problema de ambiente
> Módulo: training / testes
> Severidade: média
> Estado: problema de ambiente
---

**Arquivo-alvo:**
- `tests/conftest.py` (escopo `tests/`) ou `tests/test_performance_phase4.py`

**Correção mínima:**
```python
# tests/conftest.py (ou fixture específica)
import os
os.environ.setdefault("TRAINING_CURSOR_SECRET", "test-secret-for-performance-tests")
```

**Critérios de done:**
- [ ] `test_performance_phase4.py` executa sem `RuntimeError: TRAINING_CURSOR_SECRET não definida`
- [ ] Teste de performance mede latência real do endpoint

> **VERIFICAÇÃO INDEPENDENTE (2026-04-25):** `grep -rn "TRAINING_CURSOR_SECRET" tests/ conftest.py` → **zero matches** — variável não definida em fixtures de teste. `src/training/api/deps.py:107-134`: lógica de runtime implementada corretamente (dual-key `TRAINING_CURSOR_SECRETS` + fallback `TRAINING_CURSOR_SECRET`, `RuntimeError` em produção, valor test-fallback em `TEST`). O problema persiste para `tests/` fora do escopo `DJANGO_SETTINGS_MODULE=config.settings.test`. **Status: ❌ NÃO IMPLEMENTADO** — `tests/conftest.py` não define a variável.

**Bloqueia merge?: não**

---

### REM-4D — Tornar import de generated/ condicional em api/__init__.py

---
> ACHADO-ID: REM-4D (RC-020)
> Categoria: Drift — acoplamento de startup a artefato derivado
> Módulo: training
> Severidade: baixa
> Estado: drift provável
---

**Arquivo-alvo:**
- `src/training/api/__init__.py` (linhas 14-15)

**Correção mínima:**
```python
try:
    from generated.training import schema_parity_check  # noqa — parity gate only
except ImportError:
    pass  # generated/ ausente — skip parity check (ex: CI clean build)
```

**Critérios de done:**
- [ ] Startup do Django não falha em ambiente sem `generated/`

> **VERIFICAÇÃO INDEPENDENTE (2026-04-25):** `head -18 src/training/api/__init__.py` → imports `from ..generated.application import use_cases as _gen_use_cases` e `from ..generated.infrastructure import repository as _gen_repository` são **incondicionais** (sem try/except). Comentário no arquivo: `"NÃO remover: test_training_codegen_parity.py verifica que generated/ é importável junto com api/; remoção quebra o gate de paridade de codegen (ADR-032)."` O arquivo documenta intencionalmente que os imports são arquiteturalmente obrigatórios. **Status: ❌ NÃO IMPLEMENTADO** (e possivelmente incompatível com a arquitetura atual per ADR-032 — revisar se o critério ainda é válido).

**Bloqueia merge?: não**

---

## Resumo executivo do plano

### Menor caminho para merge (ordem exata)

```
REM-0A → REM-0B → REM-0C   (Onda 0: ~1h total — desbloquear pipeline)
     ↓
REM-1B                      (migration — 15min)
     ↓
REM-1A                      (FSM — 1h)
     ↓
REM-1C                      (error format — 4h)
     ↓
[decisão de produto: wellness model]
     ↓
REM-1E                      (wellness schema — 4-8h)
     ↓
REM-1D                      (invariantes — 2h, depende REM-1A)
     ↓
REM-2A                      (path param case — 2h)
```

**Estimativa total mínima para merge:** ~15h de implementação + 1 decisão de produto (wellness model).

### Itens que não devem ser atacados diretamente (falhas derivadas)

| Falha derivada | Resolve automaticamente quando |
|---|---|
| ACHADO-003 (READINESS_SUMMARY_GATE) | REM-0A + REM-0B executados |
| ACHADO-005 (test_contract_gates_pass) | REM-0A + REM-0B + REM-0C executados |
| ADV-006 (createTrainingSession codes) | REM-3A executado |
| ADV-009 (401 em list endpoints) | REM-3A executado |
| ADV-010 (409 em attendance) | REM-3A executado |

### Validação final do plano

Após todas as ondas executadas, rodar:

```bash
# Gate completo
python3 scripts/validate_contracts.py
# Esperado: todos os gates PASS

# Suíte de testes
python3 -m pytest src/training/tests/ -v --tb=short
# Esperado: sem falhas

# Verificação de migration
python manage.py migrate --check
# Esperado: exit 0

# Smoke test de error format
curl -X POST /api/training/training-sessions \
  -H "Authorization: Bearer <token>" \
  -d '{"invalid": "body"}' \
  -v
# Esperado: 422 com Content-Type: application/problem+json e body com traceId

# Smoke test de FSM
curl -X POST /api/training/training-sessions/{draft-session-id}/publish \
  -H "Authorization: Bearer <token>"
# Esperado: 422 (DRAFT→PUBLISHED proibido)
```
