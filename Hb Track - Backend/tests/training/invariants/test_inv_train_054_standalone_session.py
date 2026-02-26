"""
INV-TRAIN-054 — standalone_session_explicit_flag

SERVICE TEST (Classe C2) — Testa que:
1. Sessao sem microciclo tem standalone=TRUE (INV-054)
2. Sessao com microciclo (session_at dentro da semana) tem standalone=FALSE

Evidencia:
- app/services/training_session_service.py (standalone = data.microcycle_id is None, L220)
- app/models/training_session.py (standalone BOOLEAN NOT NULL)
- Hb Track - Backend/db/alembic/versions/0066_training_sessions_standalone_flag.py
"""
import pytest
import pytest_asyncio
from datetime import date, datetime, timezone
from uuid import uuid4, UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import ExecutionContext
from app.services.training_session_service import TrainingSessionService
from app.schemas.training_sessions import TrainingSessionCreate


def _make_context(user_id: UUID, org_id: UUID) -> ExecutionContext:
    """Cria um ExecutionContext minimal para testes."""
    return ExecutionContext(
        user_id=user_id,
        email="inv054@hbtrack.com",
        role_code="treinador",
        request_id=str(uuid4()),
        organization_id=org_id,
    )


class TestInvTrain054:
    """
    INV-TRAIN-054: standalone_session_explicit_flag

    Prova que:
    1) Sessao sem microciclo: service seta standalone=TRUE
    2) Sessao com microciclo (session_at dentro da semana): service seta standalone=FALSE

    Evidencia: training_session_service.py (standalone = data.microcycle_id is None)
    """

    @pytest_asyncio.fixture
    async def inv054_org(self, async_db: AsyncSession):
        """Organizacao para INV-054."""
        oid = uuid4()
        await async_db.execute(text(
            "INSERT INTO organizations (id, name) VALUES (:id, 'Org INV-054')"
        ), {"id": str(oid)})
        await async_db.flush()
        return type('Org', (), {'id': oid})()

    @pytest_asyncio.fixture
    async def inv054_user(self, async_db: AsyncSession):
        """Usuario para INV-054."""
        pid = str(uuid4())
        uid = uuid4()
        await async_db.execute(text(
            "INSERT INTO persons (id, first_name, last_name, full_name, birth_date) "
            "VALUES (:id, 'Inv', '054', 'Inv 054', '1990-01-01')"
        ), {"id": pid})
        await async_db.execute(text(
            "INSERT INTO users (id, email, person_id, password_hash, status) "
            "VALUES (:id, :email, :person_id, 'hash', 'ativo')"
        ), {"id": str(uid), "email": f"inv054_{str(uid)[:8]}@hbtrack.com", "person_id": pid})
        await async_db.flush()
        return type('User', (), {'id': uid})()

    @pytest_asyncio.fixture
    async def inv054_team(self, async_db: AsyncSession, inv054_org):
        """Time para INV-054."""
        cat_id = 9997
        await async_db.execute(text(
            "INSERT INTO categories (id, name, max_age, is_active) "
            "VALUES (:id, 'Cat INV-054', 19, true) ON CONFLICT (id) DO NOTHING"
        ), {"id": cat_id})
        tid = uuid4()
        await async_db.execute(text(
            "INSERT INTO teams (id, organization_id, category_id, name, gender, is_our_team) "
            "VALUES (:id, :org_id, :cat_id, 'Team INV-054', 'masculino', true)"
        ), {"id": str(tid), "org_id": str(inv054_org.id), "cat_id": cat_id})
        await async_db.flush()
        return type('Team', (), {'id': tid})()

    @pytest_asyncio.fixture
    async def inv054_microcycle(self, async_db: AsyncSession, inv054_org, inv054_team, inv054_user):
        """Microciclo para INV-054 (semana: 2026-03-02 a 2026-03-08)."""
        mid = uuid4()
        week_start = date(2026, 3, 2)
        week_end = date(2026, 3, 8)
        await async_db.execute(text("""
            INSERT INTO training_microcycles
                (id, organization_id, team_id, week_start, week_end, created_by_user_id)
            VALUES (:id, :org_id, :team_id, :ws, :we, :uid)
        """), {
            "id": str(mid), "org_id": str(inv054_org.id),
            "team_id": str(inv054_team.id),
            "ws": week_start, "we": week_end, "uid": str(inv054_user.id),
        })
        await async_db.flush()
        return type('Micro', (), {'id': mid, 'week_start': week_start, 'week_end': week_end})()

    @pytest.mark.asyncio
    async def test_valid_session_without_microcycle_is_standalone(
        self, async_db: AsyncSession, inv054_org, inv054_team, inv054_user
    ):
        """
        INV-054 CASO POSITIVO: Sessao sem microciclo deve ter standalone=TRUE.

        Evidencia: training_session_service.py standalone = data.microcycle_id is None (L220)
        """
        context = _make_context(inv054_user.id, inv054_org.id)
        service = TrainingSessionService(async_db, context)

        payload = TrainingSessionCreate(
            organization_id=inv054_org.id,
            team_id=inv054_team.id,
            session_at=datetime(2026, 3, 10, 10, 0, 0, tzinfo=timezone.utc),
            session_type="quadra",
            microcycle_id=None,
        )

        session = await service.create(payload)

        assert session.standalone is True
        assert session.microcycle_id is None

    @pytest.mark.asyncio
    async def test_valid_session_with_microcycle_not_standalone(
        self, async_db: AsyncSession, inv054_org, inv054_team, inv054_user, inv054_microcycle
    ):
        """
        INV-054 CASO POSITIVO: Sessao com microciclo deve ter standalone=FALSE.

        session_at dentro da semana do microciclo (2026-03-02 a 2026-03-08).
        Evidencia: training_session_service.py standalone = data.microcycle_id is None (L220)
        """
        context = _make_context(inv054_user.id, inv054_org.id)
        service = TrainingSessionService(async_db, context)

        payload = TrainingSessionCreate(
            organization_id=inv054_org.id,
            team_id=inv054_team.id,
            session_at=datetime(2026, 3, 4, 10, 0, 0, tzinfo=timezone.utc),
            session_type="quadra",
            microcycle_id=inv054_microcycle.id,
        )

        session = await service.create(payload)

        assert session.standalone is False
        assert session.microcycle_id == inv054_microcycle.id
