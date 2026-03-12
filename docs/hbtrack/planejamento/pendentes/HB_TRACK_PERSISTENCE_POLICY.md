# HB_TRACK_PERSISTENCE_POLICY.md

version: 1.0.0
status: PENDENTE
decision_type: architecture_policy
scope: hb_track
owners:
  - architecture
  - backend
  - data
  - analytics
related_decisions:
  - HB_TRACK_ARCHITECTURE_DECISION.md
related_artifacts:
  - docs/_ssot/openapi.json
  - docs/_ssot/schema.sql
  - docs/_canon/MANUAL_BACKEND_CANONICO.md
  - docs/_canon/REGRAS_SISTEMAS.md

---

## 1. Objective

Define the canonical persistence classification for each HB Track module and establish the rules for when a module or subdomain must use:

- CRUD
- EVENT_FIRST
- HYBRID

This policy exists to prevent:
- full-system Event Sourcing by enthusiasm
- loss of fact history where it matters
- architectural drift between modules
- accidental coupling between operational state and analytical history

---

## 2. Canonical Persistence Classes

### 2.1 CRUD

Definition:
A module is classified as CRUD when its primary concern is maintaining current operational state through transactional writes and direct relational reads.

Typical characteristics:
- current-state oriented
- normalized schema
- low replay value
- low need for immutable fact history
- simple queryability
- simpler debugging and migration flow

Use CRUD when:
- the latest valid state is what matters
- historical replay is not a core product capability
- audit trail can be satisfied by audit tables/logging instead of primary event streams
- derived projections are not central to the module’s value

---

### 2.2 EVENT_FIRST

Definition:
A module is classified as EVENT_FIRST when its primary source of truth is a sequence of immutable facts over time.

Typical characteristics:
- append-only or fact-oriented writes
- high replay value
- multiple derived projections
- temporal reconstruction matters
- auditability is intrinsic
- analytics depends on event order and provenance

Use EVENT_FIRST when:
- the sequence of facts matters as much as or more than the current state
- replay/rebuild is a real capability
- projections are product-critical
- immutable traceability is required

---

### 2.3 HYBRID

Definition:
A module is HYBRID when it requires both:
- transactional current-state management
- fact history preserved as append-only events for specific flows

Typical characteristics:
- operational state in relational aggregates
- selected fact streams preserved for traceability, replay, analytics, or audit
- mixed read patterns
- stricter modeling discipline required

Use HYBRID when:
- current state matters operationally
- but part of the module produces facts that should not be reduced to overwritable rows

---

## 3. Classification Matrix — Canonical HB Track Modules

| Module | Class | Canonical Reason |
|---|---|---|
| identity_access | CRUD | auth, roles, sessions, memberships, permissions are operational state |
| organizations | CRUD | master data and hierarchical ownership state |
| teams | CRUD | registry and current team structure/state |
| athletes | CRUD | athlete registry is current-state centric |
| staff | CRUD | professional registry and memberships |
| categories | CRUD | reference/catalog data |
| venues | CRUD | reference and scheduling support data |
| competitions | HYBRID | competition registry is CRUD; official occurrences/results/history may generate fact streams |
| matches | EVENT_FIRST | match timeline is fundamentally temporal and fact-based |
| scouts | EVENT_FIRST | scouting observations are facts and annotations over time |
| training | HYBRID | session planning/state is CRUD; attendance/events/progress facts may require append-only history |
| session_templates | CRUD | templates are design-time configuration artifacts |
| planning_periodization | CRUD | planning structures are primarily operational/planned state |
| attendance | EVENT_FIRST | attendance markings are historical facts with actor/time provenance |
| performance | HYBRID | current KPIs may be materialized, but measured facts should remain traceable |
| analytics | EVENT_FIRST | projections and insights derive from raw fact streams |
| reports | HYBRID | generated outputs are current artifacts, but some report inputs/refresh histories are fact-based |
| video | HYBRID | asset registry is CRUD; temporal annotations/tagging are fact streams |
| attachments | CRUD | file/blob metadata and linkage are current-state records |
| notifications | EVENT_FIRST | delivery attempts, retries, channel outcomes are fact history |
| audit | EVENT_FIRST | immutable trail by definition |
| wellbeing | HYBRID | operational forms/flags may be current state; sensitive observations/inferences require traceable history |
| tasks_workflow | CRUD | task and board state are primarily operational |
| comments_feedback | HYBRID | current thread state is relational, but authored comments are immutable interaction facts |
| integrations | CRUD | provider configs, credentials refs, sync settings are operational state |
| ingestion | EVENT_FIRST | ingestion is fact provenance, not merely mutable rows |
| projections | EVENT_FIRST | projection lifecycle depends on upstream facts and rebuildability |
| exports_imports | HYBRID | job state is CRUD; import/export execution history is factual |
| billing | CRUD | subscriptions, invoices refs, plan state are transactional |
| settings | CRUD | preferences and configuration state |
| search | CRUD | usually index-backed operational support layer, not source-of-truth fact stream |
| dashboard | HYBRID | dashboard itself is projection/read composition, backed by CRUD + event-derived sources |
| medical_health_adjacent | HYBRID / RESTRICTED | current forms may be CRUD, but measured/observed sensitive facts require strong traceability |
| psychology_support_ai | HYBRID / RESTRICTED | inference and observations require traceability, governance, and separation from generic telemetry |

---

## 4. Canonical Module Notes

### 4.1 identity_access = CRUD
Rationale:
- users, roles, grants, memberships, auth bindings and session state are current-state entities
- immutable audit is required, but belongs to `audit`, not to the module’s primary persistence model

Rule:
- do not model permission changes as the primary state through event sourcing unless there is a proven need for full replay of authorization history

---

### 4.2 matches = EVENT_FIRST
Rationale:
- match events are inherently chronological
- score evolution, possession changes, tagged incidents, tactical episodes and video references depend on temporal sequence
- the current score is a projection; it is not the primary fact

Rule:
- the canonical source must preserve event order, actor, timestamp, provenance and version
- any mutable summary table must be treated as a derived projection

---

### 4.3 scouts = EVENT_FIRST
Rationale:
- scouting is observation-driven
- overwriting an observation destroys interpretive history
- later analytics may reinterpret old observed facts under new models

Rule:
- each scouting record must be modeled as an authored fact or annotation with provenance
- editing policies must be explicit; destructive overwrite is discouraged

---

### 4.4 training = HYBRID
Rationale:
- training sessions have an operational state: draft, scheduled, in_progress, completed, cancelled
- but session occurrences also generate facts: attendance, status transitions, execution deviations, coach notes, drill completion, load observations

Rule:
- session aggregate and schedule remain CRUD
- session events with historical value should be append-only

Examples of append-only training facts:
- attendance_marked
- session_started
- session_finished
- drill_completed
- load_recorded
- coach_observation_added

---

### 4.5 analytics = EVENT_FIRST
Rationale:
- analytics should not be the primary writer of truth; it should consume truth from facts
- analytical outputs are projections, aggregations, scores and snapshots derived from historical facts

Rule:
- avoid making analytics tables the canonical source of business truth
- raw measurable facts must survive independently of today’s scoring formula

---

### 4.6 reports = HYBRID
Rationale:
- report definitions, templates and generated file metadata are relational
- generation attempts, refresh triggers, build logs and provenance chains are factual events

Rule:
- a generated report file can be current-state metadata
- generation history should remain traceable as fact records

---

### 4.7 audit = EVENT_FIRST
Rationale:
- audit loses meaning if rewritten
- immutability is the point

Rule:
- audit records are append-only
- corrections must be additive, never destructive

---

### 4.8 notifications = EVENT_FIRST
Rationale:
- notification value includes attempt history, delivery outcome, retry count, provider response and timing
- current “status” is only a projection over historical attempts

Rule:
- store each delivery attempt as an event/fact
- expose summary status via projection if needed

---

### 4.9 wellbeing / psychology_support_ai = HYBRID / RESTRICTED
Rationale:
- there may be relational operational state such as questionnaires, review workflows or status flags
- but any inference, observation, score evolution or human review chain requires traceability
- this domain is sensitive and must not be flattened into generic athlete telemetry

Rule:
- inference outputs must carry provenance, model/version context and review boundary where applicable
- destructive overwrites of sensitive interpretive facts are forbidden unless explicitly governed

---

## 5. Admission Checklist for EVENT_FIRST

A module or subdomain may be classified as EVENT_FIRST only if all items below are satisfied.

### 5.1 Mandatory criteria
- [ ] the business fact is naturally expressed as “something happened”
- [ ] historical order matters
- [ ] replay or reconstruction provides real value
- [ ] at least one derived projection is required
- [ ] the event schema can be versioned
- [ ] idempotency strategy exists
- [ ] producer identity and provenance are captured
- [ ] retention and storage policy exist
- [ ] rebuild/reprocessing policy exists
- [ ] operational observability exists for consumers/projections

### 5.2 Blocking rule
If three or more mandatory criteria are not satisfied, the module SHALL NOT be EVENT_FIRST.

---

## 6. Admission Checklist for HYBRID

A module may be HYBRID only if all items below are true.

- [ ] there is a real operational current-state aggregate
- [ ] there is a real fact stream inside the same bounded context
- [ ] the event stream has explicit consumers
- [ ] the event stream is not speculative
- [ ] state ownership vs fact ownership is clearly defined
- [ ] no ambiguity exists about which layer is source of truth for each concept

Blocking rule:
If the team cannot clearly answer “which fields are current-state aggregate” and “which facts are append-only,” the module must fall back to CRUD until clarified.

---

## 7. Canonical Source-of-Truth Rules

### 7.1 CRUD modules
Source of truth:
- relational aggregate tables

Allowed supplements:
- audit log
- change history
- derived caches
- search indexes

But these supplements do not replace the aggregate as primary truth.

### 7.2 EVENT_FIRST modules
Source of truth:
- immutable fact/event store

Allowed projections:
- read models
- dashboards
- summaries
- current-state materializations

But these projections must be rebuildable or at least traceable to facts.

### 7.3 HYBRID modules
Source of truth:
- split by concept

Example:
In `training`:
- session schedule/status = relational aggregate
- attendance marks and execution facts = append-only event stream

Hybrid modules MUST document this split explicitly.

---

## 8. Forbidden Patterns

The following are forbidden.

### 8.1 Global Event Sourcing by ideology
Do not force all modules into event sourcing for conceptual uniformity.

### 8.2 Mutable summaries as historical truth
Do not overwrite history in modules where fact sequence is product-relevant.

### 8.3 Event streams with no consumer
Do not create append-only streams that no feature, projection or audit need actually uses.

### 8.4 Mixed truth with no ownership
Do not keep the same concept half-authoritative in table state and half-authoritative in event logs without explicit priority rules.

### 8.5 Analytics-as-truth
Do not promote derived analytics outputs to primary source-of-truth for raw sports facts.

### 8.6 Sensitive inference without provenance
Do not persist psychological/wellbeing inference outputs without provenance, version context and review policy.

---

## 9. Required Cross-Module Rules

### 9.1 audit is always append-only
Any module may emit to `audit`, but cannot mutate past audit facts.

### 9.2 notifications are fact logs
Any module may trigger notifications, but notification delivery history belongs to `notifications` as factual attempts/events.

### 9.3 projections are never primary truth
No projection table may become the canonical source unless explicitly promoted by a separate decision record.

### 9.4 imports/ingestion preserve provenance
When external data enters HB Track, the ingestion layer must preserve source/provenance even if the operational layer stores normalized state.

---

## 10. Event Schema Minimum Requirements

For every EVENT_FIRST or HYBRID append-only fact, the stored record SHOULD include at minimum:

- event_id
- event_type
- aggregate_type
- aggregate_id
- occurred_at
- recorded_at
- actor_type
- actor_id
- source_type
- source_system
- source_record_id
- payload_version
- payload
- correlation_id (when applicable)
- causation_id (when applicable)

Sensitive domains SHOULD additionally include:
- review_status
- reviewer_id (if human-reviewed)
- model_name / model_version (if AI-derived)
- confidence_level (if probabilistic)
- access_classification

---

## 11. Migration Policy

### 11.1 CRUD -> HYBRID
Allowed when:
- a previously CRUD module begins producing facts with replay/audit/analytics value
- clear fact boundaries are defined
- old state model remains valid for operational current state

### 11.2 HYBRID -> EVENT_FIRST
Allowed only with explicit architecture decision because this changes primary truth semantics.

### 11.3 EVENT_FIRST -> CRUD
Strongly discouraged.
Only allowed if:
- event-first adoption was premature
- replay/projection value proved nonexistent
- migration path preserves required historical evidence

---

## 12. Review Gate for New Modules

Every new HB Track module MUST declare one of:
- CRUD
- EVENT_FIRST
- HYBRID

And MUST answer:
1. What is the canonical source of truth?
2. Does fact sequence matter?
3. Are projections required?
4. Is replay needed?
5. What is mutable state vs immutable fact?
6. Does the module process sensitive data?

A module definition is incomplete without these answers.

---

## 13. Recommended Initial Canonical Set for HB Track

### 13.1 CRUD
- identity_access
- organizations
- teams
- athletes
- staff
- categories
- venues
- session_templates
- planning_periodization
- attachments
- billing
- settings
- integrations
- tasks_workflow

### 13.2 EVENT_FIRST
- matches
- scouts
- analytics
- audit
- notifications
- ingestion
- projections
- attendance

### 13.3 HYBRID
- training
- competitions
- performance
- reports
- video
- dashboard
- comments_feedback
- exports_imports
- wellbeing
- medical_health_adjacent
- psychology_support_ai

---

## 14. Operational Consequences

### 14.1 For backend
- repositories and services must respect module persistence class
- no generic repository pattern should flatten CRUD and EVENT_FIRST semantics into the same abstraction

### 14.2 For frontend
- current-state screens may consume aggregate DTOs
- timeline, analytics and video-tagging screens should prefer projection/view endpoints derived from facts

### 14.3 For analytics
- derived metrics must reference stable raw facts, not only mutable summaries

### 14.4 For governance
- ARs and module contracts must declare persistence class explicitly
- parity checks should validate that implementation matches declared class

---

## 15. Definition of Done

This policy is DONE only when:
- every canonical module has an assigned persistence class
- module contracts reflect the assigned class
- new modules cannot be created without classification
- event-first/hybrid modules define minimum fact schema
- sensitive modules define governance overlays
- architectural review uses this policy as a blocking reference
```