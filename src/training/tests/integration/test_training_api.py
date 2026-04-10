"""
Testes de integração das ondas B/C do módulo training.
Cobrem attendance, wellness, periodização, execution records e objectives com banco real.
"""

from __future__ import annotations

import sys
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from training.domain.entities import (
    AttentionQueueItem,
    Recommendation,
    RecommendationActionType,
    RecommendationPriority,
    RecommendationStatus,
    TrainingSession,
    TrainingSessionStatus,
)
from training.infrastructure.repository import (
    AttentionQueueRepository,
    RecommendationRepository,
    TrainingSessionRepository,
)


pytestmark = pytest.mark.django_db


def _pick(data: dict, snake: str, camel: str):
    if camel in data:
        return data[camel]
    return data[snake]


def _create_session(
    *,
    status: TrainingSessionStatus = TrainingSessionStatus.DRAFT,
    session_at: datetime | None = None,
) -> TrainingSession:
    now = datetime.now(tz=timezone.utc)
    session = TrainingSession(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        session_at=session_at or (now + timedelta(hours=4)),
        session_type="TACTICAL",
        status=status,
        created_by_user_id=uuid.uuid4(),
        created_at=now,
        updated_at=now,
    )
    return TrainingSessionRepository().save(session)


class TestAttendanceEndpoints:
    def test_record_and_list_attendance(self, client):
        session = _create_session()
        athlete_id = uuid.uuid4()

        response = client.post(
            f"/api/training/training-sessions/{session.id}/attendance",
            data={
                "athlete_id": str(athlete_id),
                "status": "PRESENT",
                "source": "coach_input",
            },
            content_type="application/json",
        )

        assert response.status_code == 201
        payload = response.json()
        assert _pick(payload, "status", "status") == "PRESENT"
        assert _pick(payload, "athlete_id", "athleteId") == str(athlete_id)

        list_response = client.get(f"/api/training/training-sessions/{session.id}/attendance")
        assert list_response.status_code == 200
        items = list_response.json()["items"]
        assert len(items) == 1
        assert _pick(items[0], "status", "status") == "PRESENT"

    def test_athlete_can_preconfirm_own_attendance_only(self, client, monkeypatch):
        athlete_id = uuid.UUID("20000000-0000-0000-0000-000000000001")
        session = _create_session(session_at=datetime.now(tz=timezone.utc) + timedelta(hours=5))

        training_api = sys.modules.get("training.api")
        if training_api is None:
            import training.api as training_api

        monkeypatch.setattr(training_api, "_get_actor_role", lambda req: training_api.RoleLabel.ATHLETE)
        monkeypatch.setattr(training_api, "_get_actor_id", lambda req: athlete_id)

        allowed = client.post(
            f"/api/training/training-sessions/{session.id}/attendance",
            data={
                "athlete_id": str(athlete_id),
                "status": "PRECONFIRMED",
                "source": "athlete_selfcheck",
            },
            content_type="application/json",
        )
        assert allowed.status_code == 201

        forbidden = client.post(
            f"/api/training/training-sessions/{session.id}/attendance",
            data={
                "athlete_id": str(athlete_id),
                "status": "PRESENT",
                "source": "athlete_selfcheck",
            },
            content_type="application/json",
        )
        assert forbidden.status_code == 403


class TestWellnessEndpoints:
    def test_get_and_update_wellness_pre(self, client):
        athlete_id = uuid.uuid4()
        session = _create_session(session_at=datetime.now(tz=timezone.utc) + timedelta(hours=5))

        create_resp = client.post(
            f"/api/training/training-sessions/{session.id}/wellness-pre",
            data={
                "athlete_id": str(athlete_id),
                "sleep_quality": 3,
                "readiness": 4,
            },
            content_type="application/json",
        )
        assert create_resp.status_code == 201

        get_resp = client.get(
            f"/api/training/training-sessions/{session.id}/wellness-pre/{athlete_id}"
        )
        assert get_resp.status_code == 200
        assert _pick(get_resp.json(), "athlete_id", "athleteId") == str(athlete_id)

        patch_resp = client.patch(
            f"/api/training/training-sessions/{session.id}/wellness-pre/{athlete_id}",
            data={"sleep_quality": 5, "notes": "updated"},
            content_type="application/json",
        )
        assert patch_resp.status_code == 200
        assert _pick(patch_resp.json(), "sleep_quality", "sleepQuality") == 5

    def test_get_and_update_wellness_post(self, client):
        athlete_id = uuid.uuid4()
        session = _create_session(status=TrainingSessionStatus.IN_PROGRESS)

        create_resp = client.post(
            f"/api/training/training-sessions/{session.id}/wellness-post",
            data={
                "athlete_id": str(athlete_id),
                "perceived_exertion": 6,
                "enjoyment": 4,
                "technical_learning": 5,
            },
            content_type="application/json",
        )
        assert create_resp.status_code == 201

        get_resp = client.get(
            f"/api/training/training-sessions/{session.id}/wellness-post/{athlete_id}"
        )
        assert get_resp.status_code == 200
        assert _pick(get_resp.json(), "athlete_id", "athleteId") == str(athlete_id)

        patch_resp = client.patch(
            f"/api/training/training-sessions/{session.id}/wellness-post/{athlete_id}",
            data={"perceived_exertion": 7, "notes": "adjusted"},
            content_type="application/json",
        )
        assert patch_resp.status_code == 200
        assert _pick(patch_resp.json(), "perceived_exertion", "perceivedExertion") == 7


class TestPlanningEndpoints:
    def test_create_get_and_update_mesocycle(self, client):
        started_at = datetime.now(tz=timezone.utc) + timedelta(days=1)
        ended_at = started_at + timedelta(days=21)

        create_resp = client.post(
            "/api/training/mesocycles",
            data={
                "organization_id": str(uuid.uuid4()),
                "name": "Base 1",
                "started_at": started_at.isoformat(),
                "ended_at": ended_at.isoformat(),
                "objective": "Construir base física",
            },
            content_type="application/json",
        )
        assert create_resp.status_code == 201
        mesocycle_id = create_resp.json()["id"]

        get_resp = client.get(f"/api/training/mesocycles/{mesocycle_id}")
        assert get_resp.status_code == 200
        assert _pick(get_resp.json(), "name", "name") == "Base 1"

        patch_resp = client.patch(
            f"/api/training/mesocycles/{mesocycle_id}",
            data={"name": "Base 1 ajustada", "notes": "replanejado"},
            content_type="application/json",
        )
        assert patch_resp.status_code == 200
        assert _pick(patch_resp.json(), "name", "name") == "Base 1 ajustada"

    def test_create_get_and_update_microcycle(self, client):
        meso_create = client.post(
            "/api/training/mesocycles",
            data={
                "organization_id": str(uuid.uuid4()),
                "name": "Competição",
                "started_at": (datetime.now(tz=timezone.utc) + timedelta(days=1)).isoformat(),
                "ended_at": (datetime.now(tz=timezone.utc) + timedelta(days=28)).isoformat(),
            },
            content_type="application/json",
        )
        assert meso_create.status_code == 201
        mesocycle_id = meso_create.json()["id"]

        create_resp = client.post(
            "/api/training/microcycles",
            data={
                "organization_id": str(uuid.uuid4()),
                "mesocycle_id": mesocycle_id,
                "week_number": 1,
                "started_at": (datetime.now(tz=timezone.utc) + timedelta(days=1)).isoformat(),
                "ended_at": (datetime.now(tz=timezone.utc) + timedelta(days=7)).isoformat(),
                "planned_sessions_count": 4,
            },
            content_type="application/json",
        )
        assert create_resp.status_code == 201
        microcycle_id = create_resp.json()["id"]

        get_resp = client.get(f"/api/training/microcycles/{microcycle_id}")
        assert get_resp.status_code == 200
        assert _pick(get_resp.json(), "week_number", "weekNumber") == 1

        patch_resp = client.patch(
            f"/api/training/microcycles/{microcycle_id}",
            data={"name": "Semana 1", "planned_sessions_count": 5},
            content_type="application/json",
        )
        assert patch_resp.status_code == 200
        assert _pick(patch_resp.json(), "planned_sessions_count", "plannedSessionsCount") == 5


class TestExecutionAndObjectivesEndpoints:
    def test_create_list_and_get_execution_record(self, client):
        session = _create_session(status=TrainingSessionStatus.IN_PROGRESS)

        create_resp = client.post(
            f"/api/training/training-sessions/{session.id}/execution-records",
            data={
                "execution_type": "SESSION_EXECUTION",
                "recorded_at": datetime.now(tz=timezone.utc).isoformat(),
                "planned_value": 10,
                "actual_value": 9,
            },
            content_type="application/json",
        )
        assert create_resp.status_code == 201
        record_id = create_resp.json()["id"]

        list_resp = client.get(f"/api/training/training-sessions/{session.id}/execution-records")
        assert list_resp.status_code == 200
        assert len(list_resp.json()["data"]) == 1

        get_resp = client.get(
            f"/api/training/training-sessions/{session.id}/execution-records/{record_id}"
        )
        assert get_resp.status_code == 200
        assert _pick(get_resp.json(), "id", "id") == record_id

    def test_create_and_list_session_objectives(self, client):
        session = _create_session()

        create_resp = client.post(
            f"/api/training/training-sessions/{session.id}/objectives",
            data={
                "origin": "COMPETITIVE_FOCUS",
                "objective_type": "TACTICAL",
                "description": "Aumentar qualidade da transição ofensiva",
                "priority": 1,
            },
            content_type="application/json",
        )
        assert create_resp.status_code == 201

        list_resp = client.get(f"/api/training/training-sessions/{session.id}/objectives")
        assert list_resp.status_code == 200
        items = list_resp.json()["data"]
        assert len(items) == 1
        assert _pick(items[0], "objective_type", "objectiveType") == "TACTICAL"


class TestFeedbackAndAttentionEndpoints:
    def test_create_list_and_close_feedback_thread(self, client):
        session = _create_session()

        create_resp = client.post(
            f"/api/training/training-sessions/{session.id}/feedback-threads",
            data={
                "context_type": "SESSION",
                "context_ref_id": str(session.id),
                "conversation_outcome": "REFLECTION_DOCUMENTED",
                "content": "Boa execução coletiva",
            },
            content_type="application/json",
        )
        assert create_resp.status_code == 201
        thread_id = create_resp.json()["id"]

        list_resp = client.get(f"/api/training/training-sessions/{session.id}/feedback-threads")
        assert list_resp.status_code == 200
        assert len(list_resp.json()["data"]) == 1

        close_resp = client.post(
            f"/api/training/training-sessions/{session.id}/feedback-threads/{thread_id}/close",
            data={"resolution_summary": "Intervenção concluída e alinhada"},
            content_type="application/json",
        )
        assert close_resp.status_code == 200
        assert _pick(close_resp.json(), "decision_text", "decisionText") == "Intervenção concluída e alinhada"

    def test_list_and_action_attention_queue(self, client):
        session = _create_session()
        repo = AttentionQueueRepository()
        resolve_item = repo.save(
            AttentionQueueItem(
                id=uuid.uuid4(),
                session_id=session.id,
                athlete_id=uuid.uuid4(),
                reason="WELLNESS_ALERT",
                severity="HIGH",
                notes="Sono abaixo do limiar",
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc),
            )
        )
        dismiss_item = repo.save(
            AttentionQueueItem(
                id=uuid.uuid4(),
                session_id=session.id,
                athlete_id=uuid.uuid4(),
                reason="OVERLOAD_RISK",
                severity="MEDIUM",
                notes="Carga acumulada elevada",
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc),
            )
        )
        escalate_item = repo.save(
            AttentionQueueItem(
                id=uuid.uuid4(),
                session_id=session.id,
                athlete_id=uuid.uuid4(),
                reason="RETURN_TO_PLAY_GUARD",
                severity="CRITICAL",
                notes="Necessita avaliação adicional",
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc),
            )
        )

        list_resp = client.get(f"/api/training/training-sessions/{session.id}/attention-queue")
        assert list_resp.status_code == 200
        assert len(list_resp.json()["data"]) == 3

        resolve_resp = client.post(
            f"/api/training/training-sessions/{session.id}/attention-queue/{resolve_item.id}/resolve",
            data={"resolution_evidence": "Coach revisou e ajustou a sessão"},
            content_type="application/json",
        )
        assert resolve_resp.status_code == 200
        assert _pick(resolve_resp.json(), "resolved_by_user_id", "resolvedByUserId") is not None

        dismiss_resp = client.post(
            f"/api/training/training-sessions/{session.id}/attention-queue/{dismiss_item.id}/dismiss",
            data={"dismissal_reason": "Alerta tratado em revisão prévia"},
            content_type="application/json",
        )
        assert dismiss_resp.status_code == 200

        escalate_resp = client.post(
            f"/api/training/training-sessions/{session.id}/attention-queue/{escalate_item.id}/escalate",
            data={
                "escalation_target": "MEDICAL",
                "escalation_note": "Encaminhar para avaliação clínica",
            },
            content_type="application/json",
        )
        assert escalate_resp.status_code == 200


class TestRecommendationsAndIneligibilityEndpoints:
    def test_list_accept_and_dismiss_recommendations(self, client):
        session = _create_session()
        repo = RecommendationRepository()

        accepted_target = repo.save(
            Recommendation(
                id=uuid.uuid4(),
                session_id=session.id,
                generated_by_rule="OVERLOAD_RISK_CONSECUTIVE_HIGH_SESSIONS",
                action_type=RecommendationActionType.ADJUST_LOAD,
                description="Reduzir carga da sessão",
                status=RecommendationStatus.PENDING,
                priority=RecommendationPriority.HIGH,
                generated_by_module="ai_ingestion",
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc),
            )
        )
        dismissed_target = repo.save(
            Recommendation(
                id=uuid.uuid4(),
                session_id=session.id,
                generated_by_rule="ADHERENCE_DROP_LAST_WEEK",
                action_type=RecommendationActionType.REVIEW_ATHLETE,
                description="Revisar aderência do atleta",
                status=RecommendationStatus.PENDING,
                priority=RecommendationPriority.MEDIUM,
                generated_by_module="analytics",
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc),
            )
        )

        list_resp = client.get(f"/api/training/training-sessions/{session.id}/recommendations")
        assert list_resp.status_code == 200
        assert len(list_resp.json()["data"]) == 2

        accept_resp = client.post(
            f"/api/training/training-sessions/{session.id}/recommendations/{accepted_target.id}/accept",
            data={"coach_note": "Aceito para esta semana"},
            content_type="application/json",
        )
        assert accept_resp.status_code == 200
        assert _pick(accept_resp.json(), "status", "status") == "ACCEPTED"

        dismiss_resp = client.post(
            f"/api/training/training-sessions/{session.id}/recommendations/{dismissed_target.id}/dismiss",
            data={"dismissal_reason": "Contexto atual não exige intervenção"},
            content_type="application/json",
        )
        assert dismiss_resp.status_code == 200
        assert _pick(dismiss_resp.json(), "status", "status") == "DISMISSED"

    def test_submit_and_get_ineligibility(self, client, monkeypatch):
        athlete_id = uuid.UUID("30000000-0000-0000-0000-000000000001")
        session = _create_session(status=TrainingSessionStatus.PUBLISHED)

        training_api = sys.modules.get("training.api")
        if training_api is None:
            import training.api as training_api

        monkeypatch.setattr(training_api, "_get_actor_role", lambda req: training_api.RoleLabel.ATHLETE)
        monkeypatch.setattr(training_api, "_get_actor_id", lambda req: athlete_id)

        submit_resp = client.post(
            f"/api/training/training-sessions/{session.id}/ineligibility",
            data={
                "athlete_id": str(athlete_id),
                "reason_flags": ["INJURY_PAIN"],
            },
            content_type="application/json",
        )
        assert submit_resp.status_code == 201
        assert _pick(submit_resp.json(), "athlete_id", "athleteId") == str(athlete_id)

        get_resp = client.get(f"/api/training/training-sessions/{session.id}/ineligibility")
        assert get_resp.status_code == 200
        assert _pick(get_resp.json(), "reason_flags", "reasonFlags") == ["INJURY_PAIN"]
