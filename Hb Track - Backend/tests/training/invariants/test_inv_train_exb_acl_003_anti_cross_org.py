"""
INV-TRAIN-EXB-ACL-003: Isolamento cross-org — usuário sem ACL não acessa
exercise restricted de outra organização.
Classe B — Service Guard (ExerciseAclService)
Evidência: exercise_acl_service.py — has_access()

Regra: has_access() retorna False para usuário sem ACL entry em exercise restricted.
Usuário com ACL entry (mesmo de outra org conceitualmente) acessa: ACL é a fonte de verdade.
"""
import pytest
import pytest_asyncio
from uuid import uuid4, UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.exercise_acl_service import ExerciseAclService


class TestInvTrainExbAcl003AntiCrossOrg:
    """
    INV-EXB-ACL-003: ExerciseAclService.has_access() retorna False
    para usuário sem ACL em exercise restricted (isolamento cross-org).
    """

    @pytest_asyncio.fixture
    async def inv003_setup(self, async_db: AsyncSession, organization, user):
        """Cria restricted exercise e dois usuários: creator e outsider."""
        restricted_id = str(uuid4())
        outsider_user_id = str(uuid4())

        # Exercise restricted (criado pelo user — creator)
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Restricted Exercise INV003', 'ORG', :org_id, :user_id, 'restricted')
        """), {"id": restricted_id, "org_id": str(organization.id), "user_id": str(user.id)})

        # Outsider user (sem ACL entry no restricted exercise)
        pid = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO persons (id, first_name, last_name, full_name, birth_date)
            VALUES (:id, 'Outsider', 'User', 'Outsider User INV003', '1995-01-01')
        """), {"id": pid})
        email = f"outsider_{str(uuid4())[:8]}@example.com"
        await async_db.execute(text("""
            INSERT INTO users (id, email, person_id, password_hash, status)
            VALUES (:id, :email, :person_id, 'hash', 'ativo')
        """), {"id": outsider_user_id, "email": email, "person_id": pid})

        await async_db.flush()
        return {
            "restricted_id": UUID(restricted_id),
            "creator_user_id": user.id,
            "outsider_user_id": UUID(outsider_user_id),
        }

    @pytest.mark.asyncio
    async def test_outsider_without_acl_has_no_access(
        self, async_db: AsyncSession, inv003_setup
    ):
        """Usuário sem ACL entry não pode acessar exercise restricted."""
        service = ExerciseAclService(async_db)

        result = await service.has_access(
            exercise_id=inv003_setup["restricted_id"],
            user_id=inv003_setup["outsider_user_id"]
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_creator_always_has_access(
        self, async_db: AsyncSession, inv003_setup
    ):
        """Creator tem acesso ao próprio exercise restricted (bypass INV-EXB-ACL-005)."""
        service = ExerciseAclService(async_db)

        result = await service.has_access(
            exercise_id=inv003_setup["restricted_id"],
            user_id=inv003_setup["creator_user_id"]
        )
        assert result is True
