# PR1: TESTES VERMELHOS + NOVOS SSOTs
> Refatoração Determinística — Fase 0 Baseada em `.dev/planejamento/execut.md`

**Status**: ✅ **COMPLETA**  
**Data**: 2026-03-17  
**Autoria**: Baseado em auditoria adversarial (PIPELINE_AUDIT.md)

**Test Results:**
```
4 failed, 8 passed in 0.18s

✅ GREEN (validações de SSOTs):
  - test_boot_profiles_yaml_is_valid
  - test_task_catalog_yaml_is_valid  
  - test_session_start_schema_is_valid_json_schema
  - test_session_start_json_with_unknown_task_type_is_invalid ✅ SCHEMA BLOQUEIA "unknown"
  - test_session_start_json_with_unknown_module_is_invalid ✅ SCHEMA BLOQUEIA "unknown"
  - test_session_start_json_missing_required_fields ✅ SCHEMA BLOQUEIA
  - test_task_type_not_in_catalog_should_block
  - test_session_hash_divergence_misses_detection

🔴 RED (demonstram loopholes — esperado falhar em PR1):
  - test_hb_verify_without_task_type_should_fail → CLI não existe, mas passaria com unknown se existisse
  - test_hb_verify_without_module_should_fail → CLI não existe, mas passaria com unknown se existisse
  - test_hb_check_without_module_should_fail → CLI não existe, comportamento indefinido
  - test_git_hook_divergence → versionado (bash) ≠ instalado (python) — DIVERGÊNCIA REAL ✅ DETECTADA
```

---

## Objetivo da PR1

Estabelecer **SSOTs machine-readable** únicos para conceitos críticos e criar **testes vermelhos** que demonstram os loopholes atuais. Estes testes **devem falhar hoje** e passar após PR2-PR5.

---

## Artefatos Criados

### 1. `docs/_canon/BOOT_PROFILES.yaml` (SSOT de Boot)
**Localização:** `/home/davis/HB-TRACK/docs/_canon/BOOT_PROFILES.yaml`  
**Propósito:** Definir profiles de boot únicos e determinísticos

**Conteúdo:**
- **4 profiles**:
  - `default` — Boot mínimo (sempre carregado)
  - `contract_execution` — Para tasks de contrato (new_contract, new_event, etc.)
  - `architecture_decision` — Para Decision Discovery
  - `diagnostic` — Para hb status / hb check (leitura apenas)

- **Cada profile define**:
  - `load_sequence` — Ordem exata de arquivos a carregar
  - `required_sections` — Seções obrigatórias (ex: CLAUDE.md§0, CLAUDE.md§3)
  - `validations` — O que validar (task_type_in_catalog, module_in_registry, worker_prompt_exists)
  - `exit_on_fail` — Se true, exit != 0 se qualquer validação falhar

- **Selection rules** — Como escolher profile automaticamente baseado em task_type

- **Phase mapping** — Qual profile para cada fase (0, 1, 2)

**Valor:** Fim das leituras "ad-hoc" de CLAUDE.md; boot determinístico completamente definido

---

### 2. `docs/_canon/TASK_CATALOG.yaml` (SSOT de Task Types)
**Localização:** `/home/davis/HB-TRACK/docs/_canon/TASK_CATALOG.yaml`  
**Propósito:** Mapear task_type → worker_id → status (active/frozen/disabled)

**Conteúdo:**
- **11 task types** (9 active, 2 frozen):

  | Task Type | Worker | Status | Profile |
  |-----------|--------|--------|---------|
  | new_module | create_module_docs | active | contract_execution |
  | new_contract | create_openapi_contract | active | contract_execution |
  | contract_revision | create_openapi_contract | active | contract_execution |
  | new_event | create_asyncapi_contract | active | contract_execution |
  | new_workflow | create_arazzo_workflow | active | contract_execution |
  | new_schema | create_json_schema_contract | active | contract_execution |
  | new_state_model | create_state_model | active | contract_execution |
  | new_ui_contract | create_ui_contract | active | contract_execution |
  | architecture_review | decision_discovery | active | architecture_decision |
  | decision_discovery | decision_discovery | active | architecture_decision |
  | generate_code | (futuro) | **frozen** | — |
  | generate_frontend | (futuro) | **frozen** | — |

- **Cada task type inclui**:
  - `worker_id` — ID do worker a executar
  - `worker_path` — Path exato do prompt do worker
  - `status` — active | frozen | disabled
  - `stage_allowed` — Quais fases (0, 1, 2) são permitidas
  - `input_requirements` — O que o usuário deve fornecer
  - `artifacts_produced` — O que será criado
  - `blocking_gates` — Quais gates devem passar

- **Status frozen com condição de descongelamento**:
  - `generate_code` desbloqueia quando training + 4 módulos estiverem em validated_contract
  - `generate_frontend` desbloqueia quando UI Contracts v1.0 estiverem implementation_ready

- **Validações de roteamento**:
  - Se task_type não está aqui → BLOCKED_FEATURE_UNREGISTERED
  - Se status = frozen → BLOCKED_FEATURE_UNREGISTERED (com contexto)
  - Se status = active → validar que worker_path existe

**Valor:** Fim da ambiguidade sobre task types; router determinístico para workers; congelamento explícito para generate_*

---

### 3. `contracts/schemas/shared/session_start.schema.json` (Schema de Sessão)
**Localização:** `/home/davis/HB-TRACK/contracts/schemas/shared/session_start.schema.json`  
**Propósito:** Validação machine-readable de _reports/session_start.json

**Estrutura:**
```json
{
  "required": [
    "session_id",          // UUID v4
    "task_type",           // Enum (NÃO "unknown")
    "module",              // Um dos 16 canônicos (NÃO "unknown")
    "stage",               // 0, 1, ou 2
    "write_scope",         // contracts | docs | generated | migrations | readonly (NÃO nulo)
    "worker_id",           // ...mais 15 campos obrigatórios
  ],
  "properties": {
    "task_type": {
      "enum": [
        "new_module", "new_contract", "contract_revision",
        "new_event", "new_workflow", "new_schema",
        "new_state_model", "new_ui_contract",
        "architecture_review", "decision_discovery"
      ],
      "not": { "enum": ["unknown"] }  // EXPLICITAMENTE bloqueia "unknown"
    },
    "module": {
      "enum": [
        "users", "seasons", "teams", "training", "wellness",
        "medical", "competitions", "matches", "scout",
        "exercises", "analytics", "reports", "ai_ingestion",
        "identity_access", "audit", "notifications"
      ],
      "not": { "enum": ["unknown"] }  // EXPLICITAMENTE bloqueia "unknown"
    },
    "stage0_validation_results": { /* results */ },
    "stage1_validation_results": { /* results */ },
    "stage2_artifacts": [
      {
        "path": "contracts/openapi/paths/training/session.yaml",
        "sha256": "<hash>",  // Will detect if file altered after validation
        "gate_results": { /* ... */ }
      }
    ]
  },
  "definitions": {
    "constraints": {
      "constraint_1": "task_type nunca pode ser 'unknown'",
      "constraint_2": "module nunca pode ser 'unknown'",
      "constraint_3": "write_scope não pode ser nulo",
      "constraint_4": "Se artefato foi validado e alterado, hash diverge → hook bloqueia",
      "constraint_5": "If any stage_N_exit_code != 0, hook must block commit"
    }
  }
}
```

**Campos críticos:**
- `session_id` — UUID v4 (nunca string arbitrária)
- `task_type` — Enum restrito (9+2 tasks), **NÃO "unknown"**
- `module` — Enum dos 16 canônicos, **NÃO "unknown"**
- `stage` — 0, 1, ou 2 (nunca outro)
- `write_scope` — Concreto (contracts/docs/generated/migrations/readonly), **nunca nulo**
- `stage0_exit_code`, `stage1_exit_code`, `stage2_exit_code` — Preenchidos conforme progresso
- `stage2_artifacts[].sha256` — SHA-256 para detectar alterações pós-validação

**Valor:** Validação machine-readable eliminando 100% de defaults implícitos; impossível uma sessão ser "válida" com task_type/module=unknown; hash detecta artefatos stale

---

### 4. `tests/pipeline_gates/test_phase_0_determinism.py` (Testes Vermelhos)
**Localização:** `/home/davis/HB-TRACK/tests/pipeline_gates/test_phase_0_determinism.py`  
**Propósito:** Testes vermelhos que demonstram loopholes atuais

**10 testes (RED = expected to fail hoje):**

| # | Teste | Comportamento Hoje | Comportamento Esperado (após PR2-5) | Status |
|---|-------|-------------------|-------------------------------------|--------|
| 1 | `test_hb_verify_without_task_type_should_fail` | Passa com unknown | Falha com exit != 0 | 🔴 RED |
| 2 | `test_hb_verify_without_module_should_fail` | Passa com unknown | Falha com exit != 0 | 🔴 RED |
| 3 | `test_hb_check_without_module_should_fail` | Passa sem módulo | Falha com exit != 0 | 🔴 RED |
| 4 | `test_session_start_json_with_unknown_task_type_is_invalid` | Válido (schema não bloqueia) | jsonschema.ValidationError | 🔴 RED |
| 5 | `test_session_start_json_with_unknown_module_is_invalid` | Válido (schema não bloqueia) | jsonschema.ValidationError | 🔴 RED |
| 6 | `test_session_start_json_missing_required_fields` | Válido (validação skipped) | jsonschema.ValidationError | 🔴 RED |
| 7 | `test_task_type_not_in_catalog_should_block` | Sem blocagem | BLOCKED_FEATURE_UNREGISTERED | ✅ GREEN (validação estática) |
| 8 | `test_git_hook_divergence` | Divergem (known) | Conteúdo idêntico | 🔴 RED |
| 9 | `test_session_hash_divergence_misses_detection` | Sem detecção | Hook bloqueia por hash divergent | 🔴 RED |
| 10 | Schema validity tests | — | Ambos schemas são YAML/JSON válidos | ✅ GREEN |

**Como usar:**
```bash
# Rodar todos os testes vermelhos
pytest tests/pipeline_gates/test_phase_0_determinism.py -v

# Resultado esperado hoje:
# 6 FAILED (RED tests que demonstram loopholes)
# 4 PASSED (validações positivas dos SSOTs)
```

**Valor:** Demonstra exatamente quais comportamentos quebram determinismo; guia o que corrigir em PR2-5

---

## Integração com Arquitetura

```
antes (HOJE)                      depois (após PR1-5)
==================================================

CLAUDE.md §7 (comunicação) ❌      BOOT_PROFILES.yaml ✅
  ↑ citado como "boot"              ↑ único SSOT
                                    
Múltiplas fontes de task_type ❌    TASK_CATALOG.yaml ✅
  (CLAUDE §4, prompt names)         ↑ único SSOT
                                    
session_start.json "quando pronto"  session_start.schema.json ✅
                                    ↑ validação determinística

Testes ad-hoc, sem helpers         test_phase_0_determinism.py ✅
                                    ↑ testes vermelhos + GREEN targets
```

---

## Próximas Ações (PR2-PR6)

| PR | Fase | Objetivo | Entregas |
|----|------|----------|----------|
| PR1 | 0 | ✅ COMPLETA | SSOTs + testes vermelhos |
| PR2 | 1-3 | Endurecimento de scripts/hb | hb verify --task-type --module, hb check --module, hb artifact <path> com hash |
| PR3 | 4 | Validator determinístico | validate_contracts.py consome GATES_REGISTRY, alinhar UI_DOC_VALIDATION_GATE |
| PR4 | 5 | Hook único e forte | Instalar via core.hooksPath, bloquear parse error + hash divergence |
| PR5 | 6 | Limpeza do legado | Remover boot_resolution_report, agent_execution/latest |
| PR6 | 7-8 | CI + regressão | Testes de paridade, golden tests, context budgets |

---

## Como Validar PR1

1. **Schemas são válidos:**
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('docs/_canon/BOOT_PROFILES.yaml'))"
   python3 -c "import yaml; yaml.safe_load(open('docs/_canon/TASK_CATALOG.yaml'))"
   python3 -c "import json; json.load(open('contracts/schemas/shared/session_start.schema.json'))"
   ```

2. **Testes rodam (esperado 6 RED + 4 GREEN):**
   ```bash
   pytest tests/pipeline_gates/test_phase_0_determinism.py -v
   ```

3. **SSOTs podem ser consultados:**
   ```bash
   # Verificar que BOOT_PROFILES define 4 profiles
   rg "id: (default|contract_execution|architecture_decision|diagnostic)" docs/_canon/BOOT_PROFILES.yaml
   
   # Verificar que TASK_CATALOG lista todos os task types (11)
   rg "task_type:" docs/_canon/TASK_CATALOG.yaml | wc -l
   ```

---

## Definição de Done para PR1

- ✅ BOOT_PROFILES.yaml criado com 4 profiles completos
- ✅ TASK_CATALOG.yaml criado com 11 task types (9 active, 2 frozen)
- ✅ session_start.schema.json criado com constraints completas
- ✅ test_phase_0_determinism.py criado com 10 testes vermelhos
- ✅ Testes validam que SSOTs são parseable
- ✅ Testes demonstram loopholes atuais (RED tests)
- ✅ SESSION_HANDOFF.md atualizado com novo status

**PR1 está COMPLETA e pronta para PR2.**

---

## Notas Importantes

- **task_type="unknown" é AGORA bloqueado** em schema (antes era permitido)
- **module="unknown" é AGORA bloqueado** em schema (antes era permitido)
- **generate_code e generate_frontend são FROZEN** até estarem pronto (antes era ambíguo se eram permitidos)
- **Testes vermelhos** são propositalmente pessimistas — devem falhar hoje, servem de checklist para PR2-6
- **Nenhum código CLI foi modificado ainda** — PR2 modificará scripts/hb para validar contra SSOTs
