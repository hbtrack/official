---
doc_type: canon
version: "1.3.0"
status: active
decision_ref: D4
adr_ref: ADR-026, ADR-031
state_semantics: current-state
last_reviewed: "2026-04-24"
---

# CODE_ARCHITECTURE.md

## 0. Objetivo e limite de autoridade

Este documento descreve a **arquitetura de código atualmente materializada** no
workspace do HB Track.

Ele serve para:

- orientar navegação em `src/`, `config/` e `frontend/`;
- explicitar o que já existe de fato em backend, async runtime e frontend;
- impedir que presença estrutural seja confundida com prontidão operacional completa.

Ele não define:

- contrato HTTP, naming JSON ou policy de erros;
- lifecycle de módulo;
- deploy de produção;
- estado operacional de staging/produção.

## 1. Estrutura comprovada no workspace

```text
src/
  <module>/
    api.py | api/
    schemas.py
    models.py
    domain/
    application/
    infrastructure/
    migrations/
    tests/
      unit/
      integration/
config/
  settings.py
  urls.py
  asgi.py
  celery.py
frontend/
  src/
  package.json
  vite.config.ts
manage.py
pyproject.toml
```

Todos os 17 módulos canônicos possuem backend app materializado em `src/<module>/`.

Além da estrutura backend, o workspace **também já materializa**:

- `config/asgi.py`;
- `config/celery.py`;
- `src/*/tasks.py` em módulos que executam workload assíncrono;
- `CHANNEL_LAYERS` em `config/settings.py`;
- `frontend/` com toolchain React + Vite.

## 2. Mapeamento de camadas

| Camada | Arquivos atuais | Responsabilidade |
|---|---|---|
| Interface / API | `src/<module>/api.py`, `src/<module>/schemas.py` | implementar contrato OpenAPI e adaptar request/response |
| Application | `src/<module>/application/` | orquestrar casos de uso, políticas e serviços |
| Domain | `src/<module>/domain/` | invariantes, regras e state machines |
| Infrastructure | `src/<module>/infrastructure/` | persistência, queries e integração com Django ORM |
| Django app surface | `src/<module>/models.py`, `apps.py`, `migrations/` | exposição do app ao runtime Django |
| Async runtime | `config/celery.py`, `src/*/tasks.py` | execução assíncrona, retry, publicação e consumo de jobs |
| ASGI realtime | `config/asgi.py`, `src/notifications/consumers.py`, `config/settings.py` | HTTP + WebSocket via Channels |
| Frontend workspace | `frontend/src/`, `frontend/package.json`, `vite.config.ts` | SPA React + Vite consumindo contratos do backend |

## 3. Relação com os artefatos soberanos

O fluxo correto continua sendo:

1. contrato técnico em `contracts/**`;
2. docs normativas em `docs/_canon/` e `docs/hbtrack/modulos/<module>/`;
3. implementação em `src/<module>/`, `config/` e `frontend/`.

Fontes soberanas que este documento **consome**, mas não substitui:

- `.contract_driven/templates/api/api_rules.yaml` para convenções HTTP;
- `contracts/openapi/paths/<module>.yaml` para endpoints;
- `contracts/schemas/<module>/` para shapes reutilizáveis;
- docs de domínio, invariantes, state model e permissões por módulo;
- [ARCHITECTURE.md](./ARCHITECTURE.md);
- [RUNTIME_CURRENT_STATE.md](./RUNTIME_CURRENT_STATE.md).

## 4. O que existe em código, mas não prova operação completa

Os itens abaixo **existem no workspace** e devem ser tratados como current-state
de código:

- `config/celery.py`;
- `src/*/tasks.py`;
- `config/asgi.py`;
- `CHANNEL_LAYERS` em `config/settings.py`;
- `frontend/`.

Consequência operacional:

- Celery, Channels e WebSocket **não podem mais ser descritos como ausentes** na arquitetura de código;
- o que ainda pode estar incompleto é a operação dedicada de produção, não a materialização no repo;
- `frontend/` materializado prova workspace frontend, mas não prova deploy da SPA;
- qualquer claim de ausência desses artefatos passa a ser drift factual.

## 5. Regras de implementação que continuam válidas

- nenhum endpoint pode ser implementado sem contrato OpenAPI;
- `api.py` implementa o contrato, mas não define sozinho a regra soberana de negócio;
- `domain/` não depende de `infrastructure/`;
- testes do módulo vivem em `src/<module>/tests/`;
- presença de diretório, migration e teste **não** é prova suficiente de readiness comportamental;
- status `implemented` deve ser sustentado por evidência executável, não só por superfície.

## 6. Referências

- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [RUNTIME_CURRENT_STATE.md](./RUNTIME_CURRENT_STATE.md)
- [MODULE_REGISTRY.yaml](./MODULE_REGISTRY.yaml)
- [FEATURE_REGISTRY.yaml](./FEATURE_REGISTRY.yaml)
- [decisions/ADR-026-code-architecture.md](./decisions/ADR-026-code-architecture.md)
- [decisions/ADR-031-backend-framework.md](./decisions/ADR-031-backend-framework.md)
- [.contract_driven/templates/api/api_rules.yaml](/home/davis/HB-TRACK/.contract_driven/templates/api/api_rules.yaml)
