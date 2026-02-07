"""Audit log for training session actions (create/update/publish/close)."""

from datetime import date, datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text

from app.core.context import ExecutionContext
from app.core.permissions_map import get_permissions_for_role
from app.models.attendance import Attendance
from app.models.athlete import Athlete
from app.models.category import Category
from app.models.organization import Organization
from app.models.person import Person
from app.models.team import Team
from app.models.team_registration import TeamRegistration
from app.models.training_session import TrainingSession
from app.services.training_session_service import TrainingSessionService
from app.schemas.training_sessions import TrainingSessionCreate, TrainingSessionUpdate


@pytest.mark.asyncio
async def test_audit_logs_for_create_update_publish_and_close(async_db):
    category = Category(id=998, name="Categoria Audit", max_age=19, is_active=True)
    organization = Organization(id=str(uuid4()), name="Org Audit")
    person = Person(
        id=str(uuid4()),
        full_name="Treinador Audit",
        first_name="Treinador",
        last_name="Audit",
    )
    user_id = uuid4()
    from app.models.user import User
    user = User(id=str(user_id), email="audit.treinador@hbtrack.com", person_id=person.id)

    async_db.add_all([category, organization, person, user])
    await async_db.flush()

    team = Team(
        id=uuid4(),
        organization_id=UUID(organization.id),
        name="Equipe Audit",
        category_id=category.id,
        gender="masculino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()

    ctx = ExecutionContext(
        user_id=user_id,
        email=user.email,
        role_code="treinador",
        organization_id=UUID(organization.id),
        membership_id=uuid4(),
        team_ids=[team.id],
        permissions=get_permissions_for_role("treinador"),
    )
    service = TrainingSessionService(async_db, ctx)

    payload = TrainingSessionCreate(
        organization_id=UUID(organization.id),
        team_id=team.id,
        session_at=datetime.now(timezone.utc),
        session_type="quadra",
        main_objective="Audit create",
        duration_planned_minutes=90,
        location="Ginásio",
    )

    session = await service.create(payload)

    update_payload = TrainingSessionUpdate(notes="Atualização de audit")
    await service.update(session.id, update_payload)

    published, errors = await service.publish_session(session.id)
    assert errors == {}

    result = await async_db.execute(
        text(
            """
            SELECT action
            FROM audit_logs
            WHERE entity = 'training_session' AND entity_id = :entity_id
            """
        ),
        {"entity_id": session.id},
    )
    actions = {row[0] for row in result.fetchall()}

    assert "create" in actions
    assert "update" in actions
    assert "publish" in actions

    category = Category(id=997, name="Categoria Close", max_age=19, is_active=True)
    organization = Organization(id=str(uuid4()), name="Org Close")
    person = Person(
        id=str(uuid4()),
        full_name="Treinador Close",
        first_name="Treinador",
        last_name="Close",
    )
    user_id = uuid4()
    from app.models.user import User
    user = User(id=str(user_id), email="close.treinador@hbtrack.com", person_id=person.id)

    async_db.add_all([category, organization, person, user])
    await async_db.flush()

    team = Team(
        id=uuid4(),
        organization_id=UUID(organization.id),
        name="Equipe Close",
        category_id=category.id,
        gender="feminino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()

    athlete_person = Person(
        id=str(uuid4()),
        full_name="Atleta Close",
        first_name="Atleta",
        last_name="Close",
        birth_date=date(2007, 1, 1),
    )
    async_db.add(athlete_person)
    await async_db.flush()

    athlete = Athlete(
        id=uuid4(),
        person_id=UUID(athlete_person.id),
        athlete_name="Atleta Close",
        birth_date=date(2007, 1, 1),
    )
    async_db.add(athlete)
    await async_db.flush()

    registration = TeamRegistration(
        athlete_id=athlete.id,
        team_id=team.id,
        start_at=datetime.now(timezone.utc) - timedelta(days=10),
    )
    async_db.add(registration)

    session = TrainingSession(
        id=uuid4(),
        organization_id=UUID(organization.id),
        team_id=team.id,
        session_at=datetime.now(timezone.utc) - timedelta(hours=2),
        duration_planned_minutes=90,
        session_type="quadra",
        main_objective="Fechamento",
        location="Quadra",
        status="pending_review",
        execution_outcome="on_time",
        created_by_user_id=user_id,
    )
    async_db.add(session)
    await async_db.flush()

    attendance = Attendance(
        training_session_id=session.id,
        team_registration_id=registration.id,
        athlete_id=athlete.id,
        presence_status="present",
        created_by_user_id=user_id,
    )
    async_db.add(attendance)
    await async_db.flush()

    ctx = ExecutionContext(
        user_id=user_id,
        email=user.email,
        role_code="treinador",
        organization_id=UUID(organization.id),
        membership_id=uuid4(),
        team_ids=[team.id],
        permissions=get_permissions_for_role("treinador"),
    )
    service = TrainingSessionService(async_db, ctx)

    result = await service.close_session(session.id)
    assert result.success is True

    audit_result = await async_db.execute(
        text(
            """
            SELECT action
            FROM audit_logs
            WHERE entity = 'training_session' AND entity_id = :entity_id
            """
        ),
        {"entity_id": session.id},
    )
    actions = {row[0] for row in audit_result.fetchall()}
    assert "close" in actions
