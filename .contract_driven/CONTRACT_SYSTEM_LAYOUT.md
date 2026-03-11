# CONTRACT_SYSTEM_LAYOUT.md

## 1. Purpose
This document defines the canonical filesystem layout and naming rules for all contract artifacts in HB Track.

It governs only:
- `contracts/openapi/`
- `contracts/schemas/`
- `contracts/workflows/`
- `contracts/asyncapi/`

It does **not** replace:
- global human documentation (`README.md`, `SYSTEM_SCOPE.md`, `ARCHITECTURE.md`, `C4_CONTEXT.md`, `C4_CONTAINERS.md`, `UI_FOUNDATIONS.md`, `DESIGN_SYSTEM.md`, etc.)
- module human documentation (`modulos/<mod>/...`)
- operational rules (`CONTRACT_SYSTEM_RULES.md`)
- templates / scaffolds (`GLOBAL_TEMPLATES.md` or `templates/`)

---

## 2. Canonical Module Taxonomy

If a module is not listed here, it does not exist.

### 2.1 Functional Domain Modules
- `users`
- `seasons`
- `teams`
- `training`
- `wellness`
- `medical`
- `competitions`
- `matches`
- `scout`
- `exercises`
- `analytics`
- `reports`
- `ai_ingestion`

### 2.2 Formal Cross-Cutting Modules
- `identity_access`
- `audit`
- `notifications`

### 2.3 Critical Boundary
- `users` = person/profile domain
- `identity_access` = authentication, authorization, credentials, sessions, MFA, JWT, RBAC

### 2.4 Negative Boundary Rules
- no artifact under `users` may define authentication or authorization policy
- no artifact under `identity_access` may redefine profile, biography, or personal functional identity data
- if a responsibility overlaps both modules, the conflict must be resolved by explicit contract boundary or ADR

---

## 3. Canonical Language

### 3.1 English required for technical identifiers
The following must always be in English:
- module names
- contract folder names
- OpenAPI paths
- operationIds
- JSON property names
- schema filenames
- Arazzo filenames
- AsyncAPI filenames
- event names
- DB table/column names
- generated type names

### 3.2 Portuguese required for human documentation content
The content of `.md` files must be written in Portuguese, except for:
- code
- keys
- technical identifiers
- normative quoted snippets
- tool commands
- generated examples when required by tooling

### 3.3 Mixed-Identifier Prohibition
Mixed language inside the same technical identifier is forbidden.

Examples of forbidden identifiers:
- `treinosSession`
- `usuario_profile`
- `cadastroAuth`

---

## 4. Canonical Contract Tree

```text
contracts/
  openapi/
    openapi.yaml
    paths/
      users.yaml
      seasons.yaml
      teams.yaml
      training.yaml
      wellness.yaml
      medical.yaml
      competitions.yaml
      matches.yaml
      scout.yaml
      exercises.yaml
      analytics.yaml
      reports.yaml
      ai_ingestion.yaml
      identity_access.yaml
      audit.yaml
      notifications.yaml
    components/
      schemas/
        shared/
        users/
        seasons/
        teams/
        training/
        wellness/
        medical/
        competitions/
        matches/
        scout/
        exercises/
        analytics/
        reports/
        ai_ingestion/
        identity_access/
        audit/
        notifications/
      parameters/
      responses/
      requestBodies/
      securitySchemes/
      examples/

  schemas/
    shared/
    users/
    seasons/
    teams/
    training/
    wellness/
    medical/
    competitions/
    matches/
    scout/
    exercises/
    analytics/
    reports/
    ai_ingestion/
    identity_access/
    audit/
    notifications/

  workflows/
    _global/
    users/
    seasons/
    teams/
    training/
    wellness/
    medical/
    competitions/
    matches/
    scout/
    exercises/
    analytics/
    reports/
    ai_ingestion/
    identity_access/
    audit/
    notifications/

  asyncapi/
    asyncapi.yaml
    channels/
    operations/
    messages/
    components/
      schemas/
      messageTraits/
      operationTraits/
```

### 4.1 Canonical derived-artifacts location
Derived artifacts must live outside sovereign contract sources.

Recommended canonical location:

```text
generated/
  openapi/
  asyncapi/
  clients/
  ui-types/
  docs/
  storybook/
```

No generated artifact may be committed as if it were sovereign.

---

## 5. Layer Sovereignty

### 5.1 HTTP Public Interface
Primary source of truth:
- `contracts/openapi/openapi.yaml`

### 5.2 Reusable Data Shapes
Primary source of truth:
- `contracts/schemas/<module>/*.schema.json`

### 5.3 Multi-Step Orchestration
Primary source of truth:
- `contracts/workflows/**/*.arazzo.yaml`

### 5.4 Event Contracts
Primary source of truth:
- `contracts/asyncapi/**/*.yaml`

### 5.5 Rule
No surface may have two primary sources of truth.

### 5.6 Derived-Surface Rule
Generated or derived artifacts may exist for any surface, but they never replace the primary source defined above.

---

## 6. OpenAPI Layout Rules
- `contracts/openapi/openapi.yaml` is the entrypoint.
- `contracts/openapi/paths/<module>.yaml` contains path items for one module only.
- `contracts/openapi/components/schemas/shared/` contains shared HTTP-facing schemas.
- `contracts/openapi/components/schemas/<module>/` contains module-specific HTTP-facing schemas.
- OpenAPI may `$ref` schemas from `contracts/schemas/` when the pipeline supports this cleanly.
- No path file may contain routes from two modules.
- One module must not silently expose another module’s public surface through its own path file.

---

## 7. JSON Schema Layout Rules
- `contracts/schemas/<module>/` contains reusable, module-scoped data shapes.
- `contracts/schemas/shared/` contains shapes reused across modules.
- Filenames must end in `.schema.json`.
- JSON Schemas are reusable domain/data shapes, not replacements for the HTTP contract.
- If the same concept exists in both OpenAPI-facing schema and reusable schema, the sovereignty of each surface must remain explicit.

---

## 8. Arazzo Layout Rules
- `contracts/workflows/_global/` is reserved for cross-module workflows.
- `contracts/workflows/<module>/` is reserved for module workflows.
- A workflow file is allowed only when multi-step orchestration is real and relevant.
- One workflow file should represent one named use case.
- Workflow filenames must describe the use case, not the implementation detail.

---

## 9. AsyncAPI Layout Rules
- `contracts/asyncapi/asyncapi.yaml` is the root document.
- `channels/`, `operations/`, `messages/`, and `components/` must be split when the document grows.
- AsyncAPI is allowed only when there are real events.
- AsyncAPI files must not exist as placeholders without event reality.

---

## 10. Naming Rules

### 10.1 Module names
- `lower_snake_case`

### 10.2 OpenAPI path files
- `contracts/openapi/paths/<module>.yaml`

### 10.3 JSON Schema files
- `contracts/schemas/<module>/<entity>.schema.json`

### 10.4 Arazzo files
- `contracts/workflows/<module>/<use_case>.arazzo.yaml`

### 10.5 AsyncAPI files
- `contracts/asyncapi/<layer>/<name>.yaml`

### 10.6 Human documentation names
- global docs may use uppercase canonical names (`SYSTEM_SCOPE.md`, `API_CONVENTIONS.md`)
- module docs may use canonical uppercase placeholders (`DOMAIN_RULES_<MOD>.md`, etc.)
- inside these docs, referenced technical identifiers remain English

---

## 11. Required Human Documentation Links
Every module-level documentation set must explicitly link, when applicable, to:
- `SYSTEM_SCOPE.md`
- `HANDBALL_RULES_DOMAIN.md`

Every contract creation flow must preserve this cross-reference in the related module docs.

### 11.1 Required Cross-Reference Set for Module Docs
The minimal expected cross-reference footprint for module documentation is:
- system scope
- handball rules when trigger applies
- OpenAPI path file
- schema folder of the module

---

## 12. Anti-Patterns (Forbidden)
- mixed-language technical identifiers
- duplicated primary source of truth
- path files mixing modules
- workflow files without real orchestration
- asyncapi files without real events
- contracts placed outside canonical folders
- undocumented module names outside the 16-module taxonomy
- generated artifacts treated as sovereign
- module docs that fail to reference the required global docs when applicable

---

## 13. Contract Creation Flow (Structural)
1. choose the canonical module from the 16-module taxonomy
2. create `contracts/openapi/paths/<module>.yaml`
3. create `contracts/schemas/<module>/`
4. evaluate `contracts/workflows/<module>/`
5. evaluate `contracts/asyncapi/<module>.yaml`
6. link the human documentation of the module to `SYSTEM_SCOPE.md` and, if applicable, `HANDBALL_RULES_DOMAIN.md`

### 13.1 Structural Output Expectation
A contract creation flow is structurally acceptable only when the artifact:
- is created under the canonical tree
- uses canonical language rules
- preserves surface sovereignty
- respects module boundary
- preserves module-to-human-doc cross-reference

---

## 14. Structural Definition of Done
A contract structure is structurally valid only when:
- artifact is in the canonical folder
- naming follows canonical rules
- module belongs to the 16-module list
- surface sovereignty is respected
- no forbidden anti-pattern is present

---

## 15. Agent-Relevant Structural Rules
The agent must use this file only to determine:
- where an artifact belongs
- whether an artifact belongs to a valid module
- what the canonical folder and naming must be
- whether the artifact violates structural sovereignty

This file must not be used to invent business rules, state, permissions, or event semantics.