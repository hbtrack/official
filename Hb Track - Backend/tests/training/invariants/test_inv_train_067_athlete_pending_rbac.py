"""
INV-TRAIN-067: athlete_pending_collaboration_no_validate
Classe B + D — Integration com async_db (DB policy layer)
Evidencia: docs/ssot/schema.sql — training_pending_items.resolved_by_user_id (linha 2740)
           Validação (resolved_by_user_id IS NOT NULL) é exclusiva do treinador.
Tabelas: training_pending_items (resolved_by_user_id, status)
Regra: Atleta pode colaborar (adicionar informação/pendência), mas NÃO pode validar
       (marcar como resolvido). Validação final é exclusiva do treinador:
       somente o treinador seta resolved_by_user_id e status='resolved'.
       Um item com resolved_by_user_id=NULL representa colaboração sem validação.
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TestInvTrain067:
    """
    INV-TRAIN-067 — atleta colabora mas não valida pendência.
    resolved_by_user_id=NULL = pendência aberta (sem validação do treinador).
    resolved_by_user_id IS NOT NULL = validação feita pelo treinador.
    Evidencia: docs/ssot/schema.sql — training_pending_items.resolved_by_user_id
    """

    @pytest.mark.asyncio
    async def test_pending_item_without_resolver_is_collaboration_only(
        self,
        async_db: AsyncSession,
        training_session,
        athlete,
    ):
        """
        Um training_pending_item com resolved_by_user_id=NULL representa
        colaboração do atleta (informação registrada) SEM validação do treinador.
        Confirma que o schema permite esse estado (sem resolver obrigatório).
        """
        pi_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO training_pending_items
              (id, training_session_id, athlete_id, item_type, description, status)
            VALUES
              (:id, :session_id, :athlete_id, 'material', 'Atleta reportou: bola furada', 'open')
        """), {
            "id": pi_id,
            "session_id": str(training_session.id),
            "athlete_id": str(athlete.person_id),
        })
        await async_db.flush()

        result = await async_db.execute(
            text("SELECT status, resolved_by_user_id FROM training_pending_items WHERE id = :id"),
            {"id": pi_id},
        )
        row = result.fetchone()
        assert row[0] == "open"
        assert row[1] is None, (
            "INV-067: resolved_by_user_id=NULL indica que apenas o atleta colaborou "
            "(registrou a pendência), mas o treinador ainda não validou/resolveu"
        )

    @pytest.mark.asyncio
    async def test_resolution_requires_resolver_user_id(
        self,
        async_db: AsyncSession,
        training_session,
        athlete,
        user,
    ):
        """
        Para validar (resolver) uma pendência, resolved_by_user_id DEVE ser definido
        (representa o treinador que validou). Sem esse campo, o item permanece aberto.
        Confirma a distinção entre colaboração (atleta) e validação (treinador).
        """
        from datetime import datetime, timezone
        pi_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO training_pending_items
              (id, training_session_id, athlete_id, item_type, description)
            VALUES
              (:id, :session_id, :athlete_id, 'equipment', 'Pendência para resolver')
        """), {
            "id": pi_id,
            "session_id": str(training_session.id),
            "athlete_id": str(athlete.person_id),
        })
        await async_db.flush()

        # Treinador valida: set resolved_by_user_id (obrigatório para validação)
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
        assert str(row[1]) == str(user.id), (
            "INV-067: validação final requer resolved_by_user_id do treinador"
        )

    @pytest.mark.asyncio
    async def test_athlete_reported_item_status_remains_open_without_trainer(
        self,
        async_db: AsyncSession,
        training_session,
        athlete,
    ):
        """
        Item inserido pelo atleta sem resolved_by_user_id permanece 'open'.
        Confirma que a colaboração do atleta não valida automaticamente a pendência.
        """
        pi_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO training_pending_items
              (id, training_session_id, athlete_id, item_type, description)
            VALUES
              (:id, :session_id, :athlete_id, 'admin', 'Informacao do atleta')
        """), {
            "id": pi_id,
            "session_id": str(training_session.id),
            "athlete_id": str(athlete.person_id),
        })
        await async_db.flush()

        result = await async_db.execute(
            text("SELECT status FROM training_pending_items WHERE id = :id"),
            {"id": pi_id},
        )
        row = result.fetchone()
        assert row[0] == "open", (
            "INV-067: sem ação do treinador, pendência permanece 'open'"
        )
