# INGESTION_PROVIDER_CONTRACT.md

version: 1.0.0
status: PENDENTE
decision_type: integration_contract
scope: hb_track
owners:
  - architecture
  - backend
  - data
  - analytics
  - ai
related_decisions:
  - HB_TRACK_ARCHITECTURE_DECISION.md
  - HB_TRACK_PERSISTENCE_POLICY.md
related_modules:
  - ingestion
  - integrations
  - matches
  - scouts
  - training
  - analytics
  - video
  - reports
  - wellbeing
  - notifications
  - audit
related_artifacts:
  - docs/_ssot/openapi.json
  - docs/_ssot/schema.sql
  - docs/_canon/MANUAL_BACKEND_CANONICO.md
  - docs/_canon/REGRAS_SISTEMAS.md

---

## 1. Objective

Define the canonical ingestion contract for all data entering HB Track from any non-primary-domain source.

This contract exists to ensure that HB Track can ingest data from:
- external sports/statistics providers
- competition/federation feeds
- manual coach/staff input
- CSV/spreadsheet imports
- video-derived tagging pipelines
- AI/computer-vision pipelines
- future partner integrations

without coupling:
- domain rules
- API DTOs
- UI ViewModels
- analytics pipelines
- internal persistence model

to raw external payload shapes.

---

## 2. Core Decision

HB Track SHALL implement a canonical ingestion layer between all external or semi-structured inputs and all internal domain/application layers.

This ingestion layer SHALL:
- preserve provenance
- preserve temporal context
- preserve normalization metadata
- preserve confidence semantics when applicable
- isolate provider-specific schema drift
- output normalized internal records

HB Track SHALL NOT allow downstream modules to depend directly on provider-native field names or payload structures unless explicitly promoted into the canonical ingestion contract.

---

## 3. Ingestion Scope

The ingestion contract applies to any input whose source of truth is not already the canonical HB Track domain model.

This includes:
- official provider feeds
- manual operational entry that represents imported/observed facts
- CV/AI extracted detections
- bulk imports
- webhook/event partner payloads
- spreadsheet-based uploads
- sensor/device integrations
- message-based asynchronous integrations

This contract does NOT replace:
- domain contracts
- public API DTO contracts
- frontend ViewModel contracts

It is an internal normalization boundary.

---

## 4. Canonical Source Categories

Every ingested record MUST declare a `source_type`.

Allowed canonical values:

- `external_provider`
- `manual_staff_entry`
- `manual_coach_entry`
- `manual_athlete_entry`
- `video_annotation`
- `ai_cv_extraction`
- `spreadsheet_import`
- `csv_import`
- `federation_feed`
- `partner_webhook`
- `system_sync`
- `legacy_migration`
- `sensor_device`
- `other_controlled`

No other value is allowed unless added by explicit contract revision.

---

## 5. Ingestion Design Principles

### 5.1 Provenance is mandatory
No ingested record may become canonical internal data without preserving where it came from.

### 5.2 Normalization is explicit
Normalization is not an informal mapper. It is a contract-governed transformation boundary.

### 5.3 Raw payload is not domain truth
Raw provider payloads are evidence inputs, not automatically domain-valid truth.

### 5.4 Confidence is first-class when probabilistic
If data comes from AI/CV/inference/probabilistic extraction, confidence must be explicit.

### 5.5 Temporal context matters
Observed time and ingestion time must not be conflated.

### 5.6 Domain promotion is controlled
A field only becomes an internal canonical field after explicit mapping and validation rules.

### 5.7 Idempotency is mandatory
Duplicate arrivals of the same external fact must be detectable or governable.

### 5.8 Sensitive-domain controls propagate
If ingested data enters a sensitive domain, classification and access constraints must travel with it.

---

## 6. Canonical Ingestion Record Schema

Every ingested record MUST conform to the following logical structure.

```yaml
ingestion_record:
  ingestion_id: string
  source_type: enum
  source_system: string
  source_record_id: string | null
  source_endpoint: string | null
  source_batch_id: string | null
  source_file_name: string | null
  source_file_checksum: string | null
  source_event_type: string | null
  source_schema_version: string | null

  observed_at: datetime | null
  occurred_at: datetime | null
  ingested_at: datetime
  processed_at: datetime | null

  entity_kind: string
  entity_external_key: string | null
  aggregate_hint: string | null

  normalization_status: enum
  normalization_version: string
  mapping_profile: string | null

  confidence_level: decimal | null
  confidence_label: string | null
  review_status: enum | null

  access_classification: enum
  sensitivity_class: enum

  payload_raw: object | string | null
  payload_normalized: object
  payload_fingerprint: string

  correlation_id: string | null
  causation_id: string | null
  trace_id: string | null

  actor_type: string | null
  actor_id: string | null

  validation_status: enum
  validation_errors: array
  warnings: array

  dedupe_key: string | null
  idempotency_key: string | null

  retained_until: datetime | null
  deleted_at: datetime | null
````

---

## 7. Required Field Semantics

### 7.1 Identity and traceability fields

#### `ingestion_id`

Internal immutable identifier for the ingestion record.

Rule:

* MUST be unique
* MUST never be recycled
* MUST identify one normalized ingestion record

#### `source_system`

Human-meaningful controlled identifier for the upstream source.

Examples:

* `sportradar`
* `manual_coach_ui`
* `video_tagger_v1`
* `csv_roster_import`
* `federation_feed_cbhb`
* `open_cv_detector_v2`

#### `source_record_id`

Original upstream record identifier when available.

Rule:

* MUST be preserved exactly when supplied
* MAY be null when the source does not provide one

#### `payload_fingerprint`

Deterministic fingerprint of the normalized or relevant raw payload used for dedupe/trace purposes.

Rule:

* MUST be stable under identical input canonicalization rules

---

### 7.2 Temporal fields

#### `observed_at`

When the fact was observed in the real world or source context.

#### `occurred_at`

When the event/fact actually happened, if distinct from observation time.

#### `ingested_at`

When HB Track received the data.

#### `processed_at`

When normalization/validation processing completed.

Rule:

* `ingested_at` is mandatory
* `observed_at` and `occurred_at` must not be silently inferred as the same value unless mapping rules explicitly state so

---

### 7.3 Classification fields

#### `entity_kind`

Canonical kind of record being ingested.

Examples:

* `match_event`
* `training_attendance_fact`
* `athlete_registry_record`
* `video_annotation`
* `wellbeing_signal`
* `scout_observation`
* `report_generation_trigger`

#### `aggregate_hint`

Optional hint of the internal aggregate likely affected.

Examples:

* `match`
* `training_session`
* `athlete`
* `competition`
* `video_asset`

Rule:

* hint is advisory, not authoritative domain truth

---

### 7.4 Normalization fields

#### `normalization_status`

Allowed values:

* `pending`
* `normalized`
* `rejected`
* `quarantined`
* `partially_normalized`

#### `normalization_version`

Version of the normalization contract or mapping logic applied.

#### `mapping_profile`

Named mapping rule set used for this source/entity combination.

Examples:

* `sportradar_match_event_v1`
* `csv_athlete_roster_v2`
* `manual_training_attendance_v1`

Rule:

* any change in mapping semantics SHOULD increment `normalization_version` or mapping profile versioning

---

### 7.5 Confidence and review fields

#### `confidence_level`

Numeric confidence, required for probabilistic or inferred data.

Rule:

* MUST be null for deterministic/manual records unless explicitly meaningful
* MUST be present for AI/CV/inference-driven extracted facts when a probability/confidence exists

#### `confidence_label`

Controlled semantic bucket for confidence.

Allowed values:

* `very_low`
* `low`
* `medium`
* `high`
* `very_high`

#### `review_status`

Allowed values:

* `not_required`
* `pending_human_review`
* `reviewed_accepted`
* `reviewed_rejected`
* `reviewed_corrected`

Rule:

* AI-derived sensitive-domain records SHOULD default to `pending_human_review` when materially impactful

---

### 7.6 Access and sensitivity fields

#### `access_classification`

Allowed values:

* `public_internal`
* `restricted_staff`
* `restricted_coaching`
* `restricted_medical`
* `restricted_sensitive`
* `system_only`

#### `sensitivity_class`

Allowed values:

* `normal`
* `personal`
* `sensitive_health_adjacent`
* `sensitive_psychological`
* `sensitive_minor_related`
* `regulated_high_control`

Rule:

* classification must be assigned before downstream exposure

---

### 7.7 Validation and dedupe fields

#### `validation_status`

Allowed values:

* `valid`
* `invalid`
* `warning_only`
* `requires_review`

#### `dedupe_key`

Canonical deduplication key where supported.

#### `idempotency_key`

Key used to avoid duplicate processing side effects.

Rule:

* dedupe and idempotency are related but not identical
* both may be present

---

## 8. Raw vs Normalized Payload Rules

### 8.1 `payload_raw`

Represents the original inbound payload or essential raw excerpt.

Rule:

* SHOULD be preserved when legal, safe, and storage-appropriate
* MAY be omitted or redacted when sensitive-data minimization requires it
* MUST NOT be exposed directly to general frontend consumers

### 8.2 `payload_normalized`

Represents the canonical intermediate normalized structure produced by the ingestion layer.

Rule:

* MUST be the only payload shape consumed by downstream domain mapping layers
* MUST follow the approved mapping profile
* MUST not embed UI-specific formatting

### 8.3 Redaction rule

If raw payload contains sensitive or excessive fields not needed for downstream processing:

* redact before persistence, or
* store only controlled excerpts and secure trace metadata

---

## 9. Canonical Normalized Payload Shape

Each `payload_normalized` MUST be structured as:

```yaml
payload_normalized:
  schema_name: string
  schema_version: string
  entity_kind: string
  canonical_fields: object
  source_overrides: object | null
  provenance_summary:
    source_type: string
    source_system: string
    source_record_id: string | null
    observed_at: datetime | null
    confidence_level: decimal | null
  mapping_notes: array
```

Rules:

* `canonical_fields` contains only internal normalized fields
* `source_overrides` contains provider-specific residual fields that were not promoted to canonical fields but need controlled retention
* `mapping_notes` contains non-authoritative diagnostics, never business truth

---

## 10. Provider Abstraction Rules

### 10.1 No provider-native leakage

No downstream module may depend on:

* provider-native enum values
* provider-native field names
* provider-specific nesting structure
* provider-specific timestamp semantics

unless explicitly normalized first.

### 10.2 Controlled provider registry

Every source system must be registered in a controlled provider registry with:

* provider code
* provider display name
* auth model
* expected schemas
* supported entity kinds
* normalization owner
* risk notes

### 10.3 Coverage inequality handling

The ingestion contract MUST support partial coverage without breaking internal domain contracts.

Examples:

* provider supplies match events but not training data
* provider supplies competition metadata but not athlete-level details
* AI video extraction supplies candidate events with confidence, not verified facts

---

## 11. Manual Input as Ingestion

Manual operational input may also enter through the ingestion contract when it represents:

* externally observed facts
* imported legacy facts
* annotations tied to provenance
* staff-authored event observations
* coach video tags
* non-primary-source capture workflows

Rule:

* manual input that directly creates primary domain entities may bypass ingestion and use domain commands directly
* manual input that records observational facts SHOULD use ingestion semantics

Examples:

* creating a new team = domain command
* marking a historical match event from video review = ingestion fact
* uploading athlete roster CSV = ingestion flow
* tagging a tactical episode in video = ingestion fact

---

## 12. AI / CV Ingestion Rules

AI/CV-derived records are allowed only if they carry:

* `source_type = ai_cv_extraction`
* model identifier
* model version
* confidence metadata
* review policy
* provenance to video/source segment where applicable

Additional recommended fields inside `payload_normalized.canonical_fields` or `source_overrides`:

* `model_name`
* `model_version`
* `segment_start_ms`
* `segment_end_ms`
* `detection_type`
* `candidate_label`
* `review_required`

Rule:

* AI/CV output is not automatically equivalent to validated domain truth
* promotion into authoritative domain events must pass defined acceptance/review logic

---

## 13. Spreadsheet / CSV Import Rules

For CSV/spreadsheet imports, ingestion records MUST preserve:

* file name
* file checksum when feasible
* upload actor
* import batch id
* row number or row locator
* parser version
* mapping profile
* per-row validation results

Rule:

* batch-level success must not hide row-level failure
* row errors must be attributable and reviewable

Recommended row locator fields:

* `source_batch_id`
* `row_index`
* `sheet_name`
* `row_hash`

---

## 14. Federation / Official Feed Rules

Official or federation-origin data MUST still pass through normalization.

Rule:

* official source does not mean schema immunity
* official source increases trust, but does not remove provenance or validation requirements

Suggested metadata:

* competition authority
* feed publication timestamp
* officiality status
* amendment/correction sequence
* jurisdiction/scope

---

## 15. Sensitive-Domain Overlay

If ingested data touches:

* medical-health-adjacent data
* psychological/wellbeing data
* minors-related sensitive context
* protected personal observations

then the ingestion record MUST additionally include or derive:

* stricter `access_classification`
* stricter `sensitivity_class`
* retention control
* review boundary
* allowed-consumer policy
* exposure restrictions to analytics/dashboard layers

Rule:

* sensitive ingestion is allowed only if downstream usage policy exists
* no “collect now, govern later” behavior is permitted

---

## 16. Canonical Validation Pipeline

Every ingestion flow SHOULD implement these stages:

1. Receive
2. Identify source
3. Parse
4. Basic schema validation
5. Normalize
6. Enrich provenance
7. Classify sensitivity
8. Apply dedupe/idempotency checks
9. Validate canonical business constraints
10. Route:

* accept
* quarantine
* reject
* accept with warnings

11. Emit audit event
12. Publish for downstream consumption if accepted

---

## 17. Acceptance Outcomes

Allowed final routing outcomes:

* `accepted`
* `accepted_with_warnings`
* `quarantined`
* `rejected`
* `awaiting_review`

Definitions:

### `accepted`

Record is valid and can feed downstream processing.

### `accepted_with_warnings`

Record is usable but carries non-blocking issues.

### `quarantined`

Record is held due to unresolved integrity/sensitivity/review issues.

### `rejected`

Record is invalid and cannot proceed.

### `awaiting_review`

Record may be structurally valid but requires human decision before promotion.

---

## 18. Audit and Observability Rules

Every ingestion flow MUST emit auditable trail entries for:

* receipt
* normalization attempt
* validation result
* routing outcome
* downstream promotion decision if applicable

Recommended observability dimensions:

* source_system
* entity_kind
* mapping_profile
* normalization_version
* validation_status
* review_status
* processing_latency
* acceptance_outcome

---

## 19. Downstream Consumption Rules

### 19.1 Domain services

Consume normalized ingestion records, not raw payloads.

### 19.2 Analytics

Consume:

* authoritative promoted facts, or
* controlled ingestion facts explicitly allowed for analytics

Analytics must never silently mix:

* reviewed authoritative facts
* unreviewed AI candidates
* quarantined records

### 19.3 Frontend

Frontend must never consume ingestion records directly unless:

* an internal ops/review interface explicitly requires it
* access is authorized
* the view is designed as review tooling, not end-user product abstraction

---

## 20. Forbidden Patterns

The following are forbidden.

### 20.1 Raw payload direct-to-domain

No provider payload may be treated as domain model without normalization.

### 20.2 Raw payload direct-to-UI

No UI component may bind directly to ingestion raw payloads.

### 20.3 Silent confidence loss

No probabilistic source may be normalized into categorical truth while dropping confidence metadata.

### 20.4 Silent temporal collapse

Do not merge `occurred_at`, `observed_at`, and `ingested_at` into one field without explicit mapping rule.

### 20.5 Provider lock-in field naming

Do not promote provider-native names into internal canonical fields by convenience.

### 20.6 Sensitive-data accumulation without purpose

Do not preserve raw sensitive payload beyond what governance and product purpose justify.

### 20.7 Unreviewed AI truth promotion

Do not elevate AI/CV candidate facts into authoritative sensitive-domain truth without defined acceptance policy.

---

## 21. Example Canonical Mappings

### 21.1 External provider match event

```yaml
source_type: external_provider
source_system: sportradar
entity_kind: match_event
payload_normalized:
  schema_name: match_event_ingestion
  schema_version: 1.0.0
  entity_kind: match_event
  canonical_fields:
    external_match_id: "sr:match:123"
    event_code: "goal"
    team_external_id: "sr:competitor:456"
    athlete_external_id: "sr:player:789"
    occurred_at: "2026-03-10T20:13:00Z"
    period: 1
    clock_seconds: 754
```

### 21.2 Manual coach video tag

```yaml
source_type: manual_coach_entry
source_system: video_tagging_ui
entity_kind: video_annotation
payload_normalized:
  schema_name: video_annotation_ingestion
  schema_version: 1.0.0
  entity_kind: video_annotation
  canonical_fields:
    video_asset_id: "vid_001"
    segment_start_ms: 152000
    segment_end_ms: 164500
    tag_type: "defensive_transition_failure"
    authored_note: "late central recovery"
```

### 21.3 AI/CV detection candidate

```yaml
source_type: ai_cv_extraction
source_system: open_cv_detector_v2
entity_kind: candidate_match_event
confidence_level: 0.81
confidence_label: high
review_status: pending_human_review
payload_normalized:
  schema_name: candidate_match_event_ingestion
  schema_version: 1.0.0
  entity_kind: candidate_match_event
  canonical_fields:
    video_asset_id: "vid_001"
    segment_start_ms: 64000
    segment_end_ms: 66200
    candidate_label: "fast_break"
    model_name: "hb_cv_events"
    model_version: "2.4.1"
```

---

## 22. Promotion to Domain Truth

Ingestion records do not automatically become canonical domain truth.

Promotion requires:

* validation success
* mapping acceptance
* domain rule compatibility
* review if required
* proper source classification
* no blocking sensitivity or integrity issue

Promotion outcomes may include:

* create domain fact
* update aggregate
* create review task
* create audit entry only
* discard/reject
* quarantine for ops review

---

## 23. Review Gate for New Integrations

Every new provider/integration must define:

1. source_system code
2. supported source_type
3. supported entity kinds
4. raw payload examples
5. normalization mapping profile
6. dedupe strategy
7. idempotency strategy
8. confidence semantics if probabilistic
9. sensitivity classification rules
10. review rules
11. failure/quarantine handling
12. audit and observability hooks

A new integration is incomplete without these definitions.

---

## 24. Definition of Done

This contract is DONE only when:

* every integration source has a registered `source_system`
* normalization profiles exist for each supported source/entity kind pair
* ingestion records preserve provenance, timing, and validation outcome
* AI/CV flows preserve confidence and review status
* CSV/spreadsheet imports preserve batch and row traceability
* sensitive-domain ingestion applies classification before downstream exposure
* no downstream module depends directly on raw provider payloads
* audit trail exists for ingestion lifecycle

```


