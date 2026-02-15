# copilot.instructions.md — Reminder (CI/CD Gates)
Version: 1.0.0 | Date: 2026-02-15 | Scope: HB Track repo

## BCP14
MUST, MUST NOT, REQUIRED, SHOULD, MAY follow BCP14 (RFC2119+RFC8174).

## Reminder / Policy
You MUST run the local CI gates BEFORE every commit (and again before push) to avoid CI/CD blocks.
Do NOT create commits that have not passed the local gates.

## Canonical command (repo root)
.\scripts\checks\check_ci_gates_local.ps1

## If iterating fast
.\scripts\checks\check_ci_gates_local.ps1 -FailFast

## If gates fail
- You MUST fix the failures first, then re-run the command until PASS.
- Only after PASS you MAY proceed with `git add` + `git commit`.

---

# YAML (Machine-readable SSOT)
```yaml
policy_id: HB-CI-GATES-PRECOMMIT
version: 1.0.0
date: "2026-02-15"

reminder:
  intent: "avoid CI/CD gate blocks"
  enforcement:
    before_commit: MUST
    before_push: SHOULD

runner:
  required_cwd: repo_root
  cmd: ".\\scripts\\checks\\check_ci_gates_local.ps1"
  fast_cmd: ".\\scripts\\checks\\check_ci_gates_local.ps1 -FailFast"
  success_condition: "all gates PASS (or explicitly SKIP) and runner exit == 0"
  failure_condition: "any gate FAIL/ERROR or runner exit != 0"

agent_rules:
  - MUST: "Run runner.cmd before creating a commit."
  - MUST: "Block committing if runner exit != 0."
  - MUST: "Fix issues then rerun until success_condition is met."
  - SHOULD: "Rerun before push for final guarantee."
