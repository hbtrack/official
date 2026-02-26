"""
INV-TRAIN-EXB-ACL-001: exercises.visibility_mode must be 'org_wide' or 'restricted'
Classe A - Runtime Integration com async_db
Evidencia: db/alembic/versions/0065_exercise_bank_schema_foundation.py
Constraint: ck_exercises_visibility_mode
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class TestInvTrainExbAcl001VisibilityMode:
    """
    Testa INV-TRAIN-EXB-ACL-001: visibility_mode IN ('org_wide', 'restricted')
    Evidencia: migration 0065, ck_exercises_visibility_mode constraint
    """
    
    @pytest.mark.asyncio
    async def test_valid_visibility_org_wide(self, async_db: AsyncSession, organization, user):
        """visibility_mode 'org_wide' deve ser aceito."""
        exercise_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Org Wide Exercise', 'Visible to all in org', 'ORG', :org_id, :user_id, 'org_wide')
        """), {
            "id": exercise_id,
            "org_id": str(organization.id),
            "user_id": str(user.id)
        })
        await async_db.flush()
        
        result = await async_db.execute(text(
            "SELECT visibility_mode FROM exercises WHERE id = :id"
        ), {"id": exercise_id})
        row = result.fetchone()
        assert row is not None
        assert row[0] == 'org_wide'
    
    @pytest.mark.asyncio
    async def test_valid_visibility_restricted(self, async_db: AsyncSession, organization, user):
        """visibility_mode 'restricted' deve ser aceito."""
        exercise_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Restricted Exercise', 'Restricted access', 'ORG', :org_id, :user_id, 'restricted')
        """), {
            "id": exercise_id,
            "org_id": str(organization.id),
            "user_id": str(user.id)
        })
        await async_db.flush()
        
        result = await async_db.execute(text(
            "SELECT visibility_mode FROM exercises WHERE id = :id"
        ), {"id": exercise_id})
        row = result.fetchone()
        assert row is not None
        assert row[0] == 'restricted'
    
    @pytest.mark.asyncio
    async def test_invalid_visibility_public(self, async_db: AsyncSession, organization, user):
        """visibility_mode 'public' (nao permitido) deve ser rejeitado."""
        exercise_id = str(uuid4())
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(text("""
                INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
                VALUES (:id, 'Public Exercise', 'Invalid', 'ORG', :org_id, :user_id, 'public')
            """), {
                "id": exercise_id,
                "org_id": str(organization.id),
                "user_id": str(user.id)
            })
            await async_db.flush()
        
        error_str = str(exc_info.value).lower()
        assert 'ck_exercises_visibility_mode' in error_str or 'visibility' in error_str
    
    @pytest.mark.asyncio
    async def test_invalid_visibility_empty(self, async_db: AsyncSession, organization, user):
        """visibility_mode vazio deve ser rejeitado."""
        exercise_id = str(uuid4())
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(text("""
                INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
                VALUES (:id, 'Empty Visibility', 'Invalid', 'ORG', :org_id, :user_id, '')
            """), {
                "id": exercise_id,
                "org_id": str(organization.id),
                "user_id": str(user.id)
            })
            await async_db.flush()
        
        error_str = str(exc_info.value).lower()
        assert 'ck_exercises_visibility_mode' in error_str or 'visibility' in error_str or 'check' in error_str
