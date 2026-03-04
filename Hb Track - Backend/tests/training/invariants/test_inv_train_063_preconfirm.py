"""
INV-TRAIN-063: athlete_preconfirm_not_official
Classe A + B — Runtime Integration com async_db
Evidencia: docs/ssot/schema.sql — ck_attendance_status — permite 'preconfirm'
Tabelas: attendance (presence_status CHECK: 'present','absent','justified','preconfirm')
Regra: Atleta pode ter status 'preconfirm' em attendance, mas presença oficial
       só consolida no encerramento da sessão pelo treinador.
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class TestInvTrain063:
    """
    INV-TRAIN-063 — atleta pode pré-confirmar (preconfirm) mas presença oficial
    só é consolidada pelo treinador no encerramento (close) da sessão.
    Evidencia: docs/ssot/schema.sql — CONSTRAINT ck_attendance_status
    """

    @pytest_asyncio.fixture
    async def team_reg(self, async_db: AsyncSession, athlete, team, user):
        """Cria team_registration para uso em attendance."""
        tr_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO team_registrations (id, athlete_id, team_id, created_by_user_id)
            VALUES (:id, :athlete_id, :team_id, :user_id)
        """), {
            "id": tr_id,
            "athlete_id": str(athlete.id),
            "team_id": str(team.id),
            "user_id": str(user.id),
        })
        await async_db.flush()
        return tr_id

    @pytest.mark.asyncio
    async def test_preconfirm_status_is_valid(
        self,
        async_db: AsyncSession,
        training_session,
        athlete,
        user,
        team_reg,
    ):
        """
        Inserir attendance com presence_status='preconfirm' deve ser aceito
        pelo constraint ck_attendance_status. Representa pré-confirmação do atleta,
        mas NÃO é presença oficial (que só ocorre no close da sessão).
        """
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
            "athlete_id": str(athlete.id),
            "user_id": str(user.id),
        })
        await async_db.flush()

        result = await async_db.execute(
            text("SELECT presence_status FROM attendance WHERE id = :id"),
            {"id": att_id},
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] == "preconfirm", (
            "INV-063: status 'preconfirm' deve ser aceito como pré-confirmação do atleta"
        )

    @pytest.mark.asyncio
    async def test_preconfirm_is_not_official_status(
        self,
        async_db: AsyncSession,
        training_session,
        athlete,
        user,
        team_reg,
    ):
        """
        O valor 'official' NÃO é um status válido no enum do DB.
        Confirma que presença oficial não é um status armazenado diretamente —
        é derivada do closed_at da sessão.
        """
        att_id = str(uuid4())
        with pytest.raises(IntegrityError):
            await async_db.execute(text("""
                INSERT INTO attendance
                  (id, training_session_id, team_registration_id, athlete_id,
                   presence_status, source, created_by_user_id)
                VALUES
                  (:id, :session_id, :tr_id, :athlete_id, 'official', 'manual', :user_id)
            """), {
                "id": att_id,
                "session_id": str(training_session.id),
                "tr_id": team_reg,
                "athlete_id": str(athlete.id),
                "user_id": str(user.id),
            })
            await async_db.flush()
