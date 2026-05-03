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
Boot: `docs/_canon/AGENT_INSTRUCTIONS.md`
CDD: `docs/_canon/CONTRACT_PIPELINE.md`
Roadmap: `ROADMAP.md`
Handoff: `SESSION_HANDOFF.md`
Handoff schema: `contracts/schemas/shared/session_handoff.schema.json`
CDD skill: `.github/skills/hb-pipeline-orchestrator/SKILL.md`
ROADMAP skill: `.github/skills/hb-roadmap-executor/SKILL.md`
Merge skill: `.github/skills/hb-merge-orchestrator/SKILL.md`
</refs>

<routing>
CDD: contracts | OpenAPI | AsyncAPI | JSON Schema | state model | UI contract -> `@HB Contract`
ROADMAP: execute_roadmap_phase | phase | infra | deploy | frontend | implementation -> `@HB Contract` (uses ROADMAP skill, runs `hb verify --task-type execute_roadmap_phase --roadmap-phase <N>`)
MERGE_CI: PR | merge | CI | checks | review | parity -> `@Hb Merger`
IMPL: approved plan execution -> `@Hb Implementer`
ADV: post-PR adversarial validation -> `@Hb Adversarial Tester`
</routing>

<rules>
1. Copilot MUST read `SESSION_HANDOFF.md` when present.
2. Copilot MUST select exactly one mode: CDD, ROADMAP, MERGE_CI, IMPL, ADV.
3. Copilot MUST NOT mix modes.
4. CDD MUST follow `docs/_canon/CONTRACT_PIPELINE.md`.
5. ROADMAP MUST follow `ROADMAP.md`.
6. MERGE_CI MUST route to `@Hb Merger`.
7. Copilot MUST update `SESSION_HANDOFF.md` at session close.
8. Copilot MUST report `BLOCKED_*` codes in Portuguese.
9. Copilot MUST NOT rewrite or weaken executable gates.
10. Copilot MUST NOT use destructive git to mask state.
11. Copilot MUST NOT edit `frontend/src/api/schema.d.ts` manually.
12. Copilot MUST NOT run production deploy autonomously.
13. Copilot SHALL NOT use filler.
</rules>

<verification_trigger>
Before output, Copilot MUST verify mode, authority, refs, handoff, blockers, evidence, Portuguese.
If any MUST rule was violated, Copilot MUST correct before output.
</verification_trigger>
