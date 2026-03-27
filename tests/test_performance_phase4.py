"""
Testes de performance — FASE 4, Tarefa 4.2
Valida que endpoints de listagem respondem em < 200ms com seed data.
"""
import time
import pytest
from django.test import Client
from django.contrib.auth import get_user_model
import uuid
from datetime import date, timedelta, datetime, timezone

User = get_user_model()

# IDs fixos do seed
ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
COACH_ID = uuid.UUID("00000000-0000-0000-0000-000000000011")
TEAM_ID = uuid.UUID("00000000-0000-0000-0000-000000000020")
SEASON_ID = uuid.UUID("00000000-0000-0000-0000-000000000030")


@pytest.fixture
def seed_demo_data(transactional_db):
    """Seed de dados de teste"""
    from users.infrastructure.models import UserProfileModel
    from identity_access.infrastructure.models import UserRoleBindingModel
    from teams.infrastructure.models import TeamModel
    from seasons.infrastructure.models import SeasonModel
    from training.infrastructure.models import TrainingSessionModel
    from django.contrib.auth.hashers import make_password

    # Criar usuários
    admin, _ = User.objects.get_or_create(
        id=ADMIN_ID,
        defaults={
            "username": "admin@hbtrack.demo",
            "email": "admin@hbtrack.demo",
            "password": make_password("HBTrack@demo2026"),
            "is_staff": True,
        },
    )
    coach, _ = User.objects.get_or_create(
        id=COACH_ID,
        defaults={
            "username": "coach@hbtrack.demo",
            "email": "coach@hbtrack.demo",
            "password": make_password("HBTrack@demo2026"),
        },
    )

    # Criar profiles
    UserProfileModel.objects.get_or_create(
        id=ADMIN_ID,
        defaults={
            "organization_id": ORG_ID,
            "display_name": "Admin Demo",
            "first_name": "Admin",
            "last_name": "Demo",
            "role_label": "admin",
            "status_label": "ACTIVE",
        },
    )
    UserProfileModel.objects.get_or_create(
        id=COACH_ID,
        defaults={
            "organization_id": ORG_ID,
            "display_name": "Treinador Demo",
            "first_name": "Treinador",
            "last_name": "Demo",
            "role_label": "coach",
            "status_label": "ACTIVE",
        },
    )

    # Criar roles
    UserRoleBindingModel.objects.get_or_create(
        user_id=ADMIN_ID, role_label="admin"
    )
    UserRoleBindingModel.objects.get_or_create(
        user_id=COACH_ID, role_label="coach"
    )

    # Criar time
    TeamModel.objects.get_or_create(
        id=TEAM_ID,
        defaults={
            "organization_id": ORG_ID,
            "name": "HB Track Demo",
            "short_name": "HBD",
            "category_label": "adulto_masculino",
            "status_label": "ACTIVE",
            "staff_user_ids": [str(ADMIN_ID), str(COACH_ID)],
        },
    )

    # Criar temporada
    today = date.today()
    SeasonModel.objects.get_or_create(
        id=SEASON_ID,
        defaults={
            "organization_id": ORG_ID,
            "name": "Temporada 2026 — Demo",
            "sport_cycle_label": "handebol",
            "status_label": "ACTIVE",
            "start_date": today,
            "end_date": today + timedelta(days=180),
            "team_ids": [str(TEAM_ID)],
        },
    )

    # Criar múltiplas sessões de treino
    session_types = ["tactical", "physical", "technical", "mixed", "recovery"]
    for i in range(1, 11):  # 10 sessões
        session_at = datetime.now(tz=timezone.utc) + timedelta(days=i)
        TrainingSessionModel.objects.get_or_create(
            id=uuid.uuid5(SEASON_ID, f"demo_session_{i}"),
            defaults={
                "organization_id": ORG_ID,
                "team_id": TEAM_ID,
                "season_id": SEASON_ID,
                "created_by_user_id": ADMIN_ID,
                "session_at": session_at,
                "session_type": session_types[i % len(session_types)],
                "main_objective": f"Sessão demo #{i}",
                "status": "SCHEDULED",
                "duration_planned_minutes": 90,
            },
        )
    
    return {
        "org_id": ORG_ID,
        "admin_id": ADMIN_ID,
        "coach_id": COACH_ID,
        "team_id": TEAM_ID,
        "season_id": SEASON_ID,
    }


def _make_jwt(user_id: uuid.UUID, role: str = "admin") -> str:
    """Gera JWT válido para uso nos testes de performance."""
    from identity_access.infrastructure.jwt_adapter import JWTAdapter
    from identity_access.domain.entities import AuthSession
    from datetime import datetime, timezone

    session = AuthSession(
        id=uuid.uuid4(),
        principal_user_id=user_id,
        session_scope_label="full",
        role_labels=[role],
        auth_method_label="password",
        mfa_required=False,
        mfa_satisfied=True,
        issued_at=datetime.now(tz=timezone.utc),
        expires_at=datetime.now(tz=timezone.utc),
        revoked_at=None,
    )
    return JWTAdapter().issue_access_token(session)


def _warm_up_django(client, auth_header: str):
    """Warm-up do Django: primeira requsição inicializa DB connections,
    caches internos e imports lazy — não contabilizada nos testes de tempo."""
    client.get("/api/training/training-sessions", HTTP_AUTHORIZATION=auth_header)


class TestPerformancePhase4:
    """Testes de performance — FASE 4"""

    def test_list_training_sessions_response_time(self, seed_demo_data):
        """Validar que GET /api/training-sessions/ responde em < 200ms"""
        token = _make_jwt(COACH_ID, "coach")
        auth = f"Bearer {token}"
        client = Client()
        _warm_up_django(client, auth)

        # Medir tempo de resposta após warm-up
        start = time.perf_counter()
        response = client.get("/api/training/training-sessions", HTTP_AUTHORIZATION=auth)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert elapsed_ms < 200, f"Response time {elapsed_ms:.2f}ms exceeds 200ms threshold"
        print(f"✅ GET /api/training-sessions/ — {elapsed_ms:.2f}ms (< 200ms)")

    def test_list_teams_response_time(self, seed_demo_data):
        """Validar que GET /api/teams/ responde em < 200ms"""
        token = _make_jwt(COACH_ID, "coach")
        auth = f"Bearer {token}"
        client = Client()

        start = time.perf_counter()
        response = client.get("/api/teams", HTTP_AUTHORIZATION=auth)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 200, f"Response time {elapsed_ms:.2f}ms exceeds 200ms threshold"
        print(f"✅ GET /api/teams/ — {elapsed_ms:.2f}ms (< 200ms)")

    def test_list_seasons_response_time(self, seed_demo_data):
        """Validar que GET /api/seasons/ responde em < 200ms"""
        token = _make_jwt(COACH_ID, "coach")
        auth = f"Bearer {token}"
        client = Client()

        start = time.perf_counter()
        response = client.get("/api/seasons", HTTP_AUTHORIZATION=auth)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 200, f"Response time {elapsed_ms:.2f}ms exceeds 200ms threshold"
        print(f"✅ GET /api/seasons/ — {elapsed_ms:.2f}ms (< 200ms)")
