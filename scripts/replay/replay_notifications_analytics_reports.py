"""
Replay Pack — Ciclo 6: Notificações, Analytics e Relatórios

Cobre: notifications, analytics, reports, ai_ingestion

Endpoints principais:
  POST /api/notifications/intents/      → criar intenção de notificação
  POST /api/analytics/snapshots/        → criar snapshot analítico
  POST /api/reports/jobs/               → criar job de relatório
"""
from __future__ import annotations

CYCLE_ID = "ciclo6_notificacao_analytics"
CYCLE_MODULES = ["notifications", "analytics", "reports", "ai_ingestion"]

ENDPOINTS = [
    {"method": "POST", "path": "/api/notifications/intents/", "name": "notifications_intents_create"},
    {"method": "POST", "path": "/api/analytics/snapshots/",   "name": "analytics_snapshots_create"},
    {"method": "POST", "path": "/api/reports/jobs/",          "name": "reports_jobs_create"},
]


def describe() -> dict:
    return {
        "cycle_id": CYCLE_ID,
        "modules": CYCLE_MODULES,
        "endpoints": ENDPOINTS,
    }


def run_live(client, base_url: str, auth_header: dict) -> dict:
    """Executa replay contra staging live. Requer HB_STAGING_URL."""
    results = []

    # 1. Notificação
    r = client.post(
        f"{base_url}/api/notifications/intents/",
        json={"type": "TRAINING_REMINDER", "recipient_type": "ATHLETE", "payload": {}},
        headers=auth_header,
    )
    results.append({"step": "notifications_intents_create", "status_code": r.status_code})
    assert r.status_code in (200, 201, 202), f"notifications_intents_create falhou: {r.status_code}"

    # 2. Snapshot analítico
    r = client.post(
        f"{base_url}/api/analytics/snapshots/",
        json={"snapshot_type": "TEAM_PERFORMANCE", "period": "2024-Q2"},
        headers=auth_header,
    )
    results.append({"step": "analytics_snapshots_create", "status_code": r.status_code})
    assert r.status_code in (200, 201, 202), f"analytics_snapshots_create falhou: {r.status_code}"

    # 3. Job de relatório
    r = client.post(
        f"{base_url}/api/reports/jobs/",
        json={"report_type": "SEASON_SUMMARY", "format": "PDF", "filters": {}},
        headers=auth_header,
    )
    results.append({"step": "reports_jobs_create", "status_code": r.status_code})
    assert r.status_code in (200, 201, 202), f"reports_jobs_create falhou: {r.status_code}"

    return {"cycle": CYCLE_ID, "steps": results, "status": "PASS"}
