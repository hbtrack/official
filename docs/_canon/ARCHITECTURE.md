---
doc_type: canon
version: "1.1.0"
last_reviewed: "2026-03-23"
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
| Backend HTTP | `config/urls.py`, `config/settings.py`, `src/<module>/api.py` | existe um backend monolitico Django + Django Ninja com 17 apps e routers montados sob `/api/` |
| Organizacao de codigo | `src/<module>/domain/`, `application/`, `infrastructure/`, `models.py`, `schemas.py` | a arquitetura de codigo atual usa Interface -> Application -> Domain -> Infrastructure |
| Banco de dados local | `infra/docker-compose.yml`, `config/settings.py` | o ambiente dev materializado usa PostgreSQL em container local; o compose ainda esta em `postgres:12`, apesar do target-state aprovado apontar para PostgreSQL 16 |
| Redis | `infra/docker-compose.yml` | Redis esta provisionado como infra local, mas isso ainda nao prova runtime Celery ativo |
| Frontend | ausencia de `frontend/`; `package.json` contem apenas tooling de contratos | nao existe frontend materializado no workspace |
| Workers assíncronos | ausencia de `config/celery.py` e de `src/<module>/tasks.py` | workers Celery ainda nao sao runtime comprovado |
| WebSocket | ausencia de `CHANNEL_LAYERS` e de configuracao Channels | WebSocket/Channels ainda nao e runtime comprovado |
| Health endpoint | ausencia de `/health` em `config/urls.py` e routers | deploy ponta a ponta ainda nao pode ser tratado como operacional |

## 2. Target-state aprovado

Os seguintes itens estao aprovados arquiteturalmente, mas ainda nao podem ser lidos como runtime atual sem evidencia correspondente:

- stack backend consolidada em Django 5.x + Django Ninja 1.x + PostgreSQL 16 via [ADR-031](./decisions/ADR-031-backend-framework.md);
- frontend web React + Vite como primeira superficie de UX via [ADR-030](./decisions/ADR-030-frontend-strategy.md) e [FRONTEND_CONTRACT.md](./FRONTEND_CONTRACT.md);
- fila assíncrona via Celery + Redis e WebSocket via Channels como extensoes aprovadas do backend;
- deploy com staging e `GET /health` via [DEPLOY_PIPELINE.md](./DEPLOY_PIPELINE.md).

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

Os principais deltas entre o repo atual e o target-state aprovado sao:

1. PostgreSQL 16 esta aprovado, mas o compose local ainda usa `postgres:12`.
2. Redis existe como infra local, mas Celery nao esta configurado no codigo.
3. Frontend web esta aprovado, mas `frontend/` ainda nao existe.
4. WebSocket/Channels esta aprovado, mas nao ha configuracao correspondente.
5. `GET /health` e requisito de deploy, mas ainda nao existe no backend.
6. Middleware `X-Flow-ID` end-to-end (ADR-013) nao existe no runtime atual; apenas `correlation_id` pontual no modulo `audit`.
7. Logging estruturado em JSON (ADR-013) nao esta configurado em `config/settings.py`.

Esses deltas nao bloqueiam leitura arquitetural, mas bloqueiam qualquer afirmacao de runtime operacional que dependa deles.

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
