"""
Replay Pack — Ciclo 3: Partida e Competição

Cobre: matches, competitions

Endpoints principais:
  POST   /api/competitions/                    → criar competição
  POST   /api/competitions/{id}/teams/{id}/    → inscrever equipe
  POST   /api/matches/                         → criar partida
  PATCH  /api/matches/{id}/                    → atualizar resultado
"""
from __future__ import annotations

CYCLE_ID = "ciclo3_partida_competicao"
CYCLE_MODULES = ["matches", "competitions"]

ENDPOINTS = [
    {"method": "POST",  "path": "/api/competitions/",                 "name": "competitions_create"},
    {"method": "POST",  "path": "/api/competitions/{id}/teams/{id}/", "name": "competitions_add_team"},
    {"method": "POST",  "path": "/api/matches/",                      "name": "matches_create"},
    {"method": "PATCH", "path": "/api/matches/{id}/",                 "name": "matches_update"},
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

    # 1. Criar competição
    r = client.post(
        f"{base_url}/api/competitions/",
        json={"name": "Copa Replay 2024", "type": "LEAGUE", "gender": "M"},
        headers=auth_header,
    )
    results.append({"step": "competitions_create", "status_code": r.status_code})
    assert r.status_code in (200, 201), f"competitions_create falhou: {r.status_code}"
    comp_id = r.json().get("id")

    # 2. Inscrever equipe
    r = client.post(
        f"{base_url}/api/competitions/{comp_id}/teams/{team_id}/",
        headers=auth_header,
    )
    results.append({"step": "competitions_add_team", "status_code": r.status_code})
    assert r.status_code in (200, 201, 204), f"competitions_add_team falhou: {r.status_code}"

    # 3. Criar partida
    r = client.post(
        f"{base_url}/api/matches/",
        json={
            "competition": comp_id,
            "home_team": team_id,
            "away_team": team_id,
            "scheduled_at": "2024-06-01T15:00:00Z",
        },
        headers=auth_header,
    )
    results.append({"step": "matches_create", "status_code": r.status_code})
    assert r.status_code in (200, 201), f"matches_create falhou: {r.status_code}"
    match_id = r.json().get("id")

    # 4. Atualizar resultado
    r = client.patch(
        f"{base_url}/api/matches/{match_id}/",
        json={"home_score": 28, "away_score": 25, "status": "FINISHED"},
        headers=auth_header,
    )
    results.append({"step": "matches_update", "status_code": r.status_code})
    assert r.status_code in (200, 204), f"matches_update falhou: {r.status_code}"

    return {"cycle": CYCLE_ID, "steps": results, "status": "PASS"}
