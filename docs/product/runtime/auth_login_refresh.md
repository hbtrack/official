---
id: auth_login_refresh
doc_mode: HOWTO
status: CANONICAL
source_of_truth:
  - kind: ssot_factual
    ref: docs/_canon/HB_TRACK_PROFILE.yaml
depends_on:
  - docs/product/ARCHITECTURE.md
evidence_expected:
  - _reports/tasks/auth_login_refresh.log
---

# Runtime Scenario: Auth Login + Refresh

## Goal
Verify that JWT login and refresh token flow works end-to-end.

## Preconditions
- PostgreSQL running (via `docker-compose up -d` in `infra/`)
- Backend running (`uvicorn app.main:app --reload --port 8000` in `Hb Track - Backend/`)
- At least one user exists in the database (superadmin or seeded user)

## Steps

1. Login with valid credentials:
```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"your_password"}' \
  | python -m json.tool
```
Expected: 200 with `access_token` and `refresh_token` in response.

2. Access protected endpoint with token:
```bash
curl -s http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>" \
  | python -m json.tool
```
Expected: 200 with user profile (id, email, role_code, organization_id).

3. Attempt access without token:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/auth/me
```
Expected: 401.

4. Refresh the access token:
```bash
curl -s -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}' \
  | python -m json.tool
```
Expected: 200 with new `access_token`.

## Expected outcomes
- Login returns JWT tokens
- Protected routes reject unauthenticated requests (401)
- Refresh token produces a new access token
- ExecutionContext resolves user_id, role, org, permissions

## Failure modes
- **DB unreachable:** Login returns 500; check PostgreSQL container status
- **Invalid credentials:** Login returns 401; verify user exists and password is correct
- **Expired refresh token:** Refresh returns 401; user must re-login
- **Missing CORS headers:** Frontend cannot call backend; check CORS config in `app/main.py`

## Rollback
No destructive actions. If tokens are corrupted, clear `refresh_token` table rows for the user.
