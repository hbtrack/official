---
applyTo: "infra/**,config/**,Dockerfile*,.github/workflows/**"
---

# HB ROADMAP MODE

<identity>
Role: ROADMAP path guard.
Output MUST be Portuguese.
Control MUST be English.
</identity>

<authority>
This file MUST remain BRIDGE ONLY — NON-SOVEREIGN.
Authority MUST be `scripts/hb`, `validate_contracts.py` > `docs/_canon/**` > `ROADMAP.md` > this file.
This file MUST NOT define canon.
</authority>

<refs>
Roadmap: `ROADMAP.md`
Skill: `.github/skills/hb-roadmap-executor/SKILL.md`
Worker: `.contract_driven/agent_prompts/execute_roadmap_phase.prompt.md`
</refs>

<rules>
1. Agent MUST use ROADMAP mode for matched paths.
2. Agent MUST follow `hb-roadmap-executor`.
3. Agent MUST read `ROADMAP.md`.
4. Agent MUST read `SESSION_HANDOFF.md` if present.
5. Agent MUST verify phase N-1 criteria before phase N.
6. Agent MUST NOT route matched paths through CDD.
7. Agent MUST NOT use `pre_contract_orchestrator`.
8. Agent MUST NOT run `hb check` for matched infra artifacts.
9. Agent MUST NOT run `hb artifact` for matched infra artifacts.
10. Agent MUST NOT require `validated_contract` for matched infra artifacts.
11. Agent MUST NOT require `ADVERSARIAL_ANALYSIS_GATE` for matched infra artifacts.
12. Agent SHALL NOT use filler.
</rules>

<output_format>
Responses MUST be Portuguese.
Responses MUST report mode, path, evidence, blocker, next action.
</output_format>

<verification_trigger>
Before output, agent MUST verify matched path, ROADMAP route, refs, prohibitions, Portuguese.
If any MUST rule was violated, agent MUST correct before output.
</verification_trigger>
