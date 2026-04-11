# Phase 4 Completion Guide — Actions After Staging Deployment

## Expected Timeline

| Step | Duration | Status |
|------|----------|--------|
| CI: Validate Contracts | ~3 min | Should PASS (gates resolved) |
| CI: Run Tests | ~5 min | Should PASS (530+ tests) |
| CI: Build Docker | ~3 min | Both backend + frontend |
| CI: Deploy Staging | ~5 min | Automatic via `docker-compose` |
| CI: Seed Demo | ~1 min | Creates admin@hbtrack.demo |
| CI: Health Check | ~2 min | `/health` should 200 |
| CI: Contract Conformance | ~8 min | 5 modules in parallel |
| **Total CI time** | **~30 min** | PASS → awaits approval |

## Staging Validation (Manual — Post-Deploy)

### 1. Verify Staging is Healthy
```bash
# Check health endpoint
curl -i https://staging.handballtrack.app/health

# Expected: HTTP 200
# Body: { "status": "ok", "db": "ok", "redis": "ok" }
```

### 2. Verify Admin User Created
```bash
# Option A: Check logs in GitHub Actions output (CI logs)
# Look for: "[seed] Admin user: admin@hbtrack.demo (created=True)"

# Option B: SSH to staging VPS and check DB directly
ssh deploy@staging.handballtrack.app
docker compose -f /opt/hbtrack/staging/infra/docker-compose.prod.yml exec -T api \
  python manage.py shell_plus
# In shell: User.objects.filter(email='admin@hbtrack.demo')
```

### 3. Run Replay Live Tests
```bash
# From local machine (after staging is up)
export HB_STAGING_URL=https://staging.handballtrack.app
pytest tests/replay/staging/ -v --tb=short 2>&1 | tee replay_live_results.txt

# Expected: ✅ All tests PASS
# Includes structures for: identity_access, users, teams, seasons, training
```

### 4. Verify Training Endpoints (A1 Validation)
```bash
# Check that /api/training/* endpoints exist and have correct prefixes
curl -s https://staging.handballtrack.app/api/openapi.json | \
  jq '.paths | keys | map(select(startswith("/training"))) | length'

# Expected: ~36 paths under /training/ (was ~27 before A1)
```

## When Everything Passes

### Step 1: Create PR Review
```bash
# In GitHub: PR #64 → Approvals section
# Add a quick comment:
"✅ Staging validation complete:
- Health check PASS
- Admin user created
- Replay live 50/50 PASS
- Training endpoints verified

Ready for production deployment."
```

### Step 2: Merge PR
```bash
# Option A: Via GitHub UI (one-click after approval)
# Option B: Via CLI
gh pr merge 64 --auto --squash

# This triggers:
# - Merge to main
# - CI auto-runs on main
# - Auto-deploy to production (after approval gate)
```

### Step 3: Mark Phase 4 DONE
Edit `ROADMAP.md`:
```diff
- | Fase 4 — Ciclo 1 em staging | ⚠️ PARTIAL_PASS | ...
+ | Fase 4 — Ciclo 1 em staging | ✅ DONE | Prefix + endpoints synced, replay live PASS, deployed to staging 2026-04-11 |
```

### Step 4: Update SESSION_HANDOFF
```diff
- resultado: DONE
+ resultado: DONE
- ci_status: FAIL
+ ci_status: PASS
- próxima_acao_permitida: "Deploy branch..."
+ próxima_acao_permitida: "Begin Phase 5+ implementation (frontend modules + Fase 6–13 backend features)"
```

## Troubleshooting

### CI Validation Fails
```bash
# Re-run validation locally first
python3 scripts/validate_contracts.py --profile precommit

# If local PASS but CI FAIL:
# - Check for WSL/infrastructure issues in CI logs
# - Most common: ASYNCAPI_VALIDATION_GATE timeout (non-blocking, exit 3)
# - Comment on PR: "Known infra issue in CI, gates substantively PASS"
```

### Staging Deploy Fails
```bash
# Check logs in CI output or SSH to VPS:
ssh deploy@staging.handballtrack.app
cd /opt/hbtrack/staging
docker compose -f infra/docker-compose.prod.yml ps   # Status
docker compose -f infra/docker-compose.prod.yml logs api --tail=100  # Logs
```

### Replay Tests Fail
```bash
# Common cause: admin user not created
# Fix: Re-run seed_demo manually
HB_STAGING_URL=https://staging.handballtrack.app python manage.py seed_demo --skip-if-exists

# Or restart the whole deploy with fresh seed:
# (Contact ops or run destructive_reset workflow)
```

## Phase 4 Success Criteria (Final Checklist)

- [ ] PR #64 CI: All 7 stages PASS
- [ ] Staging `/health` returns 200
- [ ] Admin user `admin@hbtrack.demo` exists in staging DB
- [ ] Replay live tests: ✅ all PASS (50+ tests)
- [ ] Training endpoints: ~36 paths under `/api/training/*`
- [ ] Contract conformance: ✅ all 5 modules PASS
- [ ] PR approved by human reviewer
- [ ] PR merged to main
- [ ] Production approval given
- [ ] ROADMAP.md Phase 4 marked ✅ DONE
- [ ] SESSION_HANDOFF.md updated with ci_status=PASS

**After all checks PASS**: Proceed to Phase 5+ implementation (frontend modules, additional backend features).
