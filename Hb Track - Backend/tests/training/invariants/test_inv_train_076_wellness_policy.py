"""
INV-TRAIN-076: has_completed_daily_wellness — política de wellness diário completo
Classe C2 — Runtime Integration com async_db
Evidência: app/services/athlete_content_gate_service.py — has_completed_daily_wellness()
            docs/ssot/schema.sql:3080 — wellness_pre.filled_at, wellness_pre.athlete_id
            docs/ssot/schema.sql:3016 — wellness_post.training_session_id, wellness_post.athlete_id
            docs/ssot/schema.sql:2820 — training_sessions.closed_at
Regra: wellness diário completo = wellness_pre hoje + wellness_post do último treino encerrado.
       Retorna (bool, List[str]) com itens faltantes para exibição na UI.
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from uuid import uuid4, UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.athlete_content_gate_service import AthleteContentGateService


class TestInvTrain076:
    """
    INV-TRAIN-076 — has_completed_daily_wellness() verifica wellness_pre de hoje
    e wellness_post do último treino encerrado. Retorna (bool, list_missing).
    Evidência: app/services/athlete_content_gate_service.py — has_completed_daily_wellness
    """

    @pytest_asyncio.fixture
    async def closed_session(self, async_db: AsyncSession, organization, user, team):
        """Cria uma training_session com closed_at definido (treino encerrado)."""
        ts_id = str(uuid4())
        now = datetime.now(timezone.utc)
        await async_db.execute(text("""
            INSERT INTO training_sessions
              (id, organization_id, team_id, session_at, duration_planned_minutes,
               session_type, main_objective, location, status,
               created_by_user_id, closed_at)
            VALUES
              (:id, :org_id, :team_id, :session_at, 90,
               'quadra', 'Treino INV-076', 'Ginásio', 'concluída',
               :user_id, :closed_at)
        """), {
            "id": ts_id,
            "org_id": str(organization.id),
            "team_id": str(team.id),
            "session_at": now,
            "user_id": str(user.id),
            "closed_at": now,
        })
        await async_db.flush()
        return ts_id

    @pytest_asyncio.fixture
    async def wellness_pre_today(
        self, async_db: AsyncSession, athlete, organization, closed_session, user
    ):
        """Insere wellness_pre para hoje para o atleta."""
        wp_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO wellness_pre
              (id, organization_id, training_session_id, athlete_id,
               sleep_hours, sleep_quality, fatigue_pre, stress_level,
               muscle_soreness, created_by_user_id)
            VALUES
              (:id, :org_id, :session_id, :athlete_id,
               7.5, 4, 3, 2, 2, :user_id)
        """), {
            "id": wp_id,
            "org_id": str(organization.id),
            "session_id": closed_session,
            "athlete_id": str(athlete.person_id),
            "user_id": str(user.id),
        })
        await async_db.flush()
        return wp_id

    @pytest_asyncio.fixture
    async def wellness_post_for_session(
        self, async_db: AsyncSession, athlete, organization, closed_session, user
    ):
        """Insere wellness_post para o treino encerrado para o atleta."""
        wp_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO wellness_post
              (id, organization_id, training_session_id, athlete_id,
               session_rpe, fatigue_after, mood_after,
               created_by_user_id)
            VALUES
              (:id, :org_id, :session_id, :athlete_id,
               7, 5, 6, :user_id)
        """), {
            "id": wp_id,
            "org_id": str(organization.id),
            "session_id": closed_session,
            "athlete_id": str(athlete.person_id),
            "user_id": str(user.id),
        })
        await async_db.flush()
        return wp_id

    @pytest.mark.asyncio
    async def test_no_wellness_pre_returns_false_with_missing(
        self,
        async_db: AsyncSession,
        athlete,
        closed_session,
    ):
        """
        INV-076 CASO 1: Nenhum wellness_pre para hoje →
        has_completed_daily_wellness() deve retornar (False, ['wellness_pre_hoje']).
        """
        svc = AthleteContentGateService(db=async_db)

        completed, missing = await svc.has_completed_daily_wellness(
            athlete_id=athlete.person_id,
        )

        assert completed is False, (
            "INV-076: sem wellness_pre hoje deve retornar completed=False"
        )
        assert "wellness_pre_hoje" in missing, (
            "INV-076: missing deve conter 'wellness_pre_hoje' quando não há pré-treino"
        )

    @pytest.mark.asyncio
    async def test_wellness_pre_and_post_returns_true(
        self,
        async_db: AsyncSession,
        athlete,
        wellness_pre_today,
        wellness_post_for_session,
    ):
        """
        INV-076 CASO 2: wellness_pre hoje + wellness_post do último treino encerrado →
        has_completed_daily_wellness() deve retornar (True, []).
        """
        svc = AthleteContentGateService(db=async_db)

        completed, missing = await svc.has_completed_daily_wellness(
            athlete_id=athlete.person_id,
        )

        assert completed is True, (
            "INV-076: wellness_pre hoje + wellness_post do treino encerrado "
            "deve retornar completed=True"
        )
        assert missing == [], (
            "INV-076: missing deve ser vazio quando wellness completo"
        )

    @pytest.mark.asyncio
    async def test_missing_items_list_content_when_incomplete(
        self,
        async_db: AsyncSession,
        athlete,
        closed_session,
    ):
        """
        INV-076 CASO 3: wellness incompleto → missing_items lista os itens faltantes
        para exibição na UI.
        Verifica: retorno é lista de strings, não vazia, com conteúdo identificável na UI.
        """
        svc = AthleteContentGateService(db=async_db)

        completed, missing = await svc.has_completed_daily_wellness(
            athlete_id=athlete.person_id,
        )

        assert isinstance(missing, list), (
            "INV-076: missing_items deve ser uma lista"
        )
        assert len(missing) > 0, (
            "INV-076: missing_items deve ser não-vazia quando wellness incompleto"
        )
        # Todos os itens devem ser strings (para exibição na UI)
        for item in missing:
            assert isinstance(item, str), (
                f"INV-076: cada item em missing deve ser str, recebeu {type(item)}"
            )
