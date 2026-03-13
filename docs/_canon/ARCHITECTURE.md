---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-11"
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
Router (FastAPI)
  └── Service (lógica de negócio, invariantes C1/C2)
        └── Repository (acesso a dados, SQLAlchemy)
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
| Python | **3.11.9** | Runtime backend — versão mandatória local e VPS |
| FastAPI | latest compat. | Framework HTTP — roteamento, validação de request/response |
| SQLAlchemy | latest compat. | ORM — mapeamento objeto-relacional |
| Alembic | latest compat. | Migrations — versionamento de schema do banco |
| Celery | latest compat. | Workers assíncronos — tarefas background e periódicas |
| Redis | **7 (Alpine)** | Broker Celery + cache de aplicação |
| PostgreSQL | **15** (VPS prod/staging) / **12** (dev local Docker) | Banco relacional principal |
| Next.js | **13+** | Framework frontend — App Router, SSR/RSC |
| TypeScript | latest compat. | Linguagem frontend — tipagem estática |
| TailwindCSS | latest compat. | Estilo — utility-first CSS |
| @dnd-kit | latest compat. | Drag & drop no frontend (treinos, planejamento) |
| pytest | latest compat. | Framework de testes backend |
| Schemathesis | latest compat. | Testes de contrato HTTP baseados em OpenAPI |
| Jest | latest compat. | Framework de testes frontend |

**Regra**: alterações de versão canônica para Python e PostgreSQL requerem atualização de `docs/_canon/contratos/Ambiente.md` e aprovação formal.

---

## 3. Estrutura de Camadas — Backend

```
┌─────────────────────────────────────────────────────────┐
│  Router (FastAPI)                                        │
│  - Validação de request/response via Pydantic           │
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
│  - Acesso a dados via SQLAlchemy                        │
│  - Queries, filtros, paginação                          │
│  - Sem lógica de negócio                               │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Database (PostgreSQL)                                   │
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
│  Pages / Layouts (Next.js App Router)                    │
│  - Server Components (RSC) para fetch inicial           │
│  - Client Components para interatividade                │
│  - Roteamento baseado em sistema de arquivos            │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Components (React)                                      │
│  - Componentes de UI reutilizáveis                      │
│  - Drag & drop via @dnd-kit                             │
│  - Estado local e global conforme complexidade          │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  API Client (gerado via OpenAPI generator)               │
│  - Gerado automaticamente a partir de openapi.json      │
│  - Localização: Hb Track - Frontend/src/api/generated/  │
│  - NUNCA editar manualmente — regenerar via script      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Backend API (FastAPI)                                   │
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
| Coexistência psycopg2 + psycopg3 | Mantida intencionalmente | Compatibilidade com SQLAlchemy e drivers de migração. Nunca remover nenhum dos dois. |

---

## 7. Ambiente Local vs. Produção

Para especificação completa de ambiente, consulte `docs/_canon/contratos/Ambiente.md` — esse documento é o SSOT para toda questão de infraestrutura.

**Resumo de referência rápida**:

| Item | Local (dev) | VPS (prod/staging) |
|------|------------|-------------------|
| PostgreSQL | 12 (Docker, porta **5433**) | 15 (porta **5432**) |
| Redis | 7-Alpine (porta 6379) | TBD — ver Ambiente.md §3 |
| Container DB | `hbtrack-postgres-dev` | `postgres15` |
| OS | Docker (Windows 11) | Ubuntu 20.04.6 LTS |
| Python | 3.11.9 | 3.11.9 |

**Regra**: nenhum deploy, backup ou migration no VPS sem confirmar versão do PostgreSQL em `docs/_canon/contratos/Ambiente.md`.

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
- Alterar versão canônica de Python ou PostgreSQL sem atualizar `Ambiente.md`

---

## 9. Referências

- `SYSTEM_SCOPE.md` — missão, atores, macrodomínios
- `MODULE_MAP.md` — taxonomia técnica dos 16 módulos
- `.contract_driven/templates/api/api_rules.yaml` — SSOT de convenções/templates/validações de API HTTP
- `API_CONVENTIONS.md` — guia/ponteiros (não-SSOT) para API
- `DATA_CONVENTIONS.md` — convenções de dados
- `docs/_canon/contratos/Ambiente.md` — especificação completa de ambiente (SSOT)
- `.contract_driven/CONTRACT_SYSTEM_RULES.md` — regras operacionais do CDD
