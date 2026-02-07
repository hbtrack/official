"""
E2E - Training module core flows (sem dependência de Celery schedule)

Escopo:
- Criar sessão draft -> publish
- Bulk add + reorder exercícios
- Attendance batch
- Wellness pre/post (respeitando janela temporal)
- CRUD de session_templates (+ validação foco <=120)
- Analytics team endpoints (FR-012)
"""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import text

from app.core.db import engine


def _get_auth_context(auth_client):
    resp = auth_client.get("/api/v1/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("organization_id"), "organization_id ausente em /auth/me"
    assert data.get("membership_id"), "membership_id ausente em /auth/me"
    return data


def _get_first_team_athlete(auth_client, team_id: str, headers: dict):
    resp = auth_client.get(
        "/api/v1/athletes",
        params={"team_id": team_id, "has_team": True, "limit": 1},
        headers=headers,
    )
    if resp.status_code != 200:
        pytest.fail(f"Falha ao listar atletas: {resp.status_code} {resp.text}")
    items = resp.json().get("items", [])
    if not items:
        pytest.fail(
            "Pré-requisito ausente: nenhum atleta encontrado para o time. "
            "Crie pelo menos 1 atleta no módulo Athletes para o team_id usado no teste."
        )
    return items[0]["id"]


def _create_exercise(auth_client, headers: dict, name: str):
    payload = {
        "name": name,
        "description": "E2E exercise",
        "category": "E2E",
    }
    resp = auth_client.post("/api/v1/exercises", json=payload, headers=headers)
    assert resp.status_code == 201, f"Falha ao criar exercício: {resp.status_code} {resp.text}"
    return resp.json()["id"]


def _force_pending_review(session_id: str) -> None:
    """
    Coloca a sessão em pending_review diretamente no banco.
    Necessário porque não há endpoint público para essa transição.
    """
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE training_sessions SET status = 'pending_review' WHERE id = :id"),
            {"id": session_id},
        )


def test_training_flow_e2e(treinador_auth_client, treinador_team_id):
    auth_ctx = _get_auth_context(treinador_auth_client)
    team_id = str(treinador_team_id)
    org_id = auth_ctx["organization_id"]
    membership_id = auth_ctx["membership_id"]
    headers = {"x-organization-id": org_id}

    athlete_id = _get_first_team_athlete(treinador_auth_client, team_id, headers)
    exercise_id_1 = _create_exercise(treinador_auth_client, headers, f"E2E Exercise {uuid4()}")
    exercise_id_2 = _create_exercise(treinador_auth_client, headers, f"E2E Exercise {uuid4()}")

    session_at = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()
    create_payload = {
        "organization_id": org_id,
        "team_id": team_id,
        "session_at": session_at,
        "session_type": "quadra",
        "main_objective": "E2E - objetivo principal",
        "duration_planned_minutes": 90,
        "location": "Ginásio E2E",
    }
    create_resp = treinador_auth_client.post("/api/v1/training-sessions", json=create_payload, headers=headers)
    assert create_resp.status_code == 201, create_resp.text
    session_id = create_resp.json()["id"]

    publish_resp = treinador_auth_client.post(
        f"/api/v1/training-sessions/{session_id}/publish",
        json={},
        headers=headers,
    )
    assert publish_resp.status_code == 200, publish_resp.text

    # Attendance só é permitido em pending_review
    _force_pending_review(session_id)

    bulk_payload = {
        "exercises": [
            {"exercise_id": exercise_id_1, "order_index": 0, "duration_minutes": 15, "notes": "Aquecimento"},
            {"exercise_id": exercise_id_2, "order_index": 1, "duration_minutes": 20, "notes": "Parte principal"},
        ]
    }
    bulk_resp = treinador_auth_client.post(
        f"/api/v1/training-sessions/{session_id}/exercises/bulk",
        json=bulk_payload,
        headers=headers,
    )
    assert bulk_resp.status_code == 201, bulk_resp.text
    session_exercises = bulk_resp.json()
    assert len(session_exercises) >= 2

    reorder_payload = {
        "reorders": [
            {"id": session_exercises[0]["id"], "order_index": 1},
            {"id": session_exercises[1]["id"], "order_index": 0},
        ]
    }
    reorder_resp = treinador_auth_client.patch(
        f"/api/v1/training-sessions/{session_id}/exercises/reorder",
        json=reorder_payload,
        headers=headers,
    )
    assert reorder_resp.status_code == 200, reorder_resp.text

    attendance_payload = [
        {
            "athlete_id": athlete_id,
            "presence_status": "present",
            "participation_type": "full",
            "minutes_effective": 90,
            "comment": "Presença E2E",
        }
    ]
    attendance_resp = treinador_auth_client.post(
        f"/api/v1/training_sessions/{session_id}/attendance/batch",
        json=attendance_payload,
        headers=headers,
    )
    assert attendance_resp.status_code == 201, attendance_resp.text

    wellness_pre_payload = {
        "athlete_id": athlete_id,
        "organization_id": org_id,
        "created_by_membership_id": membership_id,
        "sleep_hours": 7.5,
        "sleep_quality": 4,
        "fatigue": 3,
        "stress": 2,
        "muscle_soreness": 4,
        "pain": False,
    }
    wellness_pre_resp = treinador_auth_client.post(
        f"/api/v1/wellness-pre/training_sessions/{session_id}/wellness_pre",
        json=wellness_pre_payload,
        headers=headers,
    )
    assert wellness_pre_resp.status_code == 201, wellness_pre_resp.text

    wellness_post_payload = {
        "athlete_id": athlete_id,
        "organization_id": org_id,
        "created_by_membership_id": membership_id,
        "session_rpe": 7,
        "minutes_effective": 60,
        "fatigue_after": 6,
        "mood_after": 7,
    }
    wellness_post_resp = treinador_auth_client.post(
        f"/api/v1/wellness-post/training_sessions/{session_id}/wellness_post",
        json=wellness_post_payload,
        headers=headers,
    )
    assert wellness_post_resp.status_code == 201, wellness_post_resp.text

    invalid_template_payload = {
        "name": f"E2E Template Invalid {uuid4()}",
        "focus_attack_positional_pct": 70,
        "focus_defense_positional_pct": 60,
    }
    invalid_template_resp = treinador_auth_client.post(
        "/api/v1/session-templates",
        json=invalid_template_payload,
        headers=headers,
    )
    assert invalid_template_resp.status_code == 422, invalid_template_resp.text

    valid_template_payload = {
        "name": f"E2E Template Valid {uuid4()}",
        "focus_attack_positional_pct": 60,
        "focus_defense_positional_pct": 40,
        "icon": "target",
    }
    create_template_resp = treinador_auth_client.post(
        "/api/v1/session-templates",
        json=valid_template_payload,
        headers=headers,
    )
    assert create_template_resp.status_code == 201, create_template_resp.text
    template_id = create_template_resp.json()["id"]

    update_template_resp = treinador_auth_client.patch(
        f"/api/v1/session-templates/{template_id}",
        json={"name": "E2E Template Updated"},
        headers=headers,
    )
    assert update_template_resp.status_code == 200, update_template_resp.text

    favorite_resp = treinador_auth_client.patch(
        f"/api/v1/session-templates/{template_id}/favorite",
        json={},
        headers=headers,
    )
    assert favorite_resp.status_code == 200, favorite_resp.text

    delete_resp = treinador_auth_client.delete(
        f"/api/v1/session-templates/{template_id}",
        headers=headers,
    )
    assert delete_resp.status_code == 204, delete_resp.text

    analytics_paths = [
        f"/api/v1/analytics/team/{team_id}/summary",
        f"/api/v1/analytics/team/{team_id}/weekly-load",
        f"/api/v1/analytics/team/{team_id}/deviation-analysis",
        f"/api/v1/analytics/team/{team_id}/prevention-effectiveness",
    ]
    for path in analytics_paths:
        resp = treinador_auth_client.get(path, headers=headers)
        assert resp.status_code == 200, f"{path} -> {resp.status_code}: {resp.text}"
