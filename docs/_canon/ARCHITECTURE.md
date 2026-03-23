---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-23"
status: active
---

# Arquitetura — HB Track

## 1. Princípios Arquiteturais

O HB Track é governado por 5 princípios arquiteturais. Toda decisão técnica deve ser avaliada contra eles.

### Princípio 1 — Contract-First

Todo componente público possui contrato OpenAPI antes de implementação. Isso se aplica a:
- Endpoints HTTP (OpenAPI)
- Eventos assíncronos (AsyncAPI quando aplicável)
- Workflows multi-step (Arazzo quando aplicável)
- Schemas compartilhados entre módulos

Nenhum endpoint nasce primeiro no código. O contrato é o artefato que habilita implementação.

### Princípio 2 — Monólito Modular

O HB Track é um monólito com modularidade lógica, não física. Módulos são unidades de coesão de domínio — não microserviços. O acoplamento entre módulos é explícito e declarado; chamadas cruzadas que não passam pelo contrato de módulo são proibidas.

Vantagens deste modelo: simplicidade operacional, transações ACID entre entidades relacionadas, sem overhead de comunicação inter-serviço.

Restrição: boundaries de módulo não podem ser violados por conveniência de implementação.

### Princípio 3 — Separação de Camadas

O fluxo de controle segue estritamente a hierarquia:

```
Router (Django Ninja)
  └── Service (lógica de negócio, invariantes C1/C2)
        └── Repository (acesso a dados, Django ORM)
              └── Database (PostgreSQL — constraints A/B)
```

É proibido pular camadas. Router não acessa banco. Service não faz queries SQL diretamente. Repository não contém lógica de negócio.

### Princípio 4 — Imutabilidade de Invariantes

Constraints críticas de negócio (invariantes classe A e B) vivem no banco de dados como CHECK constraints e triggers — não apenas no código de aplicação. Isso garante integridade independente do caminho de acesso (API, admin, scripts, migrations).

Invariantes aprovadas (`INV-*`) só mudam por processo formal documentado em `CHANGE_POLICY.md`.

### Princípio 5 — Observabilidade

O header `X-Flow-ID` é propagado em todas as camadas do sistema: requests HTTP → workers Celery → eventos assíncronos. Toda operação rastreável deve carregar e propagar esse identificador para permitir correlação de logs e diagnóstico de falhas.

---

## 2. Stack Canônica

| Tecnologia | Versão Canônica | Papel |
|-----------|----------------|-------|
| Python | **3.12** | Runtime backend — versão mandatória local e VPS _(ADR-031)_ |
| Django | **5.x** | Framework backend — models, admin, auth, ORM _(ADR-031)_ |
| Django Ninja | **1.x** | HTTP API layer — roteamento, validação de request/response _(ADR-031)_ |
| Django ORM | nativo | ORM — mapeamento objeto-relacional _(ADR-031, substitui SQLAlchemy)_ |
| Django Migrations | nativo | Migrations — versionamento de schema do banco _(ADR-031, substitui Alembic)_ |
| Django Channels | **4.x** | WebSocket — notificações em tempo real _(ADR-031)_ |
| Celery | **5.x** | Workers assíncronos — tarefas background e periódicas |
| Redis | **7 (Alpine)** | Broker Celery + cache de aplicação |
| PostgreSQL | **16** | Banco relacional principal — prod/staging e dev local _(ADR-031)_ |
| React | **18** | Framework frontend _(ADR-030, FRONTEND_CONTRACT.md)_ |
| Vite | **5.x** | Build tool frontend _(ADR-030, FRONTEND_CONTRACT.md)_ |
| TypeScript | latest compat. | Linguagem frontend — tipagem estática |
| React Router | **v6** | Roteamento frontend _(FRONTEND_CONTRACT.md)_ |
| Tailwind CSS | latest compat. | Estilo — utility-first CSS |
| shadcn/ui | latest compat. | Componentes de UI _(FRONTEND_CONTRACT.md)_ |
| Zustand | latest compat. | Estado global frontend _(FRONTEND_CONTRACT.md)_ |
| openapi-typescript | latest compat. | Geração de tipos TypeScript a partir do contrato OpenAPI |
| openapi-fetch | latest compat. | HTTP client frontend — gerado a partir do contrato OpenAPI _(FRONTEND_CONTRACT.md)_ |
| pytest + pytest-django | latest compat. | Framework de testes backend |
| Vitest + Testing Library | latest compat. | Testes unitários frontend _(FRONTEND_CONTRACT.md, substitui Jest)_ |
| Playwright | latest compat. | Testes E2E _(FRONTEND_CONTRACT.md)_ |
| Schemathesis | latest compat. | Testes de contrato HTTP baseados em OpenAPI |
| React Native + Expo | latest compat. | Mobile — v2.0 _(ADR-030)_ |

**Regra**: alterações de versão canônica para Python e PostgreSQL requerem atualização deste documento e, quando houver impacto operacional, de `docs/_canon/DEPLOY_PIPELINE.md`, além de aprovação formal.

---

## 3. Estrutura de Camadas — Backend

```
┌─────────────────────────────────────────────────────────┐
│  Router (Django Ninja)                         ADR-031   │
│  - Validação de request/response via Pydantic/Schema    │
│  - Autenticação e autorização (via identity_access)     │
│  - Serialização e desserialização de payloads           │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Service                                                 │
│  - Lógica de negócio e regras de domínio                │
│  - Invariantes C1 (puras) e C2 (service + DB)           │
│  - Orquestração de operações entre repositórios         │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Repository                                              │
│  - Acesso a dados via Django ORM                        │
│  - Queries, filtros, paginação                          │
│  - Sem lógica de negócio                               │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Database (PostgreSQL 16)                                │
│  - Invariantes A (CHECK constraints)                    │
│  - Invariantes B (triggers)                             │
│  - Índices parciais para soft delete                    │
└─────────────────────────────────────────────────────────┘
```

**Workers Celery**: seguem a mesma estrutura Service → Repository → Database. Não possuem camada Router. São acionados por tarefas enfileiradas no Redis.

**Classificação de invariantes por camada**:
- Classe A: constraint de banco (CHECK, UNIQUE, NOT NULL, FK)
- Classe B: trigger de banco
- Classe C1: service puro (sem acesso a banco, verificável por teste unitário)
- Classe C2: service + banco (verificável por teste de integração)
- Classe D: router / RBAC (verificável por teste de endpoint)
- Classe E1/E2: Celery (task síncrona/assíncrona)
- Classe F: OpenAPI (verificável por Schemathesis)

---

## 4. Estrutura de Camadas — Frontend

```
┌─────────────────────────────────────────────────────────┐
│  Pages / Routes (React + React Router v6)      ADR-030   │
│  - Componentes de página e layout                       │
│  - Roteamento via React Router v6                       │
│  - Estado de servidor via React Query                   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Components (React + shadcn/ui)                          │
│  - Componentes de UI reutilizáveis                      │
│  - Estado local (useState) e global (Zustand)           │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  API Client (gerado via openapi-typescript)              │
│  - Tipos gerados de openapi.yaml → frontend/src/api/    │
│  - HTTP via openapi-fetch                               │
│  - NUNCA editar manualmente — regenerar via npm run gen:api │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Backend API (Django Ninja)                              │
│  - HTTP/REST sobre contratos OpenAPI                    │
│  - JWT Bearer via header Authorization                  │
└─────────────────────────────────────────────────────────┘
```

**Regra**: o cliente HTTP do frontend deve ser sempre o gerado. Chamadas HTTP manuais fora do cliente gerado são proibidas em código de produção.

---

## 5. Diagrama C4

Os diagramas C4 formais vivem em:

- `docs/_canon/C4_CONTEXT.md`
- `docs/_canon/C4_CONTAINERS.md`

A estrutura de camadas das seções 3 e 4 deste documento continua sendo a referência arquitetural primária para implementação.

---

## 6. Decisões Arquiteturais Registradas

As ADRs formais são registradas em `docs/_canon/decisions/`.

As decisões abaixo já foram tomadas e são normativas:

| Decisão | Escolha | Justificativa |
|---------|---------|---------------|
| Nomenclatura de campos JSON | `camelCase` | SSOT de API: `.contract_driven/templates/api/api_rules.yaml` (`canonical_conventions.naming.json_fields.style`). |
| Estratégia de paginação | Cursor via `pageSize` + `pageToken` (+ `nextPageToken`) | SSOT de API: `.contract_driven/templates/api/api_rules.yaml` (`design_rules.google_aip_core.pagination`). |
| Estratégia de IDs | UUID v4 como string | Sem IDs sequenciais expostos. UUIDs gerados pelo banco (PostgreSQL `gen_random_uuid()`) ou pela aplicação. |
| Versioning de API | Sem versão na URI; compatibilidade via content-negotiation/media-type quando necessário | SSOT de API: `.contract_driven/templates/api/api_rules.yaml` (`versioning_and_compatibility`). |
| Soft delete | `deleted_at` + `deleted_reason` | Par obrigatório: nenhum campo `deleted_at` sem `deleted_reason` correspondente e vice-versa. |
| Separação `users` vs `identity_access` | `users` = perfil; `identity_access` = auth/authz | Boundary explícito: mistura de responsabilidades é proibida sem ADR formal. |
| Coexistência psycopg2 + psycopg3 | Mantida intencionalmente | Compatibilidade com toolchain legado e utilitários de migração. Nunca remover sem validação explícita. |
| Estratégia de autenticação | JWT RS256, 15min access / 7d refresh com rotation, jti blacklist Redis | ADR-007 — SSOT completo em `decisions/ADR-007-auth-strategy.md`. |
| Estratégia de autorização | RBAC flat 5 roles, deny-by-omission, BOLA/BOPLA/BFLA por camada | ADR-008 — SSOT completo em `decisions/ADR-008-authz-strategy.md`. |
| Padrão de data/hora e timezone | UTC obrigatório, RFC 3339 `Z`, `venueTimezone` IANA em partidas | ADR-009 — formaliza `DATA_CONVENTIONS.md §2` como normativo. |
| Classificação de dados sensíveis | PII / PHI / CREDENTIALS / BUSINESS_SENSITIVE com mascaramento em logs | ADR-010 — SSOT em `decisions/ADR-010-sensitive-data-policy.md`. |
| Política de retenção | 2a auditoria, 5a PHI, indefinido histórico esportivo; purge 30d pós-exclusão | ADR-011 — SSOT em `decisions/ADR-011-retention-policy.md`. |
| Gerenciamento de secrets | .env + VPS env vars, JWT key rotation 90 dias, GitHub Actions secrets | ADR-012 — SSOT em `decisions/ADR-012-secrets-policy.md`. |
| Logging e observabilidade | JSON estruturado, stdout, X-Flow-ID, PHI/CREDENTIALS nunca logados | ADR-013 — SSOT em `decisions/ADR-013-logging-policy.md`. |
| Política de deprecação | RFC 8594 headers, 90d interno / 180d externo, `deprecated: true` em OpenAPI | ADR-014 — formaliza `CHANGE_POLICY.md §7` como normativo. |
| Log de execução de agente | JSON em `_reports/agent_execution/`, retenção 30 dias | ADR-015 — SSOT em `decisions/ADR-015-agent-execution-log.md`. |
| Exposição MCP | Adiada para pós-v1.0 — ADR de deferral formal | ADR-016 — `decisions/ADR-016-mcp-surface.md`. |

---

## 6A. Estágio Decision Discovery (DSS)

Antes de `contract_creation_mode` e `contract_revision_mode`, o sistema exige um estágio formal de **Decision Discovery** quando há lacuna arquitetural relevante.

O estágio é regido integralmente por `docs/_canon/DECISION_POLICY.md` e operacionalizado pelo prompt `.contract_driven/agent_prompts/decision_discovery.prompt.md`.

**Resumo das regras**:
- Decision Discovery precede contratos — não substitui artefatos canônicos.
- O DSS é apoio à decisão humana; nenhuma sugestão é executada silenciosamente.
- Decisões aprovadas são promovidas para `docs/_canon/decisions/ADR-*.md`.
- Decisões `obrigatórias` sem ADR aprovada bloqueiam com `BLOCKED_MISSING_ARCH_DECISION`.
- O backlog de decisões em aberto é mantido em `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md`.

**Referência normativa**: `docs/_canon/DECISION_POLICY.md` (SSOT desta camada).

---

## 7. Ambiente Local vs. Produção

Este documento consolida o baseline atual de ambiente. Não existe um `Ambiente.md` separado e soberano; detalhes operacionais adicionais de deploy vivem em `docs/_canon/DEPLOY_PIPELINE.md`.

**Resumo de referência rápida**:

| Item | Local (dev) | VPS (prod/staging) |
|------|------------|-------------------|
| PostgreSQL | 16 (Docker, porta **5433**) | 16 (porta **5432**) |
| Redis | 7-Alpine (porta 6379) | TBD — registrar baseline final em `DEPLOY_PIPELINE.md` |
| Container DB | `hbtrack-postgres-dev` | `postgres15` |
| OS | Docker (Windows 11) | Ubuntu 20.04.6 LTS |
| Python | 3.11.9 | 3.11.9 |

**Regra**: nenhum deploy, backup ou migration no VPS sem confirmar a versão vigente do PostgreSQL neste documento e no `DEPLOY_PIPELINE.md`, quando aplicável.

---

## 8. Restrições Arquiteturais

As seguintes ações são proibidas sem ADR formal aprovada:

- Criar interface HTTP pública fora de contrato OpenAPI
- Criar payload estável fora de schema canônico
- Criar workflow multi-step sem Arazzo quando formalmente exigido
- Criar evento assíncrono sem AsyncAPI quando formalmente exigido
- Criar regra esportiva sem rastreio para `HANDBALL_RULES_DOMAIN.md`
- Misturar responsabilidades de `users` e `identity_access`
- Remover psycopg2 ou psycopg3 unilateralmente
- Alterar versão canônica de Python ou PostgreSQL sem atualizar este documento e o `DEPLOY_PIPELINE.md` quando houver impacto operacional
- Criar/revisar contrato com decisão arquitetural `obrigatória` em aberto sem ADR aprovada (ver `ARCHITECTURE_DECISION_BACKLOG.md`)

---

## 9. Referências

- `SYSTEM_SCOPE.md` — missão, atores, macrodomínios
- `MODULE_MAP.md` — taxonomia técnica dos 17 módulos
- `.contract_driven/templates/api/api_rules.yaml` — SSOT de convenções/templates/validações de API HTTP
- `API_CONVENTIONS.md` — guia/ponteiros (não-SSOT) para API
- `DATA_CONVENTIONS.md` — convenções de dados
- `docs/_canon/DEPLOY_PIPELINE.md` — detalhes operacionais e status atual de deploy
- `.contract_driven/CONTRACT_SYSTEM_RULES.md` — regras operacionais do CDD
- `docs/_canon/DECISION_POLICY.md` — regras do estágio Decision Discovery (DSS)
- `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` — decisões arquiteturais em aberto
