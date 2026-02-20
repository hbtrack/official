---
id: UDS_SPEC_v0_1
status: CANONICAL
normative: true
---

1. Purpose
This spec defines a deterministic documentation system for AI-assisted development.

2. Modes (Diataxis)
- REFERENCE: facts, schemas, APIs, invariants.
- HOWTO: procedures to achieve a goal.
- TUTORIAL: guided learning path.
- EXPLANATION: rationale and trade-offs.

MUST NOT mix modes in a single document.

3. Truth hierarchy
Authority precedence MUST follow docs/_INDEX.yaml.

4. DERIVED policy
Anything under docs/ssot/ is DERIVED and MUST be treated as read-only.
Manual edits are forbidden. Regeneration MUST be declared.

5. ADR policy
Architectural decisions MUST be recorded as ADRs using the template.
Every major trade-off MUST link to an ADR.

6. Gates (L0-L4)
- L0 Structure: required files/paths exist; indexes parse.
- L1 Schema: PROFILE schema validity.
- L2 Consistency: cross-references + SSOT/DERIVED rules enforced.
- L3 Evidence: expected evidence exists (configurable).
- L4 Quality: lint/readability (non-fatal by default).

L0-L2 MUST be blocking.
