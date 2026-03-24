---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-23"
status: active
state_semantics: governance
---

# Fluxos de Integração — HB Track

## 0. Objetivo e limite de autoridade

Este documento descreve os **fluxos críticos de integração entre módulos** do HB Track. Cada
fluxo é descrito tanto no seu formato atual (backend HTTP + banco de dados) quanto no target-state
aprovado (quando aplicável).

Este documento **não substitui**:

- contratos técnicos em `contracts/**` — esses são soberanos sobre shape HTTP e dados;
- regras de domínio em `docs/hbtrack/modulos/<module>/` — essas governam invariantes;
- `CODE_ARCHITECTURE.md` — esse governa a estrutura de implementação;
- `C4_COMPONENTS_BACKEND.md` — esse descreve os componentes internos.

Leitura correta: os fluxos aqui descritos seguem as camadas reais do backend atual
(`Interface → Application → Domain → Infrastructure`). Componentes marcados como
`[target-state]` ainda não existem no runtime.

---

## 1. Fluxo: Autenticação e Sessão

**Módulo soberano:** `identity_access`  
**ADRs:** ADR-007 (JWT RS256), ADR-008 (RBAC)  
**Estado atual:** backend materializado

### 1.1 Login (obtenção de tokens)

```mermaid
sequenceDiagram
  participant C as Cliente
  participant Auth as identity_access/api.py\nPOST /api/auth/login
  participant UC as LoginUseCase
  participant Domain as domain/rules.py
  participant Repo as infrastructure/repository.py
  participant DB as PostgreSQL

  C->>Auth: POST /api/auth/login\n{email, password}
  Auth->>UC: execute(email, password)
  UC->>Domain: verifica credenciais e regras de acesso
  UC->>Repo: cria AuthSession
  Repo->>DB: INSERT auth_session
  DB-->>Repo: session criada
  Repo-->>UC: AuthSession
  UC-->>Auth: (session, access_token, refresh_token)
  Auth-->>C: 200 {accessToken, refreshToken, expiresIn}
```

**Claims do access token:** `sub` (user UUID), `iss`, `aud`, `iat`, `exp`, `jti`, `roles`,
`teamId`. Algoritmo: RS256. Lifetime: 15 min (access) + 7 dias sliding (refresh).

### 1.2 Uso do access token nos demais módulos

```mermaid
flowchart LR
  C[Cliente] -->|Authorization: Bearer <jwt>| Router
  Router[NinjaAPI Router\nconfig/urls.py] --> API[src/<module>/api.py]
  API -->|extrai actor_role + actor_user_id| UC[application/use_cases.py]
  UC -->|assert_can_<operation>| Domain[domain/rules.py]
```

Cada módulo extrai `actor_role` e `actor_user_id` do JWT validado antes de chamar o use case.
Nenhum módulo repete lógica de autenticação — apenas usa os dados do token já validado.

### 1.3 Refresh e revogação

- `POST /api/auth/refresh` → emite novo par (access + refresh), invalida refresh anterior.
- `POST /api/auth/logout` → invalida sessão e refresh token.
- `GET /api/auth/session` → retorna sessão ativa atual.
- `POST /api/auth/roles/assign` / `revoke` → gerencia RBAC.

---

## 2. Fluxo: Training → Wellness → Analytics → Reports

Este é o fluxo operacional central de gestão de carga e performance atlética.

### 2.1 Visão macro

```mermaid
flowchart LR
  TR[training\n(sessão de treino)] -->|training_session_id| WE[wellness\n(check-in PSE)]
  TR -->|agrega dados| AN[analytics\n(snapshot de métricas)]
  WE -->|contribui para| AN
  AN -->|alimenta| RE[reports\n(job de relatório)]
```

### 2.2 Criação de sessão de treino

**Módulo:** `training` | `POST /api/training/sessions`

```mermaid
sequenceDiagram
  participant Coach as Coach/Staff
  participant T as training/api.py
  participant UC as CreateTrainingSession
  participant Domain as domain/rules.py\n+ state_machine.py
  participant Repo as infrastructure/repository.py

  Coach->>T: POST /api/training/sessions\n{date, teamId, objectives...}
  T->>UC: execute(actor_role, actor_user_id, payload)
  UC->>Domain: assert_can_create_session(role)
  UC->>Domain: valida invariantes (INV-TRAIN-*)
  UC->>Repo: salva TrainingSession (status=draft)
  Repo-->>UC: TrainingSession
  UC-->>T: sessão criada
  T-->>Coach: 201 {id, status: "draft", ...}
```

**FSM de treinamento:** `draft → scheduled → ongoing → completed | cancelled | suspended`

### 2.3 Check-in de wellness pós-treino

**Módulo:** `wellness` | `POST /api/wellness/entries`

```mermaid
sequenceDiagram
  participant At as Atleta
  participant W as wellness/api.py
  participant UC as CreateWellnessEntry
  participant Domain as domain/rules.py

  At->>W: POST /api/wellness/entries\n{questionnaire_date, training_session_id?,\nreadiness_score, fatigue_score...}
  W->>UC: execute(actor_role, actor_user_id, payload)
  UC->>Domain: assert_can_create_entry(role, actor, athlete)
  UC->>Domain: check_high_pain_alert (alerta clínico)
  UC->>Repo: salva WellnessEntry
  Repo-->>UC: WellnessEntry
  UC-->>W: entry criada
  W-->>At: 201 {id, questionnaire_date, readiness_score...}
```

**Nota:** o campo `training_session_id` é opcional e referencia a sessão de treino correspondente.
Não há chamada de código de `wellness` para `training` — apenas a chave UUID é armazenada.

### 2.4 Criação de snapshot de analytics

**Módulo:** `analytics` | `POST /api/analytics/snapshots`

```mermaid
sequenceDiagram
  participant Staff as Head Coach / Analyst
  participant A as analytics/api.py
  participant UC as CreateAnalyticsSnapshot
  participant Domain as domain/entities.py + rules.py
  participant Repo as infrastructure/repository.py

  Staff->>A: POST /api/analytics/snapshots\n{source_module, metric_key,\ntime_window, granularity, payload}
  A->>UC: execute(role, requester_id, payload)
  UC->>Domain: assert_can_create_snapshot(role)
  UC->>Domain: valida source_module e metric_key (VALID_SOURCE_MODULES, VALID_METRIC_KEYS)
  UC->>Repo: salva AnalyticsSnapshot
  Repo-->>UC: snapshot
  UC-->>A: snapshot criado
  A-->>Staff: 201 {id, source_module, metric_key...}
```

**`source_module`** é o módulo de origem dos dados (ex: `training`, `wellness`, `matches`).
O analytics não faz queries diretas a outros módulos no runtime atual — consome dados agregados
passados pelo chamador.

### 2.5 Geração de relatório

**Módulo:** `reports` | `POST /api/reports/jobs`

```mermaid
sequenceDiagram
  participant Staff as Usuário
  participant R as reports/api.py
  participant UC as CreateReportJob
  participant Repo as infrastructure/repository.py

  Staff->>R: POST /api/reports/jobs\n{report_type, format_label,\nsource_metric_names, ...}
  R->>UC: execute(role, requester_id, payload)
  UC->>Repo: salva ReportJob (status=pending)
  Repo-->>UC: job criado
  UC-->>R: job
  R-->>Staff: 201 {id, status: "pending", ...}

  Note over R,Repo: [target-state] worker Celery processa o job\ne atualiza status para "ready"
```

**Estado atual:** `ReportJob` é criado com `status=pending`. O processamento real (geração do
arquivo/PDF) depende de worker Celery — ainda `[target-state]`.

---

## 3. Fluxo: Notificações

**Módulo soberano:** `notifications`  
**Estado atual:** intenção de entrega persistida; despacho externo é `[target-state]`

### 3.1 Ciclo de vida de uma notificação

```mermaid
flowchart LR
  Any[Qualquer módulo\nou sistema externo] -->|cria intent| NR[notifications\nPOST /api/notifications/deliveries]
  NR --> DB[(PostgreSQL\nNotificationDelivery)]
  DB -->|[target-state]\nworker Celery| Ext[Canal externo\npush / e-mail / WhatsApp]
```

### 3.2 Criação de intent de entrega

```mermaid
sequenceDiagram
  participant Caller as Chamador (módulo ou sistema)
  participant N as notifications/api.py
  participant UC as CreateNotificationIntent
  participant Repo as infrastructure/repository.py

  Caller->>N: POST /api/notifications/deliveries\n{recipient_user_id, channel_label,\nnotification_template_ref?, event_envelope_ref?}
  N->>UC: execute(role, recipient_user_id, ...)
  UC->>Repo: salva NotificationDelivery (status=queued)
  Repo-->>UC: delivery
  UC-->>N: delivery criada
  N-->>Caller: 201 {id, delivery_status_label: "queued"}
```

**`delivery_status_label`:** `queued → dispatched → delivered | failed`

**Nota:** no runtime atual, o status permanece `queued` até que um worker (target-state)
processe e atualize. O canal real de despacho (push notification, e-mail, etc.) não está
implementado.

---

## 4. Fluxo: Vídeo e Scout

### 4.1 Vídeo — captura e sessão de mídia

**Módulo:** `video`  
**ADR:** ADR-033  
**Estado atual:** backend + FSM materializado; worker de processamento é `[target-state]`

```mermaid
flowchart LR
  User -->|POST /api/video/sessions| VS[VideoSession\n(FSM: created→processing→ready|failed)]
  VS -->|[target-state]\nworker Celery| Storage[Object Storage externo]
  VS -->|clips| VC[VideoClip]
```

**FSM de vídeo:** `created → processing → ready | failed`

```mermaid
sequenceDiagram
  participant U as Usuário
  participant V as video/api.py
  participant UC as CreateVideoSession
  participant Domain as domain/state_machine.py +\nentities.py

  U->>V: POST /api/video/sessions\n{title, match_id?, training_session_id?}
  V->>UC: execute(role, user_id, payload)
  UC->>Domain: cria VideoSession (status=created)
  UC->>Repo: persiste
  Repo-->>UC: session
  UC-->>V: session
  V-->>U: 201 {id, status: "created"}

  Note over V,Domain: [target-state] worker Celery\ntransiciona para "processing" → "ready"
```

### 4.2 Scout — análise tática e eventos de jogo

**Módulo:** `scout`  
**Estado atual:** backend materializado; eventos são registrados via API síncronos

```mermaid
sequenceDiagram
  participant An as Analista
  participant S as scout/api.py
  participant UC as use_cases.py
  participant Repo as infrastructure/repository.py

  An->>S: POST /api/scout/events\n{match_id, event_type, minute, actor_user_id, ...}
  S->>UC: execute(role, requester_id, payload)
  UC->>Domain: valida invariantes de evento tático
  UC->>Repo: salva ScoutEvent
  Repo-->>UC: evento
  UC-->>S: evento
  S-->>An: 201 {id, event_type, minute...}
```

---

## 5. Fluxo: Ingestão via IA

**Módulo:** `ai_ingestion`  
**Estado atual:** backend materializado; jobs de importação são registrados; processamento real
depende de worker `[target-state]`

```mermaid
flowchart LR
  Ext[Sistema externo\nou agente IA] -->|POST /api/ingestion/jobs| Ingest[ai_ingestion\n(IngestionJob)]
  Ingest -->|[target-state]\nworker Celery| Modules[Módulos destino\n(training, wellness, medical...)]
  Ingest --> DB[(PostgreSQL)]
```

```mermaid
sequenceDiagram
  participant Ext as Sistema externo / Agente
  participant I as ai_ingestion/api.py
  participant UC as CreateIngestionJob
  participant Repo as infrastructure/repository.py

  Ext->>I: POST /api/ingestion/jobs\n{source_type, target_module, payload...}
  I->>UC: execute(role, requester_id, payload)
  UC->>Domain: valida source_type e target_module
  UC->>Repo: salva IngestionJob (status=pending)
  Repo-->>UC: job
  UC-->>I: job criado
  I-->>Ext: 202 {id, status: "pending"}

  Note over I,Repo: [target-state] worker Celery processa\ne insere dados nos módulos destino
```

---

## 6. Propagação de identidade entre fluxos

Em todos os fluxos acima, a identidade do ator é propagada da seguinte forma:

```mermaid
flowchart LR
  JWT["JWT (Authorization: Bearer)"] -->|validado na camada HTTP| API["src/<module>/api.py"]
  API -->|actor_role + actor_user_id extraídos| UC["application/use_cases.py"]
  UC -->|assert_can_<operation>| Domain["domain/rules.py"]
```

**Regra invariante:** nenhum use case confia em inputs não validados pela camada HTTP.
O `actor_role` determina permissões; o `actor_user_id` determina o escopo de dados visíveis.

---

## 7. Fluxos target-state ainda não implementados

| Fluxo | Dependência bloqueante |
|-------|------------------------|
| Despacho real de notificações | Worker Celery + canal externo |
| Processamento de relatórios | Worker Celery |
| Processamento de vídeo | Worker Celery + Object Storage |
| Ingestão processada de dados externos | Worker Celery |
| Propagação de `X-Flow-ID` entre módulos | Middleware Django (ADR-013) |
| Notificações WebSocket em tempo real | Django Channels + Redis (ADR-031) |

---

## 8. Referências

- [C4_COMPONENTS_BACKEND.md](./C4_COMPONENTS_BACKEND.md)
- [MODULE_MAP.md](./MODULE_MAP.md)
- [CODE_ARCHITECTURE.md](./CODE_ARCHITECTURE.md)
- [RUNTIME_CURRENT_STATE.md](./RUNTIME_CURRENT_STATE.md)
- [decisions/ADR-007-auth-strategy.md](./decisions/ADR-007-auth-strategy.md)
- [decisions/ADR-008-authz-strategy.md](./decisions/ADR-008-authz-strategy.md)
- [decisions/ADR-013-logging-policy.md](./decisions/ADR-013-logging-policy.md)
- [decisions/ADR-031-backend-framework.md](./decisions/ADR-031-backend-framework.md)
- [decisions/ADR-033-video-module-canonicalization.md](./decisions/ADR-033-video-module-canonicalization.md)
