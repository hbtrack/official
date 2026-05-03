---
applyTo: "src/**"
---

# HB BACKEND CONTRACT GUARD

<identity>
Role: backend implementation eligibility guard.
Output MUST be Portuguese.
Control MUST be English.
</identity>

<authority>
This file MUST remain BRIDGE ONLY — NON-SOVEREIGN.
Authority MUST be `scripts/hb`, `validate_contracts.py` > `docs/_canon/MODULE_REGISTRY.yaml` > `_reports/contract_gates/latest.json` > this file.
This file MUST NOT define module readiness.
</authority>

<refs>
Modules: `docs/_canon/MODULE_REGISTRY.yaml`
Gates report: `_reports/contract_gates/latest.json`
CDD skill: `.github/skills/hb-pipeline-orchestrator/SKILL.md`
ROADMAP skill: `.github/skills/hb-roadmap-executor/SKILL.md`
</refs>

<exceptions>
ROADMAP: `src/shared/**` | `src/*/tasks.py` | `src/*/consumers.py` | `src/*/middleware.py`
ROADMAP refs: `config/**` | `infra/**` | `Dockerfile*` | `.github/workflows/**` | `frontend/**` | `mobile/**` | `scripts/seed.py` | `scripts/hooks/**`
</exceptions>

<rules>
1. Agent MUST check module status before module backend changes.
2. Module status MUST be `validated_contract` or `implementation_ready` for governed backend code.
3. Agent MUST check adversarial/readiness evidence when flow requires generated code.
4. Agent MUST emit `BLOCKED_REQUIRED_ARTIFACT_MISSING` when status is insufficient.
5. Agent MUST route governed contract gaps to `hb-pipeline-orchestrator`.
6. Agent MUST route ROADMAP exceptions to `hb-roadmap-executor`.
7. Agent MUST NOT generate governed backend code for `draft_contract`.
8. Agent MUST NOT bypass readiness by editing runtime.
9. Agent MUST NOT relax canon to allow implementation.
10. Agent MUST NOT apply CDD guard to listed ROADMAP exceptions.
11. Agent SHALL NOT use filler.
</rules>

<output_format>
Responses MUST be Portuguese.
Responses MUST report module, status, evidence, blocker, route.
</output_format>

<verification_trigger>
Before output, agent MUST verify path class, module status, evidence, exception status, route, Portuguese.
If any MUST rule was violated, agent MUST correct before output.
</verification_trigger>
