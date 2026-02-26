"""
INV-TRAIN-049: exercises scope/organization_id consistency
- SYSTEM scope requires organization_id IS NULL
- ORG scope requires organization_id IS NOT NULL
Classe A - Runtime Integration com async_db
Evidencia: db/alembic/versions/0065_exercise_bank_schema_foundation.py
Constraint: ck_exercises_org_scope
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class TestInvTrain049ExerciseOrgScope:
    """
    Testa INV-TRAIN-049: scope/org consistency
    Evidencia: migration 0065, ck_exercises_org_scope constraint
    """
    
    @pytest.mark.asyncio
    async def test_valid_system_null_org(self, async_db: AsyncSession, user):
        """SYSTEM scope com organization_id NULL deve ser aceito."""
        exercise_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'SYSTEM Exercise', 'Valid SYSTEM', 'SYSTEM', NULL, :user_id, 'org_wide')
        """), {"id": exercise_id, "user_id": str(user.id)})
        await async_db.flush()
        
        result = await async_db.execute(text(
            "SELECT scope, organization_id FROM exercises WHERE id = :id"
        ), {"id": exercise_id})
        row = result.fetchone()
        assert row is not None
        assert row[0] == 'SYSTEM'
        assert row[1] is None
    
    @pytest.mark.asyncio
    async def test_valid_org_with_org_id(self, async_db: AsyncSession, organization, user):
        """ORG scope com organization_id NOT NULL deve ser aceito."""
        exercise_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'ORG Exercise', 'Valid ORG', 'ORG', :org_id, :user_id, 'restricted')
        """), {
            "id": exercise_id,
            "org_id": str(organization.id),
            "user_id": str(user.id)
        })
        await async_db.flush()
        
        result = await async_db.execute(text(
            "SELECT scope, organization_id FROM exercises WHERE id = :id"
        ), {"id": exercise_id})
        row = result.fetchone()
        assert row is not None
        assert row[0] == 'ORG'
        assert row[1] is not None
    
    @pytest.mark.asyncio
    async def test_invalid_system_with_org_id(self, async_db: AsyncSession, organization, user):
        """SYSTEM scope com organization_id NOT NULL deve ser rejeitado."""
        exercise_id = str(uuid4())
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(text("""
                INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
                VALUES (:id, 'Bad SYSTEM', 'SYSTEM with org', 'SYSTEM', :org_id, :user_id, 'org_wide')
            """), {
                "id": exercise_id,
                "org_id": str(organization.id),
                "user_id": str(user.id)
            })
            await async_db.flush()
        
        error_str = str(exc_info.value).lower()
        assert 'ck_exercises_org_scope' in error_str or 'exercises' in error_str
    
    @pytest.mark.asyncio
    async def test_invalid_org_null_org_id(self, async_db: AsyncSession, user):
        """ORG scope com organization_id NULL deve ser rejeitado."""
        exercise_id = str(uuid4())
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(text("""
                INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
                VALUES (:id, 'Bad ORG', 'ORG without org', 'ORG', NULL, :user_id, 'restricted')
            """), {
                "id": exercise_id,
                "user_id": str(user.id)
            })
            await async_db.flush()
        
        error_str = str(exc_info.value).lower()
        assert 'ck_exercises_org_scope' in error_str or 'exercises' in error_str
