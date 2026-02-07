<!-- STATUS: DEPRECATED | arquivado -->

# HB Track — Technical & UX Brief (Expanded)

Audience: senior frontend/UX specialist. Goal: ship a modern, high-velocity handball platform that maximizes athlete engagement while respecting the canonical backend rules and data model.

## 1) System & Roles Snapshot
- Multi-organization handball stack (Postgres 17 + FastAPI 3.11). No mixed-gender play; only male/female everywhere.
- Roles (backend enforced): superadmin (global), dirigente (org admin), coordenador (org ops), treinador (team ops), atleta (self). No role stacking; changing role creates a new link without overlap.
- Scope: trainers only see their teams; coordenador/dirigente see org; superadmin bypass; atleta read-only when no active team_registration.
- Soft delete + audit trails for all critical writes; nothing is hard-deleted (deleted_at + deleted_reason).

## 2) Frontend Stack (Hb Track - Fronted)
- Next.js 16, React 19, TypeScript, Tailwind v4, TanStack Query v5, React Hook Form + Zod, Framer Motion, React Dropzone, Lucide icons, FullCalendar, ApexCharts.
- Cypress E2E scaffolded; eslint/prettier configured; Dockerfile and .env.production.example present.
- Structure: `src/app/(dashboard|admin)` layouts, `src/components`, `src/context`, `src/features` (intake slot), `src/icons`, `src/lib`, `src/types`. Use server components only where safe; favor client components with React Query caching for live data.

## 3) Backend Surfaces to Leverage (Hb Track - Backend/app/api/v1/routers)
- Dashboard: `dashboard.summary` returns the full dashboard payload in one call; cache TTL 120s with headers `X-Cache-TTL` and `X-Generated-At`. Data: athlete totals (active/injured/dispensed), training trends (12 weeks), matches (W/D/L/goals), wellness aggregates (sleep/fatigue/stress/mood/readiness), medical cases, alerts (top 10), next training/match.
- Intake (ficha única): transactional creator for person + contacts/docs + optional org/team inline + athlete + team_registration + membership + optional user/login + profile photo (Cloudinary) + SendGrid invite. Supports Idempotency-Key and dry-run; blocks duplicates (email/phone/RG/CPF) with 409; goalkeeper rule (offensive positions null when defensive=goalkeeper).
- Athlete lifecycle: `athletes`, `athlete_states`, `team_registrations`, `athlete_import`, `unified_registration`.
- Events & participation: `matches`, `match_roster` (cap 16), `match_attendance` (minutes cap 80), `match_events` (phase_of_play + advantage_state codes), `match_teams`.
- Trainings: `training_sessions` (+ scoped version per team), `attendance_scoped`, `attendance` with R40 editing window (10 min self-edit, up to 24h with higher role, >24h read-only).
- Wellness: `wellness_pre`, `wellness_post` (UNIQUE per athlete/session) with fatigue, sleep, stress, mood, soreness, readiness, menstrual_phase optional.
- Lookups: `positions` (offensive/defensive), `categories`, `roles`, `organizations`, `teams`, `lookup_tables`, `lookup` (generic search).
- Media: `media` router for Cloudinary signing + person_media primary photo replacement.
- Auth/context: `auth` (JWT), `permissions` helpers, `users`, `memberships`, `roles`.
- Alerts/Reports: `alerts` (load, injury-return), `reports` (attendance/minutes/load) with order_by whitelists and pagination; cache invalidated on writes.

## 4) Canonical Domain Rules to Surface in UI
- Eligibility: gender compatibility (person.gender vs team.gender), age category rule (natural or above, never below) validated on team_registration and match convocation.
- Athlete states: `ativa`, `dispensada`, `arquivada`; flags `injured`, `medical_restriction`, `suspended_until`, `load_restricted`. Blocks: injured → cannot be rostered; suspended_until ≥ match date → block; dispensada → closes registrations and organization_id=NULL.
- Organization exclusivity: athlete can have multiple active team_registrations only inside the same organization; organization_id is derived, never manually set.
- Mandatory intake data: phone + email + RG; CPF optional; address optional; birthdate locked after active link (except special approval); email/phone/RG uniqueness.
- Goalkeeper exception: defensive position = goalkeeper disables offensive positions.
- Rosters: max 16 per match; no duplicates; minutes validation (<=80, reserve cannot log minutes >0).
- Attendance: generated from active team_registrations; edited within policy windows; reasons and participation types available.
- Wellness uniqueness: one pre and one post per athlete per training_session; readiness score and medical follow-up flag available.

## 5) Engagement-First UX (athlete-centric)
- Mobile-first for athlete surfaces: quick cards for “Today’s training/match,” “Wellness to fill,” “Convocations,” and “Restrictions” (injury/suspension badges).
- Low-friction wellness: sliders (0–10) with emoji anchors, 1-tap presets, save state offline then sync; show last submitted and readiness trend.
- Convocation/roster clarity: badge eligibility (category/gender/flags), explain blockers inline (e.g., “Suspended until 2026-02-10”); confirm/decline with justification where rules allow.
- Load awareness: show weekly ACWR band (from alerts), highlight excessive/deficit with actionable guidance; link to recovery tips if available.
- Profile transparency: state + flags chips, derived org/team(s) active, category badge (natural vs team category), position chips (defensive/offensive) with goalkeeper exception.
- Notifications/comm: leverage SendGrid welcome/invite; in-product toasts for cache invalidations after edits; encourage athletes with streaks (attendance, wellness completion).

## 6) Intake Wizard (must-have behaviors)
- Steps: Person → Contacts/Docs → Org → Team → Athlete → Photo → Review. Role-aware affordances: trainers cannot create org/team; coordenador/dirigente can.
- Autocomplete with scope: organizations/teams filtered by user scope; expose “create inline” only when allowed. Pre-fill org if single membership in context.
- Client-side validation before API: CPF check digit, RG format (7–9 digits), phone mask +55, email format; birthdate 8–60y; goalkeeper disables offensive dropdowns.
- Dry-run toggle to preview errors before committing; Idempotency-Key on submit to avoid duplicates on retries.
- Autosave drafts per step; focus-first-error; motion: step transitions + subtle shake on blocking errors; progress bar + stepper; scroll-to-top on step change.
- Upload: direct-to-Cloudinary signed request; preview with square crop; when saving, set primary photo, replacing previous without duplication.
- Error taxonomy mapping: 401/403/409/422 → friendly copy (“Duplicate RG”, “Org out of scope”, “Team requires matching gender”).

## 7) Dashboard & Data Presentation (coach/org view)
- Use `/dashboard/summary` as single source; honor cache headers; set React Query staleTime 60–120s and keepPreviousData.
- Above-the-fold: next match/training, active roster status (lesionada/suspensa), wellness readiness index, ACWR alerts, attendance trend.
- Filters: team_id and season_id; fallback to context org/team; show “data age” badge using `X-Generated-At`.
- Charts: weekly training load, match outcomes, wellness trendlines (sleep/fatigue/stress/mood), medical cases open/returning.

## 8) Training & Attendance UX
- Creation/edit guardrails: enforce R40 edit windows; show countdown for 10-minute self-edit window; after 24h lock with “request admin change.”
- Attendance UI: list from active team_registrations; mark presence/absence, minutes_effective, participation_type, reason_absence; flag restrictions (injured/suspended) inline.
- Session metadata: type (quadra, físico, vídeo, reunião, teste), objectives, planned_load, phase focus toggles, intensity target, session_block (periodization tag).
- Wellness hooks: surface pending pre/post forms linked to session; prevent duplicates; show readiness score when available.

## 9) Matches, Rosters, Events
- Roster builder: max 16, no duplicates, goalkeeper badge, jersey number, position tags. Eligibility checks: active registration with team, gender match, category rule, no injured/suspended.
- Attendance (match): minutes cap 80; reserve cannot log minutes >0; starter/reserve toggle; load contribution visible.
- Events: use phase_of_play (defense, transition_offense, attack_positional, transition_defense) and advantage_state (even, numerical_superiority, numerical_inferiority) to power filters and charts; event_types/subtypes are fixed lists (do not allow free text).

## 10) Reports & Alerts
- Reports endpoints: attendance, minutes, load with pagination and order_by whitelist; use server-side sorting only on allowed fields.
- Alerts: load (ACWR thresholds) and injury-return; render as actionable cards linking to athlete profile or session detail; show severity color coding.
- Cache awareness: on writes to attendance/match/training, invalidate report cache (backend already does) and refetch; show toast “Data refreshed.”

## 11) Performance & Reliability Expectations
- Use TanStack Query for all data fetches; respect cache headers; optimistic updates only when rule-safe (e.g., inline attendance toggles within edit window).
- Large lists: use backend pagination (page/limit); avoid client-side sorting except for local presentation of already paged data.
- Error handling: map 409 conflicts (duplicate contact/doc) and 422 validation (goalkeeper rule, category/gender mismatch); surface remediation tips.
- Accessibility: keyboardable steppers, aria-live for errors, high-contrast chips for states/flags, logical tab order on long forms.

## 12) Athlete Engagement Ideas (within current APIs)
- “Today” strip: next training/match with CTA to fill wellness or view convocation; status badges (eligible/blockers).
- Streaks: attendance and wellness completion streak counters; nudge when streak is about to break.
- Recovery tips: when load alert or medical flag exists, show short guidance (static copy) and link to staff contact.
- Photo/profile completeness meter: encourage uploads (Cloudinary) and missing optional data.

## 13) Deliverables for Frontend Specialist
- Scope-aware intake wizard with autosave, dry-run, Idempotency-Key, and Cloudinary/SendGrid hooks.
- Athlete profile with states/flags, eligibility badges, derived org/team, category indicators, positions (goalkeeper exception), and history of team_registrations.
- Dashboard consuming `/dashboard/summary` with cache headers; reports/alerts pages using paginated endpoints with allowed sorting.
- Training/match flows honoring edit windows, roster/attendance limits, and wellness uniqueness; clear blocker messaging.
- Mobile-first athlete surface with “Today,” wellness tasks, convocations, load/alert highlights, and streaks.

## 14) Game-Time Dashboard (speed is decisive)
- Goal: zero-friction, game-mode UI optimized for benches/analysts—decisions in seconds determine win/loss.
- Data strategy: prefetch `/dashboard/summary` on load; keep React Query staleTime 60–120s with manual “Refresh” button; light polling (15–30s) during live games only; avoid over-fetching when idle.
- Layout: split view for live score/clock + phases/advantage-state filters + top KPIs (shot efficiency, turnovers, saves, ACWR risk flags for players on court).
- Quick actions: keyboard shortcuts (e.g., 1-4 to tag phase_of_play, S to record shot event type/subtype, T for turnover); offline-safe queue with retry if request fails mid-game.
- Roster strip: 16 slots max with badges (injured/suspended/medical restriction), jersey numbers, position chips; tap to sub/mark event; prevent invalid selections (eligibility, flags).
- Possession context: badge “even/superior/inferior”; filter events by phase and advantage; show per-period stats (match_periods) with period timer.
- Latency guards: optimistic insert for match events with rollback on 4xx; small, cached lookup lists for event_types/subtypes; debounce network to batch small writes when possible.
- Clarity: color-coded chips for states/flags; big, readable typography; dark-friendly contrast for court-side environments; large touch targets on mobile/tablet.

## 15) PDF Reports (impactful + precise)
- Purpose: impress athletes/staff/sponsors; zero ambiguity in numbers; align with backend truth (no client-side re-aggregation).
- Data source: use backend exports when available; otherwise fetch paginated data and render server-side PDF (Next.js route handler) using the same ordering as API; avoid client-only computations.
- Visual system: cover with club logo, athlete photo, name + category + positions; state/flag chips; per-section accent color; clear hierarchy with large typography for headline metrics.
- Athlete PDF contents: personal data (non-sensitive), state/flags, team registrations timeline, category badge, positions, height/weight, dominant hand; season stats (games, goals, assists, saves/blocks, turnovers, minutes), wellness adherence (%), attendance (%), load trend sparkline; medical flags if active.
- Team PDF contents: roster with states/flags, attendance, load distribution, shot map heat, GK save map, top events by subtype.
- Export UX: “Export PDF” button near reports/profile; show generation spinner; on completion, offer download + share; watermark with timestamp/user; keep color-safe for print.

## 16) Scouting UI (live, fast, spatial)
- Goal/shot map: clickable goal for marking shots and goalkeeper saves; map zones tied to event_subtypes (`shot_6m`, `shot_9m`, `shot_wing`, `seven_meter`, etc.) and GK save types. Show conversion %, save %, and shot placement heatmap.
- Court map for line players: half-court schematic with drop zones for turnovers, fouls, assists; tag phase_of_play (defense/transition_offense/attack_positional/transition_defense) and advantage_state (even/superior/inferior) on tap.
- Speed inputs: keyboard shortcuts + big touch targets; quick-pick buttons for event_types/subtypes; configurable “favorites” bar per staff member.
- Live panels: running score/time, possessions, shot efficiency by zone, turnovers by subtype, goalkeeper saves by zone; per-period breakdown (match_periods) and advantage breakdown.
- Error tolerance: optimistic enqueue with retry; offline queue for short drops; clear status (pending/sent/failed) per event; compact undo (e.g., last 10s).
- Filters: by player, phase, advantage_state, period, zone; “is_shot” and “is_possession_ending” flags to power possession and efficiency views.

## 17) Ask: propose the “perfect” frontend
With the constraints and ambitions above, propose the ideal frontend plan: visual language, component system, navigation, athlete-facing mobile experience, game-time dashboards/scouting flows, PDF/export workflows, and how to stage this into sprints. Recommend concrete patterns (e.g., map overlays, keyboard schemes, cache strategies) that make HB Track unmistakably elite for handball.

## 18) Ask: decide on the best frontend choices (and why)
- Pin down the recommended stack/config for our context (Next.js 16 + React 19 + Tailwind v4 + TanStack Query + RHF/Zod + Framer Motion), explain why it’s optimal for speed, caching, and ergonomics.
- Propose design system tokens (color/type/spacing/elevation) and layout primitives tailored to handball analytics (maps, chips, heatmaps).
- Suggest app architecture (routing, data fetching strategy, error boundaries, offline queue) that best fits live game demands and athlete mobile flows, and justify the trade-offs.
