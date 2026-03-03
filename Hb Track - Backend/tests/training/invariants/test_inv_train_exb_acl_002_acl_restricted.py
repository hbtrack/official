"""
INV-TRAIN-EXB-ACL-002: ACL só aplicável a exercises com visibility_mode='restricted'.
Classe B — Service Guard (ExerciseAclService)
Evidência: exercise_acl_service.py — grant_access()

Regra: grant_access() levanta AclNotApplicableError quando visibility_mode != 'restricted'.
"""
import pytest
import pytest_asyncio
from uuid import uuid4, UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.exercise_acl_service import ExerciseAclService
from app.core.exceptions import AclNotApplicableError


class TestInvTrainExbAcl002AclRestricted:
    """
    INV-EXB-ACL-002: ExerciseAclService.grant_access() levanta
    AclNotApplicableError para exercises org_wide.
    has_access() funciona corretamente para restricted com ACL entry.
    """

    @pytest_asyncio.fixture
    async def inv002_setup(self, async_db: AsyncSession, organization, user):
        """Cria exercises org_wide e restricted para teste."""
        org_wide_id = str(uuid4())
        restricted_id = str(uuid4())
        other_user_id = str(uuid4())

        # Exercise org_wide (criado pelo user)
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'OrgWide Exercise INV002', 'ORG', :org_id, :user_id, 'org_wide')
        """), {"id": org_wide_id, "org_id": str(organization.id), "user_id": str(user.id)})

        # Exercise restricted (criado pelo user)
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Restricted Exercise INV002', 'ORG', :org_id, :user_id, 'restricted')
        """), {"id": restricted_id, "org_id": str(organization.id), "user_id": str(user.id)})

        # Cria outro user (target para ACL)
        pid = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO persons (id, first_name, last_name, full_name, birth_date)
            VALUES (:id, 'Other', 'User', 'Other User INV002', '1995-01-01')
        """), {"id": pid})
        email = f"other_{str(uuid4())[:8]}@example.com"
        await async_db.execute(text("""
            INSERT INTO users (id, email, person_id, password_hash, status)
            VALUES (:id, :email, :person_id, 'hash', 'ativo')
        """), {"id": other_user_id, "email": email, "person_id": pid})

        # Insere ACL entry diretamente para restricted (sem chamar grant_access)
        acl_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercise_acl (id, exercise_id, user_id, granted_by_user_id)
            VALUES (:id, :exercise_id, :user_id, :granted_by)
        """), {
            "id": acl_id,
            "exercise_id": restricted_id,
            "user_id": other_user_id,
            "granted_by": str(user.id)
        })

        await async_db.flush()
        return {
            "org_wide_id": UUID(org_wide_id),
            "restricted_id": UUID(restricted_id),
            "creator_user_id": user.id,
            "other_user_id": UUID(other_user_id),
        }

    @pytest.mark.asyncio
    async def test_org_wide_exercise_raises_acl_not_applicable(
        self, async_db: AsyncSession, inv002_setup
    ):
        """grant_access() em exercise org_wide deve levantar AclNotApplicableError."""
        service = ExerciseAclService(async_db)

        with pytest.raises(AclNotApplicableError):
            await service.grant_access(
                exercise_id=inv002_setup["org_wide_id"],
                target_user_id=inv002_setup["other_user_id"],
                acting_user_id=inv002_setup["creator_user_id"]
            )

    @pytest.mark.asyncio
    async def test_restricted_exercise_acl_entry_grants_access(
        self, async_db: AsyncSession, inv002_setup
    ):
        """has_access() para restricted com ACL entry deve retornar True."""
        service = ExerciseAclService(async_db)

        result = await service.has_access(
            exercise_id=inv002_setup["restricted_id"],
            user_id=inv002_setup["other_user_id"]
        )
        assert result is True
