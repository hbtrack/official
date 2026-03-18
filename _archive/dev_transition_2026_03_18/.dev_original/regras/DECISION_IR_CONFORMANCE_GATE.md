# DECISION_IR_CONFORMANCE_GATE.md

version: 1.0.0
status: PROPOSED
scope: hb_track
artifact_type: gate_spec
authority: binary_validation_gate
owners:
  - architecture
  - ai_governance
  - backend

## 1. Objetivo

Definir a especificação binária do `DECISION_IR_CONFORMANCE_GATE`.

Este gate existe para impedir que um `MODULE_DECISION_IR` semanticamente ambíguo,
incompleto ou desalinhado com os registries soberanos entre na fase de materialização.

Regra central:
**se a materialização exigir escolha, o gate falha.**

## 2. Entradas obrigatórias

- `MODULE_DECISION_IR.yaml` ou `MODULE_DECISION_IR.json`
- `MODULE_DECISION_IR_SCHEMA.json`
- registries canônicos requeridos pelo módulo
- `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- `.contract_driven/GLOBAL_TEMPLATES.md`
- `.contract_driven/templates/api/api_rules.yaml`
- docs globais canônicas aplicáveis
- matrizes auxiliares de binding (ex.: `IR_TO_SURFACE_MAPPING.yaml`)

## 3. Saídas do gate

O gate deve produzir exatamente uma das saídas:
- `PASS`
- `FAIL_BLOCKING`

Junto com:
- lista de códigos de erro
- path/field afetado
- evidência do erro
- menor próximo passo canônico

## 4. Classes de validação

### 4.1 Schema validity
Verifica forma do IR contra `MODULE_DECISION_IR_SCHEMA.json`.

### 4.2 Registry conformance
Verifica que toda referência obrigatória existe em registries soberanos.

### 4.3 Semantic coherence
Verifica coerência interna do IR.

### 4.4 Surface completeness
Verifica se o IR contém decisão suficiente para gerar superfícies obrigatórias e condicionais aplicáveis.

### 4.5 Deterministic generation readiness
Verifica se a geração por templates pode ocorrer sem discricionariedade.

## 5. Códigos binários de rejeição

- `IR_SCHEMA_INVALID`
- `IR_UNKNOWN_MODULE`
- `IR_UNKNOWN_SEMANTIC_TYPE_REF`
- `IR_UNKNOWN_REGISTRY_REF`
- `IR_REGISTRY_DRIFT`
- `IR_ENTITY_WITHOUT_REQUIRED_FIELDS`
- `IR_FIELD_WITHOUT_CANONICAL_TYPE`
- `IR_RELATION_WITHOUT_OWNERSHIP`
- `IR_RELATION_WITHOUT_DELETE_POLICY`
- `IR_LIFECYCLE_WITHOUT_STATE_MODEL`
- `IR_INVALID_STATE_TRANSITION`
- `IR_RULE_WITHOUT_FORMAL_CHECK_HINT`
- `IR_API_USE_CASE_INCOMPLETE`
- `IR_UI_FLOW_INCOMPLETE_WHEN_UI_APPLICABLE`
- `IR_PERMISSION_MODEL_INCOMPLETE_WHEN_RBAC_APPLICABLE`
- `IR_ERROR_MODEL_INCOMPLETE_WHEN_DOMAIN_ERRORS_APPLICABLE`
- `IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE`
- `IR_OPEN_DECISION_BLOCKING`
- `IR_SURFACE_MAPPING_INCOMPLETE`
- `IR_NON_DETERMINISTIC_MATERIALIZATION_RISK`

## 6. Regras-mestre

### 6.1 Fail-closed
Qualquer falha da seção 5 resulta em `FAIL_BLOCKING`.

### 6.2 No guess rule
O agente do repositório não pode completar lacunas do IR.

### 6.3 No silent coercion
O gate não pode “corrigir” automaticamente valores não-canônicos.

### 6.4 Registry-first
Se houver conflito entre o IR e registry soberano, registry vence e IR falha.

### 6.5 Surface mapping required
Toda decisão obrigatória deve apontar para pelo menos uma superfície canônica.

### 6.6 Template slot determinism
Todo slot obrigatório de template deve ter um binding explícito no IR ou em matriz de binding autorizada.

## 7. Testes mínimos do gate

### 7.1 Exemplos que DEVEM falhar
- entidade com campo `string` sem `semantic_type_ref`
- relationship `many_to_one` sem ownership
- capability sem surface mapping
- state model com transição não declarada
- use case HTTP sem request/response refs
- `open_decision` bloqueante em API central
- UI flow obrigatório ausente quando UI aplicável
- evento declarado sem trigger

### 7.2 Exemplos que DEVEM passar
- IR com todos os blocos aplicáveis fechados
- bindings 1:1 para todas as superfícies
- sem `open_decision` bloqueante
- sem registry drift
- sem lacunas de geração

## 8. Critério de aprovação

O IR só é aprovado quando:
- valida contra schema
- referencia apenas IDs válidos
- não contém lacuna crítica
- cobre superfícies aplicáveis
- não força escolha do agente durante a materialização

## 9. Regra final

**IR válido não é suficiente.**
**IR aprovado é aquele que pode ser materializado sem interpretação criativa.**
