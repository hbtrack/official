---
doc_type: canon
version: "1.2.0"
last_reviewed: "2026-04-24"
status: active
state_semantics: governance
---

# Arquitetura - HB Track

## 0. Objetivo e limite de autoridade

Este documento governa a visao macro da arquitetura do HB Track para uso em:

- descoberta de escopo antes de contrato;
- leitura correta de `current-state` versus `target-state`;
- decisao de ADR quando existir lacuna estrutural;
- onboarding tecnico no nivel de sistema.

Este documento **nao** substitui:

- contratos tecnicos em `contracts/**`;
- regras operacionais em `.contract_driven/CONTRACT_SYSTEM_RULES.md`;
- layout e taxonomia em `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`;
- status lifecycle por modulo em `docs/_canon/MODULE_REGISTRY.yaml`;
- regras HTTP em `.contract_driven/templates/api/api_rules.yaml`;
- detalhamento funcional por modulo em `docs/hbtrack/modulos/<module>/`.

Leitura obrigatoria:

- `current-state` so pode ser afirmado com base em artefatos comprovados do repo;
- `target-state` aprovado so vale como direcao arquitetural, nao como evidencia de runtime;
- qualquer conflito com artefato de autoridade superior deve bloquear e ir para ADR.

## 1. Estado atual comprovado no workspace

| Eixo | Evidencia local | Leitura correta |
|------|------------------|-----------------|
| Backend HTTP | `config/urls.py`, `config/settings.py`, `src/<module>/api.py` | backend monolitico Django 5.0.4 + Django Ninja com 17 apps e routers montados sob `/api/` |
| Organizacao de codigo | `src/<module>/domain/`, `application/`, `infrastructure/`, `models.py`, `schemas.py` | arquitetura em camadas: Interface → Application → Domain → Infrastructure |
| Banco de dados | `infra/docker-compose.yml` (`image: postgres:16`), `config/settings.py` | PostgreSQL 16 — tanto no compose local quanto no staging |
| Redis | `infra/docker-compose.yml`, `config/settings.py` (`CHANNEL_LAYERS` + `CELERY_BROKER_URL`) | Redis 7 provisionado e configurado como broker Celery e backend de Channel Layer |
| Workers assíncronos | `config/celery.py`, `src/notifications/tasks.py` | Celery 5.x configurado com broker Redis, autodiscover ativo, sinais `before_task_publish` e `task_prerun` propagando `X-Flow-ID` |
| WebSocket / tempo real | `config/asgi.py` (`ProtocolTypeRouter`), `config/settings.py` (`CHANNEL_LAYERS`), `src/notifications/consumers.py` | Django Channels configurado com Redis Channel Layer; `NotificationConsumer` operacional; auth via subprotocolo ou header `Authorization` |
| Health endpoint | `config/urls.py:144` (`path("health", health_check)`) | `GET /health` existe e verifica PostgreSQL e Redis |
| Observabilidade / contexto | `src/shared/middleware.py` (`FlowIDMiddleware`), `src/shared/logging_formatters.py`, `config/settings.py` (`LOGGING`) | logging estruturado em JSON com `FlowIDFormatter`; `X-Flow-ID` propagado via `ContextVar` em HTTP, WebSocket e Celery |
| Frontend | `frontend/src/`, `frontend/package.json` | estrutura React + Vite inicializada; desenvolvimento em andamento (Fase 5 do ROADMAP) |
| ASGI runtime | `config/asgi.py`, `Dockerfile` (`UvicornWorker`) | servidor ASGI via Gunicorn + UvicornWorker; suporta HTTP e WebSocket simultaneamente |

## 2. Target-state aprovado

Os seguintes itens estao aprovados arquiteturalmente e ainda nao sao runtime comprovado no repo:

- **Frontend completo**: React + Vite aprovado via [ADR-030](./decisions/ADR-030-frontend-strategy.md); `frontend/src` inicializado mas sem deploy de SPA em staging ou producao.
- **Deploy de producao**: staging configurado em `infra/docker-compose.staging.yml`; ambiente VPS de producao ainda nao executado (Fase 6 do ROADMAP).
- **Mobile**: nenhum artefato de app mobile presente.
- **Observabilidade avancada**: integracao com APM externo (Sentry, Datadog, etc.) nao configurada.

Os componentes Celery, Channels/WebSocket, `GET /health`, PostgreSQL 16, Redis, logging estruturado em JSON e FlowIDMiddleware **sao current-state comprovado** — nao devem ser listados como target-state.

Regra operacional: enquanto os arquivos e pontos de entrada correspondentes nao existirem no repo, esses itens continuam sendo `target-state`, nao `current-state`.

## 3. Camadas atuais do backend

```text
Interface/API
  - src/<module>/api.py
  - src/<module>/schemas.py
        |
        v
Application / Use Cases
  - src/<module>/application/use_cases.py
        |
        v
Domain
  - src/<module>/domain/entities.py
  - src/<module>/domain/rules.py
  - src/<module>/domain/state_machine.py (quando existir)
        |
        v
Infrastructure
  - src/<module>/infrastructure/repository.py
  - src/<module>/infrastructure/models.py
        |
        v
Django ORM + migrations
  - src/<module>/models.py
  - src/<module>/migrations/
```

Leitura correta:

- o termo historico `Service` deve ser lido como **Application / Use Cases**;
- `models.py` no topo do modulo e a superficie Django do app; os detalhes ORM ficam em `infrastructure/models.py`;
- testes vivem em `src/<module>/tests/unit/` e `src/<module>/tests/integration/`.

## 4. Papel desta arquitetura dentro do sistema contract-driven

Esta arquitetura existe para responder perguntas que `.contract_driven` exige que sejam resolvidas sem inferencia:

- qual e a fronteira do sistema antes de criar contrato;
- qual e o caminho de implementacao esperado depois que o contrato estiver pronto;
- quais superficies ainda sao apenas target-state;
- quando um conflito exige `Decision Discovery` em vez de improviso.

Ela **nao** define:

- shape HTTP, naming JSON, erros ou seguranca de API: isso pertence a `api_rules.yaml`, `SECURITY_RULES.md` e aos contratos;
- regras de dominio detalhadas: isso pertence aos docs de modulo;
- readiness ou lifecycle do modulo: isso pertence a `MODULE_REGISTRY.yaml` e aos gates.

## 5. Deltas arquiteturais ainda abertos

Os deltas abaixo representam o que **ainda nao existe** no repo — itens aprovados no target-state mas sem evidencia de runtime comprovada:

1. **Frontend completo**: `frontend/src` inicializado mas desenvolvimento em andamento (Fase 5 do ROADMAP); sem deploy de SPA em staging/producao.
2. **Deploy de producao end-to-end**: staging configurado em `infra/docker-compose.staging.yml`; ambiente de producao VPS ainda nao executado (Fase 6 do ROADMAP).
3. **Mobile**: nenhum artefato de app mobile presente no workspace.
4. **Observabilidade avancada**: integracao com ferramentas externas de APM (Sentry, Datadog, etc.) nao configurada.

Todos os componentes criticos de runtime listados na secao 1 — Celery, Channels/WebSocket, `/health`, PostgreSQL 16, Redis, logging estruturado, FlowIDMiddleware — sao **current-state comprovado**, nao target-state.

Referencia factual completa do estado atual: [RUNTIME_CURRENT_STATE.md](./RUNTIME_CURRENT_STATE.md).

## 6. Regras arquiteturais invariantes

As seguintes regras continuam obrigatorias independentemente do estado atual do repo:

- nenhuma interface publica nasce antes do contrato;
- nenhum modulo fora dos 17 canônicos pode ser introduzido sem decisao formal;
- `users` e `identity_access` continuam separados por boundary explicita;
- regras HTTP e naming nao podem ser redefinidas fora da SSOT contratual;
- ausencia de ADR obrigatoria bloqueia contrato e implementacao;
- `generated/` e `_reports/` nunca sao fonte de verdade arquitetural.

## 7. Referencias

- [SYSTEM_SCOPE.md](./SYSTEM_SCOPE.md)
- [MODULE_MAP.md](./MODULE_MAP.md)
- [CODE_ARCHITECTURE.md](./CODE_ARCHITECTURE.md)
- [C4_CONTAINERS.md](./C4_CONTAINERS.md)
- [C4_COMPONENTS_BACKEND.md](./C4_COMPONENTS_BACKEND.md)
- [RUNTIME_CURRENT_STATE.md](./RUNTIME_CURRENT_STATE.md)
- [INTEGRATION_FLOWS.md](./INTEGRATION_FLOWS.md)
- [FRONTEND_CONTRACT.md](./FRONTEND_CONTRACT.md)
- [DEPLOY_PIPELINE.md](./DEPLOY_PIPELINE.md)
- [DECISION_POLICY.md](./DECISION_POLICY.md)
- [ADR_INDEX.md](./ADR_INDEX.md)
- [.contract_driven/CONTRACT_SYSTEM_RULES.md](/home/davis/HB-TRACK/.contract_driven/CONTRACT_SYSTEM_RULES.md)
- [.contract_driven/CONTRACT_SYSTEM_LAYOUT.md](/home/davis/HB-TRACK/.contract_driven/CONTRACT_SYSTEM_LAYOUT.md)
- [.contract_driven/templates/api/api_rules.yaml](/home/davis/HB-TRACK/.contract_driven/templates/api/api_rules.yaml)
