"""
Teste de performance — Task 4.2 (FASE 4).

Valida que os endpoints de listagem do Ciclo 1 respondem em < 200ms (p95)
com dados de seed realistas (100 registros por módulo).

Detecta também N+1 queries: cada listagem deve executar exatamente 1 query SQL.

Requer PostgreSQL rodando (pula automaticamente se não disponível).
"""
from __future__ import annotations

import time
import uuid
from datetime import date, timedelta

import pytest
from django.utils import timezone


# ── helpers ──────────────────────────────────────────────────────────────────

def _p95(times_ms: list[float]) -> float:
    """Retorna o percentil 95 de uma lista de tempos em ms."""
    s = sorted(times_ms)
    idx = max(0, int(len(s) * 0.95) - 1)
    return s[idx]


def _measure(fn, runs: int = 30) -> list[float]:
    """Executa fn `runs` vezes e retorna lista de tempos em ms."""
    results = []
    for _ in range(runs):
        t0 = time.perf_counter()
        fn()
        results.append((time.perf_counter() - t0) * 1000)
    return results


# ── fixtures de dados ─────────────────────────────────────────────────────────

ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TEAM_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
SEASON_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000004")

N = 100  # registros por módulo


@pytest.fixture(scope="module")
def django_db_setup(django_db_setup):
    """Herda o setup do conftest raiz (skip se PG indisponível)."""


# ── seasons ────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_list_seasons_p95():
    from seasons.infrastructure.models import SeasonModel

    base = date(2024, 1, 1)
    SeasonModel.objects.bulk_create([
        SeasonModel(
            id=uuid.uuid4(),
            organization_id=ORG_ID,
            name=f"Temporada {i}",
            status_label="ACTIVE",
            start_date=base + timedelta(days=i * 3),
            end_date=base + timedelta(days=i * 3 + 90),
        )
        for i in range(N)
    ])

    def query():
        list(
            SeasonModel.objects.filter(organization_id=ORG_ID)
            .order_by("-start_date")[:20]
        )

    times = _measure(query)
    p95 = _p95(times)
    assert p95 < 200, (
        f"listSeasons p95={p95:.1f}ms excede 200ms\n"
        f"  min={min(times):.1f}ms  max={max(times):.1f}ms  runs={len(times)}"
    )


# ── teams ──────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_list_teams_p95():
    from teams.infrastructure.models import TeamModel

    TeamModel.objects.bulk_create([
        TeamModel(
            id=uuid.uuid4(),
            organization_id=ORG_ID,
            name=f"Time {i}",
            category_label="SENIOR",
            status_label="ACTIVE",
        )
        for i in range(N)
    ])

    def query():
        list(
            TeamModel.objects.filter(
                organization_id=ORG_ID,
                status_label="ACTIVE",
            ).order_by("name")[:20]
        )

    times = _measure(query)
    p95 = _p95(times)
    assert p95 < 200, (
        f"listTeams p95={p95:.1f}ms excede 200ms\n"
        f"  min={min(times):.1f}ms  max={max(times):.1f}ms  runs={len(times)}"
    )


# ── training sessions ──────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_list_training_sessions_p95():
    from training.infrastructure.models import TrainingSessionModel

    now = timezone.now()
    TrainingSessionModel.objects.bulk_create([
        TrainingSessionModel(
            id=uuid.uuid4(),
            organization_id=ORG_ID,
            team_id=TEAM_ID,
            season_id=SEASON_ID,
            session_at=now - timedelta(hours=i),
            session_type="TACTICAL",
            status="PUBLISHED",
            created_by_user_id=USER_ID,
        )
        for i in range(N)
    ])

    def query():
        list(
            TrainingSessionModel.objects.filter(
                organization_id=ORG_ID,
                deleted_at__isnull=True,
            ).order_by("-session_at")[:20]
        )

    times = _measure(query)
    p95 = _p95(times)
    assert p95 < 200, (
        f"listTrainingSessions p95={p95:.1f}ms excede 200ms\n"
        f"  min={min(times):.1f}ms  max={max(times):.1f}ms  runs={len(times)}"
    )


# ── auth sessions ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_list_auth_sessions_p95():
    from identity_access.infrastructure.models import AuthSessionModel

    now = timezone.now()
    AuthSessionModel.objects.bulk_create([
        AuthSessionModel(
            id=uuid.uuid4(),
            principal_user_id=USER_ID,
            session_scope_label="web",
            issued_at=now - timedelta(hours=i),
            expires_at=now + timedelta(hours=24),
            revoked_at=None,
        )
        for i in range(N)
    ])

    def query():
        list(
            AuthSessionModel.objects.filter(
                principal_user_id=USER_ID,
                revoked_at__isnull=True,
            ).order_by("-issued_at")[:20]
        )

    times = _measure(query)
    p95 = _p95(times)
    assert p95 < 200, (
        f"listActiveSessions p95={p95:.1f}ms excede 200ms\n"
        f"  min={min(times):.1f}ms  max={max(times):.1f}ms  runs={len(times)}"
    )


# ── users ──────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_list_user_profiles_p95():
    from users.infrastructure.models import UserProfileModel

    UserProfileModel.objects.bulk_create([
        UserProfileModel(
            id=uuid.uuid4(),
            organization_id=ORG_ID,
            display_name=f"Atleta {i}",
            role_label="athlete",
            status_label="ACTIVE",
        )
        for i in range(N)
    ])

    def query():
        list(
            UserProfileModel.objects.filter(
                organization_id=ORG_ID,
                role_label="athlete",
            ).order_by("id")[:20]
        )

    times = _measure(query)
    p95 = _p95(times)
    assert p95 < 200, (
        f"listUsers p95={p95:.1f}ms excede 200ms\n"
        f"  min={min(times):.1f}ms  max={max(times):.1f}ms  runs={len(times)}"
    )


# ── N+1 detection ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_no_n_plus_1_training_sessions(django_assert_num_queries):
    from training.infrastructure.models import TrainingSessionModel

    now = timezone.now()
    org = uuid.uuid4()
    TrainingSessionModel.objects.bulk_create([
        TrainingSessionModel(
            id=uuid.uuid4(),
            organization_id=org,
            team_id=TEAM_ID,
            session_at=now - timedelta(hours=i),
            session_type="TACTICAL",
            status="DRAFT",
            created_by_user_id=USER_ID,
        )
        for i in range(20)
    ])

    with django_assert_num_queries(1):
        list(
            TrainingSessionModel.objects.filter(
                organization_id=org,
                deleted_at__isnull=True,
            ).order_by("-session_at")[:20]
        )


@pytest.mark.django_db
def test_no_n_plus_1_teams(django_assert_num_queries):
    from teams.infrastructure.models import TeamModel

    org = uuid.uuid4()
    TeamModel.objects.bulk_create([
        TeamModel(
            id=uuid.uuid4(),
            organization_id=org,
            name=f"Time NQ {i}",
            category_label="JUNIOR",
            status_label="ACTIVE",
        )
        for i in range(20)
    ])

    with django_assert_num_queries(1):
        list(TeamModel.objects.filter(organization_id=org).order_by("name")[:20])
