# Git Hooks for Invariants Enforcement

This directory contains versioned Git hooks to enforce invariant validation before commits/pushes.

## 📋 Available Hooks

### `pre-commit`
Runs before every `git commit`. Validates all invariants with golden baselines using `run_invariant_gate_all.ps1`.

**Behavior**:
- ✅ **EXIT 0**: All invariants pass → Commit allowed
- ⚠️ **EXIT 3**: Golden drift detected → Commit blocked (promote goldens)
- ❌ **EXIT 1**: Verification failures → Commit blocked (fix tests/SPEC)

## 🔧 Installation

### 1. Enable versioned hooks for this repository:
```bash
git config core.hooksPath .githooks
```

This tells Git to use `.githooks/` instead of `.git/hooks/` for this repository.

### 2. Verify installation:
```bash
git config --get core.hooksPath
# Should output: .githooks
```

## 🚀 Usage

Once enabled, hooks run automatically:

```bash
git add .
git commit -m "feat: add new feature"
# → pre-commit hook runs automatically
# → if EXIT=0, commit proceeds
# → if EXIT!=0, commit is blocked
```

### Bypass hook (NOT RECOMMENDED):
```bash
git commit --no-verify -m "skip hook"
```

⚠️ **Warning**: Bypassing hooks defeats the purpose of invariant enforcement. Only use in emergencies (e.g., hotfix deployment).

## 📂 Hook Scripts

- **`pre-commit`**: PowerShell script that calls `scripts/run_invariant_gate_all.ps1`
- Automatically detects repository root
- Provides clear feedback on pass/fail/drift
- Returns correct exit codes for Git to block/allow commits

## 🔄 Updating Hooks

Hooks are versioned in the repository. To update:

1. Edit `.githooks/pre-commit` (or other hooks)
2. Commit changes: `git add .githooks/ && git commit -m "chore: update pre-commit hook"`
3. All team members get updated hooks on `git pull` (no manual reinstall needed if `core.hooksPath` is already set)

## 🛠️ Troubleshooting

### Hook doesn't run:
```bash
# Check if hooks are enabled
git config --get core.hooksPath

# If not set, enable:
git config core.hooksPath .githooks
```

### Hook fails with "script not found":
- Ensure `scripts/run_invariant_gate_all.ps1` exists
- Check repository root path resolution

### Want to disable temporarily:
```bash
# Disable hooks
git config --unset core.hooksPath

# Re-enable later
git config core.hooksPath .githooks
```

## 📝 Notes

- Hooks are **local** (not pushed to remote by default, but versioned here)
- Each developer must run `git config core.hooksPath .githooks` once per repository clone
- Use `--no-verify` sparingly - defeats the purpose of quality gates
- Consider adding `pre-push` hook for additional validation before remote push

## 🎯 Why Versioned Hooks?

Traditional `.git/hooks/` are **not versioned** - every developer must manually copy scripts.

With **`core.hooksPath`**:
- ✅ Hooks are versioned in `.githooks/`
- ✅ Updates propagate via `git pull`
- ✅ Team-wide consistency
- ✅ Easier maintenance

## 🔗 Related Documentation

- [Git Hooks Documentation](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [core.hooksPath Config](https://git-scm.com/docs/git-config#Documentation/git-config.txt-corehooksPath)
- Project: `scripts/run_invariant_gate_all.ps1` (aggregated gate runner)
