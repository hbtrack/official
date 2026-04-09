"""
Replay Pack — Ciclo 5: Treino e Wellness

Cobre: training, wellness, medical, exercises

Endpoints principais:
  POST /api/training-sessions/                        → criar sessão de treino
  POST /api/training-sessions/{id}/wellness-pre/      → registrar wellness pré-treino
  POST /api/wellness/entries/                         → registrar entrada de wellness
"""
from __future__ import annotations

CYCLE_ID = "ciclo5_treino_wellness"
CYCLE_MODULES = ["training", "wellness", "medical", "exercises"]

ENDPOINTS = [
    {"method": "POST", "path": "/api/training-sessions/",                    "name": "training_sessions_create"},
    {"method": "POST", "path": "/api/training-sessions/{id}/wellness-pre/",  "name": "training_wellness_pre"},
    {"method": "POST", "path": "/api/wellness/entries/",                     "name": "wellness_entries_create"},
]


def describe() -> dict:
    return {
        "cycle_id": CYCLE_ID,
        "modules": CYCLE_MODULES,
        "endpoints": ENDPOINTS,
    }


def run_live(client, base_url: str, auth_header: dict, team_id: str) -> dict:
    """Executa replay contra staging live. Requer HB_STAGING_URL."""
    results = []

    # 1. Criar sessão de treino
    r = client.post(
        f"{base_url}/api/training-sessions/",
        json={
            "team": team_id,
            "date": "2024-06-10",
            "duration_minutes": 90,
            "type": "TECHNICAL",
        },
        headers=auth_header,
    )
    results.append({"step": "training_sessions_create", "status_code": r.status_code})
    assert r.status_code in (200, 201), f"training_sessions_create falhou: {r.status_code}"
    session_id = r.json().get("id")

    # 2. Wellness pré-treino
    r = client.post(
        f"{base_url}/api/training-sessions/{session_id}/wellness-pre/",
        json={"fatigue": 3, "mood": 4, "sleep_quality": 4, "muscle_soreness": 2},
        headers=auth_header,
    )
    results.append({"step": "training_wellness_pre", "status_code": r.status_code})
    assert r.status_code in (200, 201), f"training_wellness_pre falhou: {r.status_code}"

    # 3. Entrada de wellness geral
    r = client.post(
        f"{base_url}/api/wellness/entries/",
        json={
            "date": "2024-06-10",
            "fatigue": 3,
            "mood": 4,
            "sleep_hours": 8.0,
            "sleep_quality": 4,
        },
        headers=auth_header,
    )
    results.append({"step": "wellness_entries_create", "status_code": r.status_code})
    assert r.status_code in (200, 201), f"wellness_entries_create falhou: {r.status_code}"

    return {"cycle": CYCLE_ID, "steps": results, "status": "PASS"}
