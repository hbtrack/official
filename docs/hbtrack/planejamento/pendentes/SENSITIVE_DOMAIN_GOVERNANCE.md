# SENSITIVE_DOMAIN_GOVERNANCE.md

version: 1.0.0
status: PROPOSED
decision_type: governance_policy
scope: hb_track
owners:
  - architecture
  - backend
  - data
  - analytics
  - ai
  - security
  - compliance
related_decisions:
  - HB_TRACK_ARCHITECTURE_DECISION.md
  - HB_TRACK_PERSISTENCE_POLICY.md
  - INGESTION_PROVIDER_CONTRACT.md
  - DTO_VIEWMODEL_BOUNDARY_RULES.md
related_modules:
  - wellbeing
  - psychology_support_ai
  - medical_health_adjacent
  - athletes
  - analytics
  - reports
  - audit
  - notifications
  - identity_access
related_artifacts:
  - docs/_ssot/openapi.json
  - docs/_ssot/schema.sql
  - docs/_canon/MANUAL_BACKEND_CANONICO.md
  - docs/_canon/REGRAS_SISTEMAS.md

---

## 1. Objective

Define the canonical governance rules for any HB Track capability that handles, derives, stores, exposes, or operationalizes sensitive-domain information.

This policy exists to prevent:

- mixing sensitive inference with ordinary sports telemetry
- over-collection of high-risk personal data
- silent promotion of probabilistic inference into authoritative truth
- leakage of restricted data into dashboards, reports, exports, or notifications
- misuse of AI outputs in high-impact contexts
- architectural ambiguity about access, retention, provenance, and review boundaries

---

## 2. Core Decision

HB Track SHALL treat the following as sensitive-domain contexts whenever they are individually identifiable or reasonably linkable to a specific athlete, staff member, or minor:

- psychological / wellbeing observations
- emotional-state assessments
- health-adjacent observations
- mental readiness or distress indicators
- behavioral risk flags
- AI-derived individualized interpretations related to wellbeing, psychology, or health-adjacent status
- any score, category, alert, or trend that could materially affect how a person is evaluated, selected, restricted, escalated, or monitored

These contexts SHALL be governed as high-control domains.

They SHALL NOT be treated as ordinary analytics, convenience metadata, or generic athlete-profile enrichment.

---

## 3. Sensitive Domain Definitions

### 3.1 Sensitive-domain data

Sensitive-domain data includes any record, signal, label, flag, inference, comment, annotation, score, trend, or derived output that reveals or strongly suggests:

- mental or emotional condition
- psychological vulnerability
- health-adjacent concern
- distress, burnout, overload, instability, or behavioral risk
- protected personal context with elevated misuse risk
- individually attributable risk classification

Sensitive-domain data may be:
- human-authored
- system-derived
- AI-derived
- imported
- inferred from cross-signal combination

---

### 3.2 Sensitive-domain inference

Sensitive-domain inference means any system output that transforms inputs into an individualized interpretation such as:

- “at risk”
- “emotionally unstable”
- “burnout probability”
- “psychological readiness low”
- “attention decline”
- “stress elevated”
- “needs intervention”
- “high concern athlete”

A sensitive-domain inference remains sensitive even if probabilistic, approximate, advisory, or low-confidence.

---

### 3.3 High-impact use

A high-impact use exists when sensitive-domain data could influence:

- athlete selection or exclusion
- playing time or participation restriction
- disciplinary follow-up
- escalation to guardians/responsible adults
- referral for support
- coach or staff intervention
- reputational categorization
- longitudinal profiling

Any feature supporting these outcomes must use the strictest controls in this policy.

---

## 4. Governance Principles

### 4.1 Need-to-know only
Access to sensitive-domain data must be based on explicit operational need, not broad role convenience.

### 4.2 Minimal collection
Collect only the least amount of sensitive data necessary for the stated product use case.

### 4.3 Purpose limitation
Sensitive-domain data may only be processed for explicitly defined purposes.

### 4.4 Provenance over assumption
No sensitive-domain record may exist without provenance, origin classification, and author/source attribution.

### 4.5 Review before authority
Probabilistic or AI-derived sensitive outputs must not become authoritative truth without defined review policy.

### 4.6 Context separation
Sensitive-domain data must remain architecturally and semantically separate from general performance dashboards unless explicit policy allows bounded exposure.

### 4.7 Temporal honesty
The system must distinguish:
- observed fact
- authored interpretation
- AI-derived candidate inference
- reviewed conclusion

### 4.8 Human accountability
Where outputs may materially affect a person, the review boundary and accountable human role must be explicit.

---

## 5. Canonical Sensitive Classes

Every sensitive-domain record MUST declare a `sensitivity_class`.

Allowed canonical values:

- `sensitive_health_adjacent`
- `sensitive_psychological`
- `sensitive_minor_related`
- `regulated_high_control`

No weaker classification is allowed for this domain.

In addition, every such record MUST declare an `access_classification`.

Allowed canonical values:

- `restricted_medical`
- `restricted_sensitive`
- `system_only`

---

## 6. Allowed Sensitive-Domain Record Types

Sensitive-domain records MAY include only explicitly modeled types such as:

- `wellbeing_checkin_response`
- `psychological_observation_note`
- `health_adjacent_flag`
- `ai_wellbeing_candidate_inference`
- `reviewed_sensitive_alert`
- `sensitive_followup_recommendation`
- `guardian_contact_escalation_record`
- `sensitive_access_audit_event`

No ad hoc free-form storage bucket should exist for arbitrary sensitive data.

---

## 7. Data Categories by Authority Level

### 7.1 Observed fact
Examples:
- athlete submitted a wellbeing check-in
- coach recorded that athlete left session early
- athlete reported poor sleep in structured input

Authority:
- factual occurrence only
- does not authorize interpretive conclusion by itself

---

### 7.2 Human-authored interpretation
Examples:
- psychologist/staff note
- reviewed professional concern
- structured follow-up recommendation

Authority:
- interpretive but attributable
- must include author role, timestamp, and review context

---

### 7.3 AI-derived candidate inference
Examples:
- “elevated distress candidate”
- “possible overload pattern”
- “attention drop candidate”

Authority:
- advisory only
- never authoritative by default
- requires provenance, model metadata, and review status

---

### 7.4 Reviewed operational conclusion
Examples:
- reviewed recommendation for follow-up
- approved alert for restricted workflow
- accepted reviewed signal

Authority:
- depends on workflow and role policy
- must preserve the review trail that led to the conclusion

---

## 8. Source and Provenance Requirements

Every sensitive-domain record MUST carry at minimum:

- `record_id`
- `record_type`
- `source_type`
- `source_system`
- `source_record_id` when available
- `actor_type`
- `actor_id` when available
- `created_at`
- `observed_at` or `occurred_at` when relevant
- `sensitivity_class`
- `access_classification`
- `review_status`
- `provenance_summary`

If AI-derived, it MUST additionally carry:

- `model_name`
- `model_version`
- `confidence_level` if available
- `confidence_label` if available
- `input_scope_summary`
- `review_required`

---

## 9. Review Status Contract

Every sensitive-domain record MUST declare `review_status`.

Allowed values:

- `not_required`
- `pending_human_review`
- `reviewed_accepted`
- `reviewed_rejected`
- `reviewed_corrected`
- `expired_unreviewed`

Rules:

1. AI-derived sensitive records default to `pending_human_review`.
2. High-impact records cannot be operationalized while `pending_human_review`, unless a separate emergency policy explicitly exists.
3. `reviewed_corrected` must preserve both original and corrected interpretation.
4. `expired_unreviewed` records must not silently remain active in dashboards or alerts.

---

## 10. Access Control Rules

### 10.1 Least privilege
Only explicitly authorized roles may access sensitive-domain records.

### 10.2 Dual dimension access
Access must be evaluated by:
- role capability
- contextual scope

Examples of contextual scope:
- organization membership
- team assignment
- support assignment
- athlete relationship
- active case responsibility

### 10.3 Segmented access
Generic coaching roles must not automatically inherit access to psychological or health-adjacent detail.

### 10.4 Redaction by endpoint
Different endpoints may expose:
- full detail
- partial detail
- boolean alert only
- aggregated count only
- no access

### 10.5 Export restriction
Sensitive-domain export must be disabled by default and enabled only under explicit controlled policy.

---

## 11. Architectural Separation Rules

### 11.1 Separate bounded context
Sensitive-domain records should live in a separate bounded context or equivalent strict logical boundary.

### 11.2 No silent join into ordinary athlete profile
Sensitive-domain detail must not be merged into general athlete profile responses by convenience.

### 11.3 No generic dashboard contamination
General performance dashboards must not silently include sensitive-domain scores, flags, or inferred categories.

### 11.4 Explicit bridge endpoints only
If any dashboard or workflow needs a sensitive summary, it must use an endpoint designed for that specific exposure level.

---

## 12. DTO and ViewModel Exposure Rules

### 12.1 Explicit DTO only
Sensitive fields may appear only in DTOs explicitly designed and documented for sensitive access.

### 12.2 No leakage into generic DTO reuse
A generic `AthleteProfileDto`, `TrainingSessionDto`, or `DashboardDto` must not gain sensitive fields opportunistically.

### 12.3 ViewModels must preserve access boundaries
Frontend ViewModels must not merge restricted sensitive detail into non-sensitive views unless the endpoint and UI access policy explicitly authorize it.

### 12.4 Labels must not amplify authority
UI labels such as:
- “unstable”
- “problem athlete”
- “high risk”
- “red flag athlete”

are forbidden unless explicitly reviewed and justified by domain policy.

Prefer neutral and bounded wording such as:
- “review recommended”
- “follow-up pending”
- “sensitive status available to authorized staff”

---

## 13. Retention Rules

Every sensitive-domain record MUST define retention semantics.

Required fields:
- `retained_until` or equivalent policy reference
- `retention_basis`
- `deletion_mode`
- `legal_hold_flag` when applicable

Allowed deletion modes:
- `hard_delete_allowed`
- `soft_delete_with_audit`
- `immutable_record_with_access_revocation`

Rules:
1. No indefinite retention by accident.
2. Sensitive AI candidates that were rejected should have shorter retention unless policy requires otherwise.
3. Reviewed conclusions must preserve traceability where operationally required.
4. Deletion must not erase mandatory audit evidence of access and review actions.

---

## 14. Notification Rules

### 14.1 No raw sensitive payload in notifications
Notifications must never include raw sensitive details unless the delivery channel and access policy explicitly permit it.

### 14.2 Safer notification pattern
Notifications should carry minimal prompts such as:
- “A restricted follow-up item requires your review.”
- “A sensitive case update is available.”

### 14.3 Channel restriction
Sensitive-domain notifications must respect channel policy.
Uncontrolled channels must not receive sensitive content.

### 14.4 Recipient restriction
Notifications must be delivered only to authorized recipients with contextual scope.

---

## 15. Reporting and Analytics Rules

### 15.1 Sensitive analytics is separate by default
Sensitive-domain analytics must not be merged into ordinary performance analytics unless explicitly governed.

### 15.2 Aggregation threshold
Aggregated sensitive statistics should only be shown where re-identification risk is acceptably controlled.

### 15.3 No covert scoring
Do not derive covert composite scores that silently combine sensitive wellbeing/psychological signals with sports performance metrics.

### 15.4 Reviewed vs unreviewed segregation
Analytics must distinguish:
- reviewed sensitive records
- unreviewed AI candidates
- rejected records
- expired records

They must never be silently blended.

---

## 16. AI Governance Rules

### 16.1 AI outputs are advisory by default
Sensitive-domain AI outputs are candidates or recommendations, not authoritative truth.

### 16.2 Mandatory AI metadata
Every AI-derived sensitive output MUST include:
- model name
- model version
- generation timestamp
- input scope summary
- confidence metadata when applicable
- review requirement
- explanation summary if available and safe to expose

### 16.3 No irreversible workflow trigger by AI alone
AI output must not by itself:
- restrict participation
- label a person negatively
- create permanent status
- trigger disciplinary action
- notify guardians with sensitive detail
- alter athlete profile classification permanently

unless a reviewed policy explicitly authorizes that workflow and preserves accountability.

### 16.4 Training-data firewall
Sensitive-domain outputs must not be reused as generic product telemetry without explicit governance.

---

## 17. Minor Protection Rules

If the subject is a minor or minor-related context exists, the system MUST apply stricter control.

Required considerations:
- narrower access scope
- stricter notification policy
- guardian/escalation workflow controls
- stricter retention review
- stronger audit expectations

Minor-related sensitive data must never be exposed in convenience dashboards, broad exports, or loosely controlled messaging flows.

---

## 18. Audit Requirements

Every sensitive-domain lifecycle action MUST be auditable.

Auditable actions include:
- create
- read
- update
- review
- reject
- correct
- export attempt
- notification dispatch
- escalation action
- deletion or access revocation

Audit records must include:
- actor identity
- actor role
- timestamp
- action type
- target record
- outcome
- contextual reason when available

Sensitive audit logs themselves may require restricted access, but they must exist.

---

## 19. Canonical Workflow States

Recommended canonical workflow for sensitive-domain records:

1. received
2. classified
3. validated
4. access-scoped
5. review_pending
6. reviewed_accepted / reviewed_rejected / reviewed_corrected
7. operationalized if allowed
8. retained / archived / deleted according to policy

No record should jump from ingestion to operationalized high-impact use without passing the required review gate.

---

## 20. Forbidden Patterns

The following are forbidden.

### 20.1 Sensitive-by-inference but unsafely labeled as normal
Do not store individualized distress or psychological interpretation as ordinary analytics metadata.

### 20.2 AI truth promotion without review
Do not treat sensitive AI inference as authoritative fact without defined review policy.

### 20.3 Sensitive detail in generic DTOs
Do not leak sensitive fields into generic athlete, match, training, or dashboard transport contracts.

### 20.4 Broad-role visibility
Do not expose sensitive detail to all coaches, all staff, or all admins by convenience.

### 20.5 Notification oversharing
Do not send detailed sensitive content through uncontrolled notification channels.

### 20.6 Composite opaque scoring
Do not compute hidden athlete scores mixing psychological/wellbeing signals with performance metrics without explicit governance and disclosure.

### 20.7 Silent retention
Do not keep rejected, expired, or low-value sensitive candidates forever without policy.

### 20.8 Destructive overwrite of interpretive history
Do not overwrite reviewed conclusions or authored notes without preserving correction history.

---

## 21. Review Checklist for New Sensitive Features

Every new sensitive-domain feature must answer:

1. What exact sensitive data category is involved?
2. Is the feature observational, interpretive, or inferential?
3. Is AI involved?
4. What is the operational purpose?
5. What is the highest-impact possible outcome?
6. Who can access it and under what contextual scope?
7. What DTOs expose it?
8. What notifications can mention it?
9. What is the review gate?
10. What is the retention policy?
11. What audit events are emitted?
12. Can the same goal be achieved with less sensitive data?

If these answers are incomplete, the feature is not governance-ready.

---

## 22. Example Exposure Levels

### 22.1 Full restricted detail endpoint
Audience:
- explicitly authorized support role

Possible content:
- reviewed note
- provenance
- review history
- restricted recommendations

### 22.2 Limited coaching alert endpoint
Audience:
- authorized coach with need-to-know

Possible content:
- `followUpRecommended = true`
- `reviewStatus = reviewed_accepted`
- no detailed note body
- no raw inference rationale

### 22.3 Generic dashboard
Audience:
- broad operational user set

Possible content:
- none by default

If explicitly allowed:
- count of pending restricted items for authorized reviewer only

---

## 23. Example Record Shape

```yaml
sensitive_record:
  record_id: "sens_001"
  record_type: "ai_wellbeing_candidate_inference"
  subject_type: "athlete"
  subject_id: "ath_123"

  source_type: "ai_cv_extraction"
  source_system: "hb_wellbeing_model"
  source_record_id: "pred_889"

  created_at: "2026-03-11T18:30:00Z"
  observed_at: "2026-03-11T18:20:00Z"

  sensitivity_class: "sensitive_psychological"
  access_classification: "restricted_sensitive"

  review_status: "pending_human_review"
  review_required: true

  model_name: "hb_wellbeing_model"
  model_version: "1.2.0"
  confidence_level: 0.77
  confidence_label: "medium"

  provenance_summary:
    input_scope: "structured_checkin + recent workload indicators"
    generation_context: "pre-training screening"

  payload:
    candidate_label: "follow_up_recommended"
    rationale_summary: "pattern indicates possible overload-related concern"

  retained_until: "2026-06-11T00:00:00Z"
  retention_basis: "candidate_sensitive_inference_policy_v1"
````

---

## 24. Integration Rules with Other Contracts

### 24.1 With ingestion contract

Sensitive-domain records must inherit:

* provenance
* source classification
* normalization status
* review semantics

### 24.2 With DTO/ViewModel boundary rules

Sensitive exposure must use dedicated DTOs and bounded ViewModels only.

### 24.3 With persistence policy

Sensitive modules are typically HYBRID / RESTRICTED:

* relational current workflow state where needed
* append-only reviewed facts and audit trail where history matters

### 24.4 With notifications

Notifications must carry only minimal action prompts unless a stricter approved channel exists.

---

## 25. Definition of Done

This policy is DONE only when:

* every sensitive-domain feature declares sensitivity class and access classification
* AI-derived sensitive records always carry review status and model provenance
* sensitive fields are exposed only through explicit DTOs
* generic dashboards do not silently include sensitive signals
* notification templates do not leak raw sensitive content
* retention and deletion semantics exist for sensitive records
* all reads and review actions are auditable
* minor-related sensitive handling applies stricter controls
* no high-impact operational action occurs from unreviewed AI output alone

```