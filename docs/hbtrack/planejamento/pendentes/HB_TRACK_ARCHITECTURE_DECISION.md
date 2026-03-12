# HB_TRACK_ARCHITECTURE_DECISION.md

version: 1.0.0
status: PROPOSED
decision_type: architecture
scope: hb_track
owners:
  - architecture
  - backend
  - frontend
  - data
  - analytics
related_modules:
  - identity_access
  - organizations
  - teams
  - athletes
  - training
  - matches
  - scouts
  - analytics
  - reports
  - audit
  - notifications
  - attachments
  - wellbeing
related_artifacts:
  - docs/_ssot/openapi.json
  - docs/_ssot/schema.sql
  - docs/_canon/MANUAL_BACKEND_CANONICO.md
  - docs/_canon/REGRAS_SISTEMAS.md

---

## 1. Objective

Define the canonical architectural decisions for:
- persistence strategy
- provider abstraction
- API contract boundaries
- UI projection boundaries
- sensitive-data isolation

This document exists to prevent architectural drift, premature complexity, and coupling between:
- domain model
- HTTP contract
- UI composition
- external providers
- AI-derived analysis layers

---

## 2. Decision Summary

The HB Track architecture SHALL NOT adopt a single persistence model for the whole platform.

The platform SHALL use:
- transactional CRUD as the default persistence model
- event-first / append-only patterns only in bounded contexts where historical reconstruction, replay, auditability, and derived projections produce direct product value

The platform SHALL keep strict separation between:
- domain contract
- API DTO contract
- UI/ViewModel contract
- ingestion/provider contract

The platform SHALL treat psychological / wellbeing-related functionality as a sensitive bounded context with stronger governance, stricter access control, and explicit minimization rules.

---

## 3. Architectural Principles

### 3.1 Bounded-context-first architecture
Persistence and integration decisions MUST be made per bounded context, never globally for the whole system.

### 3.2 CRUD by default
CRUD is the default model unless there is clear evidence that append-only history is a product requirement.

### 3.3 Event-first only where history matters
Event-oriented persistence is allowed only when at least one of the following is true:
- replay is required
- historical state reconstruction is required
- immutable audit trail is required
- multiple read projections are required from the same fact stream
- temporal analytics depends on the original event sequence

### 3.4 Contracts are layered
The following contracts MUST remain distinct:
- Domain Contract
- Public API Contract
- UI Projection Contract
- Provider Ingestion Contract

### 3.5 External-source neutrality
No UI or domain rule may depend directly on one provider’s raw payload format.

### 3.6 Sensitive-domain isolation
Any wellbeing / psychological / health-adjacent feature MUST be isolated from general sports analytics and administrative flows.

---

## 4. Canonical Persistence Policy

### 4.1 CRUD-transacional obrigatório por padrão
Use relational transactional persistence for:
- identity_access
- organizations
- teams base registry
- athletes registry
- scheduling / calendar administration
- billing / subscription
- settings / preferences
- attachments registry metadata
- permissions / memberships
- static reference catalogs

Expected characteristics:
- normalized schema
- ACID writes
- direct queryability
- predictable operational maintenance
- simpler debugging and migration management

### 4.2 Event-first / append-only contexts
Use event-first or append-only persistence for:
- matches event timeline
- scouts / observational tagging
- video tagging and temporal annotations
- analytics raw fact collection
- audit
- notifications delivery log
- projection refresh triggers
- derived performance event streams

Expected characteristics:
- immutable facts
- versioned event schema
- idempotent consumers
- replay-safe projections
- explicit reprocessing strategy
- traceable producer identity

### 4.3 Hybrid contexts
The following modules MAY use hybrid design:
- training
- reports
- wellbeing

Hybrid means:
- transactional aggregate for current operational state
- append-only event log for facts that require replay, audit, or temporal analytics

Hybrid is allowed only if the event stream has a clear consumer and a defined projection model.

---

## 5. Module-by-Module Recommendation

| Module | Canonical Persistence | Notes |
|---|---|---|
| identity_access | CRUD | security, memberships, roles, auth state |
| organizations | CRUD | master data |
| teams | CRUD | registry + operational state |
| athletes | CRUD | registry; sensitive fields isolated if needed |
| training | HYBRID | session state in CRUD; attendance/status/timeline facts may be append-only |
| matches | EVENT-FIRST | game timeline, tagged events, temporal analytics |
| scouts | EVENT-FIRST | observations are facts, not mutable summaries |
| analytics | EVENT-FIRST | projections from facts; avoid treating analytics as primary write model |
| reports | HYBRID | generated artifacts + derived projections |
| audit | EVENT-FIRST | immutable by definition |
| notifications | EVENT-FIRST | delivery attempts, channel logs, retries |
| attachments | CRUD | blob/file refs + metadata |
| wellbeing | HYBRID / ISOLATED | strict governance; never mix loosely with generic coaching telemetry |

---

## 6. Event-First Admission Criteria

A module or subdomain may adopt event-first persistence only if all conditions below are satisfied:

1. The business value of fact history is explicit.
2. The core write is naturally modeled as a fact that occurred at time T.
3. At least one projection or replay use case is real, not speculative.
4. Idempotency strategy is defined.
5. Event versioning policy is defined.
6. Rebuild / reprocessing policy is defined.
7. Observability for projection failures exists.
8. Retention and storage cost are acceptable.
9. Operational team can debug event flow safely.
10. The same goal cannot be achieved more simply with audit tables + relational history.

If these conditions are not met, CRUD remains mandatory.

---

## 7. Contract Separation Rules

### 7.1 Domain Contract
Represents business meaning and invariants.
Must not be shaped by:
- HTTP transport
- provider payload quirks
- screen composition needs

### 7.2 API DTO Contract
Represents transport boundary.
Must not leak:
- internal persistence model
- provider-specific raw payloads
- UI-only composition artifacts

### 7.3 UI/ViewModel Contract
Represents screen-oriented composition.
May aggregate:
- multiple DTOs
- cached summaries
- derived formatting fields
- visualization-specific structures

Must not become the canonical backend contract.

### 7.4 Provider Ingestion Contract
Represents normalization boundary for external or semi-structured input.
Must absorb:
- provider-specific identifiers
- coverage variation
- schema drift
- partial data availability
- ingestion provenance

Must output normalized internal shapes.

---

## 8. Provider Abstraction Policy

HB Track SHALL implement a provider abstraction layer for all external sports/video/statistical sources.

Supported source categories:
- external official provider
- internal manual input by coach/staff
- video-derived AI extraction
- CSV/spreadsheet import
- federation / competition structured feeds
- future partner integrations

### 8.1 Required ingestion fields
Every ingested fact SHOULD carry:
- source_type
- source_system
- source_record_id
- ingested_at
- observed_at
- confidence_level (when applicable)
- provenance_metadata
- normalization_version

### 8.2 Anti-coupling rule
No downstream module may depend on a specific provider field name unless that field has been promoted to the internal canonical ingestion contract.

### 8.3 Strategic consequence
The competitive moat for HB Track should not depend on a single external provider. It should depend on:
- normalized ingestion
- structured coaching workflow
- video/event linkage
- projections and insights
- traceability

This is especially important because handball market coverage is uneven across providers, while Sportradar does offer official handball coverage and XPS is a strong benchmark for workflow/product UX in handball. :contentReference[oaicite:0]{index=0}

---

## 9. UI Architecture Decision

HB Track SHALL maintain strict API DTO vs ViewModel separation.

### 9.1 Why
Reasons:
- UI performance optimization
- screen-specific composition
- resilience to backend refactors
- resilience to provider replacement
- reduction of frontend churn
- support for richer video/analytics dashboards

### 9.2 Forbidden patterns
The following are forbidden:
- using provider payloads directly in UI components
- using DB entities directly as API DTOs
- using UI ViewModels as backend domain models
- binding analytics screens to raw ingestion schemas

### 9.3 Required pattern
Preferred chain:
Provider/Input -> Normalized Ingestion Contract -> Domain Logic -> API DTO -> UI ViewModel -> Components

---

## 10. Sensitive Data Boundary

### 10.1 Sensitive-domain classification
Any feature that handles or infers:
- mental wellbeing
- psychological status
- emotional state
- health-adjacent condition
- behavioral risk scoring
- individualized wellbeing flags

MUST be treated as a sensitive domain.

### 10.2 Required controls
Such domains MUST implement:
- field-level access control where applicable
- least-privilege access model
- explicit purpose limitation
- data minimization
- retention policy
- auditable access trail
- separation from generic performance dashboards when required
- explicit provenance for AI-generated inferences
- human review boundary for high-impact outputs

### 10.3 Product rule
HB Track MUST NOT silently blend sensitive wellbeing inference with ordinary performance metrics in a single undifferentiated athlete score.

### 10.4 Legal rationale
Under the LGPD, health-related personal data is treated as sensitive personal data, which raises the compliance bar for collection and processing. :contentReference[oaicite:1]{index=1}

---

## 11. Non-Goals

This decision does NOT mandate:
- full-system event sourcing
- CQRS everywhere
- one vendor as strategic dependency
- direct adoption of XPS internals
- replacing relational models with event logs in administrative modules
- using AI inference as primary source of truth

---

## 12. Architectural Risks

### 12.1 Risks if ignored
- frontend coupled to provider schemas
- migration pain when changing providers
- analytics facts overwritten instead of preserved
- audit gaps
- inflated complexity in simple modules
- sensitive-domain leakage into general coaching views

### 12.2 Risks if over-applied
- event sourcing theater
- excessive cognitive load
- projection drift
- rebuild complexity
- schema-version explosion
- slower feature delivery for operational modules

---

## 13. Canonical Decision

The canonical architecture for HB Track is:

1. CRUD-transacional is the platform default.
2. Event-first is restricted to fact-history-critical contexts.
3. Training, reports, and wellbeing may be hybrid, subject to explicit contract.
4. Domain, DTO, ViewModel, and ingestion contracts are separate layers.
5. Provider abstraction is mandatory.
6. Sensitive wellbeing/psychological functionality is isolated and governed as a high-control domain.

---

## 14. Immediate Repository Actions

The repository SHOULD next create:

1. `HB_TRACK_PERSISTENCE_POLICY.md`
   - module-by-module persistence matrix
   - CRUD vs EVENT_FIRST vs HYBRID rules
   - admission checklist for event-first

2. `INGESTION_PROVIDER_CONTRACT.md`
   - canonical ingestion fields
   - provenance policy
   - confidence semantics
   - normalization/versioning rules

3. `DTO_VIEWMODEL_BOUNDARY_RULES.md`
   - forbidden couplings
   - mapping rules
   - frontend composition contract

4. `SENSITIVE_DOMAIN_GOVERNANCE.md`
   - access model
   - retention
   - audit requirements
   - AI inference labeling rules

---

## 15. Definition of Done

This decision is considered implemented only when:
- each HB Track module has an assigned persistence classification
- ingestion contract exists
- DTO/ViewModel boundary rules exist
- sensitive-domain policy exists
- new modules cannot be created without choosing a persistence class
- architecture review checks these rules before implementation
```
