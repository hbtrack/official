"""
Testes de integração para validação da revisão operacional (pending_review -> readonly).
"""

from datetime import date, datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import ExecutionContext
from app.core.permissions_map import get_permissions_for_role
from app.models.attendance import Attendance as AttendanceModel
from app.models.athlete import Athlete
from app.models.category import Category
from app.models.organization import Organization
from app.models.person import Person
from app.models.team import Team
from app.models.team_registration import TeamRegistration
from app.models.training_session import TrainingSession as TrainingSessionModel
from app.models.user import User
from app.services.training_session_service import TrainingSessionService


@pytest.fixture
async def test_category(async_db: AsyncSession) -> Category:
    category = Category(
        id=999,
        name="Categoria Teste",
        max_age=19,
        is_active=True,
    )
    async_db.add(category)
    await async_db.flush()
    return category


@pytest.fixture
async def test_organization(async_db: AsyncSession) -> Organization:
    org = Organization(
        id=str(uuid4()),
        name="Org Teste Treinos",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest.fixture
async def test_user(async_db: AsyncSession) -> User:
    user = User(
        id=str(uuid4()),
        email="treinador.teste@hbtrack.com",
    )
    async_db.add(user)
    await async_db.flush()
    return user


@pytest.fixture
async def test_team(
    async_db: AsyncSession,
    test_category: Category,
    test_organization: Organization,
) -> Team:
    team = Team(
        id=uuid4(),
        organization_id=UUID(test_organization.id),
        name="Equipe Teste",
        category_id=test_category.id,
        gender="feminino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


@pytest.fixture
async def test_training_session(
    async_db: AsyncSession,
    test_team: Team,
    test_organization: Organization,
    test_user: User,
) -> TrainingSessionModel:
    session = TrainingSessionModel(
        id=uuid4(),
        organization_id=UUID(test_organization.id),
        team_id=test_team.id,
        session_at=datetime.now(timezone.utc) - timedelta(hours=2),
        duration_planned_minutes=90,
        session_type="quadra",
        main_objective="Treino de validacao",
        location="Ginasio Teste",
        status="pending_review",
        execution_outcome="on_time",
        created_by_user_id=UUID(test_user.id),
    )
    async_db.add(session)
    await async_db.flush()
    return session


@pytest.fixture
async def test_team_registrations(
    async_db: AsyncSession,
    test_team: Team,
) -> list[TeamRegistration]:
    registrations: list[TeamRegistration] = []

    for idx in range(2):
        person = Person(
            id=str(uuid4()),
            full_name=f"Atleta Teste {idx + 1}",
            first_name="Atleta",
            last_name=f"Teste {idx + 1}",
            birth_date=date(2007, 1, idx + 1),
        )
        athlete = Athlete(
            id=uuid4(),
            person_id=UUID(person.id),
            athlete_name=f"Atleta {idx + 1}",
            birth_date=date(2007, 1, idx + 1),
        )
        registration = TeamRegistration(
            athlete_id=athlete.id,
            team_id=test_team.id,
            start_at=datetime.now(timezone.utc),
        )

        async_db.add(person)
        async_db.add(athlete)
        async_db.add(registration)
        registrations.append(registration)

    await async_db.flush()
    return registrations


@pytest.fixture
def exec_context(test_organization: Organization, test_user: User) -> ExecutionContext:
    return ExecutionContext(
        user_id=UUID(test_user.id),
        email=test_user.email,
        role_code="treinador",
        person_id=None,
        is_superadmin=False,
        organization_id=UUID(test_organization.id),
        membership_id=uuid4(),
        team_ids=[],
        permissions=get_permissions_for_role("treinador"),
    )


async def _create_attendance(
    async_db: AsyncSession,
    session: TrainingSessionModel,
    registrations: list[TeamRegistration],
    user: User,
) -> None:
    for registration in registrations:
        attendance = AttendanceModel(
            training_session_id=session.id,
            team_registration_id=registration.id,
            athlete_id=registration.athlete_id,
            presence_status="present",
            created_by_user_id=UUID(user.id),
        )
        async_db.add(attendance)

    await async_db.flush()


@pytest.mark.asyncio
async def test_close_session_rejects_invalid_status(
    async_db: AsyncSession,
    test_team: Team,
    test_organization: Organization,
    test_user: User,
    exec_context: ExecutionContext,
) -> None:
    session = TrainingSessionModel(
        id=uuid4(),
        organization_id=UUID(test_organization.id),
        team_id=test_team.id,
        session_at=datetime.now(timezone.utc) - timedelta(hours=1),
        duration_planned_minutes=60,
        session_type="quadra",
        main_objective="Treino invalido",
        location="Ginasio Teste",
        status="draft",
        execution_outcome="on_time",
        created_by_user_id=UUID(test_user.id),
    )
    async_db.add(session)
    await async_db.flush()

    service = TrainingSessionService(async_db, exec_context)
    result = await service.close_session(session.id)

    assert result.success is False
    assert result.validation is not None
    assert result.validation.error_code == "INVALID_STATUS"


@pytest.mark.asyncio
async def test_close_session_requires_justification_when_delayed(
    async_db: AsyncSession,
    test_training_session: TrainingSessionModel,
    test_team_registrations: list[TeamRegistration],
    test_user: User,
    exec_context: ExecutionContext,
) -> None:
    test_training_session.execution_outcome = "delayed"
    test_training_session.delay_minutes = 15
    await async_db.flush()

    await _create_attendance(async_db, test_training_session, test_team_registrations, test_user)

    service = TrainingSessionService(async_db, exec_context)
    result = await service.close_session(test_training_session.id)

    assert result.success is False
    assert result.validation is not None
    assert result.validation.error_code == "MISSING_DEVIATION_JUSTIFICATION"
    assert result.validation.field_errors.deviation_justification


@pytest.mark.asyncio
async def test_close_session_blocks_missing_presence(
    async_db: AsyncSession,
    test_training_session: TrainingSessionModel,
    test_team_registrations: list[TeamRegistration],
    exec_context: ExecutionContext,
) -> None:
    await async_db.flush()

    service = TrainingSessionService(async_db, exec_context)
    result = await service.close_session(test_training_session.id)

    assert result.success is False
    assert result.validation is not None
    assert result.validation.error_code == "INCOMPLETE_PRESENCE"
    assert result.validation.field_errors.presence


@pytest.mark.asyncio
async def test_close_session_allows_canceled_without_presence(
    async_db: AsyncSession,
    test_training_session: TrainingSessionModel,
    exec_context: ExecutionContext,
) -> None:
    test_training_session.execution_outcome = "canceled"
    test_training_session.cancellation_reason = "Chuva intensa"
    test_training_session.deviation_justification = (
        "Treino cancelado por condicoes climaticas severas e risco de seguranca."
    )
    await async_db.flush()

    service = TrainingSessionService(async_db, exec_context)
    result = await service.close_session(test_training_session.id)

    assert result.success is True
    assert result.session is not None
    assert result.session.status == "readonly"
    assert result.session.closed_at is not None


@pytest.mark.asyncio
async def test_close_session_succeeds_with_complete_presence(
    async_db: AsyncSession,
    test_training_session: TrainingSessionModel,
    test_team_registrations: list[TeamRegistration],
    test_user: User,
    exec_context: ExecutionContext,
) -> None:
    await _create_attendance(async_db, test_training_session, test_team_registrations, test_user)

    service = TrainingSessionService(async_db, exec_context)
    result = await service.close_session(test_training_session.id)

    assert result.success is True
    assert result.session is not None
    assert result.session.status == "readonly"
    assert result.session.closed_at is not None
