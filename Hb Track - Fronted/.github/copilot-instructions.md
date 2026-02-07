# Copilot Instructions — HB Track (Frontend)

BOOTSTRAP (mandatory):
1) Open and follow: docs/_ai/CANON.md, docs/_ai/ROUTER.md, docs/_ai/CHECKS.md
2) Start every response with:

EVIDENCE:
- <exact file paths opened, including docs/_ai/*>

If you cannot read docs/_ai/*, STOP and say:
BLOCKED: cannot load docs/_ai/* (need repo root / context)

RULES:
- Default: minimal patch (smallest diff that solves).
- Refactor only if user includes: [ALLOW_REFACTOR]
- API integration DoD: npm run gate:api must pass (sync OpenAPI + hygiene + typecheck + lint)
- Otherwise DoD: npm run gate must pass.

Include: CANARY-SEEN: HBTRACK_DOCS_LOADED_v1 after reading CANON.md