
# CONTRACT DRIVEN - HB TRACK

+`00_ATLETAS_CROSS_LINTER_RULES.json`   -> meta-contrato
+`01_ATLETAS_OPENAPI.yaml`              ->
`04_ATLETAS_WORKFLOWS.arazzo.yaml`      ->      
+`05_ATLETAS_EVENTS.asyncapi.yaml`      ->
`06_ATLETAS_CONSUMER_CONTRACTS.md`      -> contrato de eventos
`08_ATLETAS_TRACEABILITY.yaml`          -> vinculação operação <-> código
`12_ATLETAS_EXECUTION_BINDINGS.yaml`    -> binding executável        
+`13_ATLETAS_DB_CONTRACT.yaml`          -> persistência e locking
`14_ATLETAS_UI_CONTRACT.yaml`           -> superfície testável
+`15_ATLETAS_INVARIANTS.yaml`           -> predicados de domínio
+`16_ATLETAS_AGENT_HANDOFF.json`        -> snapshot fechado
+`17_ATLETAS_PROJECTIONS.yaml`          -> materialização evento -> read model
+`18_ATLETAS_SIDE_EFFECTS.yaml`         -> artefatos para controle da IA
+`19_ATLETAS_TEST_SCENARIOS.yaml` 
+`20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md`      

`hb_plan.py`                    -> gerador determinístico do snapshot
`hb_verify.py`                  -> validador determinístico contra o snapshot

**MOTORES DE VALIDAÇÃO**

`hb_plan.py`
  -> valida schemas
  -> carrega contratos
  -> resolve checker_ids permitidos
  -> executa funções puras de validação
  -> gera handoff + manifesto de âncoras

`hb_verify.py`
  -> recarrega snapshot
  -> reexecuta checkers de verificação
  -> roda validador AST Python
  -> roda validador AST TS/TSX
  -> emite PASS/FAIL com exit code


### 00_ATLETAS_CROSS_LINTER_RULES.json

`/docs/_canon/contratos/00_ATLETAS_CROSS_LINTER_RULES.json`

* Este arquivo é o **Meta-Contrato.**
* Ele não descreve o módulo, ele descreve as regras que os contratos do módulo devem obedecer entre si.

* Impedir que:
- um campo exista no OpenAPI e não exista no DB contract
- um operationId exista sem binding
- um seletor exista na UI sem tela vinculada
- uma invariante seja referenciada sem definição formal
- um tipo seja divergente entre backend, contrato e frontend
- um write path exista sem política de concorrência
- um handoff seja emitido com dependências inconsistentes

## O Schema Formal (Meta-Validation)

* Schema valida o Linter:
-  Arquiteto não pode cometer um erro de digitação no próprio Meta-Contrato (digitar `severity: "erro"` em vez de `"error"`).
- Validar os enums de `severity`, os `exit_codes` e a estrutura das `cross_rules`.

# 01_ATLETAS_OPENAPI.yaml - Módulo ATHLETES

Este template não resolve tudo

- Resolve o que OpenAPI deve resolver: 
   * interface HTTP
   * Payload
   * Responses
   * Segurança
   * Semântica pública da operação

É esse o limite correto da ferramenta.

```yaml
openapi: 3.1.1
info:
  title: HB Track - Athletes Module API
  version: 1.0.0
  summary: Contract API for ATHLETES module
  description: >
    Public HTTP contract for athlete management in HB Track.

jsonSchemaDialect: https://json-schema.org/draft/2020-12/schema

servers:
  - url: https://api.hbtrack.local

tags:
  - name: ATHLETES
    description: Athlete management operations

security:
  - bearerAuth: []

paths:
  /api/v1/athletes:
    post:
      tags: [ATHLETES]
      operationId: athletes__athlete__create
      summary: Create athlete
      description: Creates a new athlete record.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AthleteCreateRequest'
            examples:
              validMinimal:
                $ref: '#/components/examples/AthleteCreateRequestValidMinimal'
              invalidDuplicateFederationId:
                $ref: '#/components/examples/AthleteCreateRequestDuplicateFederationId'
      responses:
        '201':
          description: Athlete created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AthleteResponse'
              examples:
                success:
                  $ref: '#/components/examples/AthleteResponseCreated'
        '409':
          $ref: '#/components/responses/AthleteFederationIdConflict'
        '422':
          $ref: '#/components/responses/ValidationError'
        '401':
          $ref: '#/components/responses/UnauthorizedError'

    get:
      tags: [ATHLETES]
      operationId: athletes__athlete__list
      summary: List athletes
      description: Returns athletes according to the provided filters.
      parameters:
        - $ref: '#/components/parameters/TeamIdQuery'
        - $ref: '#/components/parameters/CategoryIdQuery'
        - $ref: '#/components/parameters/PageQuery'
        - $ref: '#/components/parameters/PageSizeQuery'
      responses:
        '200':
          description: Paginated athlete list
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AthleteListResponse'
        '401':
          $ref: '#/components/responses/UnauthorizedError'

  /api/v1/athletes/{athlete_id}:
    get:
      tags: [ATHLETES]
      operationId: athletes__athlete__get
      summary: Get athlete by id
      parameters:
        - $ref: '#/components/parameters/AthleteIdPath'
      responses:
        '200':
          description: Athlete found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AthleteResponse'
        '404':
          $ref: '#/components/responses/AthleteNotFound'
        '401':
          $ref: '#/components/responses/UnauthorizedError'

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  parameters:
    AthleteIdPath:
      name: athlete_id
      in: path
      required: true
      schema:
        type: string
        format: uuid

    TeamIdQuery:
      name: team_id
      in: query
      required: false
      schema:
        type: string
        format: uuid

    CategoryIdQuery:
      name: category_id
      in: query
      required: false
      schema:
        type: string
        format: uuid

    PageQuery:
      name: page
      in: query
      required: false
      schema:
        type: integer
        minimum: 1
        default: 1

    PageSizeQuery:
      name: page_size
      in: query
      required: false
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20

  schemas:
    AthleteCreateRequest:
      type: object
      additionalProperties: false
      required:
        - full_name
        - birth_date
        - category_id
      properties:
        full_name:
          type: string
          minLength: 3
          maxLength: 120
        birth_date:
          type: string
          format: date
        category_id:
          type: string
          format: uuid
        team_id:
          type: [string, 'null']
          format: uuid
        federation_id:
          type: [string, 'null']
          maxLength: 50
        dominant_hand:
          $ref: '#/components/schemas/DominantHand'

    AthleteResponse:
      type: object
      additionalProperties: false
      required:
        - athlete_id
        - full_name
        - birth_date
        - category_id
        - status
        - created_at
      properties:
        athlete_id:
          type: string
          format: uuid
        full_name:
          type: string
        birth_date:
          type: string
          format: date
        category_id:
          type: string
          format: uuid
        team_id:
          type: [string, 'null']
          format: uuid
        federation_id:
          type: [string, 'null']
        dominant_hand:
          $ref: '#/components/schemas/DominantHand'
        status:
          $ref: '#/components/schemas/AthleteStatus'
        created_at:
          type: string
          format: date-time

    AthleteListItem:
      allOf:
        - $ref: '#/components/schemas/AthleteResponse'

    AthleteListResponse:
      type: object
      additionalProperties: false
      required:
        - items
        - page
        - page_size
        - total
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/AthleteListItem'
        page:
          type: integer
        page_size:
          type: integer
        total:
          type: integer

    DominantHand:
      type: string
      enum: [RIGHT, LEFT, AMBIDEXTROUS]

    AthleteStatus:
      type: string
      enum: [ACTIVE, INACTIVE]

    ErrorResponse:
      type: object
      additionalProperties: false
      required:
        - error_code
        - message
      properties:
        error_code:
          type: string
        message:
          type: string
        details:
          type: object
          additionalProperties: true

  responses:
    AthleteNotFound:
      description: Athlete not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          examples:
            default:
              value:
                error_code: ATHLETE_NOT_FOUND
                message: Athlete not found

    AthleteFederationIdConflict:
      description: Federation id already exists
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          examples:
            default:
              value:
                error_code: ATHLETE_FEDERATION_ID_CONFLICT
                message: Federation id already exists

    ValidationError:
      description: Validation failed
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'

    UnauthorizedError:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'

  examples:
    AthleteCreateRequestValidMinimal:
      value:
        full_name: Ana Souza
        birth_date: 2010-05-13
        category_id: 4d8d3d80-1f6f-4db4-a245-e8db97f6d111
        team_id: null
        federation_id: FB-2026-0001
        dominant_hand: RIGHT

    AthleteCreateRequestDuplicateFederationId:
      value:
        full_name: Ana Souza
        birth_date: 2010-05-13
        category_id: 4d8d3d80-1f6f-4db4-a245-e8db97f6d111
        federation_id: FB-2026-0001

    AthleteResponseCreated:
      value:
        athlete_id: 8b25688c-2ea9-48ad-9b8a-7ff5df6d0101
        full_name: Ana Souza
        birth_date: 2010-05-13
        category_id: 4d8d3d80-1f6f-4db4-a245-e8db97f6d111
        team_id: null
        federation_id: FB-2026-0001
        dominant_hand: RIGHT
        status: ACTIVE
        created_at: 2026-03-07T12:00:00Z
```

## 05_ATLETAS_EVENTS.asyncapi.yaml 

O Log de Eventos e Upcasting.

```yaml
asyncapi: 3.0.0
info:
  title: HB Track - Athletes Events
  version: 1.0.0
channels:
  athleteRegisteredV2:
    address: hbtrack.athletes.athlete-registered.v2
    messages:
      AthleteRegisteredV2:
        payload:
          $ref: '#/components/schemas/AthleteRegisteredV2Envelope'
channels:
  athleteRegisteredV2:
    address: hbtrack.athletes.athlete-registered.v2
    messages:
      AthleteRegisteredV2:
        payload:
          $ref: '#/components/schemas/AthleteRegisteredV2Envelope'
components:
  schemas:
    EventMetadata:
      type: object
      required: [event_id, event_type, event_version, aggregate_id, occurred_at]
      properties:
        event_id: { type: string, format: uuid }
        event_version: { type: integer, const: 2 }
        aggregate_id: { type: string, format: uuid }
        occurred_at: { type: string, format: date-time }
        replay: { type: boolean, default: false }
x-hbtrack:
  upcasting:
    rules:
      - event_type: AthleteRegistered
        from_version: 1
        to_version: 2
        stub_symbol: upcast_athlete_registered_v1_to_v2
        target_file: backend/app/events/upcasters/athletes_upcasters.py
        transformation:
          injected_fields: { federation_id: null }
  transport_ordering:
  broker: kafka
    required_partition_key: aggregate_id
    ordering_scope: per_partition_only

```
## 13_ATLETAS_DB_CONTRACT.yaml

```yaml
meta:
  document_id: DB-ATHLETES
  module_id: ATHLETES
  db_engine: postgresql
  migration_tool: alembic
file_map:
  canonical_files:
    sqlalchemy_model_file: backend/app/models/athlete.py
    alembic_migration_file: backend/alembic/versions/20260307_1200_create_athletes_table.py
database_contract:
  tables:
    - table_name: athletes
      columns:
        - name: athlete_id
          type: uuid
          nullable: false
        - name: full_name
          type: varchar(120)
          nullable: false
        - name: birth_year
          type: integer
          nullable: false
      constraints:
        - name: ck_athletes_birth_year_consistency
          check: "birth_year = EXTRACT(YEAR FROM birth_date)"
      locking_policy:
        type: optimistic_locking
        version_column: version_id
```

## 15_ATLETAS_INVARIANTS.yaml

No HB Track, invariantes precisam ser escritas em forma computável.

* Níveis Estrutirais de Invariantes:
	1.	natural_language_rule
	2.	domain_terms
	3.	formal_predicate
	4.	reference_function
	5.	enforcement_bindings

```yaml
meta:
  document_id: INV-ATHLETES
  module_id: ATHLETES
  module_version: 1.0.0
  status: DRAFT
  authority_level: DOMAIN_SSOT
  predicate_language: pseudo_logic_v1
  executor_freedom:
    reinterpret_rule_natural_language: forbidden
    replace_predicate_with_approximation: forbidden

file_map:
  canonical_files:
    invariant_policy_file: backend/app/domain/invariants/athletes_invariants.py
    reference_mapping_file: backend/app/domain/reference/category_birth_year_mapping.py
    invariant_tests_file: backend/tests/domain/test_athletes_invariants.py

domain_functions:
  - function_id: F-ATH-001
    name: category_allowed_birth_years
    location: backend/app/domain/reference/category_birth_year_mapping.py
    signature: "(competition_year: int, category_code: str) -> set[int]"
    description: Returns the complete set of allowed birth years for a competition year and category code.

  - function_id: F-ATH-002
    name: athlete_is_soft_deleted
    location: backend/app/domain/invariants/athletes_invariants.py
    signature: "(deleted_at: datetime | None) -> bool"

invariants:
  - invariant_id: INV-ATH-001
    name: federation_id_unique_when_present
    scope: athlete_create, athlete_update
    natural_language_rule: >
      federation_id, when provided, must uniquely identify an athlete record within ATHLETES.
    domain_terms:
      federation_id: external federation registration identifier
      athlete_record: persisted canonical athlete entity
    formal_predicate: |
      FOR ALL a1, a2 IN athletes:
        IF a1.federation_id IS NOT NULL
        AND a2.federation_id IS NOT NULL
        AND a1.federation_id = a2.federation_id
        THEN a1.athlete_id = a2.athlete_id
    enforcement_bindings:
      database:
        - uq_athletes_federation_id
      service:
        - athlete_create
        - athlete_update
      tests:
        - test_athlete_create_duplicate_federation_id_rejected
        - test_athlete_update_duplicate_federation_id_rejected
    blocking_level: hard_fail

  - invariant_id: INV-ATH-002
    name: category_compatibility_by_birth_year_and_competition_year
    scope: athlete_create, athlete_update, lineup_assignment
    natural_language_rule: >
      athlete category compatibility must be determined by birth year against the competition year,
      not by current age.
    domain_terms:
      competition_year: official reference year of the competition context
      birth_year: integer extracted from athlete birth_date
      category_code: official competition category code
    formal_predicate: |
      FOR ALL athlete, competition:
        let birth_year = YEAR(athlete.birth_date)
        let allowed_years = category_allowed_birth_years(competition.year, athlete.category_code)
        athlete.category_id IS VALID
        IMPLIES birth_year IN allowed_years
    reference_function:
      function_id: F-ATH-001
      mandatory_usage: true
      fallback_manual_logic_allowed: false
    executable_pseudocode: |
      birth_year = athlete.birth_date.year
      allowed_years = category_allowed_birth_years(competition.year, athlete.category_code)

      if birth_year not in allowed_years:
          raise InvariantViolation("INV-ATH-002")
    failure_mode:
      - athlete registered in ineligible category
      - downstream lineup or competition validation corruption
    enforcement_bindings:
      domain_service:
        - athlete_create
        - athlete_update
      tests:
        - test_category_compatibility_birth_year_valid
        - test_category_compatibility_birth_year_invalid
      required_inputs:
        - competition.year
        - athlete.birth_date
        - athlete.category_code
    blocking_level: hard_fail

  - invariant_id: INV-ATH-003
    name: inactive_athlete_cannot_be_assigned_to_active_lineup
    scope: lineup_assignment
    natural_language_rule: >
      inactive athletes cannot be assigned to active competition lineup.
    formal_predicate: |
      FOR ALL athlete, lineup:
        IF athlete.status = 'INACTIVE'
        THEN athlete NOT IN lineup.active_roster
    executable_pseudocode: |
      if athlete.status == "INACTIVE":
          raise InvariantViolation("INV-ATH-003")
    enforcement_bindings:
      domain_service:
        - lineup_assign_athlete
      tests:
        - test_inactive_athlete_cannot_be_assigned
    blocking_level: hard_fail

  - invariant_id: INV-ATH-010
    name: soft_deleted_athlete_must_not_appear_in_default_listing
    scope: athlete_list
    natural_language_rule: >
      soft deleted athletes must be excluded from default list operations.
    formal_predicate: |
      FOR ALL athlete IN list_athletes_default_result:
        athlete.deleted_at IS NULL
    executable_pseudocode: |
      query = query.where(athletes.deleted_at.is_(None))
    enforcement_bindings:
      repository:
        - athlete_list
      tests:
        - test_get_athletes_excludes_soft_deleted
    blocking_level: hard_fail

reference_tables:
  - table_id: REF-CATEGORY-BIRTH-YEAR
    source: canonical_reference_data
    owner_function: F-ATH-001
    versioning_policy: explicit_version
    sample_mapping:
      competition_year: 2026
      values:
        U14: [2012, 2013]
        U16: [2010, 2011]
        U18: [2008, 2009]

rules:
  - rule_id: INV-RULE-001
    description: Natural language text is informative only; formal_predicate and executable_pseudocode are normative.
  - rule_id: INV-RULE-002
    description: If a reference_function exists, the Executor must call it instead of recreating equivalent logic inline.
  - rule_id: INV-RULE-003
    description: Every hard_fail invariant must bind to at least one automated test.
  - rule_id: INV-RULE-004
    description: Invariants depending on competition context must declare required_inputs explicitly.
```
* Agora a regra é:
	•	função de referência explícita,
	•	predicado,
	•	pseudocódigo,
	•	entradas obrigatórias,
	•	binding de enforcement.

Ou seja: o Executor não implementa “idade atual”; ele é obrigado a usar competition.year e birth_year.

# 16_ATLETAS_AGENT_HANDOFF.json 

Preenchido de forma coerente com o schema aprovado e com o Contract Pack do módulo ATHLETES.

```json
{
  "handoff_id": "HANDOFF-ATHLETES-2026-03-07-001",
  "module_id": "ATHLETES",
  "module_version": "1.0.0",
  "status": "READY_FOR_EXECUTION",
  "authority_level": "EXECUTION_GATE",
  "issued_by": "HB_PLAN",
  "issued_at": "2026-03-07T13:00:00-03:00",
  "conversation_independent": true
}
```
---
```json
{
  "meta": {
    "handoff_id": "HANDOFF-ATHLETES-2026-03-07-001",
    "module_id": "ATHLETES",
    "module_version": "1.0.0",
    "status": "READY_FOR_EXECUTION",
    "authority_level": "EXECUTION_GATE",
    "issued_by": "HB_PLAN",
    "issued_at": "2026-03-07T13:00:00-03:00",
    "conversation_independent": true
  },
  "integrity": {
    "snapshot_mode": "hash_locked",
    "artifacts": [
      {
        "path": "docs/hbtrack/modulos/atletas/00_ATLETAS_CROSS_LINTER_RULES.json",
        "role": "meta_contract",
        "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      },
      {
        "path": "docs/hbtrack/modulos/atletas/01_ATLETAS_OPENAPI.yaml",
        "role": "contract_http",
        "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
      },
      {
        "path": "docs/hbtrack/modulos/atletas/08_ATLETAS_TRACEABILITY.yaml",
        "role": "execution_binding",
        "sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
      },
      {
        "path": "docs/hbtrack/modulos/atletas/13_ATLETAS_DB_CONTRACT.yaml",
        "role": "db_contract",
        "sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
      },
      {
        "path": "docs/hbtrack/modulos/atletas/14_ATLETAS_UI_CONTRACT.yaml",
        "role": "ui_contract",
        "sha256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
      },
      {
        "path": "docs/hbtrack/modulos/atletas/15_ATLETAS_INVARIANTS.yaml",
        "role": "domain_invariants",
        "sha256": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
      },
      {
        "path": "docs/hbtrack/modulos/atletas/05_ATLETAS_EVENTS.asyncapi.yaml",
        "role": "events_contract",
        "sha256": "1111111111111111111111111111111111111111111111111111111111111111"
      },
      {
        "path": "docs/hbtrack/modulos/atletas/17_ATLETAS_PROJECTIONS.yaml",
        "role": "projection_contract",
        "sha256": "2222222222222222222222222222222222222222222222222222222222222222"
      },
      {
        "path": "docs/hbtrack/modulos/atletas/18_ATLETAS_SIDE_EFFECTS.yaml",
        "role": "side_effects_contract",
        "sha256": "3333333333333333333333333333333333333333333333333333333333333333"
      },
      {
        "path": "docs/hbtrack/modulos/atletas/19_ATLETAS_TEST_SCENARIOS.yaml",
        "role": "test_scenarios_contract",
        "sha256": "4444444444444444444444444444444444444444444444444444444444444444"
      },
      {
        "path": "docs/hbtrack/modulos/atletas/20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md",
        "role": "restriction_prompt",
        "sha256": "5555555555555555555555555555555555555555555555555555555555555555"
      }
    ],
    "stale_snapshot_policy": "block_execution",
    "snapshot_hash": "9999999999999999999999999999999999999999999999999999999999999999"
  },
  "execution_scope": {
    "allowed_operation_ids": [
      "athletes__athlete__create",
      "athletes__athlete__list",
      "athletes__athlete__get"
    ],
    "forbidden_operation_ids": [
      "athletes__athlete__delete",
      "athletes__athlete__merge",
      "athletes__athlete__bulk_import"
    ],
    "allowed_file_paths": [
      "backend/app/generated/athletes_contract_types.py",
      "backend/app/generated/athletes_stub_bindings.py",
      "backend/app/models/athlete.py",
      "backend/app/schemas/athlete.py",
      "backend/app/repositories/athlete_repository.py",
      "backend/app/services/athlete_service.py",
      "backend/app/projections/athletes_projection.py",
      "backend/app/side_effects/athletes_side_effects.py",
      "backend/app/domain/invariants/athletes_invariants.py",
      "backend/app/domain/reference/category_birth_year_mapping.py",
      "backend/alembic/versions/20260307_1200_create_athletes_table.py",
      "frontend/src/lib/generated/athletes-client.ts",
      "frontend/src/app/athletes/page.tsx",
      "frontend/src/features/athletes/screens/AthleteCreateScreen.tsx",
      "frontend/src/features/athletes/screens/AthleteListScreen.tsx",
      "frontend/src/features/athletes/components/AthleteForm.tsx",
      "frontend/tests/e2e/athletes.spec.ts",
      "_reports/hb_plan_result.json",
      "_reports/hb_plan_result.md",
      "_reports/hb_verify_result.json",
      "_reports/hb_verify_result.md"
    ],
    "forbidden_write_paths": [
      "backend/app/services/training_service.py",
      "backend/app/services/competitions_service.py",
      "frontend/src/features/competitions/",
      "frontend/src/features/training/",
      "docs/hbtrack/modules/TRAINING/",
      "docs/hbtrack/modules/COMPETITIONS/"
    ],
    "operation_file_bindings": [
      {
        "operation_id": "athletes__athlete__create",
        "file_paths": [
          "backend/app/services/athlete_service.py",
          "backend/app/repositories/athlete_repository.py",
          "backend/app/models/athlete.py",
          "backend/app/schemas/athlete.py",
          "backend/app/projections/athletes_projection.py",
          "backend/app/side_effects/athletes_side_effects.py",
          "frontend/src/features/athletes/components/AthleteForm.tsx",
          "frontend/src/features/athletes/screens/AthleteCreateScreen.tsx",
          "frontend/tests/e2e/athletes.spec.ts"
        ],
        "public_symbols": [
          "athlete_create",
          "create_athlete",
          "AthleteModel",
          "AthleteCreateSchema",
          "apply_athlete_registered_v1",
          "send_athlete_registered_notification",
          "AthleteCreateScreen"
        ]
      },
      {
        "operation_id": "athletes__athlete__list",
        "file_paths": [
          "backend/app/services/athlete_service.py",
          "backend/app/repositories/athlete_repository.py",
          "backend/app/schemas/athlete.py",
          "frontend/src/features/athletes/screens/AthleteListScreen.tsx",
          "frontend/tests/e2e/athletes.spec.ts"
        ],
        "public_symbols": [
          "athlete_list",
          "list_athletes",
          "AthleteListScreen"
        ]
      },
      {
        "operation_id": "athletes__athlete__get",
        "file_paths": [
          "backend/app/services/athlete_service.py",
          "backend/app/repositories/athlete_repository.py",
          "backend/app/schemas/athlete.py"
        ],
        "public_symbols": [
          "athlete_get",
          "get_athlete"
        ]
      }
    ],
    "public_symbol_policy": {
      "public_symbols_declared_only": true,
      "private_helper_symbols": {
        "allowed": true,
        "naming_pattern": "^_",
        "allowed_scope": "inside_anchor_region_only",
        "export_forbidden": true
      }
    }
  },
  "codegen_requirements": {
    "openapi_codegen_required": true,
    "frontend_client_generation_required": true,
    "backend_stub_generation_required": true,
    "manual_symbol_creation_allowed": false,
    "required_generated_artifacts": [
      "frontend/src/lib/generated/athletes-client.ts",
      "backend/app/generated/athletes_contract_types.py",
      "backend/app/generated/athletes_stub_bindings.py"
    ]
  },
  "db_requirements": {
    "required_migrations": [
      "backend/alembic/versions/20260307_1200_create_athletes_table.py"
    ],
    "required_locking_policies": [
      {
        "aggregate": "athlete",
        "write_paths": [
          "athletes__athlete__create"
        ],
        "locking_policy": "single_transaction_no_version"
      },
      {
        "aggregate": "lineup",
        "write_paths": [
          "lineups__lineup__update"
        ],
        "locking_policy": "optimistic_locking",
        "version_column": "version_id",
        "conflict_error_code": "LINEUP_VERSION_CONFLICT",
        "retry_policy": "no_automatic_retry"
      }
    ]
  },
  "ui_requirements": {
    "selector_strategy": "data-testid",
    "playwright_selector_api": "getByTestId",
    "required_screen_state_policies": [
      {
        "screen_id": "athletes.create",
        "state": "submitting",
        "submit_button_policy": "disabled",
        "double_click_blocked": true
      },
      {
        "screen_id": "athletes.create",
        "state": "success",
        "feedback_selector": "athletes.create.feedback.success"
      },
      {
        "screen_id": "athletes.create",
        "state": "validation_error",
        "feedback_selector": "athletes.create.feedback.error"
      },
      {
        "screen_id": "athletes.list",
        "state": "loading"
      },
      {
        "screen_id": "athletes.list",
        "state": "error",
        "feedback_selector": "athletes.list.feedback.error"
      }
    ]
  },
  "type_guarantees": {
    "canonical_types": [
      {
        "field": "athlete_id",
        "contract_type": "uuid",
        "backend_type": "UUID",
        "frontend_type": "string",
        "db_type": "uuid",
        "serialized_format": "uuid-string"
      },
      {
        "field": "birth_date",
        "contract_type": "date",
        "backend_type": "date",
        "frontend_type": "string",
        "db_type": "date",
        "serialized_format": "yyyy-mm-dd"
      },
      {
        "field": "competition_reference_year",
        "contract_type": "integer",
        "backend_type": "int",
        "frontend_type": "number",
        "db_type": "integer",
        "serialized_format": "number:int"
      }
    ],
    "type_drift_policy": "block_execution"
  },
  "invariant_requirements": {
    "required_invariant_ids": [
      "INV-ATH-001",
      "INV-ATH-002",
      "INV-ATH-010"
    ],
    "reference_functions_required": [
      {
        "function_id": "F-ATH-001",
        "name": "category_allowed_birth_years",
        "fallback_manual_logic_allowed": false
      }
    ]
  },
  "validator_requirements": {
    "allowed_checker_ids": [
      "check_required_documents_exist",
      "check_openapi_operation_ids_are_traceable",
      "check_traceability_operations_exist_in_openapi",
      "check_db_nullability_matches_api_write_contract",
      "check_ui_fields_bind_to_openapi_properties",
      "check_traceability_invariants_exist_and_are_executable",
      "check_handoff_hashes_match_snapshot",
      "check_required_migrations_exist_before_execution",
      "check_projection_event_types_exist",
      "check_projection_versions_are_supported_or_upcasted",
      "check_side_effects_reference_declared_events",
      "check_projection_handlers_are_side_effect_free",
      "check_temporal_invariants_require_reference_inputs",
      "check_temporal_invariants_forbid_system_clock",
      "check_frozen_time_enabled_for_temporal_scenarios",
      "check_test_scenarios_are_canonical_only",
      "check_stub_edits_stay_within_anchors",
      "check_generated_symbols_are_immutable",
      "check_no_uncontracted_public_symbols",
      "check_contract_hash_comment_matches_snapshot",
      "check_executor_prompt_is_fail_closed"
    ],
    "required_checker_ids": [
      "check_handoff_hashes_match_snapshot",
      "check_stub_edits_stay_within_anchors",
      "check_generated_symbols_are_immutable",
      "check_no_uncontracted_public_symbols",
      "check_temporal_invariants_forbid_system_clock"
    ],
    "diff_validator_mode": "ast_python_and_ts"
  },
  "task_plan": {
    "ordered_steps": [
      {
        "step_id": "STEP-001",
        "actor": "HB_PLAN",
        "action": "validate_contract_pack_against_json_schemas",
        "blocking": true
      },
      {
        "step_id": "STEP-002",
        "actor": "HB_PLAN",
        "action": "run_cross_linter_with_allowed_checker_ids",
        "blocking": true
      },
      {
        "step_id": "STEP-003",
        "actor": "HB_PLAN",
        "action": "generate_handoff_snapshot_and_hash_lock",
        "blocking": true
      },
      {
        "step_id": "STEP-004",
        "actor": "EXECUTOR",
        "action": "generate_required_stubs_and_clients",
        "blocking": true
      },
      {
        "step_id": "STEP-005",
        "actor": "EXECUTOR",
        "action": "apply_required_migrations",
        "blocking": true
      },
      {
        "step_id": "STEP-006",
        "actor": "EXECUTOR",
        "action": "implement_only_anchor_regions_for_allowed_operations",
        "blocking": true
      },
      {
        "step_id": "STEP-007",
        "actor": "HB_VERIFY",
        "action": "run_ast_diff_validation_python_and_ts",
        "blocking": true
      },
      {
        "step_id": "STEP-008",
        "actor": "HB_VERIFY",
        "action": "run_contract_invariant_projection_and_side_effect_checks",
        "blocking": true
      },
      {
        "step_id": "STEP-009",
        "actor": "TESTER",
        "action": "verify_module_against_same_snapshot_and_canonical_scenarios",
        "blocking": true
      }
    ]
  },
  "entry_gates": [
    {
      "gate_id": "EG-001",
      "name": "cross_linter_pass",
      "required": true
    },
    {
      "gate_id": "EG-002",
      "name": "snapshot_hash_match",
      "required": true
    },
    {
      "gate_id": "EG-003",
      "name": "codegen_completed",
      "required": true
    }
  ],
  "exit_gates": [
    {
      "gate_id": "XG-001",
      "name": "contract_tests_pass",
      "required": true
    },
    {
      "gate_id": "XG-002",
      "name": "invariant_tests_pass",
      "required": true
    },
    {
      "gate_id": "XG-003",
      "name": "projection_replay_safe",
      "required": true
    },
    {
      "gate_id": "XG-004",
      "name": "side_effect_replay_policy_respected",
      "required": true
    },
    {
      "gate_id": "XG-005",
      "name": "e2e_selectors_match_ui_contract",
      "required": true
    },
    {
      "gate_id": "XG-006",
      "name": "no_unbound_symbols_detected",
      "required": true
    }
  ],
  "prohibitions": [
    "do_not_use_chat_history_as_source_of_truth",
    "do_not_create_new_symbols_outside_traceability",
    "do_not_create_new_public_symbols_outside_operation_file_bindings",
    "do_not_create_new_files_outside_allowed_file_paths",
    "do_not_reinterpret_invariants_in_natural_language",
    "do_not_use_markdown_handoff_as_authority",
    "do_not_use_datetime_now_or_date_today_in_temporal_invariant_paths",
    "do_not_trigger_side_effects_during_projection_rebuild",
    "do_not_edit_outside_anchor_regions",
    "do_not_add_functionality_not_declared_in_allowed_operation_ids"
  ],
  "notes": [
    "Snapshot emitted exclusively by hb_plan.py.",
    "All hashes are placeholders in this draft and must be replaced programmatically.",
    "Frontend anchor validation requires AST-based TypeScript checker aligned with Python anchor grammar."
  ]
}
```

## 17_ATLETAS_PROJECTIONS.yaml (Materialização e Atomicidade)

```yaml
meta:
  document_id: PROJ-ATHLETES
projection_mode:
  source_of_truth: event_store
  read_models_are_derived: true
  side_effects_during_rebuild: forbidden
read_models:
  - read_model_id: athletes_read_model
    target_table: athletes
    target_file: backend/app/projections/athletes_projection.py
    event_handlers:
      - handler_id: PROJ-H-ATH-001
        event_type: AthleteRegistered
        event_version: 2
        handler_symbol: apply_athlete_registered_v2
        purity: required
        idempotency_mode: event_id_guard
upcast_pipeline:
  required: true
  order_of_execution: [validate_event, upcast_if_needed, dispatch_to_handler]
  purity_requirements:
    db_lookup_forbidden: true
    system_clock_forbidden: true
```

# 18_ATLETAS_SIDE_EFFECTS.yaml

Você está correto: projeção e side effect não podem morar no mesmo lugar.

* A regra precisa ser:
	•	projection handler: puro, determinístico, replay-safe
	•	side-effect handler: separado, com política explícita de replay, idempotência e retry

```yaml
Template canônico:

meta:
  document_id: SIDE-EFFECTS-ATHLETES
  module_id: ATHLETES
  module_version: 1.0.0
  status: DRAFT
  authority_level: EXECUTIONAL_SSOT
  replay_safety_policy: mandatory
  executor_freedom:
    inline_side_effect_inside_projection: forbidden
    undeclared_external_call: forbidden

file_map:
  canonical_files:
    side_effects_registry_file: backend/app/side_effects/athletes_side_effects.py
    notification_service_file: backend/app/integrations/notification_service.py
    federation_sync_service_file: backend/app/integrations/federation_sync_service.py

side_effect_policies:
  - side_effect_id: SE-ATH-001
    event_type: AthleteRegistered
    event_version: 1
    action: NOTIFY_COACH
    handler_symbol: send_athlete_registered_notification
    handler_file: backend/app/side_effects/athletes_side_effects.py
    integration_symbol: notification_service.send_welcome
    trigger_mode: async_after_commit
    idempotency_key: "evt:{event_id}"
    replay_policy: skip_on_replay
    duplicate_policy: ignore_if_same_idempotency_key
    error_policy: retry_with_exponential_backoff
    max_retries: 5
    dead_letter_policy: required

  - side_effect_id: SE-ATH-002
    event_type: AthleteStatusChanged
    event_version: 1
    action: UPDATE_EXTERNAL_FEDERATION_API
    handler_symbol: sync_athlete_status_to_federation
    handler_file: backend/app/side_effects/athletes_side_effects.py
    integration_symbol: federation_sync_service.sync
    trigger_mode: async_after_commit
    idempotency_key: "athlete:{athlete_id}:status:{new_status}"
    replay_policy: manual_only
    duplicate_policy: block_if_already_applied
    error_policy: retry_with_exponential_backoff
    max_retries: 8
    dead_letter_policy: required

rules:
  - rule_id: SE-RULE-001
    description: Projection handlers must be pure and replay-safe.
  - rule_id: SE-RULE-002
    description: Side effects must never execute during projection rebuild unless replay_policy explicitly allows it.
  - rule_id: SE-RULE-003
    description: Every external call must declare idempotency_key, replay_policy and error_policy.
```

Regra sistêmica

Se um evento reconstrói estado, ele não envia notificação.
Se um evento dispara efeito externo, isso acontece em pipeline separado e idempotente.

# AGENTE EXECUTOR

Mesmo com contratos, linter transversal, handoff estruturado e schemas determinísticos, ainda existe um espaço residual de alucinação se o Executor puder escolher estrutura, inventar cenários, acoplar side effects ao replay ou extrapolar escopo “para ajudar”.

1.	projeção não pode carregar side effect
  - senão replay vira duplicação de ação.
2.	file map sem ancoragem de stub ainda deixa liberdade estrutural
  - o Executor ainda escolhe assinatura, classe, decorator, local real do código.
3.	o Testador não pode inventar dados arbitrários
  - precisa existir um conjunto canônico de cenários válidos e inválidos do domínio.

Então a resposta correta não é “confiar no prompt”.
A resposta correta é:

O EXECUTOR DEVE SER RESTRITO POR:
1) handoff estruturado,
2) stubs ancorados gerados por script,
3) allowed write paths,
4) diff validator,
5) prompt de restrição fail-closed.

O prompt é apenas a camada final de contenção.
A contenção real vem da arquitetura.

Como garantir que o **Agente Executor** não ignore o 16_ATLETAS_AGENT_HANDOFF.json e tente “ser útil” adicionando funcionalidade extra?

* Garante-se por uma combinação de:
	•	prompt de restrição
	•	workspace cercado
	•	stubs ancorados
	•	validador de diff
	•	bloqueio por escopo

- **Executor** até pode tentar extrapolar, mas o sistema deve tornar isso **detectável e bloqueável.**

A regra de ouro para o HB Track:
* O EXECUTOR NUNCA CRIA ESTRUTURA.
* O hb_plan.py GERA A ESTRUTURA.
* O EXECUTOR SÓ PREENCHE CORPOS EM ZONAS AUTORIZADAS.
* QUALQUER EDIÇÃO FORA DESSAS ZONAS = VIOLAÇÃO CONTRATUAL.

Isso é o que realmente “algema” a IA.

# O que realmente algema o Executor: stubs ancorados

* O Executor não deve escrever:
	•	nome de função
	•	assinatura
	•	decorator
	•	classe
	•	arquivo
	•	import estrutural crítico

Tudo isso deve vir gerado por hb_plan.py.

Exemplo de stub ancorado Python

```python
# GENERATED FILE - DO NOT RENAME SYMBOLS
# HB_MODULE: ATHLETES
# HB_OPERATION: athletes__athlete__create
# HB_TRACE_BINDING: athlete_create
# HB_CONTRACT_HASH: <HASH>

from uuid import UUID
from backend.app.generated.athletes_contract_types import AthleteCreateRequest, AthleteResponse

def athlete_create(request: AthleteCreateRequest) -> AthleteResponse:
    # <HB-BODY-START:athletes__athlete__create>
    raise NotImplementedError("Executor must implement body only.")
    # <HB-BODY-END:athletes__athlete__create>
```
Regra de enforcement

O diff validator deve permitir mudança apenas entre:
	•	HB-BODY-START
	•	HB-BODY-END

Qualquer alteração fora disso:
	•	exit code 2
	•	bloqueio do handoff
	•	evidência de violação

Para TS/React

```typescript
// GENERATED FILE - DO NOT CHANGE STRUCTURE
// HB_SCREEN: athletes.create
// HB_SELECTOR_SET: UI-ATHLETES
// HB_CONTRACT_HASH: <HASH>

export function AthleteCreateScreen() {
  return (
    <div data-testid="athletes.create.screen">
      {/* <HB-UI-BODY-START:athletes.create> */}
      throw new Error("Executor must implement UI body only.");
      {/* <HB-UI-BODY-END:athletes.create> */}
    </div>
  );
}
```
Isso elimina a liberdade de “andar, sala e corredor”.

# Prompt de restrição do Executor: contrato de instrução

Agora a parte que você pediu explicitamente.

O prompt do Executor não pode ser “implemente isso”.
Ele precisa ser um contrato operacional fail-closed.

* Template — `20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md`

---

TARGET: EXECUTOR
MODE: FAIL_CLOSED
AUTHORITY: 16_ATLETAS_AGENT_HANDOFF.json

VOCÊ NÃO É AUTORIZADO A INTERPRETAR O PROJETO LIVREMENTE.
VOCÊ DEVE OPERAR APENAS DENTRO DO SNAPSHOT ESTRUTURADO RECEBIDO.

FONTE DE VERDADE OBRIGATÓRIA:
1. 16_ATLETAS_AGENT_HANDOFF.json
2. 00_ATLETAS_CROSS_LINTER_RULES.json
3. contratos referenciados pelo handoff
4. stubs gerados por hb_plan.py

PROIBIÇÕES ABSOLUTAS:
- não usar histórico do chat como fonte normativa
- não criar novas funcionalidades
- não criar novos endpoints
- não criar novos eventos
- não criar novos arquivos fora de allowed_file_paths
- não renomear símbolos gerados
- não alterar assinaturas geradas
- não mover arquivos gerados
- não introduzir side effects fora de 18_ATLETAS_SIDE_EFFECTS.yaml
- não criar cenários de teste fora de 19_ATLETAS_TEST_SCENARIOS.yaml
- não alterar nada fora das zonas HB-BODY-START / HB-BODY-END
- não “melhorar” o escopo
- não preencher lacunas com inferência

OBRIGAÇÕES:
- validar que os hashes do handoff correspondem ao snapshot atual
- implementar apenas operation_ids autorizados
- editar apenas arquivos permitidos
- preencher apenas corpos ancorados
- usar apenas reference_functions obrigatórias
- obedecer locking_policy, replay_policy e idempotency_key definidos em contrato
- falhar explicitamente se qualquer dependência contratual estiver ausente

CONDUTA EM CASO DE LACUNA:
Se qualquer contrato estiver ausente, ambíguo, inconsistente ou não materializado em stub,
VOCÊ DEVE PARAR.
VOCÊ DEVE RETORNAR:
BLOCKED_INPUT
EVIDENCE:
- arquivo ausente
- binding ausente
- hash divergente
- símbolo não gerado
- regra transversal violada

CRITÉRIO DE SUCESSO:
Seu trabalho será considerado válido somente se:
- nenhum símbolo novo tiver sido criado fora do handoff
- nenhuma edição estrutural ocorrer fora das âncoras
- os testes e validadores do snapshot passarem
- o diff validator aprovar as mudanças

SE VOCÊ TENTAR SER ÚTIL FORA DO ESCOPO, SUA EXECUÇÃO É INVÁLIDA.

---

### Como impedir o Executor de “ser útil”

Não basta instruir; tem que impossibilitar ou detectar.

Os cinco mecanismos obrigatórios são:

**A.** allowed_file_paths
- Só pode editar arquivos explicitamente autorizados no handoff.
**B.** anchored stubs
- Só pode editar dentro de blocos delimitados.
**C.** diff validator
- Bloqueia qualquer mudança fora das âncoras.
**D.** cross-linter + snapshot hash
- Se o handoff estiver velho, bloqueia antes de implementar.
**E.** no_new_symbol rule
- AST/diff checker detecta símbolo novo fora do contrato.

**EXECUTOR** PODE TENTAR EXTRAPOLAR, MAS O SISTEMA **NÃO PODE ACEITAR** A EXTRAPOLAÇÃO COMO **SAÍDA VÁLIDA**.

* Artefatos:
	•	18_ATLETAS_SIDE_EFFECTS.yaml
	•	19_ATLETAS_TEST_SCENARIOS.yaml
	•	stubs ancorados gerados por hb_plan.py
	•	diff validator
	•	prompt de restrição fail-closed

* Com os novos artefatos, o Hb Trackdeixa de ser “IA guiada por documentação” e passa a ser mais próximo de:

**IA COMO PREENCHEDOR DE LACUNAS CONTROLADAS, DENTRO DE UMA MÁQUINA DETERMINÍSTICA DE CONTRATOS.**

Ainda não é prova formal total no sentido forte de refinação matemática completa.
Mas já ataca o último comportamento típico de LLM em repositório:
	•	extrapolar escopo
	•	reorganizar estrutura
	•	misturar side effect com replay
	•	inventar cenário
	•	“ser útil” fora do contrato

# 19_ATLETAS_TEST_SCENARIOS.yaml

**Testador** não pode criar “atleta nascido em 1800 só porque é possível tecnicamente.

Ele precisa operar sobre:
	•	cenários canônicos válidos
	•	cenários canônicos inválidos
	•	cenários de fronteira aprovados pelo domínio

Template:

```yaml
meta:
  document_id: TEST-SCENARIOS-ATHLETES
  module_id: ATHLETES
  module_version: 1.0.0
  status: DRAFT
  authority_level: TEST_SSOT
  executor_freedom:
    invent_new_domain_scenarios_without_contract: forbidden

scenario_policy:
  scenario_source_of_truth: canonical_only
  arbitrary_fuzzing_allowed: false
  property_based_testing_allowed_only_for:
    - schema_robustness
    - parser_robustness
  domain_validation_must_use_canonical_scenarios: true

scenarios:
  - scenario_id: SCN-ATH-001
    name: atleta_cadete_masculino_valido
    purpose: valid_create_request
    inputs:
      competition_reference_year: 2026
      athlete:
        full_name: "João Silva"
        birth_date: "2012-03-10"
        category_code: "U14"
        federation_id: "FB-2026-001"
    expected_outcome:
      result: success
      invariant_ids:
        - INV-ATH-002

  - scenario_id: SCN-ATH-002
    name: atleta_categoria_incompativel_por_ano_referencia
    purpose: invalid_create_request
    inputs:
      competition_reference_year: 2026
      athlete:
        full_name: "Pedro Souza"
        birth_date: "2009-08-20"
        category_code: "U14"
    expected_outcome:
      result: invariant_violation
      invariant_id: INV-ATH-002
      error_code: ATHLETE_CATEGORY_INCOMPATIBLE

  - scenario_id: SCN-ATH-003
    name: federation_id_duplicado
    purpose: duplicate_identifier_rejection
    preconditions:
      existing_athlete:
        federation_id: "FB-2026-001"
    inputs:
      athlete:
        full_name: "Carlos Lima"
        birth_date: "2011-05-10"
        category_code: "U16"
        federation_id: "FB-2026-001"
    expected_outcome:
      result: conflict
      invariant_id: INV-ATH-001
      error_code: ATHLETE_FEDERATION_ID_CONFLICT

rules:
  - rule_id: TSC-RULE-001
    description: Tester must use only canonical scenario_ids for domain validation.
  - rule_id: TSC-RULE-002
    description: New domain scenario requires contract update before execution.
  - rule_id: TSC-RULE-003
    description: Fuzzing cannot redefine domain truth.
```

Agora o Testador não “descobre” domínio.
Ele verifica domínio contratado.

## REGRAS ESTRUTURAIS - hb_plan.py e hb_verify.py

	1.	cada regra passa a ter checker_id obrigatório;
	2.	assertion vira apenas documentação humana;
	3.	o hb_plan.py e o hb_verify.py só executam checker_id -> função Python;
	4.	o snapshot de hashes só pode ser emitido pelo hb_plan.py;
	5.	STUB-003 precisa distinguir símbolo contratado de símbolo privado auxiliar.

Abaixo estão os dois artefatos que faltavam.

# Bootstrap correto do snapshot e hashes

Sua crítica ao paradoxo do hash está correta. O fluxo certo é:

ARQUITETO edita contratos
↓
hb_plan.py valida schemas e cross-rules
↓
se PASS:
    hb_plan.py calcula hashes
    hb_plan.py gera 16_ATLETAS_AGENT_HANDOFF.json
    hb_plan.py sela snapshot
senão:
    nenhum handoff válido é emitido

Ou seja: o Arquiteto não gera hash.
O hb_plan.py é a única fonte de verdade para snapshot e integridade. Isso evita hash “manual” inconsistente.

# Zona de sombra dos símbolos: contratado vs privado

A sua crítica à STUB-003 também procede. A regra correta não é “nenhum símbolo novo”. É:
	•	nenhum novo símbolo público/contratado
	•	símbolos privados auxiliares são permitidos apenas dentro da zona ancorada e sob política explícita

A forma correta em `08_ATLETAS_TRACEABILITY.yaml` ou no handoff é algo assim:

```yaml
symbol_policy:
  public_symbols_declared_only: true
  private_helper_symbols:
    allowed: true
    naming_pattern: "^_"
    allowed_scope: "inside_anchor_region_only"
    export_forbidden: true
```

* Então o validador precisa tratar:
	•	função pública nova: falha
	•	classe pública nova: falha
	•	helper _xyz dentro da âncora: permitido
	•	helper _xyz fora da âncora: falha
	•	helper importado/exportado como API: falha

# Algoritmo do validador de âncoras em hb_verify.py

A base técnica certa é AST para Python, porque o módulo ast foi feito exatamente para processar a gramática sintática do Python de forma programática.   

Objetivo

Garantir que, em arquivos Python gerados:
	•	imports fora da âncora não mudaram
	•	decorators fora da âncora não mudaram
	•	assinatura de função não mudou
	•	nome de símbolo público não mudou
	•	apenas o corpo entre âncoras foi alterado

Estratégia

Não confiar só em diff textual.
Usar dois níveis:
	1.	Anchor Range Check
	•	localizar pares HB-BODY-START / HB-BODY-END
	•	qualquer mudança textual fora dessas faixas = suspeita
	2.	AST Structural Check
	•	parse do arquivo original e do modificado
	•	normalizar AST removendo os corpos permitidos nas regiões ancoradas
	•	comparar ASTs normalizadas

Pseudocódigo rigoroso

```python
from dataclasses import dataclass
import ast
from pathlib import Path

@dataclass
class AnchorRegion:
    symbol_id: str
    start_line: int
    end_line: int

def extract_anchor_regions(source: str) -> list[AnchorRegion]:
    # Localiza comentários HB-BODY-START / HB-BODY-END
    # Valida pareamento, ordem e unicidade
    ...

def parse_ast(source: str) -> ast.AST:
    return ast.parse(source)

def node_within_anchor(node: ast.AST, anchors: list[AnchorRegion]) -> bool:
    lineno = getattr(node, "lineno", None)
    end_lineno = getattr(node, "end_lineno", lineno)
    if lineno is None:
        return False
    for a in anchors:
        if lineno >= a.start_line and end_lineno <= a.end_line:
            return True
    return False

def normalize_module(tree: ast.Module, anchors: list[AnchorRegion]) -> ast.Module:
    """
    Produz uma versão comparável da AST em que:
    - corpos de funções ancoradas são substituídos por um placeholder estável
    - helpers privados permitidos só sobrevivem se estiverem dentro da âncora
    - símbolos públicos fora da âncora permanecem intocados para comparação
    """
    class Normalizer(ast.NodeTransformer):
        def visit_FunctionDef(self, node: ast.FunctionDef):
            # Se a função pública tem âncora, mantém assinatura e decorator,
            # substitui corpo por placeholder fixo.
            if is_public_symbol(node.name) and has_anchor_for_symbol(node.name, anchors):
                node.body = [ast.Pass()]
                return node

            # Helper privado fora da âncora não é permitido
            if is_private_symbol(node.name) and not node_within_anchor(node, anchors):
                raise ValidationError(f"Private helper outside anchor: {node.name}")

            return self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            return self.visit_FunctionDef(node)

        def visit_ClassDef(self, node: ast.ClassDef):
            # Classe pública nova fora do contrato = falha
            if is_uncontracted_public_class(node.name):
                raise ValidationError(f"Uncontracted public class: {node.name}")
            return self.generic_visit(node)

    normalized = Normalizer().visit(tree)
    ast.fix_missing_locations(normalized)
    return normalized

def compare_normalized_ast(original_src: str, modified_src: str) -> list[str]:
    original_anchors = extract_anchor_regions(original_src)
    modified_anchors = extract_anchor_regions(modified_src)

    # âncoras não podem mudar
    if original_anchors != modified_anchors:
        return ["Anchor layout changed"]

    original_tree = parse_ast(original_src)
    modified_tree = parse_ast(modified_src)

    norm_original = normalize_module(original_tree, original_anchors)
    norm_modified = normalize_module(modified_tree, modified_anchors)

    dump_a = ast.dump(norm_original, include_attributes=False)
    dump_b = ast.dump(norm_modified, include_attributes=False)

    if dump_a != dump_b:
        return ["Structural AST drift outside allowed anchor bodies"]

    return []

def validate_python_stub(original_path: Path, modified_path: Path) -> int:
    errors = compare_normalized_ast(
        original_path.read_text(encoding="utf-8"),
        modified_path.read_text(encoding="utf-8"),
    )
    if errors:
        emit_report(errors)
        return 2
    return 0
```

# Regras executáveis: tabela checker_id -> função

O motor do linter **não pode interpretar a frase**. Ele precisa fazer **dispatch explícito**.

```python
CHECKERS = {
    "check_openapi_operation_ids_are_traceable": check_openapi_operation_ids_are_traceable,
    "check_traceability_operations_exist_in_openapi": check_traceability_operations_exist_in_openapi,
    "check_db_nullability_matches_api_write_contract": check_db_nullability_matches_api_write_contract,
    "check_handoff_hashes_match_snapshot": check_handoff_hashes_match_snapshot,
    "check_projection_handlers_are_side_effect_free": check_projection_handlers_are_side_effect_free,
    "check_temporal_invariants_forbid_system_clock": check_temporal_invariants_forbid_system_clock,
    "check_stub_edits_stay_within_anchors": check_stub_edits_stay_within_anchors
}

Execução:

def run_rule(rule: dict, context: ValidationContext) -> RuleResult:
    checker_id = rule["checker_id"]
    fn = CHECKERS.get(checker_id)
    if fn is None:
        return RuleResult.fail(rule["rule_id"], f"Unknown checker_id: {checker_id}")
    return fn(rule, context)
```
Isso fecha a lacuna entre “texto” e “bit”.

6) Veredito objetivo

* O ponto que faltava era exatamente este:
	•	schema formal do meta-contrato
	•	despacho determinístico por checker_id
	•	snapshot emitido só pelo hb_plan.py
	•	AST validator para âncoras
	•	distinção formal entre símbolo contratado e helper privado

- Com isso, a arquitetura deixa de ser “regra escrita” e passa a ser regra executável.

# HB PLAN

Objetivo do hb_plan.py

Entrada:
	•	diretório do módulo, por exemplo docs/hbtrack/modulos/atletas/

Saída:
	•	_reports/hb_plan_result.json
	•	_reports/hb_plan_result.md
	•	docs/hbtrack/modulos/atletas/16_ATLETAS_AGENT_HANDOFF.json
	•	_reports/anchor_manifest.json

Exit codes:
	•	0 = PASS
	•	2 = FAIL_ACTIONABLE
	•	3 = ERROR_INFRA
	•	4 = BLOCKED_INPUT

**JUSTIFICATIVA**: 

## Estrutura de diretórios recomendada

scripts/
  hb_plan.py
  hb_verify.py
  hbtrack_lint/
    __init__.py
    context.py
    loader.py
    hashing.py
    reports.py
    schemas.py
    anchor_manifest.py
    handoff_builder.py
    checker_registry.py
    checkers/
      __init__.py
      documents.py
      cross.py
      db.py
      ui.py
      invariants.py
      handoff.py
      events.py
      side_effects.py
      time.py
      tests.py
      anchors.py
      restrictions.py

hb_plan.py — esqueleto principal

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from hbtrack_lint.context import ValidationContext
from hbtrack_lint.loader import load_contract_pack
from hbtrack_lint.schemas import validate_documents_against_schemas
from hbtrack_lint.checker_registry import run_allowed_rules
from hbtrack_lint.anchor_manifest import build_anchor_manifest
from hbtrack_lint.handoff_builder import build_handoff
from hbtrack_lint.hashing import sha256_file, sha256_jsonable
from hbtrack_lint.reports import write_plan_reports


EXIT_PASS = 0
EXIT_FAIL_ACTIONABLE = 2
EXIT_ERROR_INFRA = 3
EXIT_BLOCKED_INPUT = 4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HB Track deterministic planner")
    parser.add_argument(
        "module_root",
        type=Path,
        help="Path to module contract pack, e.g. docs/hbtrack/modulos/atletas"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root"
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("_reports"),
        help="Output directory for reports"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        module_root = args.module_root.resolve()
        repo_root = args.repo_root.resolve()
        reports_dir = (repo_root / args.reports_dir).resolve()
        reports_dir.mkdir(parents=True, exist_ok=True)

        if not module_root.exists():
            write_plan_reports(
                reports_dir=reports_dir,
                status="BLOCKED_INPUT",
                errors=[{"reason": f"Module root does not exist: {module_root}"}],
                warnings=[],
                results=[],
                handoff_path=None,
                anchor_manifest_path=None,
            )
            return EXIT_BLOCKED_INPUT

        contracts = load_contract_pack(module_root)

        schema_results = validate_documents_against_schemas(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
        )
        if schema_results.errors:
            write_plan_reports(
                reports_dir=reports_dir,
                status="FAIL_ACTIONABLE",
                errors=schema_results.errors,
                warnings=schema_results.warnings,
                results=schema_results.results,
                handoff_path=None,
                anchor_manifest_path=None,
            )
            return EXIT_FAIL_ACTIONABLE

        ctx = ValidationContext(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
            handoff=None,
            anchor_manifest=None,
            original_files_dir=None,
            working_files_dir=None,
        )

        lint_results = run_allowed_rules(ctx)

        failures = [r for r in lint_results if r.status == "FAIL"]
        errors = [r for r in lint_results if r.status == "ERROR"]

        if failures or errors:
            write_plan_reports(
                reports_dir=reports_dir,
                status="FAIL_ACTIONABLE" if failures else "ERROR_INFRA",
                errors=[r.__dict__ for r in failures + errors],
                warnings=[],
                results=[r.__dict__ for r in lint_results],
                handoff_path=None,
                anchor_manifest_path=None,
            )
            return EXIT_FAIL_ACTIONABLE if failures else EXIT_ERROR_INFRA

        anchor_manifest = build_anchor_manifest(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
        )

        anchor_manifest_path = reports_dir / "anchor_manifest.json"
        anchor_manifest_path.write_text(
            json.dumps(anchor_manifest, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        handoff = build_handoff(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
            anchor_manifest=anchor_manifest,
            reports_dir=reports_dir,
        )

        # hash do manifesto entra no handoff
        handoff.setdefault("integrity", {})
        handoff["integrity"]["anchor_manifest_sha256"] = sha256_file(anchor_manifest_path)

        # snapshot hash final calculado somente após materializar o handoff sem snapshot_hash
        provisional_handoff = json.loads(json.dumps(handoff))
        provisional_handoff["integrity"]["snapshot_hash"] = "0" * 64
        snapshot_hash = sha256_jsonable(provisional_handoff)
        handoff["integrity"]["snapshot_hash"] = snapshot_hash

        handoff_path = module_root / "16_ATLETAS_AGENT_HANDOFF.json"
        handoff_path.write_text(
            json.dumps(handoff, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        write_plan_reports(
            reports_dir=reports_dir,
            status="PASS",
            errors=[],
            warnings=[],
            results=[r.__dict__ for r in lint_results],
            handoff_path=handoff_path,
            anchor_manifest_path=anchor_manifest_path,
        )
        return EXIT_PASS

    except Exception as exc:
        write_plan_reports(
            reports_dir=args.reports_dir,
            status="ERROR_INFRA",
            errors=[{"reason": f"{type(exc).__name__}: {exc}"}],
            warnings=[],
            results=[],
            handoff_path=None,
            anchor_manifest_path=None,
        )
        return EXIT_ERROR_INFRA


if __name__ == "__main__":
    sys.exit(main())
```

⸻

load_contract_pack

Esse loader não pode “tentar adivinhar”. Ele carrega por nome canônico.
```python
from __future__ import annotations

import json
from pathlib import Path
import yaml


REQUIRED_DOCS = [
    "00_ATLETAS_CROSS_LINTER_RULES.json",
    "01_ATLETAS_OPENAPI.yaml",
    "08_ATLETAS_TRACEABILITY.yaml",
    "13_ATLETAS_DB_CONTRACT.yaml",
    "14_ATLETAS_UI_CONTRACT.yaml",
    "15_ATLETAS_INVARIANTS.yaml",
    "17_ATLETAS_PROJECTIONS.yaml",
    "18_ATLETAS_SIDE_EFFECTS.yaml",
    "19_ATLETAS_TEST_SCENARIOS.yaml",
    "20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md",
]

OPTIONAL_DOCS = [
    "05_ATLETAS_EVENTS.asyncapi.yaml",
]


def _load_file(path: Path):
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if path.suffix in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return path.read_text(encoding="utf-8")


def load_contract_pack(module_root: Path) -> dict[str, object]:
    contracts: dict[str, object] = {}

    for name in REQUIRED_DOCS + OPTIONAL_DOCS:
        path = module_root / name
        if path.exists():
            contracts[name] = _load_file(path)

    return contracts
```

⸻

validate_documents_against_schemas

Aqui mora o “meta-juiz”.
A regra é: cada artefato tipado deve ter schema próprio.

```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
from jsonschema import Draft202012Validator


@dataclass
class SchemaValidationResult:
    errors: list[dict] = field(default_factory=list)
    warnings: list[dict] = field(default_factory=list)
    results: list[dict] = field(default_factory=list)


SCHEMA_MAP = {
    "00_ATLETAS_CROSS_LINTER_RULES.json": "schemas/00_ATLETAS_CROSS_LINTER_RULES.schema.json",
    "16_ATLETAS_AGENT_HANDOFF.json": "schemas/16_AGENT_HANDOFF.schema.json",
    # restantes entram progressivamente
}


def validate_documents_against_schemas(repo_root: Path, module_root: Path, contracts: dict[str, object]) -> SchemaValidationResult:
    result = SchemaValidationResult()

    for doc_name, schema_rel in SCHEMA_MAP.items():
        if doc_name not in contracts:
            continue

        schema_path = repo_root / schema_rel
        if not schema_path.exists():
            result.errors.append({
                "document": doc_name,
                "reason": f"Missing schema: {schema_path}"
            })
            continue

        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)

        doc_errors = sorted(validator.iter_errors(contracts[doc_name]), key=lambda e: list(e.path))
        if doc_errors:
            for err in doc_errors:
                result.errors.append({
                    "document": doc_name,
                    "reason": err.message,
                    "path": list(err.path),
                })
        else:
            result.results.append({
                "document": doc_name,
                "status": "PASS_SCHEMA"
            })

    return result
```

⸻

run_allowed_rules

O hb_plan.py não deve executar tudo cegamente.
Ele executa os checker_id permitidos pelo meta-contrato e pelo módulo.


```python
from __future__ import annotations

from hbtrack_lint.checkers import register_all_checkers
from hbtrack_lint.engine import run_rule


def run_allowed_rules(ctx):
    register_all_checkers()

    cross_rules = ctx.contracts["00_ATLETAS_CROSS_LINTER_RULES.json"]
    allowed_checker_ids = set()

    # união das regras declaradas no meta-contrato
    for section in [
        "document_shape_rules",
        "cross_rules",
        "event_rules",
        "projection_rules",
        "side_effect_rules",
        "concurrency_rules",
        "ui_state_rules",
        "time_determinism_rules",
        "test_scenario_rules",
        "stub_anchor_rules",
        "handoff_rules",
        "restriction_prompt_rules",
        "diff_validation_rules",
    ]:
        for rule in cross_rules.get(section, []):
            allowed_checker_ids.add(rule["checker_id"])

    results = []
    for section in [
        "document_shape_rules",
        "cross_rules",
        "event_rules",
        "projection_rules",
        "side_effect_rules",
        "concurrency_rules",
        "ui_state_rules",
        "time_determinism_rules",
        "test_scenario_rules",
        "stub_anchor_rules",
        "handoff_rules",
        "restriction_prompt_rules",
        "diff_validation_rules",
    ]:
        for rule in cross_rules.get(section, []):
            if rule["checker_id"] not in allowed_checker_ids:
                continue
            results.append(run_rule(rule, ctx))

    return results
```

⸻

build_anchor_manifest

Esse é o artefato que “mapeia a mina”.

Regras que ele deve seguir
	•	cada arquivo gerado com âncoras entra no manifesto
	•	cada âncora tem symbol_id
	•	cada âncora tem public_symbol
	•	cada âncora tem anchor_hash
	•	o manifesto é referenciado por hash no handoff

```python
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_anchor_manifest(repo_root: Path, module_root: Path, contracts: dict[str, object]) -> dict:
    traceability = contracts["08_ATLETAS_TRACEABILITY.yaml"]
    handoff_files = []

    for op in traceability.get("operations", []):
        operation_id = op["operation_id"]
        binding = op["implementation_binding"]

        backend_handler = binding.get("backend_handler")
        if backend_handler:
            file_path = binding.get("backend_handler_file", "backend/app/services/athlete_service.py")
            start_marker = f"# <HB-BODY-START:{operation_id}>"
            end_marker = f"# <HB-BODY-END:{operation_id}>"
            handoff_files.append({
                "path": file_path,
                "language": "python",
                "anchors": [
                    {
                        "symbol_id": operation_id,
                        "public_symbol": backend_handler,
                        "anchor_type": "function_body",
                        "start_marker": start_marker,
                        "end_marker": end_marker,
                        "anchor_hash": _hash_text(start_marker + end_marker + backend_handler)
                    }
                ]
            })

    return {
        "module_id": traceability["meta"]["module_id"],
        "snapshot_hash": "0" * 64,
        "files": handoff_files
    }
```
Observação crítica

Na implementação real, o manifesto deve ser derivado de stubs gerados, não só dos contratos.
Ou seja: o ideal é gerar os stubs primeiro e depois extrair do arquivo físico.

⸻

build_handoff

Aqui o planner transforma o pack em ordem de execução.

```python
from __future__ import annotations

from pathlib import Path
from hbtrack_lint.hashing import sha256_file


def build_handoff(repo_root: Path, module_root: Path, contracts: dict[str, object], anchor_manifest: dict, reports_dir: Path) -> dict:
    traceability = contracts["08_ATLETAS_TRACEABILITY.yaml"]
    openapi = contracts["01_ATLETAS_OPENAPI.yaml"]
    cross = contracts["00_ATLETAS_CROSS_LINTER_RULES.json"]

    allowed_operation_ids = [op["operation_id"] for op in traceability.get("operations", [])]

    operation_file_bindings = []
    allowed_file_paths = set()

    for op in traceability.get("operations", []):
        binding = op["implementation_binding"]
        file_paths = []

        for key in [
            "backend_handler_file",
            "backend_service_file",
            "repository_file",
            "projection_file",
            "side_effect_file",
            "frontend_screen_file",
            "frontend_component_file",
            "e2e_spec_file",
        ]:
            value = binding.get(key)
            if value:
                file_paths.append(value)
                allowed_file_paths.add(value)

        operation_file_bindings.append({
            "operation_id": op["operation_id"],
            "file_paths": sorted(set(file_paths)),
            "public_symbols": [
                sym for sym in [
                    binding.get("backend_handler"),
                    binding.get("backend_service"),
                    binding.get("frontend_component"),
                ] if sym
            ]
        })

    artifacts = []
    for name in [
        "00_ATLETAS_CROSS_LINTER_RULES.json",
        "01_ATLETAS_OPENAPI.yaml",
        "08_ATLETAS_TRACEABILITY.yaml",
        "13_ATLETAS_DB_CONTRACT.yaml",
        "14_ATLETAS_UI_CONTRACT.yaml",
        "15_ATLETAS_INVARIANTS.yaml",
        "05_ATLETAS_EVENTS.asyncapi.yaml",
        "17_ATLETAS_PROJECTIONS.yaml",
        "18_ATLETAS_SIDE_EFFECTS.yaml",
        "19_ATLETAS_TEST_SCENARIOS.yaml",
        "20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md",
    ]:
        path = module_root / name
        if path.exists():
            artifacts.append({
                "path": str(path.relative_to(repo_root)),
                "role": _role_for_doc(name),
                "sha256": sha256_file(path)
            })

    return {
        "meta": {
            "handoff_id": "HANDOFF-ATHLETES-2026-03-07-001",
            "module_id": traceability["meta"]["module_id"],
            "module_version": traceability["meta"]["module_version"],
            "status": "READY_FOR_EXECUTION",
            "authority_level": "EXECUTION_GATE",
            "issued_by": "HB_PLAN",
            "issued_at": "2026-03-07T13:00:00-03:00",
            "conversation_independent": True
        },
        "integrity": {
            "snapshot_mode": "hash_locked",
            "artifacts": artifacts,
            "stale_snapshot_policy": "block_execution"
        },
        "execution_scope": {
            "allowed_operation_ids": allowed_operation_ids,
            "allowed_file_paths": sorted(allowed_file_paths),
            "forbidden_write_paths": [],
            "operation_file_bindings": operation_file_bindings,
            "public_symbol_policy": {
                "public_symbols_declared_only": True,
                "private_helper_symbols": {
                    "allowed": True,
                    "naming_pattern": "^_",
                    "allowed_scope": "inside_anchor_region_only",
                    "export_forbidden": True
                }
            }
        },
        "codegen_requirements": {
            "openapi_codegen_required": True,
            "frontend_client_generation_required": True,
            "backend_stub_generation_required": True,
            "manual_symbol_creation_allowed": False,
            "required_generated_artifacts": [
                "frontend/src/lib/generated/athletes-client.ts",
                "backend/app/generated/athletes_contract_types.py",
                "backend/app/generated/athletes_stub_bindings.py"
            ]
        },
        "validator_requirements": {
            "allowed_checker_ids": _collect_checker_ids(cross),
            "required_checker_ids": [
                "check_handoff_hashes_match_snapshot",
                "check_stub_edits_stay_within_anchors",
                "check_generated_symbols_are_immutable",
                "check_no_uncontracted_public_symbols"
            ],
            "diff_validator_mode": "ast_python_and_ts"
        },
        "task_plan": {
            "ordered_steps": [
                {"step_id": "STEP-001", "actor": "HB_PLAN", "action": "validate_contract_pack_against_json_schemas", "blocking": True},
                {"step_id": "STEP-002", "actor": "HB_PLAN", "action": "run_cross_linter_with_allowed_checker_ids", "blocking": True},
                {"step_id": "STEP-003", "actor": "HB_PLAN", "action": "generate_handoff_snapshot_and_hash_lock", "blocking": True},
                {"step_id": "STEP-004", "actor": "EXECUTOR", "action": "generate_required_stubs_and_clients", "blocking": True}
            ]
        },
        "entry_gates": [
            {"gate_id": "EG-001", "name": "cross_linter_pass", "required": True}
        ],
        "exit_gates": [
            {"gate_id": "XG-001", "name": "contract_tests_pass", "required": True}
        ],
        "prohibitions": [
            "do_not_use_chat_history_as_source_of_truth",
            "do_not_create_new_symbols_outside_traceability",
            "do_not_edit_outside_anchor_regions"
        ]
    }
```

⸻

Como o hb_plan.py fecha o bootstrap

A sequência correta é:

1. carregar contratos
2. validar contratos contra schemas
3. executar checkers
4. gerar stubs
5. extrair manifesto de âncoras dos stubs
6. calcular hashes
7. gerar handoff
8. selar snapshot

Ponto importante

No esboço acima eu mantive build_anchor_manifest ainda contratual para clareza.
Na versão forte, o passo 4 e 5 precisam ser:

4. generate_stubs_from_contracts()
5. build_anchor_manifest_from_generated_files()

Porque o manifesto tem que refletir os arquivos reais.

⸻

O que falta para esse hb_plan.py virar produção
	1.	schema para cada documento do pack
	2.	gerador real de stubs Python e TSX
	3.	extração real de âncoras a partir dos stubs físicos
	4.	registry completo de checkers
	5.	escrita de report markdown/json consistente com exit code
	6.	integração com hb_verify.py

# HB VERIFY - CHECKERS 

Checkers do checkers restantes do hb_verify.py.

**check_projection_atomic_shell_integrity**

Objetivo

- Garantir que, no handler de projeção gerado, continuem existindo:
	•	with transaction_scope(projection_context) as tx
	•	projection_event_already_applied(..., tx=tx)
	•	mark_projection_event_applied(..., tx=tx)

- Impede que o Executor:
	•	apague with transaction_scope(...)
	•	apague projection_event_already_applied(...)
	•	apague mark_projection_event_applied(...)
	•	remova o tx da propagação

Ou seja: protege atomicidade + idempotência.

Estratégia:
- Para cada handler_symbol declarado em 17_ATLETAS_PROJECTIONS.yaml:
	•	localizar a FunctionDef correspondente
	•	verificar se há um With com transaction_scope(projection_context)
	•	verificar se dentro desse With existe:
	•	um if projection_event_already_applied(...): return
	•	a região ancorada
	•	uma chamada a mark_projection_event_applied(..., tx=tx) após a âncora
	•	reprovar se o With foi removido, se a chamada ao ledger foi removida, ou se o tx deixou de ser propagado

Implementação

```python
import ast


def _extract_call_name(func: ast.AST) -> tuple[str | None, str | None]:
    if isinstance(func, ast.Name):
        return func.id, None
    if isinstance(func, ast.Attribute):
        if isinstance(func.value, ast.Name):
            return func.value.id, func.attr
        return None, func.attr
    return None, None


def _keyword_uses_name(node: ast.Call, keyword_name: str, var_name: str) -> bool:
    for kw in node.keywords:
        if kw.arg == keyword_name and isinstance(kw.value, ast.Name) and kw.value.id == var_name:
            return True
    return False


class ProjectionAtomicShellVisitor(ast.NodeVisitor):
    def __init__(self, target_function: str):
        self.target_function = target_function
        self.function_found = False
        self.with_transaction_scope = False
        self.idempotency_guard_found = False
        self.ledger_mark_found = False
        self.tx_aliases: set[str] = set()
        self.violations: list[dict] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name != self.target_function:
            return

        self.function_found = True

        for stmt in node.body:
            if isinstance(stmt, ast.With):
                for item in stmt.items:
                    if isinstance(item.context_expr, ast.Call):
                        name, attr = _extract_call_name(item.context_expr.func)
                        if name == "transaction_scope" and attr is None:
                            self.with_transaction_scope = True
                            if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                                self.tx_aliases.add(item.optional_vars.id)
                            else:
                                self.violations.append({
                                    "kind": "missing_tx_alias",
                                    "lineno": stmt.lineno,
                                })
                            self._inspect_transaction_block(stmt)

        if not self.with_transaction_scope:
            self.violations.append({
                "kind": "missing_transaction_scope",
                "function": node.name,
                "lineno": node.lineno,
            })

    def _inspect_transaction_block(self, with_node: ast.With) -> None:
        for stmt in with_node.body:
            # idempotency guard
            if isinstance(stmt, ast.If) and isinstance(stmt.test, ast.Call):
                name, attr = _extract_call_name(stmt.test.func)
                if name == "projection_event_already_applied" and attr is None:
                    tx_ok = any(_keyword_uses_name(stmt.test, "tx", tx_name) for tx_name in self.tx_aliases)
                    if tx_ok:
                        self.idempotency_guard_found = True
                    else:
                        self.violations.append({
                            "kind": "idempotency_guard_missing_tx",
                            "lineno": stmt.lineno,
                        })

            # ledger mark
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                name, attr = _extract_call_name(stmt.value.func)
                if name == "mark_projection_event_applied" and attr is None:
                    tx_ok = any(_keyword_uses_name(stmt.value, "tx", tx_name) for tx_name in self.tx_aliases)
                    if tx_ok:
                        self.ledger_mark_found = True
                    else:
                        self.violations.append({
                            "kind": "ledger_mark_missing_tx",
                            "lineno": stmt.lineno,
                        })

    def finalize(self):
        if self.function_found:
            if not self.idempotency_guard_found:
                self.violations.append({"kind": "missing_idempotency_guard"})
            if not self.ledger_mark_found:
                self.violations.append({"kind": "missing_ledger_mark"})

Checker

@register_checker("check_projection_atomic_shell_integrity")
def check_projection_atomic_shell_integrity(rule: dict, ctx: ValidationContext) -> RuleResult:
    projections = ctx.contracts["17_ATLETAS_PROJECTIONS.yaml"]
    violations = []

    for read_model in projections.get("read_models", []):
        file_path = ctx.repo_root / read_model["target_file"]
        if not file_path.exists():
            violations.append({
                "file": str(file_path),
                "reason": "projection_file_missing",
            })
            continue

        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))

        for handler in read_model.get("event_handlers", []):
            visitor = ProjectionAtomicShellVisitor(handler["handler_symbol"])
            visitor.visit(tree)
            visitor.finalize()

            if not visitor.function_found:
                violations.append({
                    "file": str(file_path),
                    "handler_symbol": handler["handler_symbol"],
                    "reason": "handler_not_found",
                })
                continue

            for v in visitor.violations:
                v["file"] = str(file_path)
                v["handler_symbol"] = handler["handler_symbol"]
                violations.append(v)

    if violations:
        return RuleResult.fail(
            rule["rule_id"],
            rule["checker_id"],
            "Projection atomic shell integrity violation detected.",
            violations=violations,
        )

    return RuleResult.pass_(
        rule["rule_id"],
        rule["checker_id"],
        "Projection atomic shell integrity preserved."
    )
```

**check_side_effect_result_usage**

- Objetivo
* Garantir que o side effect gerado continue respeitando o contrato:
	•	a função retorna SideEffectResult | None
	•	o wrapper ainda faz if result is not None: mark_side_effect_delivery(...)
	•	o Executor não trocou o retorno por dict, str, bool, etc.
	•	o retorno relevante da âncora é representado por variável result

- Impede que o Executor:
	•	transforme o wrapper em função “solta”
	•	retorne dict
	•	retorne string/boolean
	•	elimine a gravação do resultado na casca
	•	elimine o return result

Ou seja: protege auditabilidade + pureza da borda.

**Limitação honesta**

A AST do Python não sabe inferir o tipo real de runtime sem análise de tipos externa. Então o checker V1 deve validar estruturalmente:
	1.	a assinatura de retorno contém SideEffectResult ou SideEffectResult | None;
	2.	existe uma variável result;
	3.	existe return result;
	4.	existe mark_side_effect_delivery(..., result=result) condicionado a result is not None;
	5.	não existe return { ... }, return "ok", etc. fora da casca prevista.

Isso já elimina a sabotagem mais comum.

Visitor

```python
class SideEffectResultUsageVisitor(ast.NodeVisitor):
    def __init__(self, target_function: str):
        self.target_function = target_function
        self.function_found = False
        self.return_annotation_ok = False
        self.result_return_found = False
        self.result_guard_found = False
        self.delivery_log_call_found = False
        self.bad_returns: list[dict] = []
        self.violations: list[dict] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name != self.target_function:
            return

        self.function_found = True
        self.return_annotation_ok = self._check_return_annotation(node.returns)

        for stmt in node.body:
            # if result is not None: mark_side_effect_delivery(..., result=result)
            if isinstance(stmt, ast.If):
                if self._is_result_not_none_check(stmt.test):
                    self.result_guard_found = True
                    for inner in stmt.body:
                        if isinstance(inner, ast.Expr) and isinstance(inner.value, ast.Call):
                            name, attr = _extract_call_name(inner.value.func)
                            if name == "mark_side_effect_delivery" and attr is None:
                                if _keyword_uses_name(inner.value, "result", "result"):
                                    self.delivery_log_call_found = True

            # return result / return None
            if isinstance(stmt, ast.Return):
                if isinstance(stmt.value, ast.Name) and stmt.value.id == "result":
                    self.result_return_found = True
                elif isinstance(stmt.value, ast.Constant) and stmt.value.value is None:
                    pass
                else:
                    self.bad_returns.append({
                        "kind": "unexpected_top_level_return",
                        "lineno": stmt.lineno,
                        "ast": ast.dump(stmt.value, include_attributes=False) if stmt.value else None,
                    })

        if not self.return_annotation_ok:
            self.violations.append({"kind": "invalid_return_annotation"})
        if not self.result_guard_found:
            self.violations.append({"kind": "missing_result_guard"})
        if not self.delivery_log_call_found:
            self.violations.append({"kind": "missing_delivery_log_call"})
        if not self.result_return_found:
            self.violations.append({"kind": "missing_return_result"})
        self.violations.extend(self.bad_returns)

    @staticmethod
    def _is_result_not_none_check(test: ast.AST) -> bool:
        # result is not None
        return (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name)
            and test.left.id == "result"
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.IsNot)
            and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value is None
        )

    @staticmethod
    def _check_return_annotation(annotation: ast.AST | None) -> bool:
        if annotation is None:
            return False
        dumped = ast.dump(annotation, include_attributes=False)
        return "SideEffectResult" in dumped

Checker

@register_checker("check_side_effect_result_usage")
def check_side_effect_result_usage(rule: dict, ctx: ValidationContext) -> RuleResult:
    contract = ctx.contracts["18_ATLETAS_SIDE_EFFECTS.yaml"]
    violations = []

    for consumer in contract.get("consumers", []):
        file_path = ctx.repo_root / consumer["handler_file"]
        if not file_path.exists():
            violations.append({
                "consumer_id": consumer["consumer_id"],
                "reason": "handler_file_missing",
                "file": str(file_path),
            })
            continue

        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))

        visitor = SideEffectResultUsageVisitor(consumer["handler_symbol"])
        visitor.visit(tree)

        if not visitor.function_found:
            violations.append({
                "consumer_id": consumer["consumer_id"],
                "reason": "handler_not_found",
                "handler_symbol": consumer["handler_symbol"],
                "file": str(file_path),
            })
            continue

        for v in visitor.violations:
            v["consumer_id"] = consumer["consumer_id"]
            v["handler_symbol"] = consumer["handler_symbol"]
            v["file"] = str(file_path)
            violations.append(v)

    if violations:
        return RuleResult.fail(
            rule["rule_id"],
            rule["checker_id"],
            "Side-effect result contract violation detected.",
            violations=violations,
        )

    return RuleResult.pass_(
        rule["rule_id"],
        rule["checker_id"],
        "Side-effect handlers preserve SideEffectResult contract."
    )
```

* Limitação honesta
O checker de SideEffectResult em AST garante estrutura, não tipo semântico completo de runtime.

- Para chegar ainda mais longe, a V2 pode usar:
	•	mypy/pyright sobre os stubs gerados
	•	Protocols das integrações
	•	retorno tipado obrigatório com análise estática complementar

Mas a V1 acima já fecha o que mais importa para o HB Track agora: o Executor não consegue “desmontar” o wrapper sem ser detectado.

Regra sistêmica

Se um evento reconstrói estado, ele não envia notificação.
Se um evento dispara efeito externo, isso acontece em pipeline separado e idempotente.

# AGENTE EXECUTOR

Mesmo com contratos, linter transversal, handoff estruturado e schemas determinísticos, ainda existe um espaço residual de alucinação se o Executor puder escolher estrutura, inventar cenários, acoplar side effects ao replay ou extrapolar escopo “para ajudar”.

1.	projeção não pode carregar side effect
  - senão replay vira duplicação de ação.
2.	file map sem ancoragem de stub ainda deixa liberdade estrutural
  - o Executor ainda escolhe assinatura, classe, decorator, local real do código.
3.	o Testador não pode inventar dados arbitrários
  - precisa existir um conjunto canônico de cenários válidos e inválidos do domínio.

Então a resposta correta não é “confiar no prompt”.
A resposta correta é:

O EXECUTOR DEVE SER RESTRITO POR:
1) handoff estruturado,
2) stubs ancorados gerados por script,
3) allowed write paths,
4) diff validator,
5) prompt de restrição fail-closed.

O prompt é apenas a camada final de contenção.
A contenção real vem da arquitetura.

Como garantir que o **Agente Executor** não ignore o 16_ATLETAS_AGENT_HANDOFF.json e tente “ser útil” adicionando funcionalidade extra?

* Garante-se por uma combinação de:
	•	prompt de restrição
	•	workspace cercado
	•	stubs ancorados
	•	validador de diff
	•	bloqueio por escopo

- **Executor** até pode tentar extrapolar, mas o sistema deve tornar isso **detectável e bloqueável.**

A regra de ouro para o HB Track:
* O EXECUTOR NUNCA CRIA ESTRUTURA.
* O hb_plan.py GERA A ESTRUTURA.
* O EXECUTOR SÓ PREENCHE CORPOS EM ZONAS AUTORIZADAS.
* QUALQUER EDIÇÃO FORA DESSAS ZONAS = VIOLAÇÃO CONTRATUAL.

Isso é o que realmente “algema” a IA.

# O que realmente algema o Executor: stubs ancorados

* O Executor não deve escrever:
	•	nome de função
	•	assinatura
	•	decorator
	•	classe
	•	arquivo
	•	import estrutural crítico

Tudo isso deve vir gerado por hb_plan.py.

Exemplo de stub ancorado Python

```python
# GENERATED FILE - DO NOT RENAME SYMBOLS
# HB_MODULE: ATHLETES
# HB_OPERATION: athletes__athlete__create
# HB_TRACE_BINDING: athlete_create
# HB_CONTRACT_HASH: <HASH>

from uuid import UUID
from backend.app.generated.athletes_contract_types import AthleteCreateRequest, AthleteResponse

def athlete_create(request: AthleteCreateRequest) -> AthleteResponse:
    # <HB-BODY-START:athletes__athlete__create>
    raise NotImplementedError("Executor must implement body only.")
    # <HB-BODY-END:athletes__athlete__create>
```
Regra de enforcement

O diff validator deve permitir mudança apenas entre:
	•	HB-BODY-START
	•	HB-BODY-END

Qualquer alteração fora disso:
	•	exit code 2
	•	bloqueio do handoff
	•	evidência de violação

Para TS/React

```typescript
// GENERATED FILE - DO NOT CHANGE STRUCTURE
// HB_SCREEN: athletes.create
// HB_SELECTOR_SET: UI-ATHLETES
// HB_CONTRACT_HASH: <HASH>

export function AthleteCreateScreen() {
  return (
    <div data-testid="athletes.create.screen">
      {/* <HB-UI-BODY-START:athletes.create> */}
      throw new Error("Executor must implement UI body only.");
      {/* <HB-UI-BODY-END:athletes.create> */}
    </div>
  );
}
```
Isso elimina a liberdade de “andar, sala e corredor”.

# Prompt de restrição do Executor: contrato de instrução

Agora a parte que você pediu explicitamente.

O prompt do Executor não pode ser “implemente isso”.
Ele precisa ser um contrato operacional fail-closed.

* Template — `20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md`

---

TARGET: EXECUTOR
MODE: FAIL_CLOSED
AUTHORITY: 16_ATLETAS_AGENT_HANDOFF.json

VOCÊ NÃO É AUTORIZADO A INTERPRETAR O PROJETO LIVREMENTE.
VOCÊ DEVE OPERAR APENAS DENTRO DO SNAPSHOT ESTRUTURADO RECEBIDO.

FONTE DE VERDADE OBRIGATÓRIA:
1. 16_ATLETAS_AGENT_HANDOFF.json
2. 00_ATLETAS_CROSS_LINTER_RULES.json
3. contratos referenciados pelo handoff
4. stubs gerados por hb_plan.py

PROIBIÇÕES ABSOLUTAS:
- não usar histórico do chat como fonte normativa
- não criar novas funcionalidades
- não criar novos endpoints
- não criar novos eventos
- não criar novos arquivos fora de allowed_file_paths
- não renomear símbolos gerados
- não alterar assinaturas geradas
- não mover arquivos gerados
- não introduzir side effects fora de 18_ATLETAS_SIDE_EFFECTS.yaml
- não criar cenários de teste fora de 19_ATLETAS_TEST_SCENARIOS.yaml
- não alterar nada fora das zonas HB-BODY-START / HB-BODY-END
- não “melhorar” o escopo
- não preencher lacunas com inferência

OBRIGAÇÕES:
- validar que os hashes do handoff correspondem ao snapshot atual
- implementar apenas operation_ids autorizados
- editar apenas arquivos permitidos
- preencher apenas corpos ancorados
- usar apenas reference_functions obrigatórias
- obedecer locking_policy, replay_policy e idempotency_key definidos em contrato
- falhar explicitamente se qualquer dependência contratual estiver ausente

CONDUTA EM CASO DE LACUNA:
Se qualquer contrato estiver ausente, ambíguo, inconsistente ou não materializado em stub,
VOCÊ DEVE PARAR.
VOCÊ DEVE RETORNAR:
BLOCKED_INPUT
EVIDENCE:
- arquivo ausente
- binding ausente
- hash divergente
- símbolo não gerado
- regra transversal violada

CRITÉRIO DE SUCESSO:
Seu trabalho será considerado válido somente se:
- nenhum símbolo novo tiver sido criado fora do handoff
- nenhuma edição estrutural ocorrer fora das âncoras
- os testes e validadores do snapshot passarem
- o diff validator aprovar as mudanças

SE VOCÊ TENTAR SER ÚTIL FORA DO ESCOPO, SUA EXECUÇÃO É INVÁLIDA.

---

### Como impedir o Executor de “ser útil”

Não basta instruir; tem que impossibilitar ou detectar.

Os cinco mecanismos obrigatórios são:

**A.** allowed_file_paths
- Só pode editar arquivos explicitamente autorizados no handoff.
**B.** anchored stubs
- Só pode editar dentro de blocos delimitados.
**C.** diff validator
- Bloqueia qualquer mudança fora das âncoras.
**D.** cross-linter + snapshot hash
- Se o handoff estiver velho, bloqueia antes de implementar.
**E.** no_new_symbol rule
- AST/diff checker detecta símbolo novo fora do contrato.

**EXECUTOR** PODE TENTAR EXTRAPOLAR, MAS O SISTEMA **NÃO PODE ACEITAR** A EXTRAPOLAÇÃO COMO **SAÍDA VÁLIDA**.

* Artefatos:
	•	18_ATLETAS_SIDE_EFFECTS.yaml
	•	19_ATLETAS_TEST_SCENARIOS.yaml
	•	stubs ancorados gerados por hb_plan.py
	•	diff validator
	•	prompt de restrição fail-closed

* Com os novos artefatos, o Hb Trackdeixa de ser “IA guiada por documentação” e passa a ser mais próximo de:

**IA COMO PREENCHEDOR DE LACUNAS CONTROLADAS, DENTRO DE UMA MÁQUINA DETERMINÍSTICA DE CONTRATOS.**

Ainda não é prova formal total no sentido forte de refinação matemática completa.
Mas já ataca o último comportamento típico de LLM em repositório:
	•	extrapolar escopo
	•	reorganizar estrutura
	•	misturar side effect com replay
	•	inventar cenário
	•	“ser útil” fora do contrato

Ajustes estruturais que eu considero obrigatórios

Para esse schema ficar coerente com o que aprovamos, eu adicionaria no 

16_ATLETAS_AGENT_HANDOFF.json real estes blocos mínimos:
	•	operation_file_bindings
	•	public_symbol_policy
	•	validator_requirements.allowed_checker_ids
	•	integrity.snapshot_hash

Sem isso, o handoff fica válido estruturalmente, mas ainda frouxo operacionalmente.

Como o Executor deve satisfazer allowed_checker_ids

No handoff, o bloco correto seria algo como:

```json
"validator_requirements": {
  "allowed_checker_ids": [
    "check_openapi_operation_ids_are_traceable",
    "check_traceability_operations_exist_in_openapi",
    "check_handoff_hashes_match_snapshot",
    "check_stub_edits_stay_within_anchors",
    "check_temporal_invariants_forbid_system_clock"
  ],
  "required_checker_ids": [
    "check_handoff_hashes_match_snapshot",
    "check_stub_edits_stay_within_anchors"
  ],
  "diff_validator_mode": "ast_python_and_ts"
}