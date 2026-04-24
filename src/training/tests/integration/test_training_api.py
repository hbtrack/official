"""
Testes de integração das ondas B/C do módulo training.
Cobrem attendance, wellness, periodização, execution records e objectives com banco real.
"""

from __future__ import annotations

import json
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
        assert payload["status"] == "PRESENT"
        assert payload["athleteId"] == str(athlete_id)

        list_response = client.get(f"/api/training/training-sessions/{session.id}/attendance")
        assert list_response.status_code == 200
        items = list_response.json()["items"]
        assert len(items) == 1
        assert items[0]["status"] == "PRESENT"

    def test_athlete_can_preconfirm_own_attendance_only(self, client, monkeypatch):
        athlete_id = uuid.UUID("20000000-0000-0000-0000-000000000001")
        session = _create_session(session_at=datetime.now(tz=timezone.utc) + timedelta(hours=5))

        import training.api as training_api
        import training.api.attendance as _attendance_mod

        monkeypatch.setattr(_attendance_mod, "_get_actor_role", lambda req: training_api.RoleLabel.ATHLETE)
        monkeypatch.setattr(_attendance_mod, "_get_actor_id", lambda req: athlete_id)

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
        """PASSO 8 — GAP-4 + P2-GAP-3: round-trip completo dos 7 campos canônicos em camelCase."""
        athlete_id = uuid.uuid4()
        session = _create_session(session_at=datetime.now(tz=timezone.utc) + timedelta(hours=5))

        create_resp = client.post(
            f"/api/training/training-sessions/{session.id}/wellness-pre",
            data={
                "athlete_id": str(athlete_id),
                "sleep_quality": 3,
                "sleep_hours": 7.5,
                "readiness": 4,
                "mood": 3,
                "fatigue": 2,
                "muscle_soreness": 1,
                "notes": "feeling good",
            },
            content_type="application/json",
        )
        assert create_resp.status_code == 201

        get_resp = client.get(
            f"/api/training/training-sessions/{session.id}/wellness-pre/{athlete_id}"
        )
        assert get_resp.status_code == 200
        data = get_resp.json()
        # Verificar todos os 7 campos canônicos em camelCase
        assert data["athleteId"] == str(athlete_id)
        assert data["trainingSessionId"] == str(session.id)
        assert data["sleepQuality"] == 3
        assert data["sleepHours"] == 7.5
        assert data["readiness"] == 4
        assert data["mood"] == 3
        assert data["fatigue"] == 2
        assert data["muscleSoreness"] == 1
        assert data["notes"] == "feeling good"
        assert "createdAt" in data
        assert "updatedAt" in data

        patch_resp = client.patch(
            f"/api/training/training-sessions/{session.id}/wellness-pre/{athlete_id}",
            data={"sleep_quality": 5, "notes": "updated"},
            content_type="application/json",
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["sleepQuality"] == 5
        assert patch_resp.json()["notes"] == "updated"

    def test_wellness_pre_response_keys_are_camelcase(self, client):
        """PASSO 2 — garante que a resposta usa camelCase conforme contrato OpenAPI."""
        athlete_id = uuid.uuid4()
        session = _create_session(session_at=datetime.now(tz=timezone.utc) + timedelta(hours=5))

        resp = client.post(
            f"/api/training/training-sessions/{session.id}/wellness-pre",
            data={
                "athlete_id": str(athlete_id),
                "sleep_quality": 3,
                "sleep_hours": 7.5,
                "muscle_soreness": 2,
            },
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.json()
        # campos camelCase obrigatórios
        assert "trainingSessionId" in data, "session_id deve ser serializado como trainingSessionId"
        assert "sleepQuality" in data, "sleep_quality deve ser serializado como sleepQuality"
        assert "muscleSoreness" in data, "muscle_soreness deve ser serializado como muscleSoreness"
        assert "athleteId" in data, "athlete_id deve ser serializado como athleteId"
        assert "createdAt" in data, "created_at deve ser serializado como createdAt"
        # campos snake_case NÃO devem aparecer
        assert "session_id" not in data, "session_id não deve aparecer em snake_case"
        assert "sleep_quality" not in data, "sleep_quality não deve aparecer em snake_case"
        assert "muscle_soreness" not in data, "muscle_soreness não deve aparecer em snake_case"

    def test_wellness_pre_sleep_hours_range(self, client):
        """PASSO 3 — INV-TRAIN-033: sleepHours deve estar em [0, 24].

        Cobertura:
          - Valores fora do range → 422
          - Boundaries válidos → 201
          - PATCH com valor inválido → 422
        """
        athlete_id = uuid.uuid4()
        session = _create_session(session_at=datetime.now(tz=timezone.utc) + timedelta(hours=5))

        # --- Boundaries INVÁLIDOS → 422 ---
        for bad_val in [25.0, -1.0, 24.1, -0.1]:
            resp = client.post(
                f"/api/training/training-sessions/{session.id}/wellness-pre",
                data={
                    "athlete_id": str(athlete_id),
                    "sleep_quality": 3,
                    "sleep_hours": bad_val,
                },
                content_type="application/json",
            )
            assert resp.status_code == 422, (
                f"sleep_hours={bad_val} deveria retornar 422, mas retornou {resp.status_code}"
            )
            # detail pode ser string (HttpError do domínio) ou lista (Pydantic/Ninja validation)
            detail_text = str(resp.json().get("detail", ""))
            assert "sleep" in detail_text.lower(), (
                f"Mensagem de erro deve mencionar 'sleep', got: {detail_text!r}"
            )

        # --- Boundaries VÁLIDOS → 201 ---
        for valid_val in [0.0, 12.5, 24.0]:
            # usar athlete_id diferente para evitar DuplicateWellnessEntry (409)
            a_id = uuid.uuid4()
            resp = client.post(
                f"/api/training/training-sessions/{session.id}/wellness-pre",
                data={
                    "athlete_id": str(a_id),
                    "sleep_quality": 3,
                    "sleep_hours": valid_val,
                },
                content_type="application/json",
            )
            assert resp.status_code == 201, (
                f"sleep_hours={valid_val} deveria retornar 201, mas retornou {resp.status_code}: {resp.json()}"
            )

        # --- PATCH com valor inválido → 422 (P3-GAP-3) ---
        # Primeiro criar um registro válido
        athlete_patch = uuid.uuid4()
        create_resp = client.post(
            f"/api/training/training-sessions/{session.id}/wellness-pre",
            data={
                "athlete_id": str(athlete_patch),
                "sleep_quality": 3,
                "sleep_hours": 7.0,
            },
            content_type="application/json",
        )
        assert create_resp.status_code == 201

        # PATCH com sleep_hours inválido deve retornar 422
        patch_resp = client.patch(
            f"/api/training/training-sessions/{session.id}/wellness-pre/{athlete_patch}",
            data={"sleep_hours": 25.0},
            content_type="application/json",
        )
        assert patch_resp.status_code == 422, (
            f"PATCH sleep_hours=25.0 deveria retornar 422, got {patch_resp.status_code}"
        )

    def test_wellness_pre_required_fields(self, client):
        """PASSO 4 — GAP-NEW-3: sleepQuality e sleepHours são obrigatórios no POST.

        Cobertura:
          - POST sem sleepQuality → 422 + detail menciona "sleepQuality"
          - POST sem sleepHours → 422 + detail menciona "sleepHours"
          - POST com sleepQuality=0 (abaixo de ge=1) → 422 + detail menciona "sleep_quality"
          - POST com sleepQuality=6 (acima de le=5) → 422 + detail menciona "sleep_quality"

        Nota: Ninja/Pydantic usa alias camelCase para erros "Field required" (campo ausente)
        e snake_case para erros de range (ge/le), por isso as duas convenções nas asserções.
        """
        session = _create_session(session_at=datetime.now(tz=timezone.utc) + timedelta(hours=5))

        # POST sem sleepQuality → 422 + Ninja informa qual campo falta em camelCase
        resp = client.post(
            f"/api/training/training-sessions/{session.id}/wellness-pre",
            data={"athlete_id": str(uuid.uuid4()), "sleep_hours": 7.5},
            content_type="application/json",
        )
        assert resp.status_code == 422, (
            f"POST sem sleepQuality deve retornar 422, got {resp.status_code}"
        )
        assert "sleepQuality" in str(resp.json().get("detail", "")), (
            f"detail deve mencionar 'sleepQuality', got: {resp.json().get('detail')!r}"
        )

        # POST sem sleepHours → 422 + Ninja informa qual campo falta em camelCase
        resp = client.post(
            f"/api/training/training-sessions/{session.id}/wellness-pre",
            data={"athlete_id": str(uuid.uuid4()), "sleep_quality": 3},
            content_type="application/json",
        )
        assert resp.status_code == 422, (
            f"POST sem sleepHours deve retornar 422, got {resp.status_code}"
        )
        assert "sleepHours" in str(resp.json().get("detail", "")), (
            f"detail deve mencionar 'sleepHours', got: {resp.json().get('detail')!r}"
        )

        # POST com sleepQuality=0 (ge=1 violado) → 422 + Ninja menciona campo e limite
        resp = client.post(
            f"/api/training/training-sessions/{session.id}/wellness-pre",
            data={"athlete_id": str(uuid.uuid4()), "sleep_quality": 0, "sleep_hours": 7.5},
            content_type="application/json",
        )
        assert resp.status_code == 422, (
            f"POST com sleepQuality=0 deve retornar 422, got {resp.status_code}"
        )
        detail_text = str(resp.json().get("detail", ""))
        assert "sleep_quality" in detail_text, (
            f"detail deve mencionar 'sleep_quality', got: {detail_text!r}"
        )
        assert "1" in detail_text, (
            f"detail deve mencionar o limite inferior 1, got: {detail_text!r}"
        )

        # POST com sleepQuality=6 (le=5 violado) → 422 + Ninja menciona campo e limite
        resp = client.post(
            f"/api/training/training-sessions/{session.id}/wellness-pre",
            data={"athlete_id": str(uuid.uuid4()), "sleep_quality": 6, "sleep_hours": 7.5},
            content_type="application/json",
        )
        assert resp.status_code == 422, (
            f"POST com sleepQuality=6 deve retornar 422, got {resp.status_code}"
        )
        detail_text = str(resp.json().get("detail", ""))
        assert "sleep_quality" in detail_text, (
            f"detail deve mencionar 'sleep_quality', got: {detail_text!r}"
        )
        assert "5" in detail_text, (
            f"detail deve mencionar o limite superior 5, got: {detail_text!r}"
        )

    def test_wellness_pre_patch_null_field(self, client):
        """PASSO 4 — GAP-NEW-4: tri-state PATCH (ausente / valor / null explícito).

        Semântica implementada:
          - campo ausente     → não altera o valor existente
          - campo com valor   → altera o valor
          - campo com null    → limpa o campo (nullable → None; notes → "")

        Corrige o comportamento anterior que ignorava todos os None.
        """
        session = _create_session(session_at=datetime.now(tz=timezone.utc) + timedelta(hours=5))
        athlete_id = uuid.uuid4()

        # Criar registro com notes e mood preenchidos
        create_resp = client.post(
            f"/api/training/training-sessions/{session.id}/wellness-pre",
            data=json.dumps({
                "athlete_id": str(athlete_id),
                "sleep_quality": 3,
                "sleep_hours": 7.5,
                "notes": "nota original",
                "mood": 4,
            }),
            content_type="application/json",
        )
        assert create_resp.status_code == 201

        # --- Cenário 1: campo AUSENTE não altera o valor ---
        patch_resp = client.patch(
            f"/api/training/training-sessions/{session.id}/wellness-pre/{athlete_id}",
            data=json.dumps({"sleep_quality": 5}),  # notes e mood ausentes
            content_type="application/json",
        )
        assert patch_resp.status_code == 200
        body = patch_resp.json()
        assert body.get("sleepQuality") == 5, "campo presente com valor deve ser alterado"
        assert body.get("notes") == "nota original", "campo ausente NÃO deve alterar o valor"
        assert body.get("mood") == 4, "campo ausente NÃO deve alterar o valor"

        # --- Cenário 2: campo com NULL explícito limpa o campo ---
        patch_resp2 = client.patch(
            f"/api/training/training-sessions/{session.id}/wellness-pre/{athlete_id}",
            data=json.dumps({"notes": None, "mood": None}),
            content_type="application/json",
        )
        assert patch_resp2.status_code == 200
        body2 = patch_resp2.json()
        assert body2.get("notes") in ("", None), (
            "PATCH com notes=null deve limpar o campo (string vazia, pois ORM não tem null=True)"
        )
        assert body2.get("mood") is None, "PATCH com mood=null deve limpar o campo para null"

        # --- Cenário 3: sleep_quality ausente permanece como definido no cenário 1 ---
        assert body2.get("sleepQuality") == 5, "campo ausente no segundo PATCH deve manter valor do primeiro"

    def test_wellness_pre_duplicate_entry(self, client):
        """R8 — INV-TRAIN-009: segundo POST para o mesmo (session, athlete) retorna 409.

        A verificação ocorre no use case (SubmitWellnessPreUseCase.execute):
          existing = repo.get_active(session_id, athlete_id)
          if existing: raise DuplicateWellnessEntry(...)  → HTTP 409

        A migration 0010 adiciona UniqueConstraint parcial (WHERE deleted_at IS NULL)
        para enforçar INV-TRAIN-009 também ao nível de banco (proteção contra race condition).
        """
        session = _create_session(session_at=datetime.now(tz=timezone.utc) + timedelta(hours=5))
        athlete_id = uuid.uuid4()

        # Primeiro POST → 201
        first_resp = client.post(
            f"/api/training/training-sessions/{session.id}/wellness-pre",
            data={"athlete_id": str(athlete_id), "sleep_quality": 3, "sleep_hours": 7.5},
            content_type="application/json",
        )
        assert first_resp.status_code == 201, (
            f"Primeiro POST deve retornar 201, got {first_resp.status_code}: {first_resp.json()}"
        )

        # Segundo POST com mesmo (session_id, athlete_id) → 409 Conflict
        second_resp = client.post(
            f"/api/training/training-sessions/{session.id}/wellness-pre",
            data={"athlete_id": str(athlete_id), "sleep_quality": 4, "sleep_hours": 8.0},
            content_type="application/json",
        )
        assert second_resp.status_code == 409, (
            f"Segundo POST com mesmo athlete deve retornar 409, got {second_resp.status_code}: {second_resp.json()}"
        )
        assert "INV-TRAIN-009" in str(second_resp.json().get("detail", "")), (
            f"detail deve mencionar INV-TRAIN-009, got: {second_resp.json().get('detail')!r}"
        )

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
        assert get_resp.json()["athleteId"] == str(athlete_id)

        patch_resp = client.patch(
            f"/api/training/training-sessions/{session.id}/wellness-post/{athlete_id}",
            data={"perceived_exertion": 7, "notes": "adjusted"},
            content_type="application/json",
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["perceivedExertion"] == 7


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
        assert get_resp.json()["name"] == "Base 1"

        patch_resp = client.patch(
            f"/api/training/mesocycles/{mesocycle_id}",
            data={"name": "Base 1 ajustada", "notes": "replanejado"},
            content_type="application/json",
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["name"] == "Base 1 ajustada"

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
        assert get_resp.json()["weekNumber"] == 1

        patch_resp = client.patch(
            f"/api/training/microcycles/{microcycle_id}",
            data={"name": "Semana 1", "planned_sessions_count": 5},
            content_type="application/json",
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["plannedSessionsCount"] == 5


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
        assert get_resp.json()["id"] == record_id

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
        assert items[0]["objectiveType"] == "TACTICAL"


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
        assert close_resp.json()["decisionText"] == "Intervenção concluída e alinhada"

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
        assert resolve_resp.json()["resolvedByUserId"] is not None

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
        assert accept_resp.json()["status"] == "ACCEPTED"

        dismiss_resp = client.post(
            f"/api/training/training-sessions/{session.id}/recommendations/{dismissed_target.id}/dismiss",
            data={"dismissal_reason": "Contexto atual não exige intervenção"},
            content_type="application/json",
        )
        assert dismiss_resp.status_code == 200
        assert dismiss_resp.json()["status"] == "DISMISSED"

    def test_submit_and_get_ineligibility(self, client, monkeypatch):
        athlete_id = uuid.UUID("30000000-0000-0000-0000-000000000001")
        session = _create_session(status=TrainingSessionStatus.PUBLISHED)

        import training.api as training_api
        import training.api.eligibility as _eligibility_mod

        monkeypatch.setattr(_eligibility_mod, "_get_actor_role", lambda req: training_api.RoleLabel.ATHLETE)
        monkeypatch.setattr(_eligibility_mod, "_get_actor_id", lambda req: athlete_id)

        submit_resp = client.post(
            f"/api/training/training-sessions/{session.id}/ineligibility",
            data={
                "athlete_id": str(athlete_id),
                "reason_flags": ["INJURY_PAIN"],
            },
            content_type="application/json",
        )
        assert submit_resp.status_code == 201
        assert submit_resp.json()["athleteId"] == str(athlete_id)

        get_resp = client.get(f"/api/training/training-sessions/{session.id}/ineligibility")
        assert get_resp.status_code == 200
        assert get_resp.json()["reasonFlags"] == ["INJURY_PAIN"]
