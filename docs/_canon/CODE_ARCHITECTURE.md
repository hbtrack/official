---
doc_type: canon
version: "1.2.0"
status: active
decision_ref: D4
adr_ref: ADR-026, ADR-031
state_semantics: current-state
---

# CODE_ARCHITECTURE.md

## 0. Objetivo e limite de autoridade

Este documento e a referencia de **arquitetura de codigo backend atualmente materializada** no workspace.

Ele serve para:

- orientar `generate_code`;
- guiar navegacao em `src/`;
- explicitar a correspondencia entre contratos, docs de modulo e codigo;
- impedir que o agente assuma camadas ou arquivos que ainda nao existem.

Ele nao define:

- contrato HTTP, naming JSON ou policy de erros;
- lifecycle do modulo;
- target-state de frontend;
- deploy ou runtime operacional de Celery/Channels.

## 1. Estrutura backend comprovada

```text
src/
  <module>/
    api.py
    schemas.py
    models.py
    generated/                 # somente modulos participantes do codegen deterministico
      domain/
      application/
      infrastructure/
      tests/
    domain/
      entities.py
      rules.py
      state_machine.py        # quando aplicavel
    application/
      use_cases.py
    infrastructure/
      models.py
      repository.py
    migrations/
    tests/
      unit/
      integration/
config/
  settings.py
  urls.py
manage.py
pyproject.toml
```

Todos os 17 modulos canônicos possuem backend app materializado em `src/<module>/` com:

- `api.py`;
- `schemas.py`;
- `models.py`;
- pastas `domain/`, `application/`, `infrastructure/`;
- `migrations/`;
- `tests/`.

Adicionalmente, modulos que entram no pipeline de codegen deterministico podem materializar
uma zona derivada em `src/<module>/generated/`. No estado atual, esse layout esta ativo
para o piloto `reports`.

## 2. Mapeamento de camadas

| Camada | Arquivos atuais | Responsabilidade |
|--------|-----------------|------------------|
| Interface / API | `src/<module>/api.py`, `src/<module>/schemas.py` | implementar o contrato OpenAPI e adaptar request/response |
| Application / Use Cases | `src/<module>/application/use_cases.py` | orquestrar casos de uso, permissao, fluxo e chamadas ao repositorio |
| Domain | `src/<module>/domain/entities.py`, `rules.py`, `state_machine.py` | modelagem de entidade, invariantes e transicoes de estado |
| Infrastructure | `src/<module>/infrastructure/repository.py`, `models.py` | persistencia, queries e adaptacao ao Django ORM |
| Generated | `src/<module>/generated/**` | codigo estrutural derivado do source graph e dos contratos soberanos; nunca fonte de verdade |
| Django app surface | `src/<module>/models.py`, `apps.py`, `migrations/` | exposicao do app para o runtime Django |

Leitura correta: a narrativa antiga de `Service` deve ser interpretada como **Application / Use Cases**.

## 3. Relacao com os artefatos soberanos

O fluxo correto continua sendo:

1. contrato tecnico em `contracts/**`;
2. docs normativas do modulo em `docs/hbtrack/modulos/<module>/`;
3. implementacao em `src/<module>/`.

Fontes soberanas que este documento **consome**, mas nao substitui:

- `.contract_driven/templates/api/api_rules.yaml` para convencoes HTTP;
- `contracts/openapi/paths/<module>.yaml` para endpoints;
- `contracts/schemas/<module>/` para shapes reutilizaveis;
- `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`;
- `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`;
- `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md` quando existir;
- `docs/hbtrack/modulos/<module>/PERMISSIONS_<MODULE>.md`.

Quando `src/<module>/generated/` existir, ele deve ser tratado como derivado do source graph
compilado, dos contratos soberanos em `contracts/**` e das docs normativas do modulo. Nenhum
arquivo em `generated/` pode introduzir regras, campos ou fluxos nao presentes nesses artefatos.

## 4. Ausencias atuais que o agente nao pode assumir

Os seguintes artefatos **nao** existem hoje no backend materializado:

- `config/celery.py`;
- `src/<module>/tasks.py`;
- configuracao `CHANNEL_LAYERS`;
- `frontend/`.

Consequencia operacional:

- Celery, workers periodicos e WebSocket continuam sendo target-state aprovado, nao arquitetura de codigo atual;
- qualquer claim de task queue no backend precisa apontar para ADR/target-state, nao para arquivo presente;
- qualquer claim de frontend em runtime precisa apontar para `FRONTEND_CONTRACT.md`, nao para o workspace atual.

## 5. Regras de implementacao que continuam validas

- nenhum endpoint pode ser implementado sem contrato OpenAPI;
- `api.py` implementa o contrato, mas nao define as regras de negocio soberanas;
- `application/use_cases.py` e a camada de orquestracao principal;
- `domain/` nao depende de `infrastructure/`;
- testes do modulo vivem em `src/<module>/tests/`, nao em `tests/<module>/`;
- `src/<module>/generated/` e zona derivada; adaptadores canônicos podem compor essa camada, mas a
  autoridade continua em `docs/_canon`, `.contract_driven`, `docs/hbtrack/modulos/<module>/` e
  `contracts/**`;
- quando uma feature virar codigo canônico, `FEATURE_REGISTRY.yaml` deve sair de `validated` para `implemented`.

## 6. Referencias

- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [MODULE_REGISTRY.yaml](./MODULE_REGISTRY.yaml)
- [FEATURE_REGISTRY.yaml](./FEATURE_REGISTRY.yaml)
- [docs/_canon/decisions/ADR-031-backend-framework.md](./decisions/ADR-031-backend-framework.md)
- [.contract_driven/templates/api/api_rules.yaml](/home/davis/HB-TRACK/.contract_driven/templates/api/api_rules.yaml)
