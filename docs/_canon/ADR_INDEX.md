---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-23"
status: active
state_semantics: governance
---

# Índice de Decisões Arquiteturais — HB Track

## 0. Objetivo e limite de autoridade

Este índice é o **ponto único de entrada para localizar e resolver referências a ADRs** no
HB Track. Ele garante que toda referência a uma decisão arquitetural seja rastreável sem
ambiguidade.

**Regras de uso:**
- Toda nova ADR deve ser adicionada aqui imediatamente após criação.
- IDs são únicos e nunca reutilizados, mesmo após supersession.
- Quando uma ADR for supersedida, atualizar as colunas `status` e `superseded_by` aqui e no
  front matter do arquivo correspondente.
- Conflito entre este índice e o front matter de uma ADR individual → abrir revisão; o front
  matter individual é soberano para o conteúdo; este índice é soberano para rastreabilidade.

**Não existe:** ADR sem ID único. Dois documentos com o mesmo ID é um erro de governança que
deve ser corrigido imediatamente.

---

## 1. Índice completo

### Grupo: Metodologia e Governança de Contratos

| ID | Título | Status | Supersede | Supersedida por | Tema |
|----|--------|--------|-----------|-----------------|------|
| ADR-001 | Adotar Contract-Driven Development | accepted | — | — | metodologia, cdd, governança |
| ADR-004 | API Policy Compiler Authority | accepted | — | — | governança, compilador, pipeline |
| ADR-005 | Instituir SPORT_SCIENCE_RULES como artefato canônico | accepted | — | — | governança, regras de domínio |
| ADR-014 | Deprecation Policy | accepted | — | — | api-lifecycle, versionamento |
| ADR-015 | Agent Execution Log | accepted | — | — | governança de agentes, observabilidade |
| ADR-016 | MCP Surface | **deferred** | — | — | ferramentas de agente, integração externa |
| ADR-024 | Contract Versioning Strategy | accepted | — | — | versionamento, contratos, api |
| ADR-025 | CDCT — Pact Strategy | accepted | — | — | testes, pact, integração |
| ADR-034 | Scope Boundary Validation — Cross-Module | **proposed** | — | — | governança, validação de boundary |

---

### Grupo: Segurança, Autenticação e Privacidade

| ID | Título | Status | Supersede | Supersedida por | Tema |
|----|--------|--------|-----------|-----------------|------|
| ADR-007 | Estratégia de Autenticação — JWT RS256 | accepted | — | — | segurança, autenticação, identity_access |
| ADR-008 | Estratégia de Autorização — RBAC | accepted | — | — | segurança, autorização, identity_access |
| ADR-010 | Sensitive Data Policy — PII/PHI | accepted | — | — | privacidade, mascaramento, LGPD |
| ADR-011 | Retention Policy | accepted | — | — | retenção de dados, privacidade, LGPD |
| ADR-012 | Secrets Policy | accepted | — | — | segurança, credenciais, rotação |

---

### Grupo: Convenções de Dados e API

| ID | Título | Status | Supersede | Supersedida por | Tema |
|----|--------|--------|-----------|-----------------|------|
| ADR-002 | UUID v4 como Identificadores | accepted | — | — | convenções, identificadores, api |
| ADR-003 | Media Type Versioning | accepted | — | — | api-design, versionamento |
| ADR-009 | Datetime e Timezone Standard | accepted | — | — | convenções, datetime, matches |

---

### Grupo: Arquitetura de Sistema e Backend

| ID | Título | Status | Supersede | Supersedida por | Tema |
|----|--------|--------|-----------|-----------------|------|
| ADR-018 | Hybrid Persistence Pattern | accepted | — | — | arquitetura, persistência, event-sourcing |
| ADR-019 | Layer Separation: Domain / DTO / ViewModel | accepted | — | — | arquitetura, camadas |
| ADR-026 | Code Architecture — Clean Architecture + Ports & Adapters | **superseded** | — | ADR-031 | arquitetura, fastapi (obsoleto) |
| ADR-028 | Data Migration Strategy | accepted (§Ferramenta supersedida) | — | ADR-031 (§Ferramenta) | migrações, banco de dados |
| ADR-031 | Backend Framework: Django Ninja | accepted | ADR-026, ADR-028 (§Ferramenta) | — | stack backend, django, ninja |

---

### Grupo: Frontend

| ID | Título | Status | Supersede | Supersedida por | Tema |
|----|--------|--------|-----------|-----------------|------|
| ADR-030 | Frontend Strategy — React + Vite | accepted | — | — | frontend, react, vite, target-state |

---

### Grupo: Observabilidade e Operações

| ID | Título | Status | Supersede | Supersedida por | Tema |
|----|--------|--------|-----------|-----------------|------|
| ADR-013 | Logging Policy e Observabilidade (X-Flow-ID) | accepted | — | — | observabilidade, logging, tracing |
| ADR-029 | Runtime Monitoring | accepted | — | — | monitoramento, runtime |

---

### Grupo: Deploy e Infraestrutura

| ID | Título | Status | Supersede | Supersedida por | Tema |
|----|--------|--------|-----------|-----------------|------|
| ADR-027 | Deploy Pipeline | accepted | — | — | deploy, ci/cd, infraestrutura |

---

### Grupo: Domínio e Módulos

| ID | Título | Status | Supersede | Supersedida por | Tema |
|----|--------|--------|-----------|-----------------|------|
| ADR-006 | Inserção do Decision Support System | accepted | — | — | dss, analytics, domínio |
| ADR-017 | Training Session State Machine | accepted | — | — | training, FSM, domínio |
| ADR-021 | Media Delivery Boundary | accepted | — | — | exercises, mídia, boundary |
| ADR-032 | Training Arch Decisions | accepted | — | — | training, arquitetura, invariantes |
| ADR-033 | Video como 17º Módulo Canônico | accepted | — | — | vídeo, módulos, mídia |

---

## 2. ADRs com pendências ou estado especial

| ID | Situação | Ação necessária |
|----|----------|-----------------|
| ADR-016 | Status `deferred` — MCP surface não implementado | Rever quando MCP for priorizado no roadmap |
| ADR-026 | Supersedida por ADR-031 | Manter apenas como referência histórica; não usar para implementação |
| ADR-028 | §Ferramenta (Alembic) supersedida por ADR-031; §Estratégia still valid | Leitura: usar Django Migrations; estratégia de migração do ADR-028 continua válida |
| ADR-034 | Status `proposed` — boundary validation | Promover para `accepted` quando implementação do gate for concluída |

---

## 3. Arquivos no diretório `decisions/`

```
docs/_canon/decisions/
  ADR-001-contract-driven-development.md
  ADR-002-uuid-v4-identifiers.md
  ADR-003-media-type-versioning.md
  ADR-004-api-policy-compiler-authority.md
  ADR-005-sports-science-rules-module.md
  ADR-006-Inserção-Decision-Support-System.md
  ADR-007-auth-strategy.md
  ADR-008-authz-strategy.md
  ADR-009-datetime-timezone-standard.md
  ADR-010-sensitive-data-policy.md
  ADR-011-retention-policy.md
  ADR-012-secrets-policy.md
  ADR-013-logging-policy.md
  ADR-014-deprecation-policy.md
  ADR-015-agent-execution-log.md
  ADR-016-mcp-surface.md                       ← deferred
  ADR-017-training-session-state-machine.md
  ADR-018-hybrid-persistence-pattern.md
  ADR-019-layer-separation-domain-dto-viewmodel.md
  ADR-021-media-delivery-boundary.md
  ADR-024-contract-versioning-strategy.md
  ADR-025-cdct-pact-strategy.md
  ADR-026-code-architecture.md                  ← superseded por ADR-031
  ADR-027-deploy-pipeline.md
  ADR-028-data-migration-strategy.md            ← §Ferramenta supersedida por ADR-031
  ADR-029-runtime-monitoring.md
  ADR-030-frontend-strategy.md
  ADR-031-backend-framework.md                  ← supersede ADR-026 + ADR-028 §Ferramenta
  ADR-032-training-arch-decisions.md
  ADR-033-video-module-canonicalization.md
  ADR-034-scope-boundary-validation.md          ← proposed
  README.md
```

**IDs ausentes (intencionais):** ADR-020, ADR-022, ADR-023 — números não foram atribuídos;
não representam ADRs deletadas.

---

## 4. Regras de numeração para novas ADRs

1. O próximo ID disponível é **ADR-035**.
2. IDs são sequenciais e nunca reutilizados.
3. Ao criar uma nova ADR: adicionar linha neste índice antes de commitar o arquivo.
4. Ao superseder uma ADR: atualizar `status` e `superseded_by` aqui **e** no front matter
   do arquivo individual.

---

## 5. Referências

- [DECISION_POLICY.md](./DECISION_POLICY.md)
- [ARCHITECTURE_DECISION_BACKLOG.md](./ARCHITECTURE_DECISION_BACKLOG.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)
