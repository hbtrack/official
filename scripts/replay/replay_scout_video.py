"""
Replay Pack — Ciclo 4: Scout e Vídeo

Cobre: scout, video

Endpoints principais:
  POST /api/video/sessions/                        → criar sessão de vídeo
  POST /api/scout/events/                          → registrar evento de scout
  POST /api/scout/sessions/{match_id}/complete/    → finalizar sessão scout
"""
from __future__ import annotations

CYCLE_ID = "ciclo4_scout_video"
CYCLE_MODULES = ["scout", "video"]

ENDPOINTS = [
    {"method": "POST", "path": "/api/video/sessions/",                     "name": "video_sessions_create"},
    {"method": "POST", "path": "/api/scout/events/",                       "name": "scout_events_create"},
    {"method": "POST", "path": "/api/scout/sessions/{match_id}/complete/", "name": "scout_sessions_complete"},
]


def describe() -> dict:
    return {
        "cycle_id": CYCLE_ID,
        "modules": CYCLE_MODULES,
        "endpoints": ENDPOINTS,
    }


def run_live(client, base_url: str, auth_header: dict, match_id: str) -> dict:
    """Executa replay contra staging live. Requer HB_STAGING_URL."""
    results = []

    # 1. Criar sessão de vídeo
    r = client.post(
        f"{base_url}/api/video/sessions/",
        json={"match": match_id, "source": "CAMERA_1", "duration_seconds": 3600},
        headers=auth_header,
    )
    results.append({"step": "video_sessions_create", "status_code": r.status_code})
    assert r.status_code in (200, 201), f"video_sessions_create falhou: {r.status_code}"

    # 2. Registrar evento de scout
    r = client.post(
        f"{base_url}/api/scout/events/",
        json={
            "match": match_id,
            "event_type": "GOAL",
            "minute": 15,
            "period": 1,
        },
        headers=auth_header,
    )
    results.append({"step": "scout_events_create", "status_code": r.status_code})
    assert r.status_code in (200, 201), f"scout_events_create falhou: {r.status_code}"

    # 3. Finalizar sessão scout
    r = client.post(
        f"{base_url}/api/scout/sessions/{match_id}/complete/",
        json={"events_count": 42},
        headers=auth_header,
    )
    results.append({"step": "scout_sessions_complete", "status_code": r.status_code})
    assert r.status_code in (200, 201, 204), f"scout_sessions_complete falhou: {r.status_code}"

    return {"cycle": CYCLE_ID, "steps": results, "status": "PASS"}
