# CONTRACT_SYSTEM_RULES.md

## 1. Purpose
This document defines the operational rules for creating, validating, evolving, and consuming contracts in HB Track.

It is the binding operational manual for contract-driven development.

---

## 2. Scope
These rules govern:
- contract creation
- contract maintenance
- contract validation
- contract consumption by AI agents
- contract-derived artifacts
- definition of readiness for implementation

---

## 3. Sovereign Normative Artifacts

The following are normative and sovereign.

### 3.1 Contract-system governance
- `CONTRACT_SYSTEM_LAYOUT.md`
- `CONTRACT_SYSTEM_RULES.md`

### 3.2 Global governance docs
- `README.md`
- `SYSTEM_SCOPE.md`
- `ARCHITECTURE.md`
- `C4_CONTEXT.md`
- `C4_CONTAINERS.md`
- `MODULE_MAP.md`
- `CHANGE_POLICY.md`
- `API_CONVENTIONS.md`
- `DATA_CONVENTIONS.md`
- `ERROR_MODEL.md`
- `GLOBAL_INVARIANTS.md`
- `DOMAIN_GLOSSARY.md`
- `HANDBALL_RULES_DOMAIN.md`
- `SECURITY_RULES.md`
- `UI_FOUNDATIONS.md`
- `DESIGN_SYSTEM.md`
- `CI_CONTRACT_GATES.md`
- `TEST_STRATEGY.md`

### 3.3 Technical contracts
- `contracts/openapi/openapi.yaml`
- `contracts/openapi/paths/*.yaml`
- `contracts/schemas/**/*.schema.json`
- `contracts/workflows/**/*.arazzo.yaml`
- `contracts/asyncapi/**/*.yaml`

### 3.4 Module minimum docs
- `modulos/<mod>/README.md`
- `MODULE_SCOPE_<MOD>.md`
- `DOMAIN_RULES_<MOD>.md`
- `INVARIANTS_<MOD>.md`
- `TEST_MATRIX_<MOD>.md`

### 3.5 Module docs when applicable
- `STATE_MODEL_<MOD>.md`
- `PERMISSIONS_<MOD>.md`
- `ERRORS_<MOD>.md`
- `UI_CONTRACT_<MOD>.md`
- `SCREEN_MAP_<MOD>.md`

### 3.6 ADRs and explicit deviations
- `decisions/ADR-*.md` when the system intentionally deviates from a prior normative rule or from official handball-domain behavior already translated into product rules

Rule:
Everything outside the lists above is non-sovereign by default unless explicitly promoted by governance.

---

## 4. Derived / Scaffold Artifacts

The following are derived and never override normative artifacts:
- implementation code (`.py`, `.ts`, `.tsx`, etc.)
- generated clients
- generated UI types
- generated bundles
- generated HTML documentation
- Storybook generated artifacts
- mocks
- payload examples
- drafts
- template boilerplates

Rules:
- generated artifacts are never normative
- generated artifacts must not be manually edited when regeneration exists
- generated artifacts must live under `generated/`
- generated artifacts must be regenerable from sovereign sources
- drift between generated artifact and normative source must fail the pipeline

---

## 5. Precedence in Case of Conflict

Order of precedence:
1. `CONTRACT_SYSTEM_LAYOUT.md`
2. `CONTRACT_SYSTEM_RULES.md`
3. valid technical contracts:
   - OpenAPI
   - JSON Schema
   - Arazzo
   - AsyncAPI
4. `HANDBALL_RULES_DOMAIN.md` when sport-derived rule applies
5. `API_CONVENTIONS.md`, `DATA_CONVENTIONS.md`, `ERROR_MODEL.md`, `SECURITY_RULES.md`
6. `DOMAIN_RULES_<MOD>.md`
7. `INVARIANTS_<MOD>.md`
8. `STATE_MODEL_<MOD>.md`
9. `PERMISSIONS_<MOD>.md`
10. `UI_CONTRACT_<MOD>.md`
11. implementation
12. generated artifacts

Same-level conflict:
- agent must emit `BLOCKED_CONTRACT_CONFLICT`

Cross-level conflict:
- higher level always wins

---

## 6. Agent Boot Protocol

### 6.1 Mandatory boot order
1. `CONTRACT_SYSTEM_LAYOUT.md`
2. `CONTRACT_SYSTEM_RULES.md`
3. `GLOBAL_TEMPLATES.md`
4. `SYSTEM_SCOPE.md`
5. `API_CONVENTIONS.md`
6. `DATA_CONVENTIONS.md`
7. `CHANGE_POLICY.md`
8. `HANDBALL_RULES_DOMAIN.md`
9. `DOMAIN_GLOSSARY.md`
10. `MODULE_MAP.md`
11. `ARCHITECTURE.md`
12. relevant contract artifacts
13. relevant module docs

### 6.2 Boot mode
Agent must use:
- minimum mandatory boot
- conditional loading on demand
- block instead of infer when a critical artifact is missing

### 6.3 Blocking condition on boot
If the agent cannot load the required boot sequence for the current task, it must declare itself blocked using a valid blocking code instead of continuing by inference.

---

## 7. Documentation Architecture Rule (Diátaxis)
HB Track documentation must distinguish at least these functions:
- tutorial
- how-to
- reference
- explanation

Rules:
- contracts and technical specs are reference artifacts
- operational rules are reference artifacts
- ADRs and architectural rationale are explanation artifacts
- templates are scaffolds, not reference sources of truth
- no artifact should mix reference and explanation if that harms deterministic use by the agent

---

## 8. Strict Mode: Forbidden Inference

The AI agent is forbidden from inventing, without explicit contract/document:
- modules
- endpoints / paths
- stable fields
- stable enums
- events
- workflows
- state transitions
- permission models
- domain-specific errors
- UI behavior
- handball rules
- external integrations
- async operations

Missing artifact => block.

---

## 9. Blocking Codes

Allowed blocking outputs:
- `BLOCKED_MISSING_MODULE`
- `BLOCKED_MISSING_OPENAPI_PATH`
- `BLOCKED_MISSING_SCHEMA`
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_INVARIANT`
- `BLOCKED_MISSING_STATE_MODEL`
- `BLOCKED_MISSING_PERMISSION_MODEL`
- `BLOCKED_MISSING_UI_CONTRACT`
- `BLOCKED_MISSING_HANDBALL_REFERENCE`
- `BLOCKED_MISSING_TEST_MATRIX`
- `BLOCKED_CONTRACT_CONFLICT`

No free-form speculative workaround is allowed.

---

## 10. Module Documentation Requirements

### 10.1 Always required
- `modulos/<mod>/README.md`
- `MODULE_SCOPE_<MOD>.md`
- `DOMAIN_RULES_<MOD>.md`
- `INVARIANTS_<MOD>.md`
- `TEST_MATRIX_<MOD>.md`
- `contracts/openapi/paths/<mod>.yaml`
- `contracts/schemas/<mod>/*.schema.json`

### 10.2 Required when applicable
- `STATE_MODEL_<MOD>.md`
- `PERMISSIONS_<MOD>.md`
- `ERRORS_<MOD>.md`
- `SCREEN_MAP_<MOD>.md`
- `UI_CONTRACT_<MOD>.md`
- `contracts/workflows/<mod>/*.arazzo.yaml`
- `contracts/asyncapi/<mod>.yaml`

---

## 11. Applicability Matrix

### 11.1 STATE_MODEL_<MOD>.md
Required when there is:
- persisted status
- lifecycle transitions
- approval/rejection
- closing/reopening
- phase progression

### 11.2 PERMISSIONS_<MOD>.md
Required when there is:
- RBAC local to module
- sensitive actions
- visibility restrictions
- actor-specific capability rules

### 11.3 ERRORS_<MOD>.md
Required when there are:
- domain-specific error codes
- business rule failures beyond generic validation
- meaningful local error semantics

### 11.4 UI_CONTRACT_<MOD>.md
Required when there is:
- UI screen
- user form
- user-triggered actions
- loading/error/empty/success states

### 11.5 SCREEN_MAP_<MOD>.md
Required when there is:
- more than one user-facing screen
- navigation flow between screens
- entry-point ambiguity
- branching user journey relevant to behavior

### 11.6 Arazzo workflow
Required when:
- 2+ API calls are chained
- output of A is mandatory input of B
- chronology/order matters
- compensation/rollback is relevant

### 11.7 AsyncAPI
Required when:
- the module publishes or consumes real events

### 11.8 Conditional artifact absence rule
If an artifact appears applicable by these rules but is missing, the agent must not decide alone. It must emit the corresponding blocking code and stop the affected work.

---

## 12. Handball Trigger Rule

A module must explicitly link to `HANDBALL_RULES_DOMAIN.md` when it addresses:
- game time
- timeout
- exclusion
- sanction
- goal
- 7m throw
- free throw
- substitution
- team composition
- goalkeeper
- goal area
- ball/category
- table/scout operations
- match phases

No inferred sport rule is allowed.

### 12.1 Product adaptation of official handball rule
The product may adapt an official handball-derived rule only when that adaptation is explicitly registered in:
- `HANDBALL_RULES_DOMAIN.md`, or
- a linked `ADR`

If no such explicit adaptation exists, the translated handball-domain rule remains binding.

---

## 13. Source of Truth by Surface

- public HTTP interface => `contracts/openapi/openapi.yaml`
- reusable data shapes => `contracts/schemas/<mod>/*.schema.json`
- multi-step orchestration => `contracts/workflows/**/*.arazzo.yaml`
- event contracts => `contracts/asyncapi/**/*.yaml`
- module business rules => `DOMAIN_RULES_<MOD>.md`
- module integrity => `INVARIANTS_<MOD>.md`
- module state => `STATE_MODEL_<MOD>.md`
- module permissions => `PERMISSIONS_<MOD>.md`
- module UI => `UI_CONTRACT_<MOD>.md`
- module screen/navigation flow => `SCREEN_MAP_<MOD>.md`

Rule:
No surface may have two primary sources.

---

## 14. Derivation Rules

- OpenAPI may reference JSON Schemas when pipeline compatibility is guaranteed
- AsyncAPI may reference JSON Schemas when pipeline compatibility is guaranteed
- UI types are generated from OpenAPI
- API clients are generated from OpenAPI
- internal models may be generated from, or aligned to, sovereign contracts only

Rule:
Derived artifacts never redefine the source.

---

## 15. Contract Creation Procedure
1. select canonical module
2. create or update OpenAPI path file
3. create or update module JSON Schemas
4. create or update module docs
5. evaluate state, permissions, errors, UI, screen flow, workflow, events
6. validate technical contracts
7. update tests and readiness artifacts
8. only then implementation may begin

---

## 16. Contract Ready for Implementation (Binary DoD)

A contract is ready only when all are true:
- OpenAPI passes Redocly CLI and Spectral
- JSON Schemas validate as JSON Schema
- Arazzo validates when present
- AsyncAPI validates when present
- zero `TODO`, `TBD`, `A definir`, or unresolved placeholders
- explicit reference to `DOMAIN_RULES_<MOD>.md`
- explicit reference to `INVARIANTS_<MOD>.md`
- explicit reference to `TEST_MATRIX_<MOD>.md`
- explicit reference to `HANDBALL_RULES_DOMAIN.md` when handball trigger applies
- naming and placement obey the layout
- language rules obey the layout and governance rules

---

## 17. Module Ready for Implementation (Binary DoD)

A module is ready for implementation only when:
- all always-required docs exist
- all conditionally-required docs exist
- all relevant contracts validate
- test matrix covers API, schema, rule, invariant, and state when applicable
- mock can be generated from contract without ambiguity
- no critical missing artifact remains

---

## 18. Module Ready for AI-Guided Development

Beyond section 17:
- inputs are unambiguous
- outputs are unambiguous
- states are unambiguous
- errors are unambiguous
- permissions are unambiguous
- invariants are unambiguous
- no critical gap forces free inference
- all open decisions are explicitly outside the current task scope

---

## 19. Fixed Validation Tooling

- OpenAPI lint/validate: `Redocly CLI`
- OpenAPI rulesets: `Spectral`
- HTTP breaking change detection: `oasdiff`
- HTTP contract/runtime tests: `Schemathesis`
- JSON Schema validation: `JSON Schema validator in pipeline`
- AsyncAPI validation: `AsyncAPI parser/validator`
- Arazzo validation: `Arazzo validator/linter defined in pipeline`
- UI docs validation when applicable: `Storybook build`

---

## 20. Agent Operation Modes

The agent operates only in the following formal modes:

### 20.1 `contract_creation_mode`
Used when creating a new contract artifact.

### 20.2 `contract_revision_mode`
Used when reviewing or changing an existing contract artifact.

### 20.3 `implementation_mode`
Used when implementing software from already-defined contracts.

### 20.4 `audit_mode`
Used when auditing contract completeness, consistency, and readiness.

Rule:
The active mode determines the minimum boot set and expected output.

---

## 21. Minimum Boot Matrix by Task Type

### 21.1 Create new contract
**Mandatory boot**
- `CONTRACT_SYSTEM_LAYOUT.md`
- `CONTRACT_SYSTEM_RULES.md`
- applicable template
- `SYSTEM_SCOPE.md`
- `API_CONVENTIONS.md`

**Conditional boot**
- `HANDBALL_RULES_DOMAIN.md` if handball trigger applies
- `DATA_CONVENTIONS.md` if new schema is created
- `MODULE_MAP.md` if module boundary is unclear
- `DOMAIN_GLOSSARY.md` if terminology is ambiguous
- existing contract of the module, if one already exists

**Expected output**
- contract created in canonical location
- no forbidden placeholder
- explicit linkage to mandatory documents

**Possible blocking codes**
- `BLOCKED_MISSING_MODULE`
- `BLOCKED_MISSING_OPENAPI_PATH`
- `BLOCKED_MISSING_SCHEMA`
- `BLOCKED_MISSING_HANDBALL_REFERENCE`
- `BLOCKED_CONTRACT_CONFLICT`

### 21.2 Review / change existing contract
**Mandatory boot**
- `CONTRACT_SYSTEM_LAYOUT.md`
- `CONTRACT_SYSTEM_RULES.md`
- target contract
- `CHANGE_POLICY.md`
- `API_CONVENTIONS.md`

**Conditional boot**
- `HANDBALL_RULES_DOMAIN.md` if sport-derived rule is touched
- `DOMAIN_RULES_<MOD>.md`
- `INVARIANTS_<MOD>.md`
- `STATE_MODEL_<MOD>.md` if state is touched
- `ERROR_MODEL.md` if error behavior is touched
- `PERMISSIONS_<MOD>.md` if access behavior is touched
- `UI_CONTRACT_<MOD>.md` if UI behavior is touched

**Expected output**
- explicit breaking/non-breaking classification
- clear contract diff
- consistent update of affected artifacts

**Possible blocking codes**
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_INVARIANT`
- `BLOCKED_MISSING_STATE_MODEL`
- `BLOCKED_MISSING_PERMISSION_MODEL`
- `BLOCKED_MISSING_UI_CONTRACT`
- `BLOCKED_CONTRACT_CONFLICT`

### 21.3 Implement module guided by contract
**Mandatory boot**
- `CONTRACT_SYSTEM_RULES.md`
- `SYSTEM_SCOPE.md`
- `MODULE_SCOPE_<MOD>.md`
- `DOMAIN_RULES_<MOD>.md`
- `INVARIANTS_<MOD>.md`
- `contracts/openapi/paths/<mod>.yaml`
- `contracts/schemas/<mod>/*.schema.json`

**Conditional boot**
- `STATE_MODEL_<MOD>.md`
- `PERMISSIONS_<MOD>.md`
- `ERRORS_<MOD>.md`
- `UI_CONTRACT_<MOD>.md`
- `TEST_MATRIX_<MOD>.md`
- `HANDBALL_RULES_DOMAIN.md` if handball trigger applies
- `contracts/workflows/<mod>/*.arazzo.yaml`
- `contracts/asyncapi/<mod>.yaml`

**Expected output**
- implementation without invented public interface
- code aligned to contract
- no inferred field/state/event outside documentation

**Possible blocking codes**
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_INVARIANT`
- `BLOCKED_MISSING_STATE_MODEL`
- `BLOCKED_MISSING_PERMISSION_MODEL`
- `BLOCKED_MISSING_UI_CONTRACT`
- `BLOCKED_MISSING_TEST_MATRIX`
- `BLOCKED_MISSING_HANDBALL_REFERENCE`

### 21.4 Audit module
**Mandatory boot**
- `CONTRACT_SYSTEM_RULES.md`
- `MODULE_SCOPE_<MOD>.md`
- `DOMAIN_RULES_<MOD>.md`
- `INVARIANTS_<MOD>.md`
- `TEST_MATRIX_<MOD>.md`
- `contracts/openapi/paths/<mod>.yaml`
- `contracts/schemas/<mod>/*.schema.json`

**Conditional boot**
- `STATE_MODEL_<MOD>.md`
- `PERMISSIONS_<MOD>.md`
- `ERRORS_<MOD>.md`
- `UI_CONTRACT_<MOD>.md`
- `HANDBALL_RULES_DOMAIN.md`
- `contracts/workflows/<mod>/*.arazzo.yaml`
- `contracts/asyncapi/<mod>.yaml`
- `CI_CONTRACT_GATES.md`

**Expected output**
- `PASS`, `FAIL`, or `BLOCKED`
- exact list of conflicts
- explicit reference to violated artifact

**Possible blocking codes**
- any `BLOCKED_MISSING_*` code that matches the absent required artifact
- `BLOCKED_CONTRACT_CONFLICT`

### 21.5 Create Arazzo workflow
**Mandatory boot**
- `CONTRACT_SYSTEM_LAYOUT.md`
- `CONTRACT_SYSTEM_RULES.md`
- `contracts/openapi/openapi.yaml`
- `contracts/openapi/paths/<mod>.yaml`

**Conditional boot**
- `DOMAIN_RULES_<MOD>.md`
- `STATE_MODEL_<MOD>.md`
- `HANDBALL_RULES_DOMAIN.md` if flow depends on sport rule

**Expected output**
- workflow only when multi-step is real
- steps linked to existing OpenAPI operations

**Possible blocking codes**
- `BLOCKED_MISSING_OPENAPI_PATH`
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_STATE_MODEL`
- `BLOCKED_MISSING_HANDBALL_REFERENCE`
- `BLOCKED_CONTRACT_CONFLICT`

### 21.6 Create AsyncAPI contract
**Mandatory boot**
- `CONTRACT_SYSTEM_LAYOUT.md`
- `CONTRACT_SYSTEM_RULES.md`
- event context
- affected module contract

**Conditional boot**
- `DOMAIN_RULES_<MOD>.md`
- `INVARIANTS_<MOD>.md`
- `STATE_MODEL_<MOD>.md`
- `HANDBALL_RULES_DOMAIN.md` if event carries sport semantics

**Expected output**
- event only when real event exists
- stable and traceable payload

**Possible blocking codes**
- `BLOCKED_MISSING_MODULE`
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_INVARIANT`
- `BLOCKED_MISSING_STATE_MODEL`
- `BLOCKED_MISSING_HANDBALL_REFERENCE`
- `BLOCKED_CONTRACT_CONFLICT`

### 21.7 Create UI contract
**Mandatory boot**
- `MODULE_SCOPE_<MOD>.md`
- `DOMAIN_RULES_<MOD>.md`
- `contracts/openapi/paths/<mod>.yaml`
- `contracts/schemas/<mod>/*.schema.json`

**Conditional boot**
- `STATE_MODEL_<MOD>.md`
- `ERRORS_<MOD>.md`
- `PERMISSIONS_<MOD>.md`
- `HANDBALL_RULES_DOMAIN.md` if sport rule impacts UI behavior
- `UI_FOUNDATIONS.md`
- `DESIGN_SYSTEM.md`

**Expected output**
- inputs
- outputs
- states
- actions
- errors
- permissions
- no invented behavior

**Possible blocking codes**
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_STATE_MODEL`
- `BLOCKED_MISSING_PERMISSION_MODEL`
- `BLOCKED_MISSING_HANDBALL_REFERENCE`
- `BLOCKED_CONTRACT_CONFLICT`

### 21.8 Create state model
**Mandatory boot**
- `DOMAIN_RULES_<MOD>.md`
- `INVARIANTS_<MOD>.md`

**Conditional boot**
- `contracts/openapi/paths/<mod>.yaml`
- `ERRORS_<MOD>.md`
- `HANDBALL_RULES_DOMAIN.md` if handball trigger applies

**Expected output**
- named states
- valid transitions
- triggers
- invalid-transition errors

**Possible blocking codes**
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_INVARIANT`
- `BLOCKED_MISSING_HANDBALL_REFERENCE`
- `BLOCKED_CONTRACT_CONFLICT`

### 21.9 Final operational rule
- do not load everything every time
- load the minimum mandatory set
- load the rest only by applicability
- if a critical artifact is missing, block instead of infer

---

## 22. Evolution Rule

All change must follow this order:
1. update normative artifact
2. validate contract
3. regenerate derived artifacts
4. update implementation
5. run tests
6. review impact

Implementation-first followed by documentation-after is forbidden.