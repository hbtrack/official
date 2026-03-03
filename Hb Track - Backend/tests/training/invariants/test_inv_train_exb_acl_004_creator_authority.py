"""
INV-TRAIN-EXB-ACL-004: Apenas o criador do exercício pode gerenciar ACL.
Classe B — Service Guard (ExerciseAclService)
Evidência: exercise_acl_service.py — grant_access(), revoke_access()

Regra: Não-criadores recebem AclUnauthorizedError ao tentar grant ou revoke.
"""
import pytest
import pytest_asyncio
from uuid import uuid4, UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.exercise_acl_service import ExerciseAclService
from app.core.exceptions import AclUnauthorizedError


class TestInvTrainExbAcl004CreatorAuthority:
    """
    INV-EXB-ACL-004: ExerciseAclService.grant_access() e revoke_access()
    levantam AclUnauthorizedError quando acting_user_id != criador.
    """

    @pytest_asyncio.fixture
    async def inv004_setup(self, async_db: AsyncSession, organization, user):
        """Cria restricted exercise (creator=user) e um non-creator user."""
        restricted_id = str(uuid4())
        non_creator_id = str(uuid4())
        target_user_id = str(uuid4())

        # Exercise restricted (criado pelo user — creator)
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Restricted Exercise INV004', 'ORG', :org_id, :user_id, 'restricted')
        """), {"id": restricted_id, "org_id": str(organization.id), "user_id": str(user.id)})

        # Non-creator user (não pode gerenciar ACL)
        pid_nc = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO persons (id, first_name, last_name, full_name, birth_date)
            VALUES (:id, 'Non', 'Creator', 'Non Creator INV004', '1995-01-01')
        """), {"id": pid_nc})
        email_nc = f"noncreator_{str(uuid4())[:8]}@example.com"
        await async_db.execute(text("""
            INSERT INTO users (id, email, person_id, password_hash, status)
            VALUES (:id, :email, :person_id, 'hash', 'ativo')
        """), {"id": non_creator_id, "email": email_nc, "person_id": pid_nc})

        # Target user (quem receberá/perderá acesso no teste de grant)
        pid_tgt = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO persons (id, first_name, last_name, full_name, birth_date)
            VALUES (:id, 'Target', 'User', 'Target User INV004', '1995-01-01')
        """), {"id": pid_tgt})
        email_tgt = f"target_{str(uuid4())[:8]}@example.com"
        await async_db.execute(text("""
            INSERT INTO users (id, email, person_id, password_hash, status)
            VALUES (:id, :email, :person_id, 'hash', 'ativo')
        """), {"id": target_user_id, "email": email_tgt, "person_id": pid_tgt})

        await async_db.flush()
        return {
            "restricted_id": UUID(restricted_id),
            "creator_user_id": user.id,
            "non_creator_id": UUID(non_creator_id),
            "target_user_id": UUID(target_user_id),
        }

    @pytest.mark.asyncio
    async def test_non_creator_grant_raises_unauthorized(
        self, async_db: AsyncSession, inv004_setup
    ):
        """Non-creator tentando grant_access deve receber AclUnauthorizedError."""
        service = ExerciseAclService(async_db)

        with pytest.raises(AclUnauthorizedError):
            await service.grant_access(
                exercise_id=inv004_setup["restricted_id"],
                target_user_id=inv004_setup["target_user_id"],
                acting_user_id=inv004_setup["non_creator_id"]
            )

    @pytest.mark.asyncio
    async def test_non_creator_revoke_raises_unauthorized(
        self, async_db: AsyncSession, inv004_setup
    ):
        """Non-creator tentando revoke_access deve receber AclUnauthorizedError."""
        service = ExerciseAclService(async_db)

        with pytest.raises(AclUnauthorizedError):
            await service.revoke_access(
                exercise_id=inv004_setup["restricted_id"],
                target_user_id=inv004_setup["target_user_id"],
                acting_user_id=inv004_setup["non_creator_id"]
            )
