"""
INV-TRAIN-069: exercise_media_accessible_to_athlete
Classe B + D — Integration com async_db (DB access policy)
Evidencia: docs/ssot/schema.sql — exercise_media (linha 1262),
           training_session_exercises (linha 2757)
Tabelas: training_session_exercises, exercise_media (exercise_id FK)
Regra: O atleta acessa mídia do exercício via sessão de treino,
       independente de visibility_mode do exercício em si.
       JOIN: training_session_exercises → exercises → exercise_media
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TestInvTrain069:
    """
    INV-TRAIN-069 — mídia do exercício acessível ao atleta via sessão,
    independente de visibility_mode (org_wide | restricted).
    Evidencia: docs/ssot/schema.sql — exercise_media + training_session_exercises
    """

    @pytest_asyncio.fixture
    async def exercise_with_media(self, async_db: AsyncSession, organization, user):
        """Cria exercise com visibility_mode='restricted' + exercise_media vinculada."""
        ex_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises
              (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES
              (:id, 'Exercício com Mídia', 'Descrição', 'ORG', :org_id, :user_id, 'restricted')
        """), {
            "id": ex_id,
            "org_id": str(organization.id),
            "user_id": str(user.id),
        })
        await async_db.flush()

        media_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercise_media
              (id, exercise_id, media_type, url, title, order_index, created_by_user_id)
            VALUES
              (:id, :ex_id, 'video', 'https://example.com/media_test.mp4',
               'Demo Exercício', 1, :user_id)
        """), {
            "id": media_id,
            "ex_id": ex_id,
            "user_id": str(user.id),
        })
        await async_db.flush()
        return {"exercise_id": ex_id, "media_id": media_id}

    @pytest.mark.asyncio
    async def test_media_accessible_via_session_join(
        self,
        async_db: AsyncSession,
        training_session,
        exercise_with_media,
    ):
        """
        Atleta acessa mídia via JOIN: training_session_exercises → exercises → exercise_media.
        visibility_mode='restricted' no exercício NÃO bloqueia acesso à mídia
        quando o exercício está vinculado à sessão de treino.
        """
        se_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO training_session_exercises
              (id, session_id, exercise_id, order_index)
            VALUES
              (:id, :session_id, :exercise_id, 1)
        """), {
            "id": se_id,
            "session_id": str(training_session.id),
            "exercise_id": exercise_with_media["exercise_id"],
        })
        await async_db.flush()

        # JOIN que o atleta usa para acessar mídia via sessão
        result = await async_db.execute(text("""
            SELECT em.id, em.media_type, em.url, e.visibility_mode
              FROM training_session_exercises tse
              JOIN exercises e ON e.id = tse.exercise_id
              JOIN exercise_media em ON em.exercise_id = e.id
             WHERE tse.session_id = :session_id
               AND tse.deleted_at IS NULL
        """), {"session_id": str(training_session.id)})
        rows = result.fetchall()
        assert len(rows) == 1, "INV-069: mídia deve ser acessível via JOIN de sessão"
        assert rows[0][1] == "video"
        assert "media_test.mp4" in rows[0][2]
        # visibility_mode='restricted' não bloqueia o acesso via sessão
        assert rows[0][3] == "restricted", (
            "INV-069: mesmo com visibility_mode='restricted', mídia é acessível via sessão"
        )

    @pytest.mark.asyncio
    async def test_media_accessible_regardless_of_visibility_mode_org_wide(
        self,
        async_db: AsyncSession,
        training_session,
        organization,
        user,
    ):
        """
        Mesmo com visibility_mode='org_wide', mídia é acessível via sessão.
        Confirma que a regra se aplica a ambos os modos.
        """
        ex_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises
              (id, name, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES
              (:id, 'Exercício Org Wide', 'ORG', :org_id, :user_id, 'org_wide')
        """), {
            "id": ex_id,
            "org_id": str(organization.id),
            "user_id": str(user.id),
        })

        media_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercise_media
              (id, exercise_id, media_type, url, order_index, created_by_user_id)
            VALUES
              (:id, :ex_id, 'image', 'https://example.com/image.png', 1, :user_id)
        """), {
            "id": media_id,
            "ex_id": ex_id,
            "user_id": str(user.id),
        })

        se_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO training_session_exercises
              (id, session_id, exercise_id, order_index)
            VALUES
              (:id, :session_id, :exercise_id, 2)
        """), {
            "id": se_id,
            "session_id": str(training_session.id),
            "exercise_id": ex_id,
        })
        await async_db.flush()

        result = await async_db.execute(text("""
            SELECT em.media_type, e.visibility_mode
              FROM training_session_exercises tse
              JOIN exercises e ON e.id = tse.exercise_id
              JOIN exercise_media em ON em.exercise_id = e.id
             WHERE tse.session_id = :session_id AND tse.exercise_id = :ex_id
               AND tse.deleted_at IS NULL
        """), {"session_id": str(training_session.id), "ex_id": ex_id})
        rows = result.fetchall()
        assert len(rows) == 1
        assert rows[0][1] == "org_wide"
