---
description: Whitelist of commands approved for Agent/Copilot execution (HB Track)
---

# Approved Commands (Agent Whitelist)

Commands approved for execution by Copilot agent. Commands NOT in this list require explicit user approval.

---

## ✅ APPROVED: PowerShell Core (Git & Validation)

### Git Operations (Read-Only Safe)
```powershell
git status --porcelain
git diff <file>
git diff --stat
git log --oneline -n <N>
git show <commit>
```

### Git Operations (Requires Approval)
```powershell
git add <file>
git add -A <path>
git commit -m "msg"          # Only with user approval
git restore -- <file>        # Only if user agrees
git restore -- <path>        # Only if user agrees
```

### Model & Validation Gates (APPROVED)
```powershell
# Single table
.\scripts\models_autogen_gate.ps1 -Table <name> -Profile strict|fk
.\scripts\models_autogen_gate.ps1 -Table <name> -Profile strict -AllowCycleWarning

# Batch (scan only)
.\scripts\models_batch.ps1 -SkipGate        # Scan, no gate execution

# Requirements (read-only)
.\venv\Scripts\python.exe scripts\model_requirements.py --table <name> --profile strict
```

### SSOT Refresh (Requires Approval)
```powershell
# Full SSOT refresh (generates all artifacts)
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\HB TRACK\scripts\inv.ps1" refresh

# Specific generators (if needed)
.\venv\Scripts\python.exe scripts\generate_docs.py --all
```

### Guard & Baseline (Requires Approval)
```powershell
# Snapshot baseline (when models change)
.\venv\Scripts\python.exe scripts\agent_guard.py snapshot --root . --out ".hb_guard/baseline.json"

# Check baseline (read-only)
.\venv\Scripts\python.exe scripts\agent_guard.py check --root . --baseline ".hb_guard\baseline.json"
```

### Docker & Database (Requires Approval)
```powershell
docker-compose down
docker-compose up -d postgres
```

### Alembic Migrations (Requires Approval)
```powershell
.\venv\Scripts\python.exe -m alembic upgrade head
.\venv\Scripts\python.exe -m alembic current
```

---

## ❌ BLOCKED: PowerShell Commands (Forbidden)

These commands are NEVER approved without explicit out-of-band user consent:

```powershell
Invoke-Expression              # ❌ Use & with array instead
git reset --hard               # ❌ Destructive, no approval
git reset --soft               # ❌ Can lose work
git clean -f                   # ❌ Destructive, no approval
git clean -fd                  # ❌ Destructive, no approval
Remove-Item -Recurse           # ❌ Destructive, no approval
rm -Recurse                    # ❌ alias for Remove-Item
```

---

## ✅ APPROVED: Python Commands

### Model Requirements (Read-Only)
```bash
python scripts/model_requirements.py --table <name> --profile strict
python scripts/model_requirements.py --table <name> --profile fk
```

### SSOT Generation (Approved)
```bash
python scripts/generate_docs.py --all
python scripts/generate_docs.py --openapi
python scripts/generate_docs.py --schema
```

### Guard Operations (Approved)
```bash
python scripts/agent_guard.py snapshot --root . --out .hb_guard/baseline.json
python scripts/agent_guard.py check --root . --baseline .hb_guard/baseline.json
```

---

## ❌ BLOCKED: Python Commands (Forbidden)

```python
# File modification without guard approval
exec(<string>)                           # ❌ Arbitrary code execution
subprocess.run([...], shell=True)        # ❌ Shell injection risk
```

---

## Protected Files (Guard Enforced)

These files cannot be modified without explicit guard approval:

```
- app/main.py                 (entry point)
- app/config.py               (configuration)
- Hb Track - Backend/alembic/versions/*  (migrations; use Alembic CLI)
- .hb_guard/baseline.json      (baseline; use agent_guard.py snapshot)
- Hb Track - Backend/.env      (secrets; user-managed)
```

---

## Conditional Approval (Ask User First)

If Copilot wants to execute a command NOT in this whitelist:

1. **Agent MUST ask:**
   ```
   This command is not in APPROVED_COMMANDS:
   $ <command>
   
   Approve? [Y/N] Or [A]pprove & record
   ```

2. **User responds:**
   - `Y` — Execute once, don't record
   - `N` — Abort
   - `A` — Execute & add to APPROVED_COMMANDS + document rationale

3. **If approved:**
   - Execute command
   - Log rationale in docs/execution_tasks/CHANGELOG.md
   - (If "A") Update `.github/instructions/commands.instructions.md`

---

## Reference: Command Classification

| Type | Safety | Approval | Use |
|------|--------|----------|-----|
| **Read-Only** (git status) | 🟢 SAFE | None | Anytime |
| **Safe Write** (git add→commit) | 🟡 CAUTION | User approval | After user reviews |
| **SSOT Generation** | 🟡 CAUTION | User approval | When updating schema |
| **Gate Execution** | 🟡 CAUTION | Automatic (gated) | After requirements PASS |
| **Destructive** (git reset, rm -R) | 🔴 DANGEROUS | Explicit approval | Emergency only |
| **Unvetted** (custom commands) | 🔴 DANGEROUS | Ask user | Conditional approval |

---

## Examples of Approval Workflow

### Example 1: Safe (No Approval Needed)
```
Agent: Scanning tables...
$ git status --porcelain
[output]
$ python scripts/model_requirements.py --table athletes --profile strict
EXIT=4 (FAIL)

Next step: Apply /parity-fix
```
✅ No approval needed (read-only commands)

### Example 2: Needs Approval (User Provides)
```
Agent: Ready to fix athletes model.
[Would execute]
$ .\scripts\models_autogen_gate.ps1 -Table athletes

Approve? [Y/N/A]

You: Y

Agent:
$ .\scripts\models_autogen_gate.ps1 -Table athletes
[executes, patches file, returns exit=0]

Next: Commit changes?
```
✅ User approved, executed

### Example 3: Conditional Question (Approval Ask)
```
Agent: Baseline out of sync. Propose:
$ python scripts/agent_guard.py snapshot --root . --out .hb_guard/baseline.json

This command UPDATES baseline. 
Approve? [Y/N/A]

You: Y

Agent: [executes snapshot, updates baseline]

Commit baseline change?
```
✅ User asked & approved

---

## Maintenance

**To add a command:**
1. Copilot (or user) proposes: `cmd`
2. User approves (if safe) or rejects
3. If approved: Update this file + commit
4. Rationale: Why is this command needed?

**To remove a command:**
1. Security concern or deprecation
2. Update this file (move to ❌ BLOCKED section)
3. Document in CHANGELOG.md

**Authority:** This file is the single source of truth (SSOT) for approved commands.
