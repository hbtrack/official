# Connectivity Diagnostic Report

**Contract:** `CONNECTIVITY_DIAGNOSTIC_CONTRACT` v1.1.0
**Status:** ✅ PASS  |  **Exit Code:** `0`

---

## Inputs

| Parameter | Value |
|-----------|-------|
| `api_base_url` | `http://191.252.185.34:8000/api/v1` |
| `frontend_origin` | `http://localhost:3000` |
| `health_path` | `/api/v1/health` |
| `readiness_path` | `/api/v1/health/readiness` |
| `env_var_names` | `['NEXT_PUBLIC_API_URL']` |
| `env_file` | `C:\HB TRACK\Hb Track - Frontend\.env.local` |
| `timeout_seconds` | `8` |
| `verify_tls` | `False` |

---

## Root Cause

**Code:** `PASS`

**Summary:** All checks passed — no connectivity issue detected.

**Recommended Action:** No action needed — all checks passed.

---

## Checks

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | `frontend_api_url_discovery` | ✅ pass | C:\HB TRACK\Hb Track - Frontend\.env.local:NEXT_PUBLIC_API_URL=http://191.252.185.34:8000/api/v1 |
| 2 | `frontend_api_url_topology_check` | ✅ pass | URL 'http://191.252.185.34:8000/api/v1' é compatível com a topologia (is_local=False, is_remote_target=True) |
| 3 | `api_url_parse` | ✅ pass | scheme=http; host=191.252.185.34; port=8000; base_path=/api/v1 |
| 4 | `dns_resolution` | ✅ pass | 191.252.185.34 -> 191.252.185.34 |
| 5 | `tcp_connectivity` | ✅ pass | 191.252.185.34:8000 reachable |
| 6 | `tls_validation` | ⏭️ skip | Skipped: scheme is http |
| 7 | `http_health_reachability` | ✅ pass | GET http://191.252.185.34:8000/api/v1/health -> 200 |
| 8 | `protocol_coherence` | ✅ pass | No mixed content risk: frontend_scheme=http, api_scheme=http |
| 9 | `cors_preflight` | ✅ pass | url=http://191.252.185.34:8000/api/v1/health; request_origin=http://localhost:3000; response_allow_origin=http://loca... |
| 10 | `backend_health_schema` | ✅ pass | url=http://191.252.185.34:8000/api/v1/health; global_status=healthy; database_status=healthy |
| 11 | `backend_readiness` | ✅ pass | url=http://191.252.185.34:8000/api/v1/health/readiness; status_code=200 |
| 12 | `backend_dependency_inference` | ✅ pass | database_status=healthy; note=Redis/queue not monitored canonically — not inferred |
