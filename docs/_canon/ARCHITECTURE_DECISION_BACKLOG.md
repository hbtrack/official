---
doc_type: canon
version: "1.1.0"
last_reviewed: "2026-03-15"
status: active
adr_origin: ADR-006-Inserção-Decision-Support-System
---

# Architecture Decision Backlog — HB Track

## 0. Objetivo

Este documento registra decisões arquiteturais que ainda precisam de ADR formal aprovada.

Ele é mantido como artefato canônico vivo: entradas são adicionadas quando identificadas pelo estágio `Decision Discovery` e removidas (ou marcadas como `resolved`) quando a ADR correspondente é aprovada.

**Este documento não é SSOT de nenhuma decisão.**
Ele é apenas um backlog de trabalho. A SSOT de cada decisão é o arquivo `ADR-*.md` correspondente.

Leia junto com:
- `docs/_canon/DECISION_POLICY.md` — regras de classificação e promoção
- `.contract_driven/agent_prompts/decision_discovery.prompt.md` — prompt operacional
- `docs/_canon/decisions/` — ADRs aprovadas

---

## 1. Status possíveis

| Status | Significado |
|--------|-------------|
| `open` | Decisão identificada, aguardando análise ou aprovação |
| `in_discovery` | Estágio `Decision Discovery` em andamento |
| `pending_approval` | Proposta DSS gerada, aguarda aprovação humana |
| `resolved` | ADR aprovada e promovida |
| `deferred` | Postergada conscientemente — revisar antes de v1.0 |
| `wont_fix` | Descartada formalmente — registrar motivo |

---

## 2. Decisões em Aberto

> **Estado atual (2026-03-15):** todas as 10 decisões do backlog inicial (ARCH-001 a ARCH-010) foram promovidas para ADRs formais. Não há decisões abertas no momento. Novas entradas serão adicionadas conforme identificadas pelo estágio `Decision Discovery`.

### ARCH-001 — Estratégia de Autenticação (AUTH_STRATEGY)

| Campo | Valor |
|-------|-------|
| ID | ARCH-001 |
| Criticidade | **obrigatória** |
| Status | resolved — ADR-007 |
| Módulos afetados | `identity_access`, todos os módulos com endpoints protegidos |
| Bloqueio | `BLOCKED_MISSING_ARCH_DECISION` se contrato de produção for criado sem esta decisão |
| Contexto | O sistema usa JWT Bearer (`Authorization: Bearer <token>`) conforme placeholders nos templates, mas não há ADR formal definindo: algoritmo de assinatura (RS256 vs HS256 vs ES256), rotação de chaves, claims mínimas obrigatórias, lifetime de access token, estratégia de refresh token, blacklist/revogação. |
| Referência | `docs/_canon/SECURITY_RULES.md`, `.contract_driven/templates/api/api_rules.yaml` |

---

### ARCH-002 — Estratégia de Autorização (AUTHZ_STRATEGY)

| Campo | Valor |
|-------|-------|
| ID | ARCH-002 |
| Criticidade | **obrigatória** |
| Status | resolved — ADR-008 |
| Módulos afetados | `identity_access`, todos os módulos com RBAC |
| Bloqueio | `BLOCKED_MISSING_ARCH_DECISION` se contrato com operações `admin` ou `role-restricted` for criado |
| Contexto | O sistema prevê RBAC (roles: admin, coordinator, coach, athlete, member) mas não há ADR formal definindo: modelo de roles (flat vs hierárquico), granularidade de permissões (endpoint vs operação vs recurso), herança de roles entre times/temporadas, BOLA/BOPLA enforcement strategy por módulo. |
| Referência | `docs/_canon/SECURITY_RULES.md`, `docs/_canon/CI_CONTRACT_GATES.md` (OWASP gate) |

---

### ARCH-003 — Padrão de Data/Hora e Política de Timezone (DATE_TIME_STANDARD + TIMEZONE_POLICY)

| Campo | Valor |
|-------|-------|
| ID | ARCH-003 |
| Criticidade | **obrigatória** |
| Status | resolved — ADR-009 |
| Módulos afetados | `matches`, `competitions`, `training`, `wellness`, `medical`, `analytics`, `seasons` |
| Bloqueio | `BLOCKED_MISSING_ARCH_DECISION` se campos `*_at`, `*_date` ou `*_time` forem criados em módulos acima |
| Contexto | O sistema usa `datetime` com ISO 8601 conforme `DATA_CONVENTIONS.md`, mas não há ADR formal definindo: UTC como padrão de armazenamento vs timezone local, estratégia de conversão para exibição, tratamento de jogos em fusos horários distintos, campos de timezone explícito obrigatório em eventos de partida. |
| Referência | `docs/_canon/DATA_CONVENTIONS.md` |

---

### ARCH-004 — Política de Dados Sensíveis e Mascaramento (SENSITIVE_DATA_POLICY + MASKING_POLICY)

| Campo | Valor |
|-------|-------|
| ID | ARCH-004 |
| Criticidade | **obrigatória** |
| Status | resolved — ADR-010 |
| Módulos afetados | `users`, `medical`, `identity_access`, `wellness` |
| Bloqueio | `BLOCKED_MISSING_ARCH_DECISION` se campos de dados pessoais ou médicos forem criados sem classificação |
| Contexto | O sistema prevê dados médicos e pessoais (atletas, prontuário, wellness) mas não há ADR formal definindo: taxonomia de classificação de sensibilidade (PII, PHI, credentials, business-sensitive), campos mascarados em logs, campos excluídos de relatórios de analytics, estratégia de anonimização para dados históricos. |
| Referência | `docs/_canon/SECURITY_RULES.md`, módulo `medical` |

---

### ARCH-005 — Política de Retenção de Dados (RETENTION_POLICY)

| Campo | Valor |
|-------|-------|
| ID | ARCH-005 |
| Criticidade | importante |
| Status | resolved — ADR-011 |
| Módulos afetados | `audit`, `medical`, `wellness`, `matches`, `analytics` |
| Deferred until | v1.0 (pré-produção) |
| Contexto | Não há ADR formal definindo: período de retenção por categoria de dado, processo de expurgo automático, implicações de LGPD para dados de atletas menores, política de backup e recuperação. |
| Referência | `docs/_canon/SECURITY_RULES.md` |

---

### ARCH-006 — Estratégia de Gerenciamento de Secrets e Rotação (SECRETS_POLICY + ROTATION_POLICY)

| Campo | Valor |
|-------|-------|
| ID | ARCH-006 |
| Criticidade | **obrigatória** |
| Status | resolved — ADR-012 |
| Módulos afetados | `identity_access`, infra, CI/CD |
| Bloqueio | `BLOCKED_MISSING_ARCH_DECISION` em qualquer contrato que referencie credenciais externas ou chaves de assinatura |
| Contexto | O sistema usa `.env` para secrets em desenvolvimento local mas não há ADR formal definindo: vault/secret manager para produção, rotação de chaves JWT, rotação de credenciais de banco, policy para segredos em CI/CD (GitHub Actions secrets), auditoria de acesso a secrets. |
| Referência | `docs/_canon/SECURITY_RULES.md`, `infra/docker-compose.yml` |

---

### ARCH-007 — Política de Logging e Observabilidade (LOGGING_POLICY)

| Campo | Valor |
|-------|-------|
| ID | ARCH-007 |
| Criticidade | importante |
| Status | resolved — ADR-013 |
| Módulos afetados | todos |
| Deferred until | v0.5 |
| Contexto | O sistema propaga `X-Flow-ID` (Princípio 5 de ARCHITECTURE.md) mas não há ADR formal definindo: formato canônico de log (JSON estruturado vs texto), nível de log por ambiente, quais campos são obrigatórios em cada log de operação crítica, política de não-logging de dados sensíveis, destino de logs em produção. |
| Referência | `docs/_canon/ARCHITECTURE.md` §1 Princípio 5 |

---

### ARCH-008 — Política de Depreciação de API (DEPRECATION_POLICY)

| Campo | Valor |
|-------|-------|
| ID | ARCH-008 |
| Criticidade | **obrigatória** |
| Status | resolved — ADR-014 |
| Módulos afetados | todos os módulos com endpoints públicos |
| Bloqueio | `BLOCKED_MISSING_ARCH_DECISION` antes da v1.0 |
| Contexto | O sistema tem ADR-003 para versionamento via media type mas não há ADR formal definindo: prazo mínimo de depreciação, header `Deprecation` e `Sunset` obrigatórios, processo de comunicação a consumidores, janela de coexistência de versões, critérios para remoção de versão depreciada. |
| Referência | `docs/_canon/CHANGE_POLICY.md`, `docs/_canon/decisions/ADR-003-media-type-versioning.md` |

---

### ARCH-009 — Política de Log de Execução de Agente (AGENT_EXECUTION_LOG)

| Campo | Valor |
|-------|-------|
| ID | ARCH-009 |
| Criticidade | importante |
| Status | resolved — ADR-015 |
| Módulos afetados | governança (transversal) |
| Deferred until | v0.5 |
| Contexto | O orquestrador pré-contrato (`.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md`) produz um bloco estruturado `[PRE_CONTRACT_ORCHESTRATOR]` a cada execução, mas não há ADR formal definindo: destino e formato canônico desse log (arquivo, stdout, `_reports/`), política de retenção do log de agente, campos obrigatórios (fase, módulo, bloqueios, artefatos lidos, worker destino), integração com `audit` ou com `_reports/contract_gates/`. Sem esta política, o audit trail de comportamento de agente exigido pelo Foundation Tier (InfoQ Agentic AI Architecture Framework) permanece informal. |
| Referência | `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` §Observabilidade, `docs/_canon/ARCHITECTURE.md` §1 Princípio 5 |

---

### ARCH-010 — Exposição de Tools Canônicos via MCP (MCP_SURFACE)

| Campo | Valor |
|-------|-------|
| ID | ARCH-010 |
| Criticidade | opcional |
| Status | deferred — ADR-016 (formal deferral pós-v1.0) |
| Módulos afetados | governança, `identity_access`, infra |
| Deferred until | v1.0 |
| Contexto | O artigo InfoQ "The Architectural Shift: AI Agents Become Execution Engines" (out. 2025) posiciona o Model Context Protocol (MCP) como protocolo universal de interação entre agentes e sistemas, análogo ao HTTP para a web. Atualmente, o HB Track expõe seus tools canônicos (gates, compiler, prompts) apenas via invocação manual. Não há ADR formal definindo: se/quando expor gates, contracts e compiler como MCP resources; modelo de autenticação para agentes externos via MCP; política de autorização granular por tool; implicações de segurança (SSRF, injection via MCP inputs); e relação com o ARCH_DECISION_PRESENCE_GATE para agentes externos. Esta decisão deve ser tomada antes de qualquer integração com plataformas de orquestração de agentes externas. |
| Referência | `docs/_canon/SECURITY_RULES.md`, `docs/_canon/decisions/ADR-006-Inserção-Decision-Support-System.md` |

---

### ARCH-011 — State Machine Canônica de `training_session`

| Campo | Valor |
|-------|-------|
| ID | ARCH-011 |
| Criticidade | **obrigatória** |
| Status | resolved — ADR-017 |
| Módulos afetados | `training` |
| Contexto | Três fontes definiam a state machine de `training_session` de formas incompatíveis: DOMAIN_AXIOMS.json global (6 estados, incluindo PLANNED sem equivalente operacional), INV-TRAIN-006 operacional (5 estados: draft/scheduled/in_progress/pending_review/readonly) e ARCH-DEC-TRAIN TRAIN-DEC-026 (7 estados com PUBLISHED e ARCHIVED). Conflito documentado como LAC-001 em CONTRACT_TRAINING.md §16. Identificado pelo estágio Decision Discovery em 2026-03-15. |
| Referência | `docs/_canon/decisions/ADR-017-training-session-state-machine.md` |

---

## 3. Decisões Resolvidas

| ID | Decisão | ADR | Data |
|----|---------|-----|------|
| — | Versionamento via media type | ADR-003 | 2026-03-11 |
| — | UUIDs v4 como identificadores | ADR-002 | 2026-03-11 |
| — | Contract-driven development | ADR-001 | 2026-03-11 |
| — | API Policy Compiler como autoridade | ADR-004 | 2026-03-12 |
| — | SPORT_SCIENCE_RULES como artefato canônico | ADR-005 | 2026-03-14 |
| — | DSS / Decision Discovery stage | ADR-006 | 2026-03-15 |
| ARCH-001 | Estratégia de Autenticação — JWT RS256 | ADR-007 | 2026-03-15 |
| ARCH-002 | Estratégia de Autorização — RBAC flat 5 roles | ADR-008 | 2026-03-15 |
| ARCH-003 | Padrão Data/Hora — UTC + RFC 3339 Z + venueTimezone | ADR-009 | 2026-03-15 |
| ARCH-004 | Política de Dados Sensíveis e Mascaramento | ADR-010 | 2026-03-15 |
| ARCH-005 | Política de Retenção de Dados (LGPD) | ADR-011 | 2026-03-15 |
| ARCH-006 | Gerenciamento de Secrets e Política de Rotação | ADR-012 | 2026-03-15 |
| ARCH-007 | Política de Logging e Observabilidade | ADR-013 | 2026-03-15 |
| ARCH-008 | Política de Deprecação de Contratos e APIs | ADR-014 | 2026-03-15 |
| ARCH-009 | Política de Log de Execução de Agente | ADR-015 | 2026-03-15 |
| ARCH-010 | Exposição MCP — Adiada pós-v1.0 (deferred) | ADR-016 | 2026-03-15 |
| ARCH-011 | State Machine Canônica de `training_session` | ADR-017 | 2026-03-15 |

---

## 4. Regras de Manutenção

1. Toda entrada nova deve ter ID sequencial (`ARCH-NNN`), criticidade, status e módulos afetados.
2. Entradas `obrigatórias` com status `open` disparam `BLOCKED_MISSING_ARCH_DECISION` no estágio `Decision Discovery`.
3. Quando uma ADR é aprovada, mover a entrada para a seção §3 (Resolvidas) com referência ao ADR.
4. Revisar entradas `deferred` antes de cada marco de release (v0.5, v1.0).
5. Este arquivo não pode conter decisões — apenas ponteiros para onde as decisões vivem (`ADR-*.md`).
