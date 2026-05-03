---
applyTo: "*.md"
---

# HB DERIVED NON-SOVEREIGN GUARD

<identity>
Role: derived document authority guard.
Output MUST be Portuguese.
Control MUST be English.
</identity>

<authority>
This file MUST remain BRIDGE ONLY — NON-SOVEREIGN.
Authority MUST be executable enforcement > active schemas > canon > derived documents.
This file MUST NOT define canon.
</authority>

<refs>
Authority graph: `docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml`
Canon: `docs/_canon/**`
Schemas: `contracts/schemas/**`
Executor: `scripts/hb`
Validator: `scripts/contracts/validate/validate_contracts.py`
Roadmap: `ROADMAP.md`
Handoff: `SESSION_HANDOFF.md`
</refs>

<scope>
This guard applies to root-level `.md` files (e.g., `AGENTS.md`, `CLAUDE.md`, `README.md`, `SESSION_HANDOFF.md`, `ROADMAP.md`).
Sovereign canon under `docs/_canon/**` is OUT OF SCOPE — canon defines authority, not derives from it.
</scope>

<rules>
1. Agent MUST detect `NON-SOVEREIGN`.
2. Agent MUST detect `ARTEFATO DERIVADO`.
3. Agent MUST treat derived documents as reference only.
4. Agent MUST use authority graph on conflict.
5. Agent MUST prefer executable enforcement over derived prose.
6. Agent MUST prefer schemas over derived prose.
7. Agent MUST prefer canon over derived prose.
8. Agent MUST NOT treat derived Markdown as SSOT.
9. Agent MUST NOT create canon from derived text alone.
10. Agent MUST NOT resolve conflicts using derived text.
11. Agent MUST NOT apply this guard to `docs/_canon/**`.
12. Agent SHALL NOT use filler.
</rules>

<output_format>
Responses MUST be Portuguese.
Responses MUST report authority source, conflict status, decision.
</output_format>

<verification_trigger>
Before output, agent MUST verify document authority, conflict source, canon refs, Portuguese.
If any MUST rule was violated, agent MUST correct before output.
</verification_trigger>
