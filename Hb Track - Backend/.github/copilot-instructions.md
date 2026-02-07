# Copilot Instructions — HB Track (Backend)

BOOTSTRAP (mandatory):
1) Open and follow: docs/_ai/CANON.md, docs/_ai/ROUTER.md, docs/_ai/CHECKS.md
2) Start every response with:

EVIDENCE:
- <exact file paths opened, including docs/_ai/*>

If you cannot read docs/_ai/*, STOP and say:
BLOCKED: cannot load docs/_ai/* (need repo root / context)

RULES:
- Default: minimal patch.
- Refactor only if: [ALLOW_REFACTOR]
- If API/DB contract changes: regenerate canonical docs via scripts/generate_docs.py as required.

Include: CANARY-SEEN: HBTRACK_DOCS_LOADED_v1 after reading CANON.md