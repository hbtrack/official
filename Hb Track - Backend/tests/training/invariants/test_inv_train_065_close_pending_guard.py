"""
INV-TRAIN-065: closure_allows_inconsistency_as_pending
Classe B — Runtime Integration com async_db
Evidencia: docs/ssot/schema.sql — training_sessions.closed_at (linha 2820),
           training_pending_items.status (linha 2740)
Tabelas: training_sessions (closed_at), training_pending_items (status)
Regra: O encerramento (close) da sessão DEVE funcionar mesmo que existam
       inconsistências/pendências — itens inconsistentes viram training_pending_items
       com status='open'. O close NÃO é bloqueado por pendências existentes.
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TestInvTrain065:
    """
    INV-TRAIN-065 — fechamento da sessão não é bloqueado por inconsistências;
    inconsistências viram pendências (training_pending_items status='open').
    Evidencia: docs/ssot/schema.sql — training_sessions.closed_at,
               CONSTRAINT ck_pending_item_status permite 'open' como default.
    """

    @pytest.mark.asyncio
    async def test_close_session_with_pending_items_coexist(
        self,
        async_db: AsyncSession,
        training_session,
        athlete,
        user,
    ):
        """
        Um training_pending_item com status='open' pode existir para a sessão
        enquanto a sessão é encerrada (closed_at preenchido).
        Verifica que não há constraint de DB impedindo o coexistência.
        """
        # Criar pendência para a sessão
        pi_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO training_pending_items
              (id, training_session_id, athlete_id, item_type, description, status)
            VALUES
              (:id, :session_id, :athlete_id, 'admin', 'Inconsistencia de presença', 'open')
        """), {
            "id": pi_id,
            "session_id": str(training_session.id),
            "athlete_id": str(user.id),
        })
        await async_db.flush()

        # Encerrar a sessão (close) — deve funcionar mesmo com pendências abertas
        now_utc = datetime.now(timezone.utc)
        await async_db.execute(text("""
            UPDATE training_sessions SET closed_at = :ts WHERE id = :id
        """), {"ts": now_utc, "id": str(training_session.id)})
        await async_db.flush()

        # Verificar que closed_at foi definido (sessão encerrada)
        result = await async_db.execute(
            text("SELECT closed_at FROM training_sessions WHERE id = :id"),
            {"id": str(training_session.id)},
        )
        row_session = result.fetchone()
        assert row_session[0] is not None, (
            "INV-065: sessão deve poder ser encerrada mesmo com pendências abertas"
        )

        # Verificar que a pendência ainda está 'open' (não foi bloqueada nem removida)
        result2 = await async_db.execute(
            text("SELECT status FROM training_pending_items WHERE id = :id"),
            {"id": pi_id},
        )
        row_pi = result2.fetchone()
        assert row_pi is not None
        assert row_pi[0] == "open", (
            "INV-065: pendência deve permanecer 'open' após encerramento — é fila separada"
        )

    @pytest.mark.asyncio
    async def test_pending_item_status_enum_allows_open(
        self,
        async_db: AsyncSession,
        training_session,
        athlete,
        user,
    ):
        """
        ck_pending_item_status: status 'open' é o valor default e sempre permitido.
        Confirma que o schema suporta a noção de pendência como item não resolvido.
        """
        pi_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO training_pending_items
              (id, training_session_id, athlete_id, item_type, description)
            VALUES
              (:id, :session_id, :athlete_id, 'other', 'Teste status open default')
        """), {
            "id": pi_id,
            "session_id": str(training_session.id),
            "athlete_id": str(user.id),
        })
        await async_db.flush()

        result = await async_db.execute(
            text("SELECT status FROM training_pending_items WHERE id = :id"),
            {"id": pi_id},
        )
        row = result.fetchone()
        assert row[0] == "open"


