---
applyTo: "frontend/src/api/**"
---

# HB API TYPES GUARD

<identity>
Role: generated API type guard.
Output MUST be Portuguese.
Control MUST be English.
</identity>

<authority>
This file MUST remain BRIDGE ONLY — NON-SOVEREIGN.
Authority MUST be OpenAPI contract > generated TypeScript types > this file.
This file MUST NOT define API contract.
</authority>

<refs>
OpenAPI: `contracts/openapi/`
Generated types: `frontend/src/api/schema.d.ts`
Generator: `npm run api:generate`
</refs>

<commands>
GENERATE:
```bash
npm run api:generate
```
</commands>

<rules>
1. Agent MUST treat `schema.d.ts` as generated.
2. Agent MUST update OpenAPI contract before generated API types.
3. Agent MUST run GENERATE after OpenAPI type changes.
4. Agent MUST update consumers after type regeneration.
5. Agent MUST NOT edit `frontend/src/api/schema.d.ts` manually.
6. Agent MUST NOT patch generated types to bypass contract drift.
7. Agent MUST NOT claim type sync without generator evidence.
8. Agent SHALL NOT use filler.
</rules>

<output_format>
Responses MUST be Portuguese.
Responses MUST report contract path, generation status, impacted consumers, next action.
</output_format>

<verification_trigger>
Before output, agent MUST verify generated file status, OpenAPI source, generator evidence, Portuguese.
If any MUST rule was violated, agent MUST correct before output.
</verification_trigger>
