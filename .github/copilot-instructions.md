# HB TRACK — COPILOT GLOBAL RULES

<identity>
Project MUST be HB Track.
Output MUST be Portuguese.
Control MUST be English.
</identity>

<authority>
This file MUST remain BRIDGE ONLY — NON-SOVEREIGN.
Authority MUST be `scripts/hb`, `validate_contracts.py`, `merge-readiness.json` > `contracts/schemas/**` > `docs/_canon/**` > this file.
This file MUST NOT define canon.
This file MUST NOT override SSOT.
</authority>

<refs>
SSOT: `merge-readiness.json`
CDD: `docs/_canon/CONTRACT_PIPELINE.md`
Roadmap: `ROADMAP.md`
Handoff: `SESSION_HANDOFF.md`
Session validator: `contracts/schemas/shared/session_handoff.schema.json`
Roadmap verify: `hb verify --task-type execute_roadmap_phase --roadmap-phase <N>`
</refs>

<routing>
CDD: contracts | OpenAPI | AsyncAPI | JSON Schema | state model | UI contract
ROADMAP: phase | infra | deploy | frontend | implementation
MERGE_CI: PR | merge | CI | checks | review | parity -> `@HandTracker`
</routing>

<rules>
1. Copilot MUST read `SESSION_HANDOFF.md` when present.
2. Copilot MUST select exactly one mode: CDD, ROADMAP, MERGE_CI.
3. Copilot MUST NOT mix modes.
4. CDD MUST follow `docs/_canon/CONTRACT_PIPELINE.md`.
5. ROADMAP MUST follow `ROADMAP.md`.
6. MERGE_CI MUST route to `@HandTracker`.
7. Copilot MUST update `SESSION_HANDOFF.md` at session close.
8. Copilot MUST report `BLOCKED_*` in Portuguese.
9. Copilot MUST NOT rewrite gate force.
10. Copilot MUST NOT use destructive git to mask state.
11. Copilot MUST NOT edit `frontend/src/api/schema.d.ts` manually.
12. Copilot MUST NOT run production deploy autonomously.
13. Copilot SHALL NOT use filler.
</rules>

<verification_trigger>
Before output, Copilot MUST verify mode, authority, refs, handoff, blockers, evidence, Portuguese.
If any MUST rule was violated, Copilot MUST correct before output.
</verification_trigger>
