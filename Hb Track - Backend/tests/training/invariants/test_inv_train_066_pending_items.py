"""
INV-TRAIN-066: pending_queue_separate
Classe A — Runtime Integration com async_db
Evidencia: docs/ssot/schema.sql — CREATE TABLE public.training_pending_items (linha 2740)
           ck_pending_item_status: 'open','resolved','cancelled'
           ck_pending_item_type: 'equipment','material','admin','other'
Tabelas: training_pending_items (tabela separada de attendance e training_sessions)
Regra: Pendências do treino ficam em tabela separada (training_pending_items),
       isoladas da tabela de presença (attendance) e da sessão em si.
       Cada item tem ciclo de vida próprio (open → resolved | cancelled).
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class TestInvTrain066:
    """
    INV-TRAIN-066 — pendências vão para fila separada training_pending_items,
    com ciclo de vida próprio independente da sessão.
    Evidencia: docs/ssot/schema.sql — training_pending_items (tabela separada)
    """

    @pytest.mark.asyncio
    async def test_pending_item_insert_separate_from_attendance(
        self,
        async_db: AsyncSession,
        training_session,
        athlete,
        user,
    ):
        """
        Insere training_pending_item e confirma que é uma entidade separada.
        Não há ligação obrigatória com a tabela attendance.
        """
        pi_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO training_pending_items
              (id, training_session_id, athlete_id, item_type, description, status)
            VALUES
              (:id, :session_id, :athlete_id, 'equipment', 'Faltou colete #7', 'open')
        """), {
            "id": pi_id,
            "session_id": str(training_session.id),
            "athlete_id": str(user.id),
        })
        await async_db.flush()

        result = await async_db.execute(
            text("SELECT item_type, status, description FROM training_pending_items WHERE id = :id"),
            {"id": pi_id},
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] == "equipment"
        assert row[1] == "open"
        assert "Faltou colete" in row[2]

    @pytest.mark.asyncio
    async def test_pending_item_lifecycle_open_to_resolved(
        self,
        async_db: AsyncSession,
        training_session,
        athlete,
        user,
    ):
        """
        Ciclo de vida: open → resolved. resolved_by_user_id marca quem resolveu
        (treinador). Confirma que o schema suporta o ciclo de vida completo.
        """
        from datetime import datetime, timezone
        pi_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO training_pending_items
              (id, training_session_id, athlete_id, item_type, description)
            VALUES
              (:id, :session_id, :athlete_id, 'admin', 'Documento faltando')
        """), {
            "id": pi_id,
            "session_id": str(training_session.id),
            "athlete_id": str(user.id),
        })
        await async_db.flush()

        now = datetime.now(timezone.utc)
        await async_db.execute(text("""
            UPDATE training_pending_items
               SET status = 'resolved',
                   resolved_at = :ts,
                   resolved_by_user_id = :user_id
             WHERE id = :id
        """), {"ts": now, "user_id": str(user.id), "id": pi_id})
        await async_db.flush()

        result = await async_db.execute(
            text("SELECT status, resolved_by_user_id FROM training_pending_items WHERE id = :id"),
            {"id": pi_id},
        )
        row = result.fetchone()
        assert row[0] == "resolved"
        assert row[1] is not None

    @pytest.mark.asyncio
    async def test_pending_item_invalid_type_rejected(
        self,
        async_db: AsyncSession,
        training_session,
        athlete,
        user,
    ):
        """
        ck_pending_item_type rejeita tipos não válidos.
        Somente 'equipment','material','admin','other' são permitidos.
        """
        with pytest.raises(IntegrityError):
            await async_db.execute(text("""
                INSERT INTO training_pending_items
                  (id, training_session_id, athlete_id, item_type, description)
                VALUES
                  (:id, :session_id, :athlete_id, 'invalid_type', 'Test')
            """), {
                "id": str(uuid4()),
                "session_id": str(training_session.id),
                "athlete_id": str(user.id),
            })
            await async_db.flush()


