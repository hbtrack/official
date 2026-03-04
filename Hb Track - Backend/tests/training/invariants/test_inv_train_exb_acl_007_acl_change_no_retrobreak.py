"""
EXB-ACL-007: Mudancas de ACL ou visibility_mode NAO destroem referencias historicas de session_exercise.
Classe A -- DB Constraint (FK preservacao)
Evidencia: exercises / training_session_exercises -- FK RESTRICT

Regra: revogar ACL ou alterar visibility_mode NAO pode deletar training_session_exercises existentes.
"""
import pytest
import pytest_asyncio
from uuid import uuid4, UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TestExbAcl007AclChangeNoRetroBreak:
    """
    EXB-ACL-007: Mudanca de ACL/visibility_mode nao retroage sobre training_session_exercises.
    """

    @pytest_asyncio.fixture
    async def acl007_setup(
        self, async_db: AsyncSession, organization, user, training_session
    ):
        """
        Cria exercicio restricted + training_session_exercise.
        ACL entry do proprio user (creator) inserida via SQL para teste de delecao.
        """
        exercise_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Exercicio ACL007', 'Desc', 'ORG', :org_id, :user_id, 'restricted')
        """), {
            "id": exercise_id,
            "org_id": str(organization.id),
            "user_id": str(user.id),
        })

        # ACL entry para o user (ja existe no DB como person+user)
        await async_db.execute(text("""
            INSERT INTO exercise_acl (exercise_id, user_id, granted_by_user_id)
            VALUES (:eid, :uid, :uid)
            ON CONFLICT DO NOTHING
        """), {"eid": exercise_id, "uid": str(user.id)})

        # training_session_exercise
        se_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO training_session_exercises (id, session_id, exercise_id, order_index)
            VALUES (:id, :session_id, :exercise_id, 0)
        """), {
            "id": se_id,
            "session_id": str(training_session.id),
            "exercise_id": exercise_id,
        })
        await async_db.flush()

        return {
            "exercise_id": UUID(exercise_id),
            "session_exercise_id": UUID(se_id),
            "creator_id": user.id,
        }

    @pytest.mark.asyncio
    async def test_acl_deletion_does_not_delete_session_exercise(
        self, async_db: AsyncSession, acl007_setup
    ):
        """Invariante: deletar exercise_acl NAO remove training_session_exercise (EXB-ACL-007)."""
        await async_db.execute(text("""
            DELETE FROM exercise_acl
            WHERE exercise_id = :eid AND user_id = :uid
        """), {
            "eid": str(acl007_setup["exercise_id"]),
            "uid": str(acl007_setup["creator_id"]),
        })
        await async_db.flush()

        result = await async_db.execute(text("""
            SELECT id FROM training_session_exercises WHERE id = :id
        """), {"id": str(acl007_setup["session_exercise_id"])})
        row = result.fetchone()
        assert row is not None, (
            "training_session_exercise deletado ao remover ACL -- violacao EXB-ACL-007"
        )

    @pytest.mark.asyncio
    async def test_visibility_mode_change_does_not_delete_session_exercise(
        self, async_db: AsyncSession, acl007_setup
    ):
        """Invariante: alterar visibility_mode NAO destroi training_session_exercise (EXB-ACL-007)."""
        await async_db.execute(text("""
            UPDATE exercises SET visibility_mode = 'org_wide' WHERE id = :id
        """), {"id": str(acl007_setup["exercise_id"])})
        await async_db.flush()

        result = await async_db.execute(text("""
            SELECT id, exercise_id FROM training_session_exercises WHERE id = :id
        """), {"id": str(acl007_setup["session_exercise_id"])})
        row = result.fetchone()
        assert row is not None, (
            "training_session_exercise deletado apos mudar visibility_mode -- violacao EXB-ACL-007"
        )
        assert str(row[1]) == str(acl007_setup["exercise_id"])

    @pytest.mark.asyncio
    async def test_exercise_delete_blocked_when_session_exercise_exists(
        self, async_db: AsyncSession, acl007_setup
    ):
        """Invariante: FK RESTRICT em training_session_exercises bloqueia deleção fisica do exercício."""
        # Remover ACL (CASCADE exercise_acl.exercise_id é CASCADE, nao RESTRICT)
        await async_db.execute(text("""
            DELETE FROM exercise_acl WHERE exercise_id = :eid
        """), {"eid": str(acl007_setup["exercise_id"])})
        await async_db.flush()

        # FK RESTRICT em training_session_exercises.exercise_id deve bloquear
        with pytest.raises(Exception):
            await async_db.execute(text("""
                DELETE FROM exercises WHERE id = :id
            """), {"id": str(acl007_setup["exercise_id"])})
            await async_db.flush()
