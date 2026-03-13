# DTO_VIEWMODEL_BOUNDARY_RULES.md 

version: 1.0.0
status: PENDENTE
decision_type: interface_boundary_policy
scope: hb_track
owners:
  - architecture
  - backend
  - frontend
  - analytics
related_decisions:
  - HB_TRACK_ARCHITECTURE_DECISION.md
  - HB_TRACK_PERSISTENCE_POLICY.md
  - INGESTION_PROVIDER_CONTRACT.md
related_modules:
  - frontend
  - backend
  - api
  - analytics
  - video
  - training
  - matches
  - reports
  - dashboard

---

## 1. Objective

Define the canonical boundary rules between:

- Domain Model
- API DTO
- ViewModel
- UI Component Props

This contract exists to prevent:

- frontend coupling to backend internals
- UI coupling to provider payloads
- persistence leakage into API contracts
- API DTO inflation to satisfy screens
- ViewModel misuse as domain truth
- accidental cross-layer drift

---

## 2. Core Decision

HB Track SHALL maintain strict separation between:

- Domain Model
- API DTO Contract
- ViewModel Contract
- UI Component Props

These layers are not interchangeable.

No layer may be used as a shortcut replacement for another merely for convenience, speed, or code reuse.

---

## 3. Canonical Layer Definitions

### 3.1 Domain Model

Definition:
The domain model expresses business meaning, invariants, state transitions, identities, and rules.

Examples:
- TrainingSession aggregate
- MatchEvent fact
- Athlete entity
- Notification delivery attempt
- Attendance mark fact

The domain model:
- may be richer than API contracts
- may contain internal invariants
- may contain internal IDs and operational metadata
- must not be shaped by UI rendering needs
- must not be shaped by provider raw payload quirks

---

### 3.2 API DTO

Definition:
API DTO is the transport contract exposed by backend endpoints.

Purpose:
- stable transport boundary
- explicit input/output schema
- versionable public contract
- backend-to-frontend interchange

API DTO:
- is not a domain entity
- is not a database entity
- is not a UI-specific screen model
- may be narrower or broader than the domain model depending on endpoint purpose
- must be intentionally designed

---

### 3.3 ViewModel

Definition:
A ViewModel is a frontend-facing composition model optimized for a screen, section, interaction flow, or visualization.

Purpose:
- aggregate data for a view
- adapt transport data to render-friendly shape
- localize formatting and composition decisions
- shield UI components from API churn

ViewModel:
- is not source of truth
- is not a backend contract
- may join multiple DTOs
- may include derived display fields
- may include UI-state-friendly structures
- must not become canonical business truth

---

### 3.4 UI Component Props

Definition:
Props are the smallest boundary, specific to component composition.

Props:
- may be narrower than ViewModels
- should be minimal for the component’s responsibility
- should not force unrelated DTO knowledge into the component

---

## 4. Canonical Data Flow

Preferred canonical flow:

Provider/Input
-> Ingestion Contract
-> Domain Logic
-> API DTO
-> ViewModel
-> UI Component Props
-> Rendered UI

This flow may be simplified only when the skipped layer truly does not exist as a separate concern.

Example:
For a trivial static settings page:
Domain -> DTO -> Props

But the simplification must be justified, not assumed.

---

## 5. Layer Responsibilities

| Layer | Responsibility | Must Not Do |
|---|---|---|
| Domain Model | business meaning, invariants, lifecycle, source-of-truth semantics | adapt to screen rendering convenience |
| API DTO | transport boundary and contract versioning | expose DB entities or UI rendering artifacts directly |
| ViewModel | screen-specific aggregation and transformation | become public API contract or source of truth |
| Component Props | component rendering contract | carry unrelated transport/domain baggage |

---

## 6. Separation Rules

### 6.1 Domain != DTO
A domain model must not be exposed directly as transport output.

Reason:
- internal invariants may leak
- future domain refactors would break clients
- persistence and operational details may leak into frontend

---

### 6.2 DTO != ViewModel
An API DTO must not be treated as the final screen model by default.

Reason:
- screens often need composition from multiple endpoints
- formatting and grouping are UI concerns
- screen needs change faster than API contracts

---

### 6.3 ViewModel != Domain
A ViewModel must never be used as business truth.

Reason:
- it may contain formatted strings
- it may collapse distinct concepts for UX convenience
- it may omit required invariants
- it may merge fields from multiple sources

---

### 6.4 DB Entity != DTO
Persistence entities must not be returned directly from public endpoints.

Reason:
- schema leakage
- accidental exposure of internal columns
- tight coupling to migrations
- brittle clients

---

### 6.5 Provider Payload != DTO/ViewModel
Raw provider payloads must never be exposed directly as DTOs or ViewModels unless an explicit review/internal endpoint exists for operational tooling.

Reason:
- provider lock-in
- schema instability
- semantic inconsistency
- uncontrolled surface area

---

## 7. API DTO Design Rules

### 7.1 DTOs are endpoint contracts
Each DTO must exist because an endpoint needs a transport shape, not because a database table or frontend component exists.

### 7.2 DTOs must be explicit
Each DTO should have:
- explicit name
- explicit purpose
- explicit field semantics
- stable schema ownership

### 7.3 DTOs should avoid UI formatting
DTOs should carry semantic values, not presentation strings, unless the presentation string itself is a product requirement.

Preferred:
- `started_at: datetime`
- `duration_seconds: integer`

Avoid:
- `started_at_label: "Ontem às 18:30"`
- `duration_label: "1h 25min"`

These belong in ViewModel or formatting layer.

### 7.4 DTOs may expose summaries intentionally
DTOs may expose summary fields when those summaries are part of the API use case.

Example:
- `current_score`
- `attendance_rate`
- `last_notification_status`

But such summaries must be explicit, not accidental leakage from internal projections.

### 7.5 DTOs must not expose raw persistence semantics unless intentional
Avoid leaking:
- join-table structure
- internal foreign-key naming
- raw event-store storage format
- internal soft-delete columns
- migration artifacts

---

## 8. ViewModel Design Rules

### 8.1 ViewModels are screen-oriented
A ViewModel may be created per:
- page
- dashboard widget
- list row
- details panel
- timeline section
- chart adapter
- modal
- form state initializer

### 8.2 ViewModels may combine multiple DTOs
This is allowed and expected.

Examples:
- Training session header + attendance summary + notification state
- Match metadata + event timeline + video clip links
- Athlete profile + performance trend + wellbeing warning banner

### 8.3 ViewModels may include derived display fields
Allowed examples:
- `statusBadge`
- `formattedDate`
- `chartSeries`
- `groupedTimeline`
- `ctaState`
- `emptyStateMessage`

These are not DTO fields by default.

### 8.4 ViewModels may flatten nested transport structures
Allowed when it improves UI ergonomics.

Example:
API DTO:
```json
{
  "athlete": { "id": "a1", "name": "Maria" },
  "team": { "id": "t1", "name": "Sub-16" }
}
````

ViewModel:

```json
{
  "athleteId": "a1",
  "athleteName": "Maria",
  "teamName": "Sub-16"
}
```

### 8.5 ViewModels must not hide semantic ambiguity

Do not collapse distinct domain meanings into one display field if the UI still needs the distinction.

Bad example:

* `status: "active"`

When backend distinctions matter:

* scheduled
* in_progress
* completed
* suspended
* archived

If the UI needs only one badge, derive it consciously, but do not lose canonical distinctions upstream.

---

## 9. Mapping Rules

### 9.1 All non-trivial mappings must be explicit

Transformations between layers must be intentional and reviewable.

Mappings should be explicit for:

* Domain -> DTO
* DTO -> ViewModel
* ViewModel -> Form State
* Ingestion normalized payload -> Domain command/fact

### 9.2 Mapping code is part of architecture

Mapping code is not glue to be ignored.
It is a controlled anti-coupling boundary.

### 9.3 Mapping ownership

Recommended ownership:

* backend owns Domain -> DTO mapping
* frontend owns DTO -> ViewModel mapping
* backend owns Ingestion -> Domain promotion mapping

### 9.4 No hidden transport adaptation in leaf UI components

Leaf components should not receive raw DTOs and silently map them internally unless the component is explicitly a boundary adapter.

---

## 10. Canonical Naming Rules

### 10.1 DTO naming

Use transport-oriented names.

Examples:

* `TrainingSessionResponseDto`
* `TrainingSessionListItemDto`
* `MatchTimelineEventDto`
* `AthleteProfileDto`
* `NotificationDeliveryAttemptDto`

Avoid:

* `TrainingSessionModel`
* `AthleteEntity`
* `MatchData`

### 10.2 ViewModel naming

Use screen/use-case-oriented names.

Examples:

* `TrainingSessionCardViewModel`
* `TrainingAgendaDayViewModel`
* `MatchTimelineViewModel`
* `AthleteDashboardViewModel`
* `WellbeingAlertBannerViewModel`

Avoid:

* `AthleteDtoView`
* `MatchEntityView`
* `SessionData`

### 10.3 Props naming

Use component-oriented names.

Examples:

* `SessionCardProps`
* `TimelineRowProps`
* `AttendanceChipProps`

---

## 11. Screen Composition Rules

### 11.1 API endpoints serve use cases, not tables

Endpoints should expose transport shapes aligned with product use cases.

### 11.2 ViewModels absorb composition volatility

When screens change often, volatility belongs primarily in ViewModel composition, not in domain model redesign.

### 11.3 Dashboard screens are ViewModel-heavy by nature

For dashboards, analytics panels, timelines, and video interfaces, ViewModels are expected to be richer and more screen-specific.

### 11.4 Forms may require separate input/output models

A form may use:

* input DTO schema from API
* local form ViewModel/state
* submission DTO back to API

These are separate artifacts.

---

## 12. Canonical Anti-Coupling Rules

### 12.1 Backend must not emit UI-only strings by default

Avoid embedding:

* localized phrases
* badge labels
* CSS-oriented tokens
* view-specific grouping markers

unless explicitly required by product contract.

### 12.2 Frontend must not depend on backend enum presentation names

Frontend should depend on stable semantic codes, then map to localized labels/theme tokens locally.

Preferred:

* DTO: `status = "in_progress"`
* ViewModel/UI: `statusLabel = "Em andamento"`

### 12.3 Frontend must not infer hidden domain rules from DTO accidents

If a screen depends on business semantics, those semantics must be explicit in DTO or documentation, not guessed from incidental fields.

### 12.4 ViewModels must not mirror backend DTOs 1:1 without reason

If a “ViewModel” is just a DTO clone, it is likely useless ceremony.
Either:

* use DTO directly for that trivial case, or
* create a real screen model

---

## 13. Special Rules for Analytics, Video, and Timelines

### 13.1 Analytics DTOs should remain semantic

Analytics DTOs should expose:

* measures
* dimensions
* periods
* identifiers
* units
* provenance if needed

Avoid DTOs that already contain chart-library-specific structure unless the endpoint is explicitly chart-oriented.

### 13.2 Chart data usually belongs in ViewModel

Examples:

* axis labels
* color labels
* chart series grouping
* tooltip text
* legend structure

These are UI concerns unless the API is intentionally a chart API.

### 13.3 Video timeline screens require strong ViewModel adaptation

Video and event-timeline interfaces often need:

* grouped clips
* synchronized labels
* interaction flags
* merged event+video slices

This composition belongs in ViewModel or dedicated frontend adapter layer, not in raw domain objects.

---

## 14. Special Rules for Sensitive Domains

### 14.1 Sensitive fields must not be spread by convenience

Wellbeing / psychological / health-adjacent fields must only appear in DTOs that explicitly require them.

### 14.2 ViewModels must preserve access boundaries

Frontend composition must not merge restricted sensitive data into generic athlete dashboards unless the endpoint and access policy explicitly allow it.

### 14.3 Masking/redaction may differ per DTO

Different DTOs may expose:

* full value
* redacted value
* boolean flag only
* summary status only

This is legitimate and expected in sensitive domains.

---

## 15. Forbidden Patterns

The following are forbidden.

### 15.1 Returning ORM/model objects directly from API

This leaks persistence and removes contract control.

### 15.2 Designing DTOs to satisfy a single component prop shape forever

This creates brittle coupling between backend transport and frontend implementation detail.

### 15.3 Treating OpenAPI schemas as ViewModels

OpenAPI describes transport, not screen composition.

### 15.4 Using ViewModels in backend business logic

A ViewModel has no authority in domain decisions.

### 15.5 Duplicating business rules only in frontend ViewModels

Business rules belong in backend/domain unless clearly presentation-only.

### 15.6 Using formatted labels as canonical semantics

Labels change with locale and UI policy; semantics must stay stable.

### 15.7 Letting ingestion normalized payload become public DTO by accident

The ingestion layer is an internal anti-corruption layer, not a public API surface.

---

## 16. Review Checklist for New Endpoints

Every new endpoint should answer:

1. What is the endpoint use case?
2. Which DTO is exposed?
3. Why is this DTO not a direct domain/persistence object?
4. Which frontend screens will consume it?
5. Does the screen need a ViewModel?
6. Which fields are semantic vs presentation-oriented?
7. Does this endpoint expose sensitive data?
8. Could this DTO accidentally lock the UI to current backend internals?

If these answers are not clear, the endpoint contract is not mature.

---

## 17. Review Checklist for New Screens

Every new screen should answer:

1. Which DTOs does it consume?
2. Does it need a dedicated ViewModel?
3. Which transformations are presentation-only?
4. Which fields are derived?
5. Is any sensitive field being combined with non-sensitive data?
6. Are component props minimal and local?
7. Is any component depending on raw DTO complexity it does not need?

If not, screen architecture is likely under-specified.

---

## 18. Example Patterns

### 18.1 Good pattern — Training card

Backend DTO:

```json
{
  "sessionId": "ts_1",
  "title": "Treino técnico ofensivo",
  "status": "scheduled",
  "scheduledStart": "2026-03-11T18:30:00Z",
  "athleteCount": 18
}
```

Frontend ViewModel:

```json
{
  "id": "ts_1",
  "title": "Treino técnico ofensivo",
  "statusCode": "scheduled",
  "statusLabel": "Agendado",
  "startsAtLabel": "Hoje, 18:30",
  "subtitle": "18 atletas previstas",
  "isLateRisk": false
}
```

Component Props:

```json
{
  "title": "Treino técnico ofensivo",
  "statusLabel": "Agendado",
  "subtitle": "18 atletas previstas"
}
```

---

### 18.2 Good pattern — Match timeline

Backend DTO:

```json
{
  "matchId": "m_1",
  "events": [
    {
      "eventId": "e_1",
      "eventType": "goal",
      "occurredAt": "2026-03-11T19:02:10Z",
      "athleteId": "a_7",
      "teamSide": "home"
    }
  ]
}
```

Frontend ViewModel:

```json
{
  "matchId": "m_1",
  "timelineGroups": [
    {
      "minuteLabel": "02'",
      "items": [
        {
          "id": "e_1",
          "icon": "goal",
          "label": "Gol de Ana",
          "side": "home"
        }
      ]
    }
  ]
}
```

This is correct because timeline grouping and label formatting are UI concerns.

---

### 18.3 Bad pattern — Provider leakage

Bad DTO:

```json
{
  "sr_match_id": "sr:match:123",
  "sport_event_status": { "match_status": "live" },
  "competitors": [...]
}
```

Why bad:

* provider-native field names leaked
* transport contract tied to upstream schema
* internal UI/domain will couple to provider structure

Correct approach:
normalize first, then emit stable DTO fields.

---

## 19. Recommended Implementation Policy

### 19.1 Backend

Backend should expose DTO schemas via OpenAPI and keep mappers/adapters explicit.

### 19.2 Frontend

Frontend should maintain a dedicated adapter layer for:

* DTO -> ViewModel
* DTO -> Form Initial State
* DTO collection -> table rows / charts / cards / timelines

### 19.3 Shared types

Shared types are allowed only for stable semantic contracts, not as a shortcut to erase layer boundaries.

### 19.4 Generated API clients

Generated clients are transport clients.
They do not remove the need for ViewModel composition.

---

## 20. Definition of Done

This policy is DONE only when:

* endpoints do not expose ORM/persistence entities directly
* DTOs are explicitly modeled as transport contracts
* non-trivial screens define ViewModels or explicit justification for not needing them
* analytics/video/timeline screens use presentation-oriented ViewModel adaptation
* sensitive fields are exposed only in explicit DTOs
* provider-native payloads are not leaked to public API contracts
* frontend components are not tightly coupled to raw DTO complexity
* OpenAPI is treated as transport contract, not screen contract

```
