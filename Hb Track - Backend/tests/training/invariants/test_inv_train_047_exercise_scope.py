"""
INV-TRAIN-047: exercises.scope must be 'SYSTEM' or 'ORG'
Classe A - Runtime Integration com async_db
Evidencia: db/alembic/versions/0065_exercise_bank_schema_foundation.py
Constraint: ck_exercises_scope
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class TestInvTrain047ExerciseScope:
    """
    Testa INV-TRAIN-047: scope IN ('SYSTEM', 'ORG')
    Evidencia: migration 0065, ck_exercises_scope constraint
    """
    
    @pytest_asyncio.fixture
    async def exercise_setup(self, async_db: AsyncSession, organization, user):
        """Setup comum para criar exercises com org e user."""
        return {
            "organization_id": str(organization.id),
            "created_by_user_id": str(user.id),
        }
    
    @pytest.mark.asyncio
    async def test_valid_scope_system(self, async_db: AsyncSession, user):
        """SYSTEM scope com organization_id NULL deve ser aceito."""
        exercise_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Test SYSTEM', 'System exercise', 'SYSTEM', NULL, :user_id, 'org_wide')
        """), {"id": exercise_id, "user_id": str(user.id)})
        await async_db.flush()
        
        result = await async_db.execute(text(
            "SELECT scope FROM exercises WHERE id = :id"
        ), {"id": exercise_id})
        row = result.fetchone()
        assert row is not None
        assert row[0] == 'SYSTEM'
    
    @pytest.mark.asyncio
    async def test_valid_scope_org(self, async_db: AsyncSession, organization, user):
        """ORG scope com organization_id NOT NULL deve ser aceito."""
        exercise_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Test ORG', 'Org exercise', 'ORG', :org_id, :user_id, 'restricted')
        """), {
            "id": exercise_id,
            "org_id": str(organization.id),
            "user_id": str(user.id)
        })
        await async_db.flush()
        
        result = await async_db.execute(text(
            "SELECT scope FROM exercises WHERE id = :id"
        ), {"id": exercise_id})
        row = result.fetchone()
        assert row is not None
        assert row[0] == 'ORG'
    
    @pytest.mark.asyncio
    async def test_invalid_scope_rejected(self, async_db: AsyncSession, organization, user):
        """Scope invalido deve ser rejeitado pelo ck_exercises_scope."""
        exercise_id = str(uuid4())
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(text("""
                INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
                VALUES (:id, 'Invalid', 'Bad scope', 'INVALID', :org_id, :user_id, 'org_wide')
            """), {
                "id": exercise_id,
                "org_id": str(organization.id),
                "user_id": str(user.id)
            })
            await async_db.flush()
        
        # Verificar que o erro menciona a constraint
        error_str = str(exc_info.value).lower()
        assert 'ck_exercises_scope' in error_str or 'scope' in error_str
    
    @pytest.mark.asyncio
    async def test_invalid_scope_global_rejected(self, async_db: AsyncSession, user):
        """Scope 'GLOBAL' (nao permitido) deve ser rejeitado."""
        exercise_id = str(uuid4())
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(text("""
                INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
                VALUES (:id, 'Global', 'Not allowed', 'GLOBAL', NULL, :user_id, 'org_wide')
            """), {
                "id": exercise_id,
                "user_id": str(user.id)
            })
            await async_db.flush()
        
        error_str = str(exc_info.value).lower()
        assert 'ck_exercises_scope' in error_str or 'scope' in error_str
