"""
EXB-ACL-005: O criador do exercício tem acesso implícito — sem necessidade de entrada na exercise_acl.
Classe B — Service Guard (ExerciseAclService.has_access)
Evidência: exercise_acl_service.py linhas 97-98 — creator bypass

Regra: has_access(exercise_id, user_id) → True para o criador mesmo sem linha em exercise_acl.
       has_access(exercise_id, outsider_id) → False para usuário sem ACL e não-criador.
"""
import pytest
import pytest_asyncio
from uuid import uuid4, UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.exercise_acl_service import ExerciseAclService


class TestExbAcl005CreatorImplicitAccess:
    """
    EXB-ACL-005: Criador tem acesso implícito sem entrada em exercise_acl.
    """

    @pytest_asyncio.fixture
    async def acl005_setup(self, async_db: AsyncSession, organization, user):
        """Cria exercício restricted com created_by_user_id=user. Sem entrada em exercise_acl."""
        exercise_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Exercicio ACL005', 'Desc', 'ORG', :org_id, :user_id, 'restricted')
        """), {
            "id": exercise_id,
            "org_id": str(organization.id),
            "user_id": str(user.id),
        })

        await async_db.flush()

        return {
            "exercise_id": UUID(exercise_id),
            "creator_id": user.id,
            # UUID aleatorio -- outsider sem ACL (has_access nao faz lookup do user no DB)
            "outsider_id": uuid4(),
        }

    @pytest.mark.asyncio
    async def test_creator_has_access_without_acl_entry(
        self, async_db: AsyncSession, acl005_setup
    ):
        """Happy: criador obtém has_access=True mesmo sem linha em exercise_acl."""
        service = ExerciseAclService(async_db)

        # Garantir ausência de linha ACL para o criador
        count_result = await async_db.execute(text("""
            SELECT COUNT(*) FROM exercise_acl
            WHERE exercise_id = :eid AND user_id = :uid
        """), {"eid": str(acl005_setup["exercise_id"]), "uid": str(acl005_setup["creator_id"])})
        acl_count = count_result.scalar()
        assert acl_count == 0, f"Setup inválido: existem {acl_count} linhas ACL para o criador"

        has = await service.has_access(
            exercise_id=acl005_setup["exercise_id"],
            user_id=acl005_setup["creator_id"],
        )
        assert has is True, "Criador deve ter acesso implícito — bypass do criador ausente (EXB-ACL-005)"

    @pytest.mark.asyncio
    async def test_outsider_without_acl_has_no_access(
        self, async_db: AsyncSession, acl005_setup
    ):
        """Violation: usuário sem autoria e sem ACL obtém has_access=False."""
        service = ExerciseAclService(async_db)

        has = await service.has_access(
            exercise_id=acl005_setup["exercise_id"],
            user_id=acl005_setup["outsider_id"],
        )
        assert has is False, "Outsider sem ACL deve ter has_access=False"
