"""
INV-TRAIN-050: exercise_favorites unique on (user_id, exercise_id)
Classe A - Runtime Integration com async_db
Evidencia: db/alembic/versions/0065 - PK (user_id, exercise_id) already satisfies uniqueness
Constraint: exercise_favorites_pkey (PK)
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class TestInvTrain050ExerciseFavoritesUnique:
    """
    Testa INV-TRAIN-050: exercise_favorites unique
    Evidencia: PK (user_id, exercise_id) garante unicidade
    """
    
    @pytest_asyncio.fixture
    async def exercise(self, async_db: AsyncSession, organization, user):
        """Cria um exercise para teste."""
        exercise_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Test Exercise', 'For favorites test', 'ORG', :org_id, :user_id, 'org_wide')
        """), {
            "id": exercise_id,
            "org_id": str(organization.id),
            "user_id": str(user.id)
        })
        await async_db.flush()
        return type('Exercise', (), {'id': exercise_id})()
    
    @pytest.mark.asyncio
    async def test_valid_favorite_insert(self, async_db: AsyncSession, exercise, user):
        """Um usuario pode favoritar um exercise."""
        await async_db.execute(text("""
            INSERT INTO exercise_favorites (user_id, exercise_id)
            VALUES (:user_id, :exercise_id)
        """), {
            "user_id": str(user.id),
            "exercise_id": str(exercise.id)
        })
        await async_db.flush()
        
        result = await async_db.execute(text("""
            SELECT user_id, exercise_id FROM exercise_favorites
            WHERE user_id = :user_id AND exercise_id = :exercise_id
        """), {
            "user_id": str(user.id),
            "exercise_id": str(exercise.id)
        })
        row = result.fetchone()
        assert row is not None
    
    @pytest.mark.asyncio
    async def test_duplicate_favorite_rejected(self, async_db: AsyncSession, exercise, user):
        """Usuario nao pode favoritar o mesmo exercise duas vezes."""
        # Primeiro insert
        await async_db.execute(text("""
            INSERT INTO exercise_favorites (user_id, exercise_id)
            VALUES (:user_id, :exercise_id)
        """), {
            "user_id": str(user.id),
            "exercise_id": str(exercise.id)
        })
        await async_db.flush()
        
        # Segundo insert deve falhar
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(text("""
                INSERT INTO exercise_favorites (user_id, exercise_id)
                VALUES (:user_id, :exercise_id)
            """), {
                "user_id": str(user.id),
                "exercise_id": str(exercise.id)
            })
            await async_db.flush()
        
        error_str = str(exc_info.value).lower()
        # Pode ser PK violation ou unique constraint - ambos indicam duplicidade
        assert 'duplicate' in error_str or 'unique' in error_str or 'pkey' in error_str
    
    @pytest.mark.asyncio
    async def test_different_users_can_favorite_same_exercise(self, async_db: AsyncSession, exercise, user, person_id):
        """Usuarios diferentes podem favoritar o mesmo exercise."""
        # Criar segundo user
        user2_id = uuid4()
        person2_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO persons (id, first_name, last_name, full_name, birth_date)
            VALUES (:id, 'User', 'Two', 'User Two', '1990-01-01')
        """), {"id": person2_id})
        await async_db.execute(text("""
            INSERT INTO users (id, email, person_id, password_hash, status)
            VALUES (:id, :email, :person_id, 'hash', 'ativo')
        """), {
            "id": str(user2_id),
            "email": f"user2_{str(user2_id)[:8]}@example.com",
            "person_id": person2_id
        })
        await async_db.flush()
        
        # User 1 favorita
        await async_db.execute(text("""
            INSERT INTO exercise_favorites (user_id, exercise_id)
            VALUES (:user_id, :exercise_id)
        """), {
            "user_id": str(user.id),
            "exercise_id": str(exercise.id)
        })
        
        # User 2 favorita o mesmo - deve funcionar
        await async_db.execute(text("""
            INSERT INTO exercise_favorites (user_id, exercise_id)
            VALUES (:user_id, :exercise_id)
        """), {
            "user_id": str(user2_id),
            "exercise_id": str(exercise.id)
        })
        await async_db.flush()
        
        result = await async_db.execute(text("""
            SELECT COUNT(*) FROM exercise_favorites WHERE exercise_id = :exercise_id
        """), {"exercise_id": str(exercise.id)})
        count = result.scalar()
        assert count == 2
