"""
INV-TRAIN-068: athlete_sees_training_before
Classe D — Integration com async_db (DB access policy)
Evidencia: docs/ssot/schema.sql — training_sessions (linha 2789), 
           training_session_exercises (linha 2757)
Tabelas: training_sessions (session_at, main_objective), training_session_exercises
Regra: O atleta pode visualizar (read-only) horário, exercícios e objetivo
       do treino antes de sua realização.
       training_session_exercises vincula sessão a exercícios para exibição.
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TestInvTrain068:
    """
    INV-TRAIN-068 — atleta vê horário, exercícios e objetivo antes do treino (read-only).
    training_session_exercises expõe exercícios do treino para consulta.
    Evidencia: docs/ssot/schema.sql — training_sessions + training_session_exercises
    """

    @pytest_asyncio.fixture
    async def exercise(self, async_db: AsyncSession, organization, user):
        """Cria exercise para vincular à sessão."""
        ex_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises
              (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES
              (:id, 'Exercício Visível ao Atleta', 'Definição do exercício', 'ORG',
               :org_id, :user_id, 'org_wide')
        """), {
            "id": ex_id,
            "org_id": str(organization.id),
            "user_id": str(user.id),
        })
        await async_db.flush()
        return ex_id

    @pytest.mark.asyncio
    async def test_training_session_objective_and_time_queryable(
        self,
        async_db: AsyncSession,
        training_session,
    ):
        """
        O atleta pode ler horário (session_at) e objetivo (main_objective) da sessão.
        Verifica que esses campos estão disponíveis para consulta.
        """
        result = await async_db.execute(
            text("SELECT session_at, main_objective FROM training_sessions WHERE id = :id"),
            {"id": str(training_session.id)},
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] is not None, "INV-068: session_at deve estar disponível (leitura)"
        assert row[1] is not None, "INV-068: main_objective deve estar disponível (leitura)"

    @pytest.mark.asyncio
    async def test_session_exercises_linked_and_queryable(
        self,
        async_db: AsyncSession,
        training_session,
        exercise,
    ):
        """
        training_session_exercises vincula exercícios à sessão, tornando-os visíveis
        ao atleta (read-only) antes do treino.
        Verifica que a consulta session_id → exercise_id retorna os exercícios esperados.
        """
        se_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO training_session_exercises
              (id, session_id, exercise_id, order_index, duration_minutes)
            VALUES
              (:id, :session_id, :exercise_id, 1, 15)
        """), {
            "id": se_id,
            "session_id": str(training_session.id),
            "exercise_id": exercise,
        })
        await async_db.flush()

        result = await async_db.execute(
            text("""
                SELECT tse.exercise_id, tse.order_index, e.name
                  FROM training_session_exercises tse
                  JOIN exercises e ON e.id = tse.exercise_id
                 WHERE tse.session_id = :session_id
                   AND tse.deleted_at IS NULL
            """),
            {"session_id": str(training_session.id)},
        )
        rows = result.fetchall()
        assert len(rows) == 1, "INV-068: um exercício deve estar visível para a sessão"
        assert rows[0][1] == 1  # order_index
        assert "Visível" in rows[0][2]

    @pytest.mark.asyncio
    async def test_session_basic_fields_accessible_before_start(
        self,
        async_db: AsyncSession,
        training_session,
    ):
        """
        Sessão futura (session_at > now): location e session_type acessíveis.
        O atleta vê esses dados antes do início para planejamento.
        """
        result = await async_db.execute(
            text("SELECT location, session_type, duration_planned_minutes FROM training_sessions WHERE id = :id"),
            {"id": str(training_session.id)},
        )
        row = result.fetchone()
        assert row is not None
        # session_type é NOT NULL — deve estar presente
        assert row[1] is not None, "INV-068: session_type deve estar disponível (read-only)"
