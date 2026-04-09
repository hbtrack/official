"""
Replay Pack — Ciclo 1: Identidade e Acesso

Cobre: identity_access, users, audit

Endpoints principais:
  POST /api/auth/login    → obter JWT (authLogin, retorna accessToken)
  POST /api/auth/refresh  → renovar JWT (authRefreshToken)
  GET  /api/auth/me       → sessão do usuário autenticado
  GET  /api/audit/logs/   → listar logs de auditoria
"""
from __future__ import annotations

CYCLE_ID = "ciclo1_identidade_acesso"
CYCLE_MODULES = ["identity_access", "users", "audit"]

ENDPOINTS = [
    {"method": "POST", "path": "/api/auth/login",   "name": "auth_login"},
    {"method": "POST", "path": "/api/auth/refresh", "name": "auth_refresh"},
    {"method": "GET",  "path": "/api/auth/me",      "name": "auth_me"},
    {"method": "GET",  "path": "/api/audit/logs/",  "name": "audit_logs"},
]


def describe() -> dict:
    return {
        "cycle_id": CYCLE_ID,
        "modules": CYCLE_MODULES,
        "endpoints": ENDPOINTS,
    }


def run_live(client, base_url: str, credentials: dict) -> dict:
    """Executa replay contra staging live. Requer HB_STAGING_URL."""
    results = []

    # 1. Autenticação
    r = client.post(
        f"{base_url}/api/auth/login",
        json={"email": credentials["email"], "password": credentials["password"]},
    )
    results.append({"step": "auth_login", "status_code": r.status_code})
    assert r.status_code == 200, f"auth/login falhou: {r.status_code}"
    data = r.json()
    assert "accessToken" in data, "Resposta sem campo 'accessToken'"
    access_token = data["accessToken"]

    # 2. Sessão do usuário autenticado
    r = client.get(
        f"{base_url}/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    results.append({"step": "auth_me", "status_code": r.status_code})
    assert r.status_code == 200, f"auth/me falhou: {r.status_code}"

    # 3. Logs de auditoria
    r = client.get(
        f"{base_url}/api/audit/logs/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    results.append({"step": "audit_logs", "status_code": r.status_code})
    assert r.status_code in (200, 403), f"audit/logs status inesperado: {r.status_code}"

    return {"cycle": CYCLE_ID, "steps": results, "status": "PASS"}
