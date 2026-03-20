# PIPELINE_QUICK_REFERENCE.md
> Consulta rápida estruturada • Interligações fase→gate→task→worker • Atualizado: 2026-03-20

---

## 📌 Matriz de Orquestração: Fases × Gates × Tasks × Workers

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                          SEQUÊNCIA OBRIGATÓRIA DO PIPELINE                                      │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

FASE 0: PRÉ-CONTRATO (Entry Point)
├─ Validar boot profile (BOOT_PROFILES.yaml)
├─ Carregar AGENT_INSTRUCTIONS.md§0-6
├─ Determinar task_type correto
├─ Gates Bloqueantes (9):
│  1. AXIOM_INTEGRITY_GATE          → DOMAIN_AXIOMS.json válido?
│  2. PATH_CANONICALITY_GATE        → paths canônicos?
│  3. SCOPE_BOUNDARY_GATE           → cross-module refs autorizados?
│  4. MODULE_REGISTRY_GATE          → MODULE_REGISTRY.yaml (16 módulos)?
│  5. MODULE_SOURCE_AUTHORITY_MATRIX_GATE → matriz autoridade?
│  6. PRE_CONTRACT_EVIDENCE_GATE    → SESSION_HANDOFF.md schema válido?
│  7. SHADOW_AUTHORITY_GATE         → docs não-soberanos com disclaimer?
│  8. CANON_ALLOWLIST_GATE          → artefatos autorizados em docs/_canon/?
│  9. TOOLING_CONFIG_GATE           → toolchain presente? (oasdiff, schemathesis)
└─ ✅ Output: _reports/session_start.json
   └─ Próxima fase liberada?

────────────────────────────────────────────────────────────────────────────────────────────

FASE 1: DECISÃO ARQUITETURAL (Condicional)
├─ Trigger: ADRs abertas em ARCHITECTURE_DECISION_BACKLOG.md?
├─ IF Sim:
│  ├─ Task: architecture_review
│  ├─ Worker: decision_discovery.prompt.md
│  └─ Output: docs/_canon/decisions/ADR-*.md
├─ IF Não:
│  └─ ⏭️  Pular para Fase 2
└─ ✅ Todas decisions resolvidas?

────────────────────────────────────────────────────────────────────────────────────────────

FASE 2: AUTORIA (Criação de Artefatos)
├─ Boot Profile: contract_execution (obrigatório)
├─ Task Type roteado automaticamente:
│  ├─ new_contract        → create_openapi_contract.prompt.md
│  ├─ contract_revision   → create_openapi_contract.prompt.md
│  ├─ new_event          → create_asyncapi_contract.prompt.md
│  ├─ new_workflow       → create_arazzo_workflow.prompt.md
│  ├─ new_schema         → create_json_schema_contract.prompt.md
│  ├─ new_state_model    → create_state_model.prompt.md
│  ├─ new_ui_contract    → create_ui_contract.prompt.md
│  ├─ new_module         → create_module_docs.prompt.md
│  └─ readiness_promotion → readiness_promotion.prompt.md
├─ Regra de Ouro: ✅ Artefato escrito no path canônico
│                     (verificado por PATH_CANONICALITY_GATE próximo)
├─ Gates de Validação: 2
│  1. REQUIRED_ARTIFACT_PRESENCE_GATE  → artefatos obrigatórios presentes?
│  2. MODULE_DOC_CROSSREF_GATE         → headers YAML canônicos?
└─ ✅ Output: contracts/openapi/, contracts/asyncapi/, docs/hbtrack/modulos/

────────────────────────────────────────────────────────────────────────────────────────────

FASE 3: VALIDAÇÃO (Semântica & Integridade)
├─ Execução: python3 scripts/contracts/validate/validate_contracts.py
├─ Gates Bloqueantes (11):
│  1. API_NORMATIVE_DUPLICATION_GATE       → duplicação HTTP?
│  2. OWASP_API_CONTROL_MATRIX_GATE        → segurança OWASP?
│  3. BOUNDARY_USERS_IDENTITY_ACCESS_GATE  → users vs identity_access separados?
│  4. WELLNESS_MEDICAL_BOUNDARY_GATE       → wellness vs medical separados?
│  5. SCOUT_TAXONOMY_GATE                  → scout taxonomy artefato?
│  6. ASYNC_REQUIRED_MODULE_GATE           → AsyncAPI p/ módulos com eventos?
│  7. EXTERNAL_SOURCE_AUTHORITY_GATE       → sources externas como SSOT?
│  8. PLACEHOLDER_RESIDUE_GATE             → TODO/TBD removidos?
│  9. REF_HERMETICITY_GATE                 → refs herméticos?
│  10. DECISION_IR_CONFORMANCE_GATE        → MODULE_DECISION_IR válido?
└─ ✅ Output: _reports/contract_gates/latest.json
   └─ Todos gates PASS?

────────────────────────────────────────────────────────────────────────────────────────────

FASE 4: READINESS (Elegibilidade para Implementation)
├─ Task: readiness_promotion
├─ Worker: readiness_promotion.prompt.md
├─ Critério Binário (todos devem ser ✅):
│  1. Status MODULE_REGISTRY.yaml: validated_contract?
│  2. Todas expected_surfaces presentes?
│  3. Sem decisões arquiteturais abertas?
│  4. Gates Fase 3: todos PASS?
├─ Gates: 2
│  1. MODULE_REGISTRY_GATE
│  2. PRE_CONTRACT_EVIDENCE_GATE
└─ ✅ Output: MODULE_REGISTRY.yaml atualizado com status=implementation_ready
   └─ Liberado para implementation?

────────────────────────────────────────────────────────────────────────────────────────────

FASE 5: HANDOFF (Registro de Evidência)
├─ Artefato: SESSION_HANDOFF.md (finalizado)
├─ Conteúdo obrigatório:
│  └─ Trilha completa de execução do pipeline
├─ Ação: git commit
│  └─ git add SESSION_HANDOFF.md docs/_canon/MODULE_REGISTRY.yaml
│  └─ git commit -m "feat(contract): {module} — {task_type} pipeline PASS"
└─ ✅ Evidência rastreável registrada

────────────────────────────────────────────────────────────────────────────────────────────

✅ IMPLEMENTAÇÃO LIBERADA
```

---

## 🎯 Mapa Rápido: Task Type → Worker → Boot Profile

| Task Type | Worker Prompt | Boot Profile | # Artefatos | Fases Permitidas |
|-----------|------|-------------|-----------|----------|
| `pre_contract_boot` | pre_contract_orchestrator | contract_execution | 1 | [0] |
| `new_module` | create_module_docs | contract_execution | 2 | [0,1,2] |
| `new_contract` | create_openapi_contract | contract_execution | 1 | [0,1,2] |
| `contract_revision` | create_openapi_contract | contract_execution | 1+ | [0,1,2] |
| `new_event` | create_asyncapi_contract | contract_execution | 1 | [0,1,2] |
| `new_workflow` | create_arazzo_workflow | contract_execution | 1 | [0,1,2] |
| `new_schema` | create_json_schema_contract | contract_execution | 1 | [0,1,2] |
| `new_state_model` | create_state_model | contract_execution | 1 | [0,1,2] |
| `new_ui_contract` | create_ui_contract | contract_execution | 1 | [0,1,2] |
| `readiness_promotion` | readiness_promotion | contract_execution | 1 | [3,4] |
| `architecture_review` | decision_discovery | architecture_decision | 1+ | [1,2] |
| *(auditorias)* | audit_*.prompt.md | diagnostic | 1+ | [any] |

---

## 📦 Correspondência: Task Type → Caminho de Saída

| Task Type | Artefato Gerado | Path Canônico |
|-----------|---------|---------|
| `new_module` | Module README | `docs/hbtrack/modulos/{module}/README.md` |
| | Domain Rules | `docs/hbtrack/modulos/{module}/DOMAIN_RULES_{MODULE}.md` |
| `new_contract` | OpenAPI Path | `contracts/openapi/paths/{module}.yaml` |
| `contract_revision` | OpenAPI Path (update) | `contracts/openapi/paths/{module}.yaml` |
| `new_event` | AsyncAPI Channel | `contracts/asyncapi/channels/{module}/{event}.yaml` |
| `new_workflow` | Arazzo Workflow | `contracts/workflows/{module}/{workflow}.arazzo.yaml` |
| `new_schema` | JSON Schema | `contracts/schemas/{module}/{schema}.schema.json` |
| `new_state_model` | State Model Markdown | `docs/hbtrack/modulos/{module}/STATE_MODEL_{MODULE}.md` |
| `new_ui_contract` | UI Contract Markdown | `docs/hbtrack/modulos/{module}/UI_CONTRACT_{MODULE}.md` |
| `readiness_promotion` | MODULE_REGISTRY.yaml (updated) | `docs/_canon/MODULE_REGISTRY.yaml` |
| `architecture_review` | ADR Markdown | `docs/_canon/decisions/ADR-*.md` |

---

## 🔐 Gate Dependency Graph (Ordem de Execução)

```
AXIOM_INTEGRITY_GATE (0)
  ↓
PATH_CANONICALITY_GATE (1)
  ↓ + ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ↓
SCOPE_BOUNDARY_GATE (1.5)          REQUIRED_ARTIFACT_PRESENCE_GATE (2)
  ↓                                  ↓ (dep: 1)
MODULE_SOURCE_AUTHORITY_MATRIX (2D) ↓
  ↓                                  ├→ MODULE_DOC_CROSSREF_GATE (2A)
MODULE_REGISTRY_GATE (2D1)           ├→ API_NORMATIVE_DUPLICATION_GATE (2B)
  ↓                                  ├→ OWASP_API_CONTROL_MATRIX (2C)
PRE_CONTRACT_EVIDENCE_GATE (2J)      ├→ BOUNDARY_USERS_IDENTITY_ACCESS (2E)
  ↓                                  ├→ WELLNESS_MEDICAL_BOUNDARY (2F)
SHADOW_AUTHORITY_GATE (2K)           ├→ SCOUT_TAXONOMY_GATE (2G)
  ↓                                  ├→ ASYNC_REQUIRED_MODULE (2H)
CANON_ALLOWLIST_GATE (2N)            ├→ EXTERNAL_SOURCE_AUTHORITY (2I)
  ↓                                  └→ DECISION_IR_CONFORMANCE (2L)
TOOLING_CONFIG_GATE (4A)                   ↓
  ↓                                  PLACEHOLDER_RESIDUE_GATE (3)
┌─────────────────────────────────────────→ ↓
│                                    REF_HERMETICITY_GATE (4)
│                                          ↓
└──────────────────────────────────────────→ ✅ VALIDATION PASS
```

---

## 🧭 Rotas de Entrada (Entry Points por Cenário)

### Cenário 1: Criar novo contrato HTTP para módulo existente
```
[Input: module=training, task_type=new_contract, method=POST]
  ↓
pre_contract_boot → determina task=new_contract
  ↓
Boot profile: contract_execution
  ↓
Worker: create_openapi_contract.prompt.md
  ↓
Output: contracts/openapi/paths/training.yaml (atualizado)
  ↓
Fase 3: Validação executa todos gates
  ↓
✅ ou ❌
```

### Cenário 2: Criar novo evento (AsyncAPI)
```
[Input: module=training, task_type=new_event, event_name=TrainingSessionStarted]
  ↓
pre_contract_boot → task=new_event
  ↓
Boot profile: contract_execution
  ↓
Worker: create_asyncapi_contract.prompt.md
  ↓
Output: contracts/asyncapi/channels/training/TrainingSessionStarted.yaml
  ↓
REQUIRED_ARTIFACT_PRESENCE_GATE: AsyncAPI root (asyncapi.yaml) existe?
ASYNC_REQUIRED_MODULE_GATE: AsyncAPI obrigatório p/ este módulo?
  ↓
✅ ou ❌
```

### Cenário 3: Resolver ADR arquitetural aberta
```
[Input: decision_id=ADR-031, context="Como separar wellness de medical?"]
  ↓
pre_contract_boot → task_type=architecture_review
  ↓
Boot profile: architecture_decision
  ↓
Worker: decision_discovery.prompt.md
  ↓
Output: docs/_canon/decisions/ADR-031-*.md (criado/atualizado)
  ↓
docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md (atualizado)
  ↓
Próxima fase: Autoria pode prosseguir com decisão resolvida
```

### Cenário 4: Promover módulo para implementation_ready
```
[Input: module=training, task_type=readiness_promotion]
  ↓
pre_contract_boot → task=readiness_promotion
  ↓
Boot profile: contract_execution
  ↓
Verificações (readiness_promotion worker):
  ├─ training status no MODULE_REGISTRY = validated_contract?
  ├─ ALL expected_surfaces para training presentes?
  ├─ ADR backlog vazio?
  ├─ Gates Fase 3 = PASS?
  └─ → Se tudo ✅: atualizar status → implementation_ready
  ↓
Output: docs/_canon/MODULE_REGISTRY.yaml atualizado
  ↓
✅ training pronto para implementation
```

---

## ⚡ Validações por Fase (Gate Coverage)

### Fase 0: PRÉ-CONTRATO (9 Gates)
- **Axiom** — semântica global
- **Path** — soberania de paths
- **Scope** — boundaries cross-module
- **Registry** — 16 módulos, status, superfícies
- **Authority Matrix** — fontes autorizadas
- **Evidence** — SESSION_HANDOFF.md schema
- **Shadow Authority** — docs não-soberanas
- **Canon Allowlist** — artefatos autorizados
- **Tooling** — toolchain health

### Fase 2: AUTORIA (2 Gates)
- **Required Artifacts** — presença obrigatória
- **Module Doc Crossref** — headers canônicos

### Fase 3: VALIDAÇÃO (10 Gates)
- **API Duplication** — (warning)
- **OWASP** — segurança
- **Boundary (Users/IA)** — separação módulos
- **Boundary (Wellness/Medical)** — separação módulos
- **Scout Taxonomy** — scout artefato
- **Async Required** — AsyncAPI p/ eventos
- **External Source Authority** — SSOT soberana
- **Placeholder Residue** — TODO/TBD
- **Ref Hermeticity** — refs herméticos
- **Decision IR** — MODULE_DECISION_IR schema

---

## 📍 Artefatos "SSOT" (Single Source of Truth)

| Artefato | Path | Propósito | Atualização |
|----------|------|---------|-----------|
| MODULE_REGISTRY | docs/_canon/MODULE_REGISTRY.yaml | Status e superfícies dos 16 módulos | readiness_promotion |
| DOMAIN_AXIOMS | .contract_driven/DOMAIN_AXIOMS.json | Enums, formats, state machines globais | architecture_review |
| TASK_CATALOG | .contract_driven/TASK_CATALOG.yaml | Task types → workers → profiles | CHANGE_POLICY |
| BOOT_PROFILES | .contract_driven/BOOT_PROFILES.yaml | Profiles de boot e validações | CHANGE_POLICY |
| GATES_REGISTRY | docs/_canon/gates/GATES_REGISTRY.yaml | 21 gates, ordem, dependências | CHANGE_POLICY |
| AGENT_INSTRUCTIONS | docs/_canon/AGENT_INSTRUCTIONS.md | Boot obrigatório | CHANGE_POLICY |
| CONTRACT_PIPELINE | docs/_canon/CONTRACT_PIPELINE.md | Estágios formais | CHANGE_POLICY |

---

## 🔄 Compilação API Policy (When Needed)

**Trigger**: Após mudança em artefatos globais:
- `.contract_driven/DOMAIN_AXIOMS.json`
- `contracts/templates/api/api_rules.yaml`
- Qualquer policy global

**Ação**:
```bash
python3 scripts/contracts/validate/api/compile_api_policy.py --all
```

**Efeito**: Regenera policies locais derivadas, re-sincroniza refs globais

---

## 🚨 Critério de Falha (Pipeline Bloqueia)

| Condição | Gate | Severidade | Remedy |
|----------|------|-----------|--------|
| AXIOM inválido | AXIOM_INTEGRITY | CRITICAL | Editar DOMAIN_AXIOMS.json |
| Path não-canônico | PATH_CANONICALITY | CRITICAL | Mover artefato p/ path correto |
| Cross-module ref não autorizado | SCOPE_BOUNDARY | HIGH | Editar SCOPE_BOUNDARY_POLICY.md + ADR |
| Artefato obrigatório faltando | REQUIRED_ARTIFACT_PRESENCE | CRITICAL | Criar artefato |
| TODO/TBD não removido | PLACEHOLDER_RESIDUE | HIGH | Completar ou remover artefato |
| Ref hermeticity breach | REF_HERMETICITY | CRITICAL | Corrigir $ref p/ estar dentro do grafo |
| Toolchain faltando (oasdiff) | TOOLING_CONFIG | CRITICAL | `./scripts/contract_gates/provision_oasdiff.sh` |

---

## ✅ Checklist Pré-Commit

```
PRÉ-COMMIT (antes de git commit):

☐ SESSION_HANDOFF.md atualizado com fase atual + resultados
☐ _reports/session_start.json existe e é válido
☐ _reports/contract_gates/latest.json mostra PASS
☐ MODULE_REGISTRY.yaml atualizado (se readiness_promotion)
☐ Nenhum TODO/TBD em artefatos soberanos
☐ Refs herméticos (grepped com jq/grep)
☐ Nenhum artefato novo fora de paths canônicos
☐ CHANGE_POLICY.md atualizado (se mudança em canon)

GIT COMMIT:
git add SESSION_HANDOFF.md [artefatos] MODULE_REGISTRY.yaml
git commit -m "feat(contract): {module} — {task_type} pipeline PASS"
```

---

**📊 Referência rápida compilada:** 2026-03-20  
**🔗 Mapa completo:** [PIPELINE_MAPPING.json](PIPELINE_MAPPING.json)  
**📖 Guia visual:** [PIPELINE_REAL_MAP.md](PIPELINE_REAL_MAP.md)
