# Pull Request Template

Thank you for contributing to HB Track! Please complete this template before submitting a PR.

## Description

*Briefly describe the changes in this PR.*

- What problem does this solve?
- What are the key changes?
- Are there any breaking changes?

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] CI/Infrastructure
- [ ] Refactoring
- [ ] Tests

## Checklist

### Code Quality

- [ ] Code follows project style (PEP-8 for Python, ESLint for TypeScript)
- [ ] All newly created files have headers/docstrings
- [ ] No hardcoded secrets or PII in code
- [ ] No temporary files or debug code left behind

### Testing

- [ ] Tests added/updated for new functionality
- [ ] All tests pass locally
- [ ] No regressions in existing tests
- [ ] Coverage maintained or improved

### Documentation

- [ ] Canonical docs updated (if applicable)
- [ ] ADR created/updated (if architectural decision)
- [ ] README updated (if public API changes)
- [ ] Changelog entry added

### Git Hygiene

- [ ] Commits are atomic and descriptive
- [ ] Branch name follows convention: `feature/` or `fix/` or `chore/`
- [ ] No merge commits (rebase if needed)
- [ ] PR title follows convention: `fix(scope): description` or `feat(scope): description`

### Gate Validation

- [ ] `git status --porcelain` is clean (no uncommitted changes outside this PR)
- [ ] `parity_gate.ps1` passes (if models changed)
- [ ] `agent_guard.py` passes (baseline not modified without approval)
- [ ] `models_autogen_gate.ps1` passes (if models changed)
- [ ] Quality gates pass (complexity, LOC, coverage)

### Workflow Validation

- [ ] GitHub Actions workflows pass
- [ ] No lint/type errors reported by CI
- [ ] No security vulnerabilities flagged

## Related Issues

Closes: #XXX (if applicable)

## Reviewer Notes

*Any additional context for reviewers?*

---

**Thank you for contributing!** We'll review this PR as soon as possible.
