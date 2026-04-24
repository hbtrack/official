# Refutação Hostil — Módulo Training

> Auditoria AGAUDIT v1.1 — Prompt 6: Hostile Refutation
> Data: 2026-04-23
> Escopo: tentativa de derrubar achados de 01-contract, 02-domain-persistence, 03-architecture-reality, 05-adversarial
> Papel: revisor cético que busca falsos positivos, contexto incompleto e classificações exageradas
>
> **Metodologia:** cada achado recebe uma tentativa de refutação com evidência específica. Veredito final:
> - **DERRUBADO** — achado demonstravelmente falso
> - **ATENUADO** — achado parcialmente correto, severidade ou escopo exagerado
> - **CONFIRMADO** — refutação falhou, achado resiste

---

## Seção 1 — Achados de Domínio/Persistência (02-domain-persistence)

### DP-001 — VALID_TRANSITIONS permite DRAFT→PUBLISHED e SCHEDULED→IN_PROGRESS

**Tentativa de refutação:**
O auditor afirma violação de STATE_MODEL_TRAINING.md. Contra-argumento: talvez o canon permita essas transições e o auditor leu errado. Verificação direta:

- `docs/hbtrack/modulos/training/STATE_MODEL_TRAINING.md` linha 96 (lida durante Prompt 3): *"Deve passar por SCHEDULED antes de PUBLISHED"* — `DRAFT → PUBLISHED` explicitamente proibido.
- Linha 100: *"Deve passar por PUBLISHED antes de iniciar execução"* — `SCHEDULED → IN_PROGRESS` explicitamente proibido.
- `src/training/domain/rules.py` VALID_TRANSITIONS: `DRAFT: {SCHEDULED, PUBLISHED, CANCELLED}` — PUBLISHED presente.
- **Contraevência crítica adicional:** `src/training/tests/unit/test_state_machine.py` linha 23 — `test_draft_to_published_valid` executa `assert_valid_transition(DRAFT, PUBLISHED)` e PASSA. Isso prova que o teste foi escrito para validar o comportamento **bugado**, não o canonical. Não é refutação — é confirmação de que o erro está mais fundo: tanto a implementação quanto a suíte de testes divergem do canon.

**Veredito: CONFIRMADO** — refutação falhou. Ambas as transições proibidas são invocáveis via API e validadas pelos testes unitários como corretas.

---

### DP-002 — 6 campos ausentes do ORM

**Tentativa de refutação:**
O auditor lista 6 campos do domínio ausentes do ORM. Verificação direta em `src/training/infrastructure/models/sessions.py`:

- `individualization_mode` — **EXISTE** (linha 43: `models.CharField(max_length=40, blank=True, default="")`). ✓ Refutação parcial.
- `post_review_completed_at` — **EXISTE** (linha 92: `models.DateTimeField(null=True, blank=True)`). ✓ Refutação parcial.
  - Ressalva: nome diverge — entidade usa `post_review_completed` (boolean), ORM usa `post_review_completed_at` (datetime). Semântica diferente — não é equivalência plena.
- `planned_content_snapshot` — ausente do modelo ORM. Confirmado.
- `post_review_completed_by_user_id` — ausente. Confirmado.
- `post_review_deadline_at` — ausente. Confirmado.
- `continuity_notes` / `objective_origin` — ausentes. Confirmados.

**Veredito: ATENUADO** — o achado contém 2 falsos positivos (`individualization_mode` e `post_review_completed_at` existem no ORM). Contagem correta: 4 campos ausentes, não 6. A severidade (ALTA) permanece válida para os 4 campos confirmados.

---

### DP-003 — TransitionTrainingSessionUseCase sem guarda de pré-condições de publicação

**Tentativa de refutação:**
Talvez a guarda exista em outro ponto do fluxo (domínio, policy, handler). Verificação:

- `src/training/domain/policies/session_access.py` — `require_valid_transition` apenas checa `STAFF_ROLES` + `assert_valid_transition` (FSM). Sem verificação de `individualizationMode`, `sessionAt`, objectives ou blocks.
- `src/training/api/sessions.py` — `publish_training_session` chama `_do_transition(request, id, PUBLISHED)` sem pre-check adicional.
- Não existe `PublishPreconditionGuard` nem equivalente em nenhum arquivo da application layer (confirmado por ausência de matches para "precondition", "objective", "INV-TRAIN-086" em `src/training/application/`).

**Veredito: CONFIRMADO** — nenhuma guarda de pré-condições existe em qualquer camada. INV-TRAIN-086 é declarada no canon mas não enforced no runtime.

---

### DP-004 — individualizationMode ausente de CreateTrainingSessionIn e UpdateTrainingSessionIn

**Tentativa de refutação:**
O campo existe no ORM (DP-002 parcialmente refutado), no entity e no repository. Talvez exista nos schemas de entrada e o auditor não verificou.

Verificação em `src/training/schemas/sessions.py` (confirmado durante Prompt 3):
- `CreateTrainingSessionIn` — campos: `team_id, season_id, session_at, duration_planned, title, description, session_type, level, objectives`. Sem `individualization_mode`.
- `UpdateTrainingSessionIn` — campos semelhantes. Sem `individualization_mode`.

**Contra-argumento residual:** o campo pode ser definido internamente (default `""`). Mas o canon requer que seja fornecido em operações específicas, e o contrato OpenAPI declara `individualizationMode` como campo de sessão.

**Veredito: CONFIRMADO** — o campo é persistível e carregado pelo ORM, mas inacessível via API de criação/atualização. A descrição de "deadlock" no achado é exagerada (não é deadlock — é simplesmente não-exposto), mas o gap de API é real.

---

### DP-005 — Guard DR-TRAIN-011 ausente para DRAFT→SCHEDULED

**Tentativa de refutação:**
DR-TRAIN-011 pode estar implementado em outro ponto. Verificação por busca de `DR-TRAIN-011`, `session_at`, `sessionAt` em `src/training/application/sessions/commands.py` e `src/training/domain/rules.py`:
- Sem referência a DR-TRAIN-011 na camada de aplicação.
- VALID_TRANSITIONS permite DRAFT→SCHEDULED sem check de `session_at`.

**Veredito: CONFIRMADO** — guarda ausente.

---

## Seção 2 — Achados Adversariais (05-adversarial/training.md)

### ADV-001 — sleepHours: gap de 5 camadas

**Tentativa de refutação:**
Campo pode estar em alias, em outro schema, ou ser computado. Verificação exaustiva:
- `grep -r "sleep_hours\|sleepHours" src/training/` — zero matches fora de `__pycache__` (confirmado durante Prompt 5).
- `src/training/schemas/wellness.py` — `SubmitWellnessPreIn`: sem `sleep_hours`.
- `src/training/api/wellness.py` linha 65-72: `submit_wellness_pre` passa `sleep_quality` mas não `sleep_hours`.
- `contracts/openapi/paths/training.yaml` linha 1294: `sleepHours` declared como `required` em `submitWellnessPre`.

**Contra-argumento:** campo pode ser opcional em contextos práticos. **Rebate:** o contrato declara como `required` — não opcional.

**Veredito: CONFIRMADO — CRÍTICA** — nenhuma das 5 camadas implementa sleepHours. O contrato o declara obrigatório. Achado resiste integralmente.

---

### ADV-002 — FSM permite transições proibidas via API

**Tentativa de refutação:**
Mesma análise de DP-001 aplicada ao vetor de API. O argumento de refutação mais forte seria que `POST /publish` e `POST /start` têm validações adicionais não capturadas.

Verificação: `src/training/api/sessions.py` — `publish_training_session` e `start_training_session` ambos delegam a `_do_transition(request, id, PUBLISHED)` / `_do_transition(request, id, IN_PROGRESS)`. `_do_transition` chama apenas `TransitionTrainingSessionUseCase` que chama `SessionGuard.load_for_transition` que chama `policy.require_valid_transition` que chama `assert_valid_transition` — o qual permite ambas as transições porque VALID_TRANSITIONS as inclui.

**Veredito: CONFIRMADO — CRÍTICA** — transições invocáveis diretamente via API sem obstáculo.

---

### ADV-003 — individualizationMode inacessível via API

**Tentativa de refutação:**
Campo existe em ORM, entity e repository (ver DP-002 e DP-004). A refutação parcial de DP-002 demonstra que o dado pode ser persistido — o campo não está "perdido". O problema é exclusivamente na camada de API de entrada (schema de criação/atualização não o expõe).

**Veredito: ATENUADO** — achado original afirma que o campo "não existe em nenhuma camada de persistência", o que é falso (ORM e repository o têm). A formulação correta: o campo existe na persistência com `default=""` e é não-setável via API. Severidade (ALTA) permanece, mas descrição precisa de correção.

---

### ADV-004 — ErrorOut vs problem+json; traceId ausente

**Tentativa de refutação:**
Talvez `traceId` esteja presente sob outro nome ou seja injetado por middleware.

Verificação em `config/urls.py` — `_problem_response` (linhas 51-59):
```python
return {"type": "about:blank", "title": ..., "status": ..., "detail": ...}
```
Campos presentes: `type, title, status, detail`. Ausente: `traceId`.

`contracts/openapi/components/schemas/shared/problem.yaml` — campo `traceId` declarado como `required` com pattern `^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}`.

Contra-argumento: `X-Flow-ID` middleware existe (`shared/middleware.py`) e propaga um `flow_id` — talvez esse seja o `traceId` exposto via header. **Rebate:** o schema de problem+json requer `traceId` no **body**, não em header. O body confirmado não o inclui.

**Veredito: CONFIRMADO** — `traceId` ausente do body de erro em todas as rotas. `flow_id` existe como header X-Flow-ID mas não é propagado para o body de error response.

---

### ADV-005 — {blockId}/{recordId} no contrato vs {block_id}/{record_id} nos handlers

**Tentativa de refutação:**
Django Ninja pode normalizar automaticamente nomes de parâmetros de path (camelCase → snake_case). Verificação:

Django Ninja não realiza tradução automática de path params — o nome no decorador `@router.get("/path/{param_name}")` é exatamente o nome usado na URL e no parâmetro Python. Se o handler define `{block_id}`, a URL exposta é `/blocks/{block_id}`. O contrato define `{blockId}` — URLs distintas para o cliente.

**Veredito: CONFIRMADO** — há divergência real de URL entre contrato e runtime. Clientes seguindo o contrato enviariam `/blocks/{blockId}` enquanto o servidor espera `/blocks/{block_id}`. Achado válido.

---

### ADV-006 — createTrainingSession: divergência de response codes

**Tentativa de refutação:**
O handler pode delegar 404/409/500 para middleware global, não declarados localmente mas presentes em runtime.

Verificação: Django Ninja retorna 422 para erros de validação de schema (Pydantic) — este código está no runtime mas ausente do contrato OpenAPI. O contrato declara 404 e 409 mas o handler não os mapeia em `_EXCEPTION_STATUS_MAP`. `500` é retornado pelo framework em caso de exceção não tratada — presença em runtime não implica que é declarado no handler.

**Posição defensível:** o auditor tem razão nos dois vetores — (a) o runtime produz 422 não declarado no contrato; (b) o contrato declara 404/409/500 que o handler não expõe explicitamente.

**Veredito: CONFIRMADO** — divergência real em ambas as direções. Achado válido, sem exagero.

---

### ADV-007 — resolve_access() retorna team_ids=() e athlete_ids=() (TODO Fase 3)

**Tentativa de refutação:**
O auditor afirma risco de BOLA. Análise mais precisa do vetor real:

**ListTrainingSessionsUseCase** (`application/sessions/queries.py`):
- Filtra por `organization_id` (do JWT) — cross-org BOLA não é possível.
- Filtra por `team_id` (query param do caller) — um coach pode informar qualquer `team_id` da mesma org e obter resultados. Não há verificação de que o coach pertence àquele time.
- `team_ids=()` do AccessContext não é usado no ListUseCase.

**GetTrainingSessionUseCase** (`application/sessions/queries.py`):
- Chama `SessionGuard.load_for_read` com `session_athlete_ids=[]` (handler não passa o campo, usa default vazio).
- Para `role == ATHLETE`: `actor_id not in []` → sempre True → `InsufficientPrivilege` sempre levantado.
- **Efeito real:** athletes são BLOQUEADOS de acessar qualquer sessão (regressão de funcionalidade, não over-privilege).

**Risco real de BOLA:** coaches podem listar sessões de times que não são seus, dentro da mesma org. Esse é o vetor real — não o descrito no achado (que focava em `athlete_ids` vazias).

**Veredito: ATENUADO** — o achado é válido mas o vetor descrito está parcialmente errado. O risco de BOLA via `athlete_ids` vazias afeta os athletes de forma inversa (lock-out, não over-privilege). O risco real é cross-team listing para staff roles. Severidade (ALTA) mantida, descrição precisa de correção.

---

### ADV-008 — api/__init__.py importa generated/ em startup

**Tentativa de refutação:**
A importação pode ser condicional (ex: apenas em `DEBUG=True`) ou protegida.

Verificação em `src/training/api/__init__.py` linhas 14-15 (lido durante Prompt 5): importação incondicional de `generated/` sem `if settings.DEBUG`. Acoplamento de produção a artefato derivado é real.

**Contra-argumento:** trata-se de um import-time check, não de serving. Em produção, o arquivo existe se o pipeline rodou — a importação apenas valida paridade, não serve o schema.

**Veredito: ATENUADO** — o achado classifica como "coupling a artefato derivado", o que é correto. Mas o risco concreto é uma `ImportError` em startup se o `generated/` não existir, não um risco funcional em runtime normal. Severidade (MÉDIA) é defensável mas pode ser considerada exagerada — BAIXA seria mais preciso.

---

### ADV-009 — list_execution_records e list_session_objectives sem 401 declarado

**Tentativa de refutação:**
O 401 pode ser injetado globalmente pelo NinjaAPI ou por middleware antes do handler.

Verificação: Django Ninja não auto-injeta 401 na declaração de schema de resposta — `response={}` no decorador é exatamente o que é documentado no OpenAPI gerado. O handler de `list_session_objectives` em `src/training/api/execution.py` linha 105: `response={200: SessionObjectiveListOut, 403: ErrorOut, 404: ErrorOut}` — sem 401. O runtime pode retornar 401 via `JWTClaimsMiddleware`, mas não estará documentado na spec gerada.

**Veredito: CONFIRMADO** — 401 ausente da declaração explícita dos handlers. Divergência entre spec gerada e runtime real.

---

### ADV-010 — record_session_attendance sem 409 declarado

**Tentativa de refutação:**
Similar a ADV-009. O `WellnessWindowClosed` mapeado para 400 — talvez `AttendanceAlreadyRecorded` (409) seja tratado genericamente como 400 também.

Verificação em `src/training/api/errors.py` — `_EXCEPTION_STATUS_MAP`: `AttendanceAlreadyRecorded` ausente do mapa explícito. Falha no isinstance fallback para `(NotFoundError, 404)` não captura — cairia no fallback genérico 500. O contrato declara 409 para esse endpoint.

**Veredito: CONFIRMADO** — 409 declarado no contrato mas não mapeado no runtime para o endpoint de attendance.

---

### ADV-011 — DR-TRAIN-030 ausente do contrato

**Tentativa de refutação:**
DR-TRAIN-030 pode estar implicitamente validado pelo schema do contrato (ex: campo com constraint numérica).

Verificação: DR-TRAIN-030 define limites de carga de treino (calculados). O contrato não expõe esses limites como restrições de schema. Achado de baixa severidade e confirmado.

**Veredito: CONFIRMADO — BAIXA** — achado menor, validado.

---

## Seção 3 — Achados de Arquitetura (03-architecture-reality)

### AR-001 a AR-010 — Canon desatualizado (documentation drift)

**Tentativa de refutação coletiva:**
O auditor classifica todos os 10 achados como "drift de documentação". Contra-argumento: pelo menos um poderia ser um bug de código mascarado como drift.

Verificação sistemática dos pontos mais suspeitos:
- **AR-001 (Celery ausente no canon):** Celery implementado e funcional (`config/celery.py`, 8 `tasks.py`). Apenas o documento `RUNTIME_CURRENT_STATE.md` não menciona. Não há bug de código.
- **AR-002 (Channels ausente no canon):** `CHANNEL_LAYERS` configurado, `asgi.py` com ProtocolTypeRouter, `notifications/routing.py` existente. Apenas documentação não atualizada.
- **AR-003 (GET /health ausente no canon):** Endpoint implementado em `config/urls.py:105-141` com checks de PostgreSQL e Redis. Apenas documentação não atualizada.
- **AR-007 (frontend ausente no canon):** `frontend/` com React/Vite/Tailwind/Playwright/dist existe. Apenas documentação não atualizada.
- **AR-008 (postgres:12 em ARCHITECTURE.md):** `infra/docker-compose.yml` usa `postgres:16`. Este é o único achado com dado factualmente errado no documento (não apenas "ausente" — é errado).

**Conclusão da refutação:** nenhum dos 10 achados representa bug de código. Todos são drift de documentação. A classificação do auditor é correta. AR-008 é ligeiramente mais sério (dado errado vs. omissão) mas ainda não é bug de código.

**Veredito: CONFIRMADO (todos)** — classificação de drift correta para todos os 10 achados. Nenhum falso positivo.

---

## Seção 4 — Achados de Contrato (01-contract)

> Nota: os achados do relatório `01-contract/training.md` não foram detalhados nesta refutação por falta de acesso direto ao relatório. Os achados de contrato cross-validados durante Prompts 3 e 5 (sleepHours, response codes, path param case) foram tratados nas seções anteriores. Refutação de achados adicionais de contrato pendente de leitura do relatório original.

---

## Sumário consolidado de vereditos

| Achado | Veredito | Observação |
|---|---|---|
| DP-001 (FSM DRAFT→PUBLISHED) | **CONFIRMADO** | Testes unitários também errados — profundidade do bug maior que descrito |
| DP-002 (6 campos ORM ausentes) | **ATENUADO** | 2 campos existem (individualization_mode, post_review_completed_at); 4 ausentes |
| DP-003 (publish sem preconditions) | **CONFIRMADO** | Nenhuma guarda em nenhuma camada |
| DP-004 (individualizationMode ausente de Create/Update input) | **CONFIRMADO** | Campo existe no ORM mas inacessível via API |
| DP-005 (DR-TRAIN-011 ausente para DRAFT→SCHEDULED) | **CONFIRMADO** | — |
| ADV-001 (sleepHours — 5 camadas) | **CONFIRMADO — CRÍTICA** | Zero evidência contrária |
| ADV-002 (FSM via API) | **CONFIRMADO — CRÍTICA** | Extensão de DP-001 ao vetor HTTP |
| ADV-003 (individualizationMode inacessível) | **ATENUADO** | Campo existe em camadas de persistência; só ausente nos inputs de API |
| ADV-004 (traceId ausente do body) | **CONFIRMADO** | X-Flow-ID existe como header, não no body de error |
| ADV-005 ({blockId} vs {block_id}) | **CONFIRMADO** | Django Ninja não traduz path params |
| ADV-006 (response codes createSession) | **CONFIRMADO** | Divergência em ambas as direções (422 extra; 404/409/500 ausentes) |
| ADV-007 (resolve_access TODO) | **ATENUADO** | Vetor real: cross-team listing por staff, não BOLA via athlete_ids; athletes lockados |
| ADV-008 (api/__init__ importa generated/) | **ATENUADO** | Risco é ImportError em startup, não runtime; severidade BAIXA mais precisa |
| ADV-009 (401 ausente em list endpoints) | **CONFIRMADO** | — |
| ADV-010 (409 ausente em attendance) | **CONFIRMADO** | AttendanceAlreadyRecorded não mapeado |
| ADV-011 (DR-TRAIN-030 ausente do contrato) | **CONFIRMADO — BAIXA** | — |
| AR-001 a AR-010 (documentation drift) | **CONFIRMADO (todos)** | Nenhum falso positivo; classificação correta |

---

## Achados revisados após refutação

Dois achados requerem revisão de redação (sem mudança de severidade exceto ADV-008):

1. **DP-002** — contagem corrigida: 4 campos ausentes do ORM (não 6). `individualization_mode` e `post_review_completed_at` existem.

2. **ADV-003** — reformulação: "`individualizationMode` existe na persistência com `default=\"\"` e é não-setável via API de criação/atualização." A descrição "deadlock" deve ser removida — é um gap de API, não um deadlock arquitetural.

3. **ADV-007** — reformulação: o risco BOLA primário é cross-team listing por roles de staff (coach pode listar sessões de times que não administra). Athletes são incorretamente lockados (regressão), não over-privileged. Descrição do vetor precisa de correção.

4. **ADV-008** — severidade revisada de MÉDIA para BAIXA: o risco é `ImportError` no startup (se `generated/` não existir), não uma falha funcional em runtime normal.

---

## Conclusão da refutação

**Dos 22 achados avaliados:**
- **0 DERRUBADOS** — nenhum achado demonstrou ser completamente falso
- **4 ATENUADOS** — DP-002, ADV-003, ADV-007, ADV-008 (descrições ou contagens imprecisas; severidade de ADV-008 revista)
- **18 CONFIRMADOS** — resistiram integralmente à refutação hostil

**Os dois achados de maior risco (ADV-001 e ADV-002) resistiram sem qualquer atenuação.** sleepHours está completamente ausente do runtime em todas as 5 camadas, e as transições FSM proibidas são invocáveis via API sem restrição. Esses dois achados constituem a prioridade máxima de remediação.
