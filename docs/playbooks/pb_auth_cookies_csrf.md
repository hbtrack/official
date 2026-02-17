---
id: pb_auth_cookies_csrf
doc_mode: HOWTO
status: CANONICAL
source_of_truth:
  - kind: runtime_evidence
    ref: docs/product/runtime/_INDEX.yaml
depends_on:
  - docs/product/runtime/auth_login_refresh.md
evidence_expected: []
---

# Playbook: Auth / Cookies / CSRF Issues

## Trigger
- Frontend receives 401 on authenticated requests
- Login succeeds but subsequent API calls fail
- CORS errors in browser console

## Related runtime scenarios
- `auth_login_refresh` — verifies the full JWT flow

## Diagnosis

1. Check if the access token is being sent:
```bash
# In browser DevTools > Network tab, inspect the Authorization header
# Expected: Authorization: Bearer <token>
```

2. Check CORS configuration:
```bash
curl -s -I -X OPTIONS http://localhost:8000/api/v1/auth/me \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET"
```
Expected: `Access-Control-Allow-Origin` header present.

3. Check token expiration:
```bash
# Decode JWT payload (base64):
echo "<jwt_payload_part>" | base64 -d | python -m json.tool
# Check "exp" timestamp
```

4. Check refresh token in DB:
```sql
SELECT id, user_id, expires_at, revoked_at
FROM refresh_token
WHERE user_id = '<user_uuid>'
ORDER BY created_at DESC LIMIT 1;
```

## Action

| Symptom | Fix |
|---------|-----|
| Missing CORS header | Add frontend origin to `allow_origins` in `app/main.py` |
| Token expired, refresh works | Frontend must auto-refresh before expiry |
| Token expired, refresh fails | User must re-login; clear stored tokens |
| 401 on all requests | Check `SECRET_KEY` env var matches between restarts |

## Verification
Re-run the `auth_login_refresh` runtime scenario end-to-end.
