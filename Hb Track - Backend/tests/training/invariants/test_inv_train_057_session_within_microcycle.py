"""
INV-TRAIN-057 — session_within_microcycle_week

SERVICE TEST (Classe C2) — Testa que sessoes vinculadas a microciclo devem
ter session_at dentro da semana (week_start <= session_at.date() <= week_end).

Evidencia:
- app/services/training_session_service.py (SessionOutsideMicrocycleWeekError guard L222-240)
- app/core/exceptions.py (SessionOutsideMicrocycleWeekError L91-95)
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
from app.core.exceptions import SessionOutsideMicrocycleWeekError


def _make_context_057(user_id: UUID, org_id: UUID) -> ExecutionContext:
    """Cria um ExecutionContext minimal para testes INV-057."""
    return ExecutionContext(
        user_id=user_id,
        email="inv057@hbtrack.com",
        role_code="treinador",
        request_id=str(uuid4()),
        organization_id=org_id,
    )


class TestInvTrain057:
    """
    INV-TRAIN-057: session_within_microcycle_week

    Prova que:
    1) session_at dentro da semana do microciclo -> valido
    2) session_at fora da semana (antes ou depois) -> SessionOutsideMicrocycleWeekError

    Evidencia: training_session_service.py (L222-240)
    """

    @pytest_asyncio.fixture
    async def inv057_setup(self, async_db: AsyncSession):
        """Cria org, team, user e microciclo para INV-057."""
        cat_id = 9994
        await async_db.execute(text(
            "INSERT INTO categories (id, name, max_age, is_active) "
            "VALUES (:id, 'Cat INV-057', 19, true) ON CONFLICT (id) DO NOTHING"
        ), {"id": cat_id})

        org_id = uuid4()
        await async_db.execute(text(
            "INSERT INTO organizations (id, name) VALUES (:id, 'Org INV-057')"
        ), {"id": str(org_id)})

        pid = str(uuid4())
        uid = uuid4()
        await async_db.execute(text(
            "INSERT INTO persons (id, first_name, last_name, full_name, birth_date) "
            "VALUES (:id, 'Inv', '057', 'Inv 057', '1990-01-01')"
        ), {"id": pid})
        await async_db.execute(text(
            "INSERT INTO users (id, email, person_id, password_hash, status) "
            "VALUES (:id, :email, :person_id, 'hash', 'ativo')"
        ), {"id": str(uid), "email": f"inv057_{str(uid)[:8]}@hbtrack.com", "person_id": pid})

        team_id = uuid4()
        await async_db.execute(text(
            "INSERT INTO teams (id, organization_id, category_id, name, gender, is_our_team) "
            "VALUES (:id, :org_id, :cat_id, 'Team INV-057', 'masculino', true)"
        ), {"id": str(team_id), "org_id": str(org_id), "cat_id": cat_id})

        # Microciclo: semana 2026-04-06 (segunda) a 2026-04-12 (domingo)
        micro_id = uuid4()
        week_start = date(2026, 4, 6)
        week_end = date(2026, 4, 12)
        await async_db.execute(text("""
            INSERT INTO training_microcycles
                (id, organization_id, team_id, week_start, week_end, created_by_user_id)
            VALUES (:id, :org_id, :team_id, :ws, :we, :uid)
        """), {
            "id": str(micro_id), "org_id": str(org_id), "team_id": str(team_id),
            "ws": week_start, "we": week_end, "uid": str(uid),
        })
        await async_db.flush()

        return {
            "org_id": org_id, "team_id": team_id, "user_id": uid,
            "micro_id": micro_id, "week_start": week_start, "week_end": week_end,
        }

    @pytest.mark.asyncio
    async def test_valid_session_within_week(self, async_db: AsyncSession, inv057_setup):
        """
        INV-057 CASO POSITIVO: session_at dentro da semana do microciclo deve ser aceita.

        Semana: 2026-04-06 a 2026-04-12. Session_at: 2026-04-08 (quarta).
        Evidencia: training_session_service.py L222-240
        """
        d = inv057_setup
        context = _make_context_057(d["user_id"], d["org_id"])
        service = TrainingSessionService(async_db, context)

        # session_at dentro da semana do microciclo
        payload = TrainingSessionCreate(
            organization_id=d["org_id"],
            team_id=d["team_id"],
            session_at=datetime(2026, 4, 8, 10, 0, 0, tzinfo=timezone.utc),  # quarta-feira
            session_type="quadra",
            microcycle_id=d["micro_id"],
        )

        session = await service.create(payload)

        assert session.id is not None
        assert session.microcycle_id == d["micro_id"]
        assert session.standalone is False

    @pytest.mark.asyncio
    async def test_invalid_session_before_week_start(self, async_db: AsyncSession, inv057_setup):
        """
        INV-057 CASO NEGATIVO: session_at ANTES do week_start deve levantar
        SessionOutsideMicrocycleWeekError.

        Semana: 2026-04-06 a 2026-04-12. Session_at: 2026-04-05 (antes).
        Evidencia: training_session_service.py L234-240
        """
        d = inv057_setup
        context = _make_context_057(d["user_id"], d["org_id"])
        service = TrainingSessionService(async_db, context)

        # session_at ANTES da semana do microciclo
        payload = TrainingSessionCreate(
            organization_id=d["org_id"],
            team_id=d["team_id"],
            session_at=datetime(2026, 4, 5, 10, 0, 0, tzinfo=timezone.utc),  # domingo antes
            session_type="quadra",
            microcycle_id=d["micro_id"],
        )

        with pytest.raises(SessionOutsideMicrocycleWeekError):
            await service.create(payload)

    @pytest.mark.asyncio
    async def test_invalid_session_after_week_end(self, async_db: AsyncSession, inv057_setup):
        """
        INV-057 CASO NEGATIVO: session_at APOS o week_end deve levantar
        SessionOutsideMicrocycleWeekError.

        Semana: 2026-04-06 a 2026-04-12. Session_at: 2026-04-13 (depois).
        Evidencia: training_session_service.py L234-240
        """
        d = inv057_setup
        context = _make_context_057(d["user_id"], d["org_id"])
        service = TrainingSessionService(async_db, context)

        # session_at APOS a semana do microciclo
        payload = TrainingSessionCreate(
            organization_id=d["org_id"],
            team_id=d["team_id"],
            session_at=datetime(2026, 4, 13, 10, 0, 0, tzinfo=timezone.utc),  # segunda seguinte
            session_type="quadra",
            microcycle_id=d["micro_id"],
        )

        with pytest.raises(SessionOutsideMicrocycleWeekError):
            await service.create(payload)
