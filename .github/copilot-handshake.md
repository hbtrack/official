# GitHub Copilot Handshake Template

## What is a Handshake?

A **handshake** is a structured acknowledgment between Copilot and the HB Track codebase when a new session begins. It ensures that Copilot:

1. Has read foundational SSOT documents
2. Understands the codebase architecture and conventions
3. Acknowledges guardrails and constraints
4. Commits to deterministic behavior

## Handshake Format

```
[HANDSHAKE_ACK]
  ROLE_TOKEN = github-copilot-[version]
  FILES_READ = 
    - c:\HB TRACK\docs\_ai\_INDEX.md
    - c:\HB TRACK\docs\_canon\00_START_HERE.md
    - c:\HB TRACK\docs\_canon\01_AUTHORITY_SSOT.md
    - c:\HB TRACK\.github\copilot-instructions.md
  CONSTRAINTS_ACKNOWLEDGED = true
  DETERMINISM_COMMITMENT = true
  STATUS = ready
[/HANDSHAKE_ACK]
```

## Required Reading Before Task Execution

Copilot MUST read and acknowledge these files:

### Tier 1 (CRITICAL - Blocks Task Execution)
1. `docs/_ai/_INDEX.md` — Navigation and context map
2. `docs/_canon/00_START_HERE.md` — Canonical entry point
3. `docs/_canon/01_AUTHORITY_SSOT.md` — SSOT hierarchy and precedence
4. `.github/copilot-instructions.md` — Global rules and enforcement

### Tier 2 (HIGHLY RECOMMENDED - Part of Full Context)
5. `docs/_canon/02_CONTEXT_MAP.md` — Intent → Documentation mapping
6. `docs/_canon/03_WORKFLOWS.md` — Operational workflows and checklists
7. `docs/ADR/_INDEX_ADR.md` — Architecture decision records

### Tier 3 (ROLE-SPECIFIC - Load per Task Type)
- Code review: `docs/_canon/05_MODELS_PIPELINE.md`
- AI automation: `docs/_ai/_prompts/HB_TRACK_CODE_REVIEW_AGENT.md`
- Git operations: `docs/_canon/10_GIT_PR_MERGE_WORKFLOW.md`
- Models/schema: `docs/_canon/04_SOURCES_GENERATED.md`

## Enforcement

**If handshake is incomplete:**
- Agent cannot proceed with task execution
- Must request files and re-attempt handshake
- Document handshake ACK in conversation summaries

**If constraints violated:**
- Immediate rollback (git restore)
- Report violation to user
- Request explicit override permission

## Template for Sessions

```markdown
## Session Handshake ✓

**Copilot Version**: [version]
**Timestamp**: [ISO 8601]

**SSOT Files Read**:
- [x] docs/_ai/_INDEX.md
- [x] docs/_canon/00_START_HERE.md
- [x] docs/_canon/01_AUTHORITY_SSOT.md
- [x] .github/copilot-instructions.md
- [x] [Role-specific files per task]

**Constraints Acknowledged**:
- [x] PowerShell 5.1 (no pwsh/bash)
- [x] Working dir: C:\HB TRACK
- [x] No temp files in repo
- [x] Capture $LASTEXITCODE immediately
- [x] Stop-on-first-failure policy
- [x] No git reset --hard without explicit approval
- [x] No destruction (Remove-Item, git clean) without preview

**Determinism Commitment**: ✓ ENABLED
- Same inputs → Same behavior
- All decisions cite canonical docs
- Tools invoked deterministically

**Status**: READY FOR TASKS
```

---

**Reference**: `.github/copilot-instructions.md`
