# SENSITIVE_DOMAIN_WORKFLOWS.md

version: 1.0.0
status: PENDENTE
decision_type: operational_workflow_policy
scope: hb_track
owners:
  - architecture
  - backend
  - analytics
  - ai
  - security
  - compliance
related_decisions:
  - HB_TRACK_ARCHITECTURE_DECISION.md
  - HB_TRACK_PERSISTENCE_POLICY.md
  - INGESTION_PROVIDER_CONTRACT.md
  - DTO_VIEWMODEL_BOUNDARY_RULES.md
  - SENSITIVE_DOMAIN_GOVERNANCE.md
related_modules:
  - wellbeing
  - psychology_support_ai
  - medical_health_adjacent
  - audit
  - notifications
  - identity_access
  - reports
  - analytics

---

## 1. Objective

Define the canonical operational workflows for sensitive-domain records in HB Track.

This document exists to operationalize the governance rules into explicit flows with:

- states
- actors
- transitions
- gates
- review requirements
- exposure levels
- side effects
- audit obligations

Without these workflows, sensitive-domain governance remains theoretical and non-enforceable.

---

## 2. Core Decision

No sensitive-domain record may move directly from creation or ingestion to high-impact operational use without passing through an explicitly defined workflow.

Every workflow MUST define:

- input origin
- record type
- state machine
- authorized actors
- review gate
- allowed side effects
- audit events
- exposure rules
- terminal outcomes

---

## 3. Canonical Workflow Families

HB Track SHALL support the following sensitive-domain workflow families:

1. `wellbeing_checkin_workflow`
2. `human_sensitive_observation_workflow`
3. `ai_sensitive_candidate_inference_workflow`
4. `reviewed_sensitive_alert_workflow`
5. `guardian_or_responsible_escalation_workflow`
6. `sensitive_export_request_workflow`
7. `sensitive_record_correction_workflow`
8. `sensitive_retention_disposition_workflow`

No new sensitive workflow should be created without explicit contract addition.

---

## 4. Canonical Global States

The following state vocabulary is canonical across sensitive workflows where applicable.

Allowed states:

- `received`
- `classified`
- `validated`
- `quarantined`
- `review_pending`
- `under_review`
- `reviewed_accepted`
- `reviewed_rejected`
- `reviewed_corrected`
- `approved_for_limited_exposure`
- `approved_for_restricted_action`
- `operationalized`
- `expired_unreviewed`
- `archived`
- `deleted`
- `access_revoked`

Not every workflow must use all states, but no ad hoc synonyms should be introduced without reason.

---

## 5. Actor Classes

Every transition must be attributable to an actor class.

Allowed actor classes:

- `system`
- `authorized_coach`
- `authorized_support_staff`
- `authorized_sensitive_reviewer`
- `medical_or_health_adjacent_reviewer`
- `psychology_or_wellbeing_reviewer`
- `compliance_or_security_reviewer`
- `guardian_or_responsible_contact`
- `athlete_self`
- `admin_limited`
- `integration_source`

Rules:
- broad `admin` authority is not automatically sufficient for sensitive review
- the workflow must declare which actor classes can perform which transition

---

## 6. Transition Contract

Every workflow transition MUST define:

- `from_state`
- `to_state`
- `trigger`
- `allowed_actor_classes`
- `preconditions`
- `side_effects`
- `audit_event`
- `exposure_change`
- `notes`

A transition is invalid if any of these are missing.

---

## 7. Workflow 1 — Wellbeing Check-In

### 7.1 Purpose

Handle structured self-reported or staff-assisted wellbeing check-in submissions.

### 7.2 Input examples

- athlete submits structured check-in
- staff records structured response during support interaction
- pre-training readiness form

### 7.3 Record types

- `wellbeing_checkin_response`
- `health_adjacent_flag`
- `sensitive_followup_recommendation` if derived later

### 7.4 State machine

`received`
-> `classified`
-> `validated`
-> (`review_pending` if sensitive interpretation required)
-> (`approved_for_limited_exposure` OR `reviewed_accepted` OR `reviewed_rejected`)
-> `archived`

### 7.5 Rules

1. Raw response submission is not automatically an alert.
2. Structured responses may be stored as observed fact.
3. Any interpretive conclusion derived from the response requires review if it enters sensitive workflow.
4. Generic dashboards must not receive raw detail by default.

### 7.6 Example transitions

#### T1
- from_state: `received`
- to_state: `classified`
- trigger: submission accepted
- allowed_actor_classes: `system`
- preconditions:
  - source identified
  - subject identified
- side_effects:
  - assign sensitivity class
  - assign access classification
- audit_event: `sensitive_record_classified`
- exposure_change: none

#### T2
- from_state: `classified`
- to_state: `validated`
- trigger: schema and policy validation pass
- allowed_actor_classes: `system`
- preconditions:
  - required fields present
- side_effects:
  - store validated structured response
- audit_event: `sensitive_record_validated`
- exposure_change: none

#### T3
- from_state: `validated`
- to_state: `review_pending`
- trigger: system identifies need for human review
- allowed_actor_classes: `system`
- preconditions:
  - response matches review threshold policy
- side_effects:
  - create restricted review task
- audit_event: `sensitive_review_requested`
- exposure_change:
  - restricted reviewers can see pending item count

---

## 8. Workflow 2 — Human Sensitive Observation

### 8.1 Purpose

Handle human-authored sensitive observations or notes.

### 8.2 Input examples

- authorized staff note
- restricted coach observation requiring protected handling
- support note tied to an athlete or minor-related concern

### 8.3 Record types

- `psychological_observation_note`
- `health_adjacent_flag`
- `reviewed_sensitive_alert`

### 8.4 State machine

`received`
-> `classified`
-> `validated`
-> `under_review` or directly `reviewed_accepted` depending on policy
-> `approved_for_restricted_action` or `archived`

### 8.5 Rules

1. Author identity is mandatory.
2. Free-text notes are allowed only in controlled record types.
3. The original note must remain preserved if later corrected.
4. Detail exposure must remain restricted.

### 8.6 High-control transition

#### T-H1
- from_state: `validated`
- to_state: `under_review`
- trigger: note marked as high-impact or sensitive_psychological
- allowed_actor_classes: `system`
- preconditions:
  - author attribution exists
- side_effects:
  - lock broad visibility
  - route to restricted reviewer queue
- audit_event: `sensitive_note_sent_for_review`
- exposure_change:
  - access limited to reviewer cohort

---

## 9. Workflow 3 — AI Sensitive Candidate Inference

### 9.1 Purpose

Handle any AI-generated sensitive candidate inference.

### 9.2 Input examples

- candidate distress inference
- overload-related concern candidate
- low readiness candidate
- behavior-risk candidate

### 9.3 Record types

- `ai_wellbeing_candidate_inference`

### 9.4 State machine

`received`
-> `classified`
-> `validated`
-> `review_pending`
-> (`reviewed_accepted` OR `reviewed_rejected` OR `reviewed_corrected`)
-> (`approved_for_limited_exposure` OR `approved_for_restricted_action`)
-> `archived`

### 9.5 Hard rules

1. AI sensitive records always start as non-authoritative.
2. They always require review before operational use.
3. They may never directly trigger high-impact action.
4. Rejected AI candidates must remain auditable but should not remain active.
5. Reviewed-corrected must preserve original candidate and corrected conclusion.

### 9.6 Canonical gates

#### Gate A — Provenance Gate
Must verify:
- model name
- model version
- generation timestamp
- input scope summary
- subject identity binding
- confidence metadata if available

Failure outcome:
- `quarantined`

#### Gate B — Review Gate
Must verify:
- authorized reviewer identity
- review outcome
- rationale summary
- exposure decision
- action eligibility

Without Gate B passing:
- no alert
- no dashboard exposure beyond restricted pending count
- no notification to coach/guardian
- no participation restriction

### 9.7 Example transitions

#### T-AI1
- from_state: `validated`
- to_state: `review_pending`
- trigger: candidate inference stored
- allowed_actor_classes: `system`
- preconditions:
  - Gate A passed
- side_effects:
  - create review task
  - suppress general exposure
- audit_event: `ai_sensitive_candidate_pending_review`
- exposure_change:
  - restricted reviewers may see queue entry only

#### T-AI2
- from_state: `review_pending`
- to_state: `reviewed_accepted`
- trigger: reviewer accepts candidate as valid concern
- allowed_actor_classes:
  - `authorized_sensitive_reviewer`
  - `psychology_or_wellbeing_reviewer`
- preconditions:
  - reviewer authorized
  - rationale provided
- side_effects:
  - create reviewed conclusion
  - preserve original candidate
- audit_event: `ai_sensitive_candidate_reviewed_accepted`
- exposure_change:
  - eligible for restricted downstream exposure

#### T-AI3
- from_state: `review_pending`
- to_state: `reviewed_rejected`
- trigger: reviewer rejects candidate
- allowed_actor_classes:
  - `authorized_sensitive_reviewer`
  - `psychology_or_wellbeing_reviewer`
- preconditions:
  - reviewer authorized
- side_effects:
  - deactivate candidate from operational views
- audit_event: `ai_sensitive_candidate_reviewed_rejected`
- exposure_change:
  - no dashboard detail
  - no notification

#### T-AI4
- from_state: `review_pending`
- to_state: `reviewed_corrected`
- trigger: reviewer corrects or reframes candidate
- allowed_actor_classes:
  - `authorized_sensitive_reviewer`
  - `psychology_or_wellbeing_reviewer`
- preconditions:
  - reviewer rationale recorded
- side_effects:
  - preserve original candidate
  - create corrected reviewed record
- audit_event: `ai_sensitive_candidate_reviewed_corrected`
- exposure_change:
  - depends on corrected exposure class

---

## 10. Workflow 4 — Reviewed Sensitive Alert

### 10.1 Purpose

Operationalize only reviewed and approved sensitive concerns into constrained alerts.

### 10.2 Record types

- `reviewed_sensitive_alert`
- `sensitive_followup_recommendation`

### 10.3 State machine

`reviewed_accepted`
or `reviewed_corrected`
-> `approved_for_limited_exposure`
or `approved_for_restricted_action`
-> `operationalized`
-> `archived`

### 10.4 Rules

1. A reviewed conclusion does not automatically mean broad visibility.
2. Exposure level must be chosen explicitly.
3. Alert wording must be neutral and bounded.
4. Raw rationale should remain behind restricted access.
5. Notification payloads must be minimal.

### 10.5 Exposure levels

Allowed exposure levels:

- `none`
- `reviewer_only`
- `restricted_support_only`
- `limited_coaching_signal`
- `guardian_escalation_candidate`

No other exposure level allowed without explicit revision.

### 10.6 Transition example

#### T-AL1
- from_state: `reviewed_accepted`
- to_state: `approved_for_limited_exposure`
- trigger: reviewer authorizes limited coaching signal
- allowed_actor_classes:
  - `authorized_sensitive_reviewer`
  - `psychology_or_wellbeing_reviewer`
- preconditions:
  - exposure rationale exists
  - endpoint policy exists
- side_effects:
  - create limited exposure alert artifact
- audit_event: `sensitive_alert_approved_for_limited_exposure`
- exposure_change:
  - authorized coach can see bounded signal only

---

## 11. Workflow 5 — Guardian or Responsible Escalation

### 11.1 Purpose

Govern any escalation to guardians or responsible adults in minor-related sensitive scenarios.

### 11.2 State machine

`reviewed_accepted`
or `reviewed_corrected`
-> `guardian_escalation_candidate`
-> (`approved_for_restricted_action` OR `reviewed_rejected`)
-> `operationalized`
-> `archived`

### 11.3 Hard rules

1. Minor-related context must be explicit.
2. Escalation must not be triggered by AI candidate alone.
3. Channel and recipient must be verified.
4. Content must be minimized.
5. Every escalation must be auditable.

### 11.4 Required preconditions

- subject identified as minor-related case if applicable
- reviewer authorization exists
- escalation policy basis exists
- approved recipient exists
- approved channel exists
- wording template is controlled

### 11.5 Forbidden action

No raw model output, confidence score, or speculative rationale should be sent to guardians directly.

---

## 12. Workflow 6 — Sensitive Export Request

### 12.1 Purpose

Control export of sensitive-domain records.

### 12.2 State machine

`received`
-> `under_review`
-> (`approved_for_restricted_action` OR `reviewed_rejected`)
-> `operationalized`
-> `archived`

### 12.3 Rules

1. Export is denied by default.
2. Export requires explicit purpose, scope, actor, and format review.
3. Bulk export requires stricter justification.
4. Export artifact must be logged.
5. Access to exported artifact must be bounded and time-limited where possible.

### 12.4 Required request fields

- requestor identity
- requestor role
- purpose
- requested scope
- record count estimate
- output format
- retention of export artifact
- destination/channel

---

## 13. Workflow 7 — Sensitive Record Correction

### 13.1 Purpose

Correct a sensitive record without destroying interpretive history.

### 13.2 State machine

`reviewed_accepted`
or `reviewed_corrected`
-> `under_review`
-> `reviewed_corrected`
-> `archived`

### 13.3 Rules

1. Original record must remain preserved.
2. Correction must reference corrected target.
3. Reason for correction is mandatory.
4. Exposure artifacts derived from original record must be re-evaluated.
5. Notifications may need revocation or replacement.

### 13.4 Side effects

Possible side effects:
- create superseding reviewed record
- revoke previous limited alert
- notify restricted reviewers of correction
- mark downstream derived artifacts stale

---

## 14. Workflow 8 — Retention and Disposition

### 14.1 Purpose

Dispose of or archive sensitive records according to policy.

### 14.2 State machine

`archived`
-> (`deleted` OR `access_revoked`)

### 14.3 Rules

1. No indefinite silent retention.
2. Rejected AI candidates should usually be dispositioned earlier than reviewed accepted conclusions.
3. Deletion must not erase mandatory audit evidence.
4. Access revocation may be used where immutable evidence must remain.

### 14.4 Required checks

- retention basis exists
- legal hold evaluated
- linked workflows resolved
- downstream exposure artifacts deactivated
- audit trail preserved

---

## 15. Quarantine Workflow

### 15.1 Purpose

Hold records with broken provenance, failed validation, suspicious source properties, or policy ambiguity.

### 15.2 Entry conditions

A sensitive record must go to `quarantined` if any of the following is true:

- missing provenance
- missing sensitivity/access classification
- missing subject binding where required
- invalid model metadata for AI records
- failed validation
- unapproved source system
- policy conflict
- corrupted or partial payload

### 15.3 Quarantine exit paths

`quarantined`
-> `review_pending`
-> `reviewed_rejected`
-> `deleted`
-> `archived`

### 15.4 Rules

No quarantined record may be exposed operationally.

---

## 16. Side Effects Catalog

Allowed side effects must be declared per workflow.

Allowed side effect categories:

- `create_restricted_review_task`
- `emit_audit_event`
- `create_limited_alert`
- `send_minimal_notification`
- `mark_dashboard_pending_count`
- `revoke_alert`
- `archive_record`
- `apply_access_revocation`
- `create_guardian_escalation_case`
- `create_export_artifact`
- `mark_downstream_projection_stale`

Forbidden side effects for unreviewed AI sensitive records:

- participation restriction
- broad dashboard flag
- guardian notification
- negative permanent classification
- unrestricted report inclusion
- generic coach broadcast

---

## 17. Audit Events

Every workflow transition MUST emit an audit event.

Canonical audit event names include:

- `sensitive_record_received`
- `sensitive_record_classified`
- `sensitive_record_validated`
- `sensitive_record_quarantined`
- `sensitive_review_requested`
- `sensitive_review_started`
- `sensitive_review_completed`
- `sensitive_record_reviewed_accepted`
- `sensitive_record_reviewed_rejected`
- `sensitive_record_reviewed_corrected`
- `sensitive_alert_approved`
- `sensitive_alert_operationalized`
- `sensitive_export_requested`
- `sensitive_export_approved`
- `sensitive_export_rejected`
- `sensitive_record_archived`
- `sensitive_record_deleted`
- `sensitive_access_revoked`

---

## 18. Notification Policy by State

### 18.1 Allowed notifications

`review_pending`
- allowed recipients:
  - restricted reviewers
- content:
  - minimal queue/update prompt

`approved_for_limited_exposure`
- allowed recipients:
  - authorized coach or support role with contextual scope
- content:
  - bounded action recommendation only

`guardian_escalation_candidate`
- no direct guardian notification yet

`approved_for_restricted_action`
- notification allowed only if policy-specific channel exists

### 18.2 Forbidden notifications

No notification may include:
- raw sensitive note body by default
- raw AI rationale
- confidence score unless explicitly justified in reviewer-only tooling
- stigmatizing or conclusory language
- details sent to uncontrolled channels

---

## 19. Reporting and Dashboard Exposure Matrix

| State | Generic Dashboard | Restricted Dashboard | Reviewer Queue | Coach Limited View | Export Eligible |
|---|---|---|---|---|---|
| received | no | no | no | no | no |
| classified | no | no | no | no | no |
| validated | no | no | no | no | no |
| quarantined | no | limited ops only | yes | no | no |
| review_pending | no | restricted count only | yes | no | no |
| reviewed_accepted | no | restricted detail | yes | only if separately approved | no |
| reviewed_rejected | no | reviewer/history only | yes | no | no |
| reviewed_corrected | no | restricted detail | yes | only if separately approved | no |
| approved_for_limited_exposure | no | restricted detail | yes | yes, bounded | no |
| approved_for_restricted_action | no | restricted detail | yes | maybe, policy-specific | maybe |
| operationalized | no | restricted detail | yes | bounded only | policy-specific |

---

## 20. Canonical Example — AI Candidate to Reviewed Alert

### 20.1 Flow

1. AI model generates `ai_wellbeing_candidate_inference`
2. System stores record with provenance and `review_pending`
3. Reviewer opens restricted queue
4. Reviewer chooses:
   - reject
   - accept
   - correct
5. If accepted/corrected:
   - reviewer sets exposure level
   - optional limited alert artifact created
6. Minimal notification sent to authorized recipient if allowed
7. Audit trail emitted for every step

### 20.2 Hard guardrails

- no raw candidate shown in generic athlete dashboard
- no guardian escalation without reviewed action
- no performance score contamination
- no irreversible operational action from candidate alone

---

## 21. Review Checklist for Workflow Readiness

Every sensitive workflow must answer:

1. What starts the workflow?
2. What record types are involved?
3. Which states are used?
4. Which actors can transition each state?
5. What is the review gate?
6. What is the highest allowed exposure level?
7. Which side effects are allowed?
8. Which notifications are allowed?
9. What gets audited?
10. What are the terminal states?
11. What is the retention/disposition path?
12. What happens if provenance or policy fails?

If these are unclear, the workflow is not implementable.

---

## 22. Forbidden Patterns

The following are forbidden.

### 22.1 Direct AI-to-alert
No AI sensitive candidate may directly become active alert without review.

### 22.2 Direct AI-to-guardian
No AI candidate may directly trigger guardian/responsible escalation.

### 22.3 Unbounded coach visibility
No broad coach population may see sensitive detail by default.

### 22.4 Silent correction overwrite
No reviewed sensitive record may be corrected by destructive overwrite only.

### 22.5 Export by convenience
No sensitive export may occur without explicit approval workflow.

### 22.6 Dashboard leakage
No generic athlete or performance dashboard may display sensitive workflow state by accident.

### 22.7 Missing audit
No sensitive workflow transition may occur without audit.

---

## 23. Integration with Other Contracts

### 23.1 With persistence policy
Sensitive workflows usually operate on HYBRID / RESTRICTED modules:
- current workflow state in relational tables
- append-only review and audit history

### 23.2 With ingestion contract
Workflow entry records must inherit provenance, source classification, timing, and validation outputs.

### 23.3 With DTO/ViewModel boundary rules
Only dedicated restricted DTOs may expose workflow details.
ViewModels must preserve exposure level and scope boundaries.

### 23.4 With notifications
Notification content and recipients must remain bounded by workflow state and exposure approval.

---

## 24. Definition of Done

This workflow policy is DONE only when:

- every sensitive record type is mapped to a workflow family
- workflow states and transitions are explicit
- actor permissions exist per transition
- AI sensitive records always pass review gate before operational use
- guardian escalation has separate approval path
- export requests have explicit approval workflow
- correction preserves history
- quarantine path exists for broken provenance/policy cases
- notifications are state-bounded and minimal
- every transition emits audit events
```
