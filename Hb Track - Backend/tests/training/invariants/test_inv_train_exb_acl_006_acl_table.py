"""
INV-TRAIN-EXB-ACL-006: exercise_acl unique on (exercise_id, user_id)
Classe A - Runtime Integration com async_db
Evidencia: db/alembic/versions/0065_exercise_bank_schema_foundation.py
Constraint: uq_exercise_acl_exercise_user
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class TestInvTrainExbAcl006AclTable:
    """
    Testa INV-TRAIN-EXB-ACL-006: exercise_acl unique
    Evidencia: migration 0065, uq_exercise_acl_exercise_user constraint
    """
    
    @pytest_asyncio.fixture
    async def exercise(self, async_db: AsyncSession, organization, user):
        """Cria um exercise restrito para teste de ACL."""
        exercise_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Restricted Exercise', 'For ACL tests', 'ORG', :org_id, :user_id, 'restricted')
        """), {
            "id": exercise_id,
            "org_id": str(organization.id),
            "user_id": str(user.id)
        })
        await async_db.flush()
        return type('Exercise', (), {'id': uuid4.__class__(exercise_id)})()
    
    @pytest_asyncio.fixture
    async def grantee_user(self, async_db: AsyncSession):
        """Cria um segundo user para receber ACL."""
        person_id = str(uuid4())
        user_id = uuid4()
        await async_db.execute(text("""
            INSERT INTO persons (id, first_name, last_name, full_name, birth_date)
            VALUES (:id, 'Grantee', 'User', 'Grantee User', '1990-01-01')
        """), {"id": person_id})
        await async_db.execute(text("""
            INSERT INTO users (id, email, person_id, password_hash, status)
            VALUES (:id, :email, :person_id, 'hash', 'ativo')
        """), {
            "id": str(user_id),
            "email": f"grantee_{str(user_id)[:8]}@example.com",
            "person_id": person_id
        })
        await async_db.flush()
        return type('User', (), {'id': user_id})()
    
    @pytest.mark.asyncio
    async def test_valid_acl_grant(self, async_db: AsyncSession, exercise, user, grantee_user):
        """ACL grant valido deve ser aceito."""
        acl_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercise_acl (id, exercise_id, user_id, granted_by_user_id)
            VALUES (:id, :exercise_id, :user_id, :granted_by)
        """), {
            "id": acl_id,
            "exercise_id": str(exercise.id),
            "user_id": str(grantee_user.id),
            "granted_by": str(user.id)
        })
        await async_db.flush()
        
        result = await async_db.execute(text(
            "SELECT exercise_id, user_id FROM exercise_acl WHERE id = :id"
        ), {"id": acl_id})
        row = result.fetchone()
        assert row is not None
    
    @pytest.mark.asyncio
    async def test_duplicate_acl_grant_rejected(self, async_db: AsyncSession, exercise, user, grantee_user):
        """ACL duplicado para mesmo (exercise, user) deve ser rejeitado."""
        acl1_id = str(uuid4())
        acl2_id = str(uuid4())
        
        # Primeiro grant
        await async_db.execute(text("""
            INSERT INTO exercise_acl (id, exercise_id, user_id, granted_by_user_id)
            VALUES (:id, :exercise_id, :user_id, :granted_by)
        """), {
            "id": acl1_id,
            "exercise_id": str(exercise.id),
            "user_id": str(grantee_user.id),
            "granted_by": str(user.id)
        })
        await async_db.flush()
        
        # Segundo grant para mesmo (exercise, user) deve falhar
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(text("""
                INSERT INTO exercise_acl (id, exercise_id, user_id, granted_by_user_id)
                VALUES (:id, :exercise_id, :user_id, :granted_by)
            """), {
                "id": acl2_id,
                "exercise_id": str(exercise.id),
                "user_id": str(grantee_user.id),
                "granted_by": str(user.id)
            })
            await async_db.flush()
        
        error_str = str(exc_info.value).lower()
        assert 'uq_exercise_acl_exercise_user' in error_str or 'unique' in error_str or 'duplicate' in error_str
    
    @pytest.mark.asyncio
    async def test_same_user_different_exercises_allowed(self, async_db: AsyncSession, organization, user, grantee_user):
        """Mesmo user pode ter ACL em diferentes exercises."""
        # Criar segundo exercise
        exercise1_id = str(uuid4())
        exercise2_id = str(uuid4())
        
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Exercise 1', 'First', 'ORG', :org_id, :user_id, 'restricted')
        """), {
            "id": exercise1_id,
            "org_id": str(organization.id),
            "user_id": str(user.id)
        })
        
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Exercise 2', 'Second', 'ORG', :org_id, :user_id, 'restricted')
        """), {
            "id": exercise2_id,
            "org_id": str(organization.id),
            "user_id": str(user.id)
        })
        await async_db.flush()
        
        # Grant ACL para ambos exercises ao mesmo user
        await async_db.execute(text("""
            INSERT INTO exercise_acl (id, exercise_id, user_id, granted_by_user_id)
            VALUES (:id, :exercise_id, :user_id, :granted_by)
        """), {
            "id": str(uuid4()),
            "exercise_id": exercise1_id,
            "user_id": str(grantee_user.id),
            "granted_by": str(user.id)
        })
        
        await async_db.execute(text("""
            INSERT INTO exercise_acl (id, exercise_id, user_id, granted_by_user_id)
            VALUES (:id, :exercise_id, :user_id, :granted_by)
        """), {
            "id": str(uuid4()),
            "exercise_id": exercise2_id,
            "user_id": str(grantee_user.id),
            "granted_by": str(user.id)
        })
        await async_db.flush()
        
        result = await async_db.execute(text("""
            SELECT COUNT(*) FROM exercise_acl WHERE user_id = :user_id
        """), {"user_id": str(grantee_user.id)})
        count = result.scalar()
        assert count == 2
