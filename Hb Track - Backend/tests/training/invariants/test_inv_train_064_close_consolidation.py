"""
INV-TRAIN-064: official_attendance_at_closure
Classe B — Runtime Integration com async_db
Evidencia: docs/ssot/schema.sql — training_sessions.closed_at (linha 2820)
           COMMENT: 'Timestamp de encerramento da sessão'
Tabelas: training_sessions (closed_at), attendance (presence_status)
Regra: Presença oficial só é consolidada no encerramento da sessão
       (quando training_sessions.closed_at é preenchido pelo treinador).
       Antes do encerramento, status permanece 'preconfirm'.
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TestInvTrain064:
    """
    INV-TRAIN-064 — presença oficial consolida somente ao encerrar a sessão.
    O campo training_sessions.closed_at marca o momento do encerramento.
    Evidencia: docs/ssot/schema.sql — training_sessions.closed_at
    """

    @pytest_asyncio.fixture
    async def team_reg(self, async_db: AsyncSession, athlete, team, user):
        tr_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO team_registrations (id, athlete_id, team_id, created_by_user_id)
            VALUES (:id, :athlete_id, :team_id, :user_id)
        """), {
            "id": tr_id,
            "athlete_id": str(athlete.person_id),
            "team_id": str(team.id),
            "user_id": str(user.id),
        })
        await async_db.flush()
        return tr_id

    @pytest.mark.asyncio
    async def test_session_open_attendance_preconfirm(
        self,
        async_db: AsyncSession,
        training_session,
        athlete,
        user,
        team_reg,
    ):
        """
        Sessão ainda aberta (closed_at IS NULL): attendance com 'preconfirm'
        representa estado pré-oficial. Verifica que a sessão não tem closed_at
        e que 'preconfirm' é aceito como status pendente de encerramento.
        """
        # Confirmar sessão está aberta
        result = await async_db.execute(
            text("SELECT closed_at FROM training_sessions WHERE id = :id"),
            {"id": str(training_session.id)},
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] is None, "INV-064: sessão recém-criada deve ter closed_at=NULL (aberta)"

        # Inserir attendance 'preconfirm' (estado pré-oficial)
        att_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO attendance
              (id, training_session_id, team_registration_id, athlete_id,
               presence_status, source, created_by_user_id)
            VALUES
              (:id, :session_id, :tr_id, :athlete_id, 'preconfirm', 'manual', :user_id)
        """), {
            "id": att_id,
            "session_id": str(training_session.id),
            "tr_id": team_reg,
            "athlete_id": str(athlete.person_id),
            "user_id": str(user.id),
        })
        await async_db.flush()

        result2 = await async_db.execute(
            text("SELECT presence_status FROM attendance WHERE id = :id"),
            {"id": att_id},
        )
        row2 = result2.fetchone()
        assert row2[0] == "preconfirm"

    @pytest.mark.asyncio
    async def test_session_closure_sets_closed_at(
        self,
        async_db: AsyncSession,
        training_session,
    ):
        """
        O ato de encerrar a sessão define closed_at. Após o encerramento,
        a presença oficial pode ser consolidada (closed_at IS NOT NULL).
        Simula o encerramento via UPDATE direto.
        """
        now_utc = datetime.now(timezone.utc)
        await async_db.execute(text("""
            UPDATE training_sessions SET closed_at = :ts WHERE id = :id
        """), {"ts": now_utc, "id": str(training_session.id)})
        await async_db.flush()

        result = await async_db.execute(
            text("SELECT closed_at FROM training_sessions WHERE id = :id"),
            {"id": str(training_session.id)},
        )
        row = result.fetchone()
        assert row[0] is not None, (
            "INV-064: após encerramento, closed_at deve estar preenchido"
        )
