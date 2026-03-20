# HB TRACK — Pipeline CDD (Contract-Driven Development)
> **Mapa canônico da estrutura real** • Atualizado: 2026-03-20

---

## 📊 Visão Geral Executiva

| Aspecto | Contagem | Núcleo |
|---------|----------|--------|
| **Fases do Pipeline** | 6 | Pre-contract → Decision → Authoring → Validation → Readiness → Handoff |
| **Gates de Validação** | 21 | 19 bloqueantes + 2 warnings |
| **Task Types Ativos** | 14 | 11 de contrato + 3 auditorias |
| **Módulos Canônicos** | 16 | Todos em `implementation_ready` |
| **Boot Profiles** | 4 | default, contract_execution, architecture_decision, diagnostic |
| **Worker Prompts** | 18 | 1 orquestrador + 10 de contrato + 3 de auditoria + 2 de geração |
| **Workflows CI/CD** | 4 | contract-gates (crítico) + deploy + 2 auditorias |

---

## 🔄 Pipeline — 6 Fases (Sequência Obrigatória)

```
PRÉ-CONTRATO (Fase 0)
    ↓ [9 gates bloqueantes]
DECISÃO ARQUITETURAL (Fase 1)
    ↓ [optional, se houver ADRs abertas]
AUTORIA (Fase 2)
    ↓ [criar artefatos: OpenAPI, AsyncAPI, Schemas, UIs, Docs]
VALIDAÇÃO (Fase 3)
    ↓ [10 gates semânticos + hermeticidade]
READINESS (Fase 4)
    ↓ [2 gates de elegibilidade para implementation_ready]
HANDOFF (Fase 5)
    ↓ [registro de evidência pré-contrato]
✅ IMPLEMENTAÇÃO LIBERADA
```

### Fase 0: PRÉ-CONTRATO (Entrada Obrigatória)
**Validação de Boot & Determinismo**

| Gate | Ordem | Bloqueante | Propósito |
|------|-------|-----------|----------|
| **AXIOM_INTEGRITY_GATE** | 0 | ✅ | Axiomas semânticos válidos? (DOMAIN_AXIOMS.json) |
| **PATH_CANONICALITY_GATE** | 1 | ✅ | Artefatos apenas em paths canônicos? |
| **SCOPE_BOUNDARY_GATE** | 1.5 | ✅ | Cross-module refs autorizadas? |
| **MODULE_REGISTRY_GATE** | 2D1 | ✅ | MODULE_REGISTRY.yaml válido? (16 módulos) |
| **MODULE_SOURCE_AUTHORITY_MATRIX_GATE** | 2D | ✅ | Matriz de autoridade definida? |
| **PRE_CONTRACT_EVIDENCE_GATE** | 2J | ✅ | SESSION_HANDOFF.md válido? |
| **SHADOW_AUTHORITY_GATE** | 2K | ✅ | Docs não-soberanos com disclaimer? |
| **CANON_ALLOWLIST_GATE** | 2N | ✅ | Artefatos autorizados em `docs/_canon/`? |
| **TOOLING_CONFIG_GATE** | 4A | ✅ | Toolchain OK? (oasdiff, schemathesis) |

**✅ Output:** `_reports/session_start.json` validado → próxima fase liberada

---

### Fase 1: DECISÃO ARQUITETURAL (Condicional)
**Architecture Decision Discovery**

**Task Type**: `architecture_review` → worker: `decision_discovery`  
**Trigger**: Se houver ADRs abertas em `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md`  
**Output**: `docs/_canon/decisions/ADR-*.md` atualizado

---

### Fase 2: AUTORIA (Criação de Artefatos)
**Contract Authoring & Generation**

| Task Type | Worker | Output |
|-----------|--------|--------|
| `new_module` | create_module_docs | `docs/hbtrack/modulos/{module}/README.md` + DOMAIN_RULES |
| `new_contract` | create_openapi_contract | `contracts/openapi/paths/{module}.yaml` |
| `contract_revision` | create_openapi_contract | `contracts/openapi/paths/{module}.yaml` (update) |
| `new_event` | create_asyncapi_contract | `contracts/asyncapi/channels/{module}/{event}.yaml` |
| `new_workflow` | create_arazzo_workflow | `contracts/workflows/{module}/{workflow}.arazzo.yaml` |
| `new_schema` | create_json_schema_contract | `contracts/schemas/{module}/{schema}.schema.json` |
| `new_state_model` | create_state_model | `docs/hbtrack/modulos/{module}/STATE_MODEL_{MODULE}.md` |
| `new_ui_contract` | create_ui_contract | `docs/hbtrack/modulos/{module}/UI_CONTRACT_{MODULE}.md` |

**Regra de Ouro**: ✅ Artefato escrito no path canônico (verificado por PATH_CANONICALITY_GATE)

---

### Fase 3: VALIDAÇÃO (10 Gates Semânticos)
**Contract Validation & Integrity Checks**

| Gate | Propósito | Crítico? |
|------|-----------|----------|
| **REQUIRED_ARTIFACT_PRESENCE_GATE** | Artefatos obrigatórios por módulo presentes? | ✅ CRÍTICO |
| **MODULE_DOC_CROSSREF_GATE** | Headers YAML canônicos em docs de módulo? | ✅ CRÍTICO |
| **API_NORMATIVE_DUPLICATION_GATE** | Duplicação HTTP fora da SSOT? | ⚠️ WARNING |
| **OWASP_API_CONTROL_MATRIX_GATE** | Segurança OWASP presente? | ✅ CRÍTICO |
| **BOUNDARY_USERS_IDENTITY_ACCESS_GATE** | `users` vs `identity_access` separados? | ✅ CRÍTICO |
| **WELLNESS_MEDICAL_BOUNDARY_GATE** | `wellness` vs `medical` separados? | ✅ CRÍTICO |
| **SCOUT_TAXONOMY_GATE** | Scout taxonomy artefato presente? | ✅ CRÍTICO |
| **ASYNC_REQUIRED_MODULE_GATE** | AsyncAPI presente p/ módulos com eventos? | ✅ CRÍTICO |
| **EXTERNAL_SOURCE_AUTHORITY_GATE** | Sources externas não tratadas como SSOT? | ✅ CRÍTICO |
| **PLACEHOLDER_RESIDUE_GATE** | TODO/TBD removidos? | ✅ CRÍTICO |
| **REF_HERMETICITY_GATE** | Refs herméticos (não apontam fora)? | ✅ CRÍTICO |

**⚙️ Instrumento**: `python3 scripts/contracts/validate/validate_contracts.py`  
**📊 Relatório**: `_reports/contract_gates/latest.json`

---

### Fase 4: READINESS (Elegibilidade para Implementation)
**Module Readiness & Promotion**

**Task Type**: `readiness_promotion` → worker: `readiness_promotion`

**Critério Binário** (todos devem ser V):
- ✅ Status atual: `validated_contract` (no MODULE_REGISTRY.yaml)
- ✅ Todas `expected_surfaces` para o módulo presentes (conforme MODULE_REGISTRY.yaml)
- ✅ Sem decisões arquiteturais abertas (ARCHITECTURE_DECISION_BACKLOG.md)
- ✅ Todos gates de Fase 3 em PASS

**Output**: `docs/_canon/MODULE_REGISTRY.yaml` atualizado com `status: implementation_ready`

---

### Fase 5: HANDOFF (Registro de Evidência)
**Implementation Handoff**

**Output**:
- `SESSION_HANDOFF.md` finalizado
- `git commit` com evidência de pipeline (trilha completa)

---

## 🚪 16 Módulos Canônicos (Todos em `implementation_ready`)

### Plataforma Base (4)
- **users** — identidade pessoal, profile, dados de atleta
- **identity_access** — auth, autorização, credenciais, RBAC
- **audit** — trilha de operações, logging, compliance
- **notifications** — eventos, alertas, comunicação

### Operações de Handebol (5)
- **seasons** — períodos, calendários, estrutura de temporada
- **teams** — equipes, rosters, alocação de atletas
- **competitions** — competições, estrutura de torneios
- **matches** — jogos, placar, eventos de jogo
- **scout** — análise tática, avaliação de adversários, taxonomia

### Performance & Técnica (5)
- **training** — sessões, exercícios, programação (state model integrado)
- **wellness** — recuperação, fadiga, prontidão, biometria
- **medical** — prontuário, diagnóstico, lesões (HIPAA compliance)
- **exercises** — catálogo canônico de movimentos, progressões
- **analytics** — agregação, relatórios, BI (read-only)

### Infraestrutura (2)
- **ai_ingestion** — orquestração de dados p/ ML, processamento
- **reports** — geração dinâmica de relatórios, documentação
- **video** — gerenciamento de mídia, armazenamento, análise

---

## 📦 Estrutura Canônica de Artefatos

```
contracts/
├── openapi/
│   ├── openapi.yaml                    [RAIZ do OpenAPI 3.1.0]
│   ├── paths/
│   │   ├── users.yaml
│   │   ├── seasons.yaml
│   │   └── ... [14 mais, 1 por módulo]
│   └── components/
│       ├── schemas/
│       ├── parameters/
│       ├── responses/
│       ├── requestBodies/
│       └── securitySchemes/
├── schemas/
│   ├── shared/                         [Compartilhados]
│   ├── users/, seasons/, ...           [16 pastas]
│   └── {module}/{schema_name}.schema.json
├── workflows/
│   ├── _global/
│   └── {module}/{workflow_name}.arazzo.yaml
└── asyncapi/
    ├── asyncapi.yaml                   [RAIZ do AsyncAPI 2.6.0]
    └── channels/
        └── {module}/{event_name}.yaml

docs/_canon/
├── AGENT_INSTRUCTIONS.md               [BOOT OBRIGATÓRIO §0-6]
├── CONTRACT_PIPELINE.md                [Estágios formais]
├── MODULE_REGISTRY.yaml                [16 módulos + status + superfícies]
├── DOMAIN_AXIOMS.json                  [SSOT semântica global]
├── gates/
│   └── GATES_REGISTRY.yaml             [21 gates, ordem, dependências]
├── decisions/
│   └── ADR-*.md
└── security/
    └── OWASP_API_CONTROL_MATRIX.yaml

.contract_driven/
├── TASK_CATALOG.yaml                   [11 task_types ativos]
├── BOOT_PROFILES.yaml                  [4 profiles: default, contract_execution, architecture_decision, diagnostic]
├── CONTRACT_SYSTEM_RULES.md
├── CONTRACT_SYSTEM_LAYOUT.md
├── DOMAIN_AXIOMS.json
├── agent_prompts/                      [18 worker prompts]
│   ├── pre_contract_orchestrator.prompt.md
│   ├── create_openapi_contract.prompt.md
│   └── ... [15 mais]
└── templates/
    ├── globais/
    └── modulos/

docs/hbtrack/modulos/{module}/
├── README.md                           [module_docs_minimum]
├── DOMAIN_RULES_{MODULE}.md
├── STATE_MODEL_{MODULE}.md             [quando applicable]
└── UI_CONTRACT_{MODULE}.md             [quando applicable]
```

---

## 🔌 Worker Prompts (Orquestração de Tarefas)

**Localização**: `.contract_driven/agent_prompts/`

### Orquestração (1)
- `pre_contract_orchestrator.prompt.md` — determina task_type correto

### Contrato (9)
- `create_openapi_contract.prompt.md` — HTTP API (new_contract, contract_revision)
- `create_asyncapi_contract.prompt.md` — eventos (new_event)
- `create_arazzo_workflow.prompt.md` — workflows multi-step (new_workflow)
- `create_json_schema_contract.prompt.md` — domain shapes (new_schema)
- `create_state_model.prompt.md` — FSM (new_state_model)
- `create_ui_contract.prompt.md` — telas (new_ui_contract)
- `create_module_docs.prompt.md` — documentação (new_module)
- `decision_discovery.prompt.md` — ADRs (architecture_review)
- `readiness_promotion.prompt.md` — elegibilidade (readiness_promotion)

### Auditoria (3)
- `audit_context_efficiency.prompt.md`
- `audit_domain_completeness.prompt.md`
- `audit_red_team_pipeline.prompt.md`

### Geração (2)
- `generate_code.prompt.md` — backend
- `generate_frontend.prompt.md` — frontend

---

## 🎯 Boot Profiles (Seleção Automática)

| Profile | Quando? | Carrega | Validações |
|---------|---------|---------|-----------|
| **default** | Sempre (fallback) | AGENT_INSTRUCTIONS.md, OPERATIONS.md | task_type, module, worker_prompt_exists |
| **contract_execution** | task_type ∈ {new_contract, new_event, ...} | CONTRACT_PIPELINE.md, GATES_REGISTRY | session_start_valid, task_type_active, stage_in_range |
| **architecture_decision** | task_type = architecture_review | ARCHITECTURE_DECISION_BACKLOG.md, DECISION_POLICY.md | decision_ir_exists |
| **diagnostic** | task_type = {audit_*, hb status/check} | CONTRACT_SYSTEM_RULES.md | (nenhuma obrigatória) |

---

## 🚀 CI/CD Workflows

### 🔴 Críticos para Pipeline
| Workflow | Trigger | Fase |
|----------|---------|------|
| **contract-gates.yml** | Push/PR em main/develop | Validação (Fase 3) |
| **deploy.yml** | Push em main (ou manual) | Validação + Build + Deploy |

### ⚪ Auditorias (Não-Bloqueante)
| Workflow | Trigger | Propósito |
|----------|---------|----------|
| **context-efficiency-audit.yml** | Schedule, workflow_dispatch | Auditar eficiência de contexto |
| **domain-completeness-audit.yml** | Schedule, workflow_dispatch | Auditar completude de domínio |

---

## ⚠️ Regras Críticas (MUST NOT Violar)

### 🚫 Sem Exceções
1. ❌ **Nunca pular fases** — o pipeline é sequencial total
2. ❌ **Nunca criar artefatos antes de `hb verify`** — gates devem passar antes
3. ❌ **Nunca deixar TODO/TBD em produção** — PLACEHOLDER_RESIDUE_GATE bloqueia
4. ❌ **Nunca modificar paths canônicos sem ADR** — PATH_CANONICALITY_GATE bloqueia
5. ❌ **Nunca adicionar módulo fora dos 16** — MODULE_REGISTRY_GATE bloqueia
6. ❌ **Nunca referenciar fora do grafo soberano** — REF_HERMETICITY_GATE bloqueia
7. ❌ **Nunca commitar sem `git add SESSION_HANDOFF.md`** — evidência é obrigatória

### ✅ Antes de Implementação
- ✅ Todas 6 fases completadas
- ✅ Todos 21 gates PASS
- ✅ MODULE_READINESS_SCORECARD confirmado
- ✅ Decisões arquiteturais resolvidas (se houver)

---

## 🔍 Debugging & Diagnostics

### Verificar Status do Pipeline
```bash
python3 scripts/contracts/validate/validate_contracts.py
# Output: _reports/contract_gates/latest.json
```

### Verificar Boot Profile
```bash
cat _reports/session_start.json | grep boot_profile_id
```

### Listar Todas as Superfícies de um Módulo
```bash
grep -A 20 "module: {nome}" docs/_canon/MODULE_REGISTRY.yaml | grep expected_surfaces
```

### Diagnosticar Gate Específico
```bash
grep -A 10 "gate_id: {GATE_NAME}" docs/_canon/gates/GATES_REGISTRY.yaml
```

---

## 📋 Terminologia Rápida

| Termo | Significado |
|-------|-----------|
| **SSOT** | Single Source of Truth (autoridade única) |
| **Soberano** | Artefato normativo (contracts/, docs/_canon/) |
| **Derivado** | Gerado (generated/, _reports/) |
| **Canônico** | Autorizado, definido no registry (MODULE_REGISTRY.yaml) |
| **Harme­ticidade** | Refs não apontam para fora do grafo normativo |
| **Gate** | Validação binária (PASS/FAIL) com blocking/warning |
| **Readiness** | Estado de elegibilidade para materialização |

---

## 📍 Referências Canônicas

- **Boot obrigatório**: [docs/_canon/AGENT_INSTRUCTIONS.md](docs/_canon/AGENT_INSTRUCTIONS.md)
- **Pipeline formal**: [docs/_canon/CONTRACT_PIPELINE.md](docs/_canon/CONTRACT_PIPELINE.md)
- **Registry de modules**: [docs/_canon/MODULE_REGISTRY.yaml](docs/_canon/MODULE_REGISTRY.yaml)
- **Task routing**: [.contract_driven/TASK_CATALOG.yaml](.contract_driven/TASK_CATALOG.yaml)
- **Gates detalhados**: [docs/_canon/gates/GATES_REGISTRY.yaml](docs/_canon/gates/GATES_REGISTRY.yaml)
- **Regras do sistema**: [.contract_driven/CONTRACT_SYSTEM_RULES.md](.contract_driven/CONTRACT_SYSTEM_RULES.md)
- **Layouts de filesystem**: [.contract_driven/CONTRACT_SYSTEM_LAYOUT.md](.contract_driven/CONTRACT_SYSTEM_LAYOUT.md)

---

**⏰ Última atualização:** 2026-03-20  
**📊 Status Pipeline:** ✅ PASS (todos gates bloqueantes verdes)
