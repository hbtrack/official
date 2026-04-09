"""
Replay Pack — Ciclo 2: Equipe e Temporada

Cobre: teams, seasons

Endpoints principais:
  POST /api/teams/                           → criar equipe
  POST /api/seasons/                         → criar temporada
  POST /api/seasons/{id}/teams/{id}/         → vincular equipe à temporada
  POST /api/teams/{id}/athletes/{id}/        → adicionar atleta à equipe
"""
from __future__ import annotations

from .common import SEED_ORG_ID, SEED_CATEGORY_LABEL

CYCLE_ID = "ciclo2_equipe_temporada"
CYCLE_MODULES = ["teams", "seasons"]

ENDPOINTS = [
    {"method": "POST", "path": "/api/teams/",                    "name": "teams_create"},
    {"method": "POST", "path": "/api/seasons/",                  "name": "seasons_create"},
    {"method": "POST", "path": "/api/seasons/{id}/teams/{id}/",  "name": "seasons_add_team"},
    {"method": "POST", "path": "/api/teams/{id}/athletes/{id}/", "name": "teams_add_athlete"},
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

    # 1. Criar equipe
    r = client.post(
        f"{base_url}/api/teams/",
        json={
            "organizationId": SEED_ORG_ID,
            "name": "Replay Team",
            "categoryLabel": SEED_CATEGORY_LABEL,
        },
        headers=auth_header,
    )
    results.append({"step": "teams_create", "status_code": r.status_code})
    assert r.status_code in (200, 201), f"teams_create falhou: {r.status_code}"
    team_id = r.json().get("id")

    # 2. Criar temporada
    r = client.post(
        f"{base_url}/api/seasons/",
        json={"name": "Temporada Replay 2024", "startDate": "2024-01-01", "endDate": "2024-12-31"},
        headers=auth_header,
    )
    results.append({"step": "seasons_create", "status_code": r.status_code})
    assert r.status_code in (200, 201), f"seasons_create falhou: {r.status_code}"
    season_id = r.json().get("id")

    # 3. Vincular equipe à temporada
    r = client.post(
        f"{base_url}/api/seasons/{season_id}/teams/{team_id}/",
        headers=auth_header,
    )
    results.append({"step": "seasons_add_team", "status_code": r.status_code})
    assert r.status_code in (200, 201, 204), f"seasons_add_team falhou: {r.status_code}"

    return {"cycle": CYCLE_ID, "steps": results, "status": "PASS"}
