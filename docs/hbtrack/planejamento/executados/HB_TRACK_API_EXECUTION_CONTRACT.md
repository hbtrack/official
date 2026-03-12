## HB TRACK API EXECUTION_CONTRACT.md

Hb Track é um sistema contract-driven onde o agente cria o agente cria o contrato. O sistema deixa de depender de “guidelines interpretados” e passa a depender de uma cadeia fechada de decisão:

`ARCHITECTURE_MATRIX` → `MODULE_PROFILE_REGISTRY` → `API_RULES` com gramática formal → compilador determinístico → política resolvida por superfície → contrato gerado → manifesto com hash → gates de conformidade.

Isso incorpora os quatro endurecimentos que você exigiu:
matriz de compatibilidade entre conjuntos de regras, tabela de sufixos canônicos, herança semântica no registro de tipos e assinatura/hash do artefato gerado.

O plano abaixo não é um “template bonito”. Ele é um desenho de governança computável para impedir que o agente:

* escolha perfil,
* escolha estilo,
* escolha tipo,
* escolha resolução de conflito,
* ou falsifique rastreabilidade.

O agente só pode consumir política resolvida e materializar artefatos compatíveis.

## 1. Arquitetura normativa final

A stack mínima canônica do HB Track fica assim:

```text
docs/_canon/decisions/
  HB_TRACK_ARCHITECTURE_DECISION.md

.contract_driven/templates/API_RULES/
  ARCHITECTURE_MATRIX.yaml
  MODULE_PROFILE_REGISTRY.yaml
  API_RULES.yaml
  CANONICAL_TYPE_REGISTRY.yaml

.contract_driven/templates/API_RULES/schemas/
  ARCHITECTURE_MATRIX.schema.json
  MODULE_PROFILE_REGISTRY.schema.json
  API_RULES.schema.json
  CANONICAL_TYPE_REGISTRY.schema.json
  TRACEABILITY_MANIFEST.schema.json

scripts/contracts/validate/api/
  compile_api_intent.py
  intent_compiler.py
  validate_architecture_matrix.py
  validate_module_profiles.py
  validate_api_rules.py
  validate_canonical_types.py
  compile_api_policy.py
  verify_traceability_manifest.py
  verify_contract_hash.py
  verify_cross_surface_parity.py
  verify_rule_compatibility.py
  verify_contract_to_code_conformance.py

generated/
  resolved_policy/
    training.sync.resolved.yaml
    training.event.resolved.yaml
  contracts/
    openapi/paths/training.yaml
    asyncapi/channels/training_attendance_marked.yaml
  manifests/
    training.sync.traceability.yaml
    training.event.traceability.yaml
```

Regra-mãe do sistema:

```yaml
governance_axiom:
  id: "HB-API-GOV-001"
  severity: "MUST"
  description: "Nenhum contrato pode ser gerado diretamente por agente. Todo contrato deve ser subproduto de política compilada e validada."
```

## 2. Fluxo determinístico obrigatório

O pipeline deve operar nesta ordem rígida:

```text
1. Validar ARCHITECTURE_MATRIX
2. Validar MODULE_PROFILE_REGISTRY
3. Verificar consistência MATRIX ↔ PROFILE
4. Validar API_RULES contra schema
5. Validar CANONICAL_TYPE_REGISTRY
6. Compilar Intent (DSL) -> contrato fonte (paths/<module>.yaml)
7. Resolver política efetiva por módulo + superfície
8. Executar matriz de compatibilidade entre regras ativas
9. Gerar manifesto de rastreabilidade
10. Calcular hash SHA-256 do contrato gerado
11. Validar Hash(Contrato) == Manifesto.hash
12. Executar gates cross-surface
13. Executar gates contrato ↔ código
14. Só então liberar para consumo do agente
```

Se qualquer etapa falhar, o resultado é `FAIL_ACTIONABLE` ou `BLOCKED_INPUT`. Nunca fallback heurístico.

## 3. ARCHITECTURE_MATRIX.yaml

Esse arquivo impede o “determinismo do erro” por rotulagem livre. Ele é a matriz estrutural dura do sistema.

```yaml
version: "1.0.0"

modules:
  identity_access:
    allowed_module_classes: ["CRUD"]
    allowed_surfaces: ["sync"]
    sensitive: false

  teams:
    allowed_module_classes: ["CRUD"]
    allowed_surfaces: ["sync"]
    sensitive: false

  training:
    allowed_module_classes: ["HYBRID"]
    allowed_surfaces: ["sync", "event"]
    sensitive: false

  matches:
    allowed_module_classes: ["EVENT_FIRST"]
    allowed_surfaces: ["event", "sync"]
    sensitive: false

  wellbeing:
    allowed_module_classes: ["HYBRID"]
    allowed_surfaces: ["sync", "event"]
    sensitive: true
```

Gate estrutural:

```yaml
architecture_contradiction_gate:
  id: "HB-ARCH-GATE-001"
  severity: "MUST"
  description: "MODULE_PROFILE_REGISTRY não pode declarar classe ou superfície fora da ARCHITECTURE_MATRIX."
```

## 4. MODULE_PROFILE_REGISTRY.yaml

Aqui o módulo é selado para compilação. O agente não escolhe nada.

```yaml
version: "1.0.0"

modules:
  training:
    module_class: "HYBRID"
    enabled_surfaces: ["sync", "event"]
    overlays: []
    contract_targets:
      sync: "openapi"
      event: "asyncapi"

  wellbeing:
    module_class: "HYBRID"
    enabled_surfaces: ["sync", "event"]
    overlays: ["sensitive_overlay"]
    contract_targets:
      sync: "openapi"
      event: "asyncapi"

  teams:
    module_class: "CRUD"
    enabled_surfaces: ["sync"]
    overlays: []
    contract_targets:
      sync: "openapi"
```

Regra determinística:
`HYBRID` não ativa ruleset híbrido. Apenas autoriza coexistência de superfícies distintas.

## 5. API_RULES.yaml — gramática formal

A regra canônica não pode ser prosa. A unidade mínima precisa ser computável.

```yaml
version: "1.0.0"

meta:
  agent_role: "consumer_only"
  decision_owner: "compiler"

style_veto:
  naming_casing:
    json_fields: "camelCase"
    query_params: "camelCase"
    path_params: "camelCase"
    async_payload_fields: "camelCase"
    uri_paths: "kebab-case"
    headers: "Hyphenated-Pascal-Case"
    enum_values: "UPPER_SNAKE_CASE"

  canonical_suffixes:
    identifier: "Id"
    timestamp: "At"
    datetime: "At"
    date: "Date"
    count: "Count"
    total_count: "TotalCount"
    amount: "Amount"
    ratio: "Ratio"
    percentage: "Percentage"
    status: "Status"
    type: "Type"
    version: "Version"
    url: "Url"
    uri: "Uri"

  source_conflict_policy:
    if_source_conflicts_with_style_veto: "style_veto_wins"

precedence:
  order:
    - architecture_gates
    - global_rules
    - profile_rules
    - surface_rules
    - module_overrides
    - templates
  collision_policy: "fail_closed"
  override_policy:
    explicit_only: true
    strict_rules_cannot_be_overridden: true
```

Formato obrigatório de regra:

```yaml
global_rules:
  - id: "API-GLOBAL-001"
    severity: "MUST"
    when:
      all:
        - contract_target in ["openapi", "asyncapi"]
        - surface in ["sync", "event"]
    then:
      enforce:
        field_casing: "camelCase"
    conflict_set: "field_naming"
    priority: 100
    strict: true
    override_allowed: false
    sources:
      - "ADIDAS"
      - "ZALANDO"
    rationale: "Evitar inconsistência de naming entre contratos"

  - id: "API-GLOBAL-002"
    severity: "MUST"
    when:
      all:
        - surface in ["sync", "event"]
    then:
      enforce:
        require_surface_binding: true
    conflict_set: "surface_binding"
    priority: 100
    strict: true
    override_allowed: false
    sources:
      - "HB_INTERNAL"
```

## 6. Matrizes de perfil e superfície

Perfis:

```yaml
profile_rules:
  crud_sync:
    allowed_surfaces: ["sync"]
    allowed_targets: ["openapi"]

  event_stream:
    allowed_surfaces: ["event"]
    allowed_targets: ["asyncapi"]

  sensitive_overlay:
    additive_only: true
    allowed_surfaces: ["sync", "event"]
    allowed_targets: ["openapi", "asyncapi"]
```

Superfícies:

```yaml
surface_rules:
  sync:
    requires:
      - http_method_semantics
      - status_code_semantics
      - operation_id
      - error_envelope
      - dto_boundary
    forbids:
      - event_offset_semantics
      - replay_contract_fields

  event:
    requires:
      - event_name
      - event_version
      - producer_identity
      - compatibility_mode
      - event_envelope
    forbids:
      - http_status_semantics
      - patch_semantics
```

## 7. Matriz de compatibilidade cross-set

Essa é a primeira lacuna que você apontou corretamente. Não basta checar colisão no mesmo `conflict_set`; é preciso validar satisfatibilidade entre conjuntos.

Estrutura:

```yaml
compatibility_matrix:
  - id: "COMP-001"
    set_a: "security_baseline"
    set_b: "cache_behavior"
    relation: "conditional"
    rule:
      if:
        - response_contains_sensitive_data == true
      then:
        require:
          cache_policy in ["no-store", "private"]
      else:
        allow: true

  - id: "COMP-002"
    set_a: "event_ordering"
    set_b: "idempotency"
    relation: "compatible"
    rule:
      require:
        consumer_idempotency_key: true

  - id: "COMP-003"
    set_a: "field_redaction"
    set_b: "projection_expansion"
    relation: "restricted"
    rule:
      if:
        - sensitive_overlay_active == true
      then:
        forbid:
          expanded_projection_contains_sensitive_fields: true
```

Algoritmo de arbitragem final:

```text
1. Selecionar regras aplicáveis por predicado.
2. Resolver conflito intra-set por priority/strict/override.
3. Montar conjunto efetivo de regras.
4. Avaliar pares e n-uplas relevantes na compatibility_matrix.
5. Se união for insatisfatível:
   - FAIL_CLOSED
6. Se união for condicional:
   - aplicar restrição derivada
7. Emitir política resolvida e prova de resolução
```

Isso transforma o compilador em resolvedor de política, não em mesclador de YAML.

## 8. Veto de estilo completo com sufixos canônicos

Essa era a sua segunda lacuna residual. O casing sozinho é insuficiente.

Tabela canônica recomendada para HB Track:

```yaml
style_veto:
  canonical_suffixes:
    entity_identifier: "Id"
    external_identifier: "ExternalId"
    source_identifier: "SourceId"
    timestamp: "At"
    creation_timestamp: "CreatedAt"
    update_timestamp: "UpdatedAt"
    deletion_timestamp: "DeletedAt"
    occurrence_timestamp: "OccurredAt"
    schedule_date: "Date"
    start_datetime: "StartAt"
    end_datetime: "EndAt"
    duration: "Duration"
    count: "Count"
    total_count: "TotalCount"
    sequence_number: "Number"
    amount: "Amount"
    percentage: "Percentage"
    score: "Score"
    status: "Status"
    category_type: "Type"
    schema_version: "Version"
    confidence_metric: "Confidence"
```

Regras:

* identificadores internos canônicos terminam em `Id`;
* UUID é formato, não sufixo;
* não usar `Uuid` no nome do campo se o tipo já declara `format: uuid`;
* timestamps terminam em `At`;
* datas puras terminam em `Date`;
* contadores terminam em `Count`;
* valores monetários terminam em `Amount`.

Exemplos válidos:

* `athleteId`
* `trainingSessionId`
* `sourceRecordId`
* `createdAt`
* `observedAt`
* `sessionDate`
* `retryCount`

Exemplos inválidos:

* `athleteUuid`
* `createdTimestamp`
* `session_datetime`
* `countTotal`

## 9. CANONICAL_TYPE_REGISTRY com herança semântica

Essa era a terceira lacuna: evitar monólito inflado de tipos 1:1 repetitivos.

Modelo correto: tipos base + tipos derivados + aliases semânticos.

```yaml
version: "1.0.0"

base_types:
  Identifier:
    primitive_type: "string"
    format: "uuid"
    nullable: false

  ExternalIdentifier:
    primitive_type: "string"
    nullable: false

  Timestamp:
    primitive_type: "string"
    format: "date-time"
    nullable: false

  Date:
    primitive_type: "string"
    format: "date"
    nullable: false

  Count:
    primitive_type: "integer"
    minimum: 0
    nullable: false

derived_types:
  AthleteId:
    inherits: "Identifier"
    semantic_id: "core.athlete.id.v1"

  TrainingSessionId:
    inherits: "Identifier"
    semantic_id: "training.session.id.v1"

  MatchId:
    inherits: "Identifier"
    semantic_id: "matches.match.id.v1"

  ObservedAt:
    inherits: "Timestamp"
    semantic_id: "core.observed_at.v1"

  RetryCount:
    inherits: "Count"
    semantic_id: "core.retry_count.v1"
```

Regras:

* campos em OpenAPI e AsyncAPI referenciam `semantic_id`, não apenas tipo primitivo;
* igualdade cross-surface é verificada por `semantic_id`;
* tipos derivados não podem contradizer o tipo base;
* exceções exigem novo derivado explícito.

Exemplo de binding:

```yaml
field_bindings:
  - field_name: "athleteId"
    canonical_type_ref: "core.athlete.id.v1"

  - field_name: "occurredAt"
    canonical_type_ref: "core.observed_at.v1"
```

## 10. Axiomas cross-surface

Essa camada garante que sync e event falem a mesma verdade semântica.

```yaml
cross_surface_axioms:
  - id: "XSA-001"
    severity: "MUST"
    description: "Mesmo semantic_id deve manter equivalência de tipo primitivo, formato e nullability em todas as superfícies."

  - id: "XSA-002"
    severity: "MUST"
    description: "Mesmo semantic_id deve manter naming canônico compatível com style_veto."

  - id: "XSA-003"
    severity: "MUST"
    description: "Campos sensíveis marcados em uma superfície devem preservar classificação e controles nas demais."

  - id: "XSA-004"
    severity: "MUST"
    description: "OpenAPI e AsyncAPI não podem divergir sobre enumeração canônica do mesmo semantic_id sem waiver explícito."
```

Gate:

```yaml
cross_surface_parity_gate:
  id: "HB-XSURF-GATE-001"
  on_failure: "FAIL_ACTIONABLE"
```

## 11. Module overrides restritos

Override só parametriza. Nunca muda fundamento universal.

```yaml
module_overrides:
  training:
    parameters:
      pagination_strategy: "cursor"
      sync_publish_requires_idempotency: true
    overrides:
      - rule_id: "API-SYNC-PAGINATION-001"
        override_allowed: true
        replacement:
          strategy: "cursor"

  wellbeing:
    parameters:
      default_redaction_policy: "strict"
      prohibit_projection_expansion: true
```

Regras:

* override sem `override_allowed: true` falha;
* override em regra `strict: true` falha;
* override gera prova explícita no manifesto.

## 12. Templates sem poder decisório

Template só renderiza shape final.

```yaml
templates:
  openapi:
    collection_path: "/{resourcePlural}"
    item_path: "/{resourcePlural}/{resourceId}"
    error_schema: "Problem"

  asyncapi:
    channel_pattern: "{boundedContext}.{aggregate}.{eventName}"
    envelope:
      required_fields:
        - eventId
        - eventType
        - eventVersion
        - occurredAt
        - producer
        - payload
```

Templates não podem:
* ativar perfil;
* mudar naming;
* mudar tipo;
* contornar gating.

## 13. Manifesto de rastreabilidade com prova e hash

Essa era sua quarta lacuna residual. O manifesto precisa provar o vínculo físico com o contrato.

```yaml
traceability_manifest:
  artifact_id: "training.sync.openapi"
  compiler_version: "1.0.0"
  source_inputs:
    - "ARCHITECTURE_MATRIX.yaml"
    - "MODULE_PROFILE_REGISTRY.yaml"
    - "API_RULES.yaml"
    - "CANONICAL_TYPE_REGISTRY.yaml"
  generated_contract_path: "generated/contracts/training.openapi.yaml"
  generated_contract_sha256: "..."
  applied_rules:
    - rule_id: "API-GLOBAL-001"
      effect: "field naming => camelCase"
    - rule_id: "API-SYNC-004"
      effect: "resource collection pagination"
    - rule_id: "API-MODULE-TRAINING-002"
      effect: "cursor pagination required"
  transformation_chain:
    - step: 1
      input: "MODULE_PROFILE.training"
      output: "sync surface active"
    - step: 2
      input: "profile_rules.crud_sync"
      output: "openapi target bound"
    - step: 3
      input: "style_veto"
      output: "trainingSessionId"
  compiler_checks:
    - "architecture_consistency: PASS"
    - "compatibility_matrix: PASS"
    - "cross_surface_parity: PASS"
    - "strict_override_check: PASS"
```

Gate criptográfico obrigatório:

```yaml
hash_integrity_gate:
  id: "HB-HASH-GATE-001"
  severity: "MUST"
  description: "Hash SHA-256 do contrato gerado deve coincidir com o manifesto."
```

Verificação:

```text
if sha256(contract_file_bytes) != manifest.generated_contract_sha256:
    FAIL_CLOSED
```

Isso impede “manifesto honesto para contrato adulterado”.

## 14. Gates finais

Conjunto mínimo de gates:

```yaml
validation_gates:
  - id: "GATE-001"
    name: "architecture_consistency"
    on_failure: "BLOCKED_INPUT"

  - id: "GATE-002"
    name: "rule_schema_validity"
    on_failure: "FAIL_ACTIONABLE"

  - id: "GATE-003"
    name: "intra_set_conflict_resolution"
    on_failure: "FAIL_ACTIONABLE"

  - id: "GATE-004"
    name: "cross_set_compatibility_sat"
    on_failure: "FAIL_ACTIONABLE"

  - id: "GATE-005"
    name: "style_veto_enforcement"
    on_failure: "FAIL_ACTIONABLE"

  - id: "GATE-006"
    name: "cross_surface_parity"
    on_failure: "FAIL_ACTIONABLE"

  - id: "GATE-007"
    name: "sensitive_overlay_required"
    on_failure: "FAIL_ACTIONABLE"

  - id: "GATE-008"
    name: "manifest_hash_integrity"
    on_failure: "FAIL_CLOSED"

  - id: "GATE-009"
    name: "contract_validation"
    on_failure: "FAIL_ACTIONABLE"

  - id: "GATE-010"
    name: "contract_to_code_conformance"
    on_failure: "FAIL_ACTIONABLE"
```

## 15. Política de fontes e veto interno

Para evitar deriva entre RAGs, a regra precisa ser explícita:

```yaml
source_registry:
  ADIDAS:
    role: "contract_linting_rest_async_split"

  ZALANDO:
    role: "rest_pragmatism_compatibility_events"

  GOOGLE_AIP:
    role: "resource_and_operation_design"

  OWASP:
    role: "security_overlay_priority"

internal_vetoes:
  - id: "VETO-STYLE-001"
    description: "Style veto interno do HB Track prevalece sobre divergências entre fontes."
  - id: "VETO-SEC-001"
    description: "OWASP prevalece em decisões de segurança quando houver tensão com conveniência de modelagem."
```

## 16. Ordem de implantação recomendada

Ordem segura, sem salto de complexidade:

Fase 1: `ARCHITECTURE_MATRIX.yaml`
Fase 2: `MODULE_PROFILE_REGISTRY.yaml`
Fase 3: `CANONICAL_TYPE_REGISTRY.yaml` com herança
Fase 4: `API_RULES.yaml` com gramática formal
Fase 5: `compile_api_policy.py`
Fase 6: `verify_rule_compatibility.py`
Fase 7: `verify_cross_surface_parity.py`
Fase 8: geração de contrato + manifesto + hash
Fase 9: `verify_contract_to_code_conformance.py`

---

## 17. Protocolo de feedback do compiler (Actionable errors para agente)

Quando qualquer etapa **fail-closed** falhar (ex.: `GATE-005` style veto ou `GATE-004` compatibilidade), o compiler deve emitir um erro **estruturado e rastreável por ID**, de modo que um agente consiga:
- localizar o artefato exato (`artifact`),
- localizar o ponto exato (`json_path`),
- identificar a regra (`rule_id` + `gate_id`),
- e aplicar uma ação corretiva sem tentativa-e-erro.

### 17.1 Saída canônica (JSON)

O comando `python3 scripts/contracts/validate/api/compile_api_policy.py --format json ...` emite (em caso de falha) **um único JSON** no `stderr` com este envelope:

```json
{
  "artifact_id": "HBTRACK_API_POLICY_COMPILER_ERROR",
  "status": "FAIL_ACTIONABLE | BLOCKED_INPUT | FAIL_CLOSED",
  "blocking_code": "…",
  "summary": "…",
  "violations": [
    {
      "gate_id": "GATE-005-style_veto_enforcement",
      "rule_id": "HB-STYLE-VETO-002",
      "code": "BLOCKED_STYLE_VETO_UUID_SUFFIX",
      "severity": "error",
      "artifact": "contracts/…/file.yaml",
      "json_path": "$.properties.userUuid",
      "location": { "line": 42, "column": 5 },
      "message": "Sufixo proibido `Uuid` para UUID v4 (use `...Id`).",
      "hint": "Renomeie para `...Id` (ex.: userId, athleteId).",
      "ssot_refs": [
        { "path": ".contract_driven/templates/API_RULES/API_RULES.yaml", "pointer": "$.hbtrack_api_rules.…" },
        { "path": ".contract_driven/templates/API_RULES/CANONICAL_TYPE_REGISTRY.yaml", "pointer": "$.field_bindings" }
      ]
    }
  ],
  "actions": [
    "Corrigir o contrato fonte (ou o manifesto de intenção, quando aplicável).",
    "Reexecutar: python3 scripts/contracts/validate/api/compile_api_policy.py --all"
  ],
  "details": {
    "artifact": "contracts/…/file.yaml",
    "enforcement": "pre-signature (fail-closed before manifest/hash)"
  }
}
```

### 17.2 Exemplo: violação de sufixo canônico (`Id` vs `Uuid`)

Se um schema contiver `userUuid` com `format: uuid` (ou pattern UUID v4), o compiler deve falhar com:
- `status=FAIL_ACTIONABLE`
- `violations[].rule_id` em `HB-STYLE-VETO-002` e/ou `HB-STYLE-VETO-003`
- `violations[].json_path` apontando para o field específico

### 17.3 Exemplo: conflito de compatibilidade (GATE-004)

Para compatibilidade, o envelope acima é estendido com um `details.compatibility` determinístico (sem heurística), para apontar a **causa raiz**:

```json
{
  "details": {
    "compatibility": {
      "unsat_core": ["API-GLOBAL-017", "API-SYNC-004"],
      "conflicts": [
        {
          "compatibility_id": "COMP-003",
          "set_a": "field_redaction",
          "set_b": "projection_expansion",
          "rules_involved": ["API-GLOBAL-017", "API-SYNC-004"]
        }
      ]
    }
  }
}
```

Regra de usabilidade:
- o agente **nunca** recebe apenas “FAIL_CLOSED”; ele recebe `unsat_core` e `rules_involved` para corrigir o manifesto/política.

### 17.4 Intent compiler (DSL) — erros apontam para `.intent.yaml`

No fluxo dirigido por intenção, o comando:

`python3 scripts/contracts/validate/api/compile_api_intent.py --module <module> --format json`

deve emitir violações com:
- `artifact` apontando para `contracts/openapi/intents/<module>.intent.yaml`
- `json_path` apontando para a DSL (ex.: `$.hbtrack_api_intent.local_semantic_types[0].semantic_id`)
- `location` com linha/coluna no `.intent.yaml` (o agente corrige o **input**, não o YAML técnico gerado)
