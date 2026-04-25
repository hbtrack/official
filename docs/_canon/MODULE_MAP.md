---
doc_type: canon
version: "1.2.0"
last_reviewed: "2026-04-24"
status: active
state_semantics: governance
---

# Mapa de Modulos — HB Track

## 0. Objetivo e limite de autoridade

Este documento existe para:

- explicar a taxonomia tecnica dos 17 modulos canônicos;
- ajudar na escolha do modulo correto antes de contrato ou implementacao;
- explicitar boundaries criticas entre modulos;
- separar responsabilidade funcional de evidencia de runtime.

Este documento **nao** substitui:

- `MODULE_REGISTRY.yaml` para status lifecycle;
- `contracts/**` para superficies tecnicas soberanas;
- docs de modulo para regras detalhadas;
- `SYSTEM_SCOPE.md` para escopo macro de negocio.

## 1. Nota de taxonomia

Os macrodominios de negocio de `SYSTEM_SCOPE.md` sao agrupamentos de comunicacao. Os modulos abaixo sao a taxonomia tecnica fechada do sistema.

Regra fundamental: se um modulo nao estiver nesta lista, ele nao existe sem decisao formal registrada em `docs/_canon/decisions/`.

## 2. Evidencia transversal do repo atual

| Sinal | Evidencia atual |
|------|------------------|
| Backend app por modulo | 17/17 modulos possuem `src/<module>/` com `api.py`, `models.py`, `schemas.py`, `migrations/` e `tests/` |
| Contrato HTTP por modulo | 17/17 modulos possuem `contracts/openapi/paths/<module>.yaml` |
| JSON Schema por modulo | 17/17 modulos possuem `contracts/schemas/<module>/` |
| Docs minimas por modulo | 17/17 modulos possuem `README`, `MODULE_SCOPE`, `DOMAIN_RULES`, `INVARIANTS`, `TEST_MATRIX` |
| Worker runtime atual | 8 modulos possuem `src/<module>/tasks.py` (`ai_ingestion`, `analytics`, `audit`, `matches`, `notifications`, `reports`, `scout`, `video`) |
| Frontend runtime atual | `frontend/` existe com React/Vite, hooks API e testes |

Leitura correta:

- contratos e codigo backend estao amplamente materializados;
- UI web, ASGI/WebSocket e parte do runtime assíncrono ja estao materializados no repo;
- isso nao prova, por si só, operacao completa de producao nem cobertura funcional total por modulo.

## 3. Modulos funcionais (14)

| Modulo | Responsabilidade | Contratos e docs atualmente presentes | Runtime atual comprovado |
|--------|------------------|----------------------------------------|--------------------------|
| `users` | perfis, preferencias e dados cadastrais sem auth | OpenAPI, JSON Schema, docs minimas, `PERMISSIONS_USERS`, workflow | app Django + router + migrations + testes |
| `seasons` | temporadas, mesociclos e microciclos | OpenAPI, JSON Schema, docs minimas, `PERMISSIONS_SEASONS`, workflow | app Django + router + migrations + testes |
| `teams` | equipes e composicao de elenco | OpenAPI, JSON Schema, docs minimas, `PERMISSIONS_TEAMS`, workflow | app Django + router + migrations + testes |
| `training` | sessoes de treino, blocos, objetivos, feedback e execucao | OpenAPI, JSON Schema, docs minimas, `STATE_MODEL`, `SPORT_SCIENCE_RULES`, `ERRORS`, `UI_CONTRACT`, `SCREEN_MAP`, workflows e mensagens/eventos | app Django + router + migrations + testes; sem worker runtime atual |
| `wellness` | check-in diario, PSE, carga, sono e energia | OpenAPI, JSON Schema, docs minimas, `SPORT_SCIENCE_RULES`, workflow, mensagens/eventos | app Django + router + migrations + testes |
| `medical` | lesoes, historico medico e retorno ao jogo | OpenAPI, JSON Schema, docs minimas, `SPORT_SCIENCE_RULES` | app Django + router + migrations + testes |
| `competitions` | torneios, fases e classificacao | OpenAPI, JSON Schema, docs minimas, workflow | app Django + router + migrations + testes |
| `matches` | partidas, placar e eventos oficiais | OpenAPI, JSON Schema, docs minimas, workflow | app Django + router + migrations + testes |
| `scout` | analise tatica e eventos detalhados de jogo | OpenAPI, JSON Schema, docs minimas, workflow, mensagens/eventos | app Django + router + migrations + testes |
| `exercises` | biblioteca de exercicios e metadados | OpenAPI, JSON Schema, docs minimas, workflow | app Django + router + migrations + testes |
| `analytics` | metricas agregadas e consultas analiticas | OpenAPI, JSON Schema, docs minimas, `ERRORS_ANALYTICS` | app Django + router + migrations + testes |
| `reports` | empacotamento e entrega de relatorios | OpenAPI, JSON Schema, docs minimas, workflow | app Django + router + migrations + testes |
| `ai_ingestion` | ingestao externa e jobs de importacao | OpenAPI, JSON Schema, docs minimas, workflow, mensagens/eventos | app Django + router + migrations + testes |
| `video` | captura, sessao de midia, clipping e distribuicao tecnica | OpenAPI, JSON Schema, docs minimas, `STATE_MODEL_VIDEO`, workflows e mensagens/eventos | app Django + router + migrations + testes; sem worker runtime atual |

## 4. Modulos transversais (3)

| Modulo | Responsabilidade | Contratos e docs atualmente presentes | Runtime atual comprovado |
|--------|------------------|----------------------------------------|--------------------------|
| `identity_access` | autenticacao, sessao, tokens, RBAC, MFA e autorizacao | OpenAPI, JSON Schema, docs minimas, `PERMISSIONS_IDENTITY_ACCESS`, workflow | app Django + router + migrations + testes |
| `audit` | trilha imutavel de auditoria e rastreabilidade | OpenAPI, JSON Schema, docs minimas, workflow, mensagens/eventos | app Django + router + migrations + testes |
| `notifications` | disparo e rastreio de notificacoes | OpenAPI, JSON Schema, docs minimas, workflow | app Django + router + migrations + testes |

## 5. Deltas target-state ainda nao materializados

Os seguintes itens aparecem em ADRs, contratos ou docs aprovadas, mas ainda nao podem ser lidos como operacao completa de runtime:

- worker dedicado por modulo em producao;
- deploy validado do frontend para todos os fluxos previstos;
- WebSocket/Channels com operacao comprovada em ambiente produtivo;
- adapters externos operacionais de notificacao, storage e BI.

## 6. Fronteiras criticas

| Fronteira | Separacao obrigatoria |
|-----------|-----------------------|
| `users` vs `identity_access` | perfil da pessoa nunca se mistura com credencial, sessao ou RBAC |
| `training` vs `exercises` | `training` e operacao contextual; `exercises` e biblioteca reutilizavel |
| `matches` vs `scout` | `matches` e registro oficial; `scout` e leitura analitica derivada |
| `wellness` vs `medical` | `wellness` e auto-relato operacional; `medical` e informacao clinica |
| `analytics` vs `reports` | metrica nasce em `analytics`; `reports` apenas empacota saida |
| `competitions` vs `matches` | competicao estrutura o torneio; partida tem lifecycle proprio |

## 7. Como usar este mapa no fluxo contract-driven

Antes de criar contrato ou codigo, responder:

1. qual modulo e autoridade do comportamento?
2. a regra e funcional ou transversal?
3. existe boundary critica ja normatizada?
4. o fluxo precisa de ADR porque continua ambiguo?

Se a resposta continuar ambigua, a acao correta e `Decision Discovery`, nao inferencia.

## 8. Referencias

- [SYSTEM_SCOPE.md](./SYSTEM_SCOPE.md)
- [MODULE_REGISTRY.yaml](./MODULE_REGISTRY.yaml)
- [.contract_driven/CONTRACT_SYSTEM_RULES.md](/home/davis/HB-TRACK/.contract_driven/CONTRACT_SYSTEM_RULES.md)
- [.contract_driven/CONTRACT_SYSTEM_LAYOUT.md](/home/davis/HB-TRACK/.contract_driven/CONTRACT_SYSTEM_LAYOUT.md)
