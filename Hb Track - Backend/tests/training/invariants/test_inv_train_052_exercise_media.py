"""
INV-TRAIN-052: exercise_media unique on (exercise_id, order_index)
Classe A - Runtime Integration com async_db
Evidencia: db/alembic/versions/0065_exercise_bank_schema_foundation.py
Constraint: uq_exercise_media_exercise_order
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class TestInvTrain052ExerciseMedia:
    """
    Testa INV-TRAIN-052: exercise_media order uniqueness
    Evidencia: migration 0065, uq_exercise_media_exercise_order constraint
    """
    
    @pytest_asyncio.fixture
    async def exercise(self, async_db: AsyncSession, organization, user):
        """Cria um exercise para teste de media."""
        exercise_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Media Test Exercise', 'For media tests', 'ORG', :org_id, :user_id, 'org_wide')
        """), {
            "id": exercise_id,
            "org_id": str(organization.id),
            "user_id": str(user.id)
        })
        await async_db.flush()
        return type('Exercise', (), {'id': uuid4.__class__(exercise_id)})()
    
    @pytest.mark.asyncio
    async def test_valid_media_insert(self, async_db: AsyncSession, exercise, user):
        """Media com order_index unico deve ser aceito."""
        media_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercise_media (id, exercise_id, media_type, url, order_index, created_by_user_id)
            VALUES (:id, :exercise_id, 'video', 'https://example.com/video.mp4', 1, :user_id)
        """), {
            "id": media_id,
            "exercise_id": str(exercise.id),
            "user_id": str(user.id)
        })
        await async_db.flush()
        
        result = await async_db.execute(text(
            "SELECT media_type, order_index FROM exercise_media WHERE id = :id"
        ), {"id": media_id})
        row = result.fetchone()
        assert row is not None
        assert row[0] == 'video'
        assert row[1] == 1
    
    @pytest.mark.asyncio
    async def test_valid_multiple_media_different_order(self, async_db: AsyncSession, exercise, user):
        """Multiplos media com order_index diferentes devem ser aceitos."""
        media1_id = str(uuid4())
        media2_id = str(uuid4())
        
        await async_db.execute(text("""
            INSERT INTO exercise_media (id, exercise_id, media_type, url, order_index, created_by_user_id)
            VALUES (:id, :exercise_id, 'video', 'https://example.com/video1.mp4', 1, :user_id)
        """), {
            "id": media1_id,
            "exercise_id": str(exercise.id),
            "user_id": str(user.id)
        })
        
        await async_db.execute(text("""
            INSERT INTO exercise_media (id, exercise_id, media_type, url, order_index, created_by_user_id)
            VALUES (:id, :exercise_id, 'image', 'https://example.com/image.png', 2, :user_id)
        """), {
            "id": media2_id,
            "exercise_id": str(exercise.id),
            "user_id": str(user.id)
        })
        await async_db.flush()
        
        result = await async_db.execute(text("""
            SELECT COUNT(*) FROM exercise_media WHERE exercise_id = :exercise_id
        """), {"exercise_id": str(exercise.id)})
        count = result.scalar()
        assert count == 2
    
    @pytest.mark.asyncio
    async def test_duplicate_order_index_rejected(self, async_db: AsyncSession, exercise, user):
        """Dois media com mesmo order_index para o mesmo exercise deve ser rejeitado."""
        media1_id = str(uuid4())
        media2_id = str(uuid4())
        
        # Primeiro insert
        await async_db.execute(text("""
            INSERT INTO exercise_media (id, exercise_id, media_type, url, order_index, created_by_user_id)
            VALUES (:id, :exercise_id, 'video', 'https://example.com/video1.mp4', 1, :user_id)
        """), {
            "id": media1_id,
            "exercise_id": str(exercise.id),
            "user_id": str(user.id)
        })
        await async_db.flush()
        
        # Segundo insert com mesmo order_index deve falhar
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(text("""
                INSERT INTO exercise_media (id, exercise_id, media_type, url, order_index, created_by_user_id)
                VALUES (:id, :exercise_id, 'image', 'https://example.com/image.png', 1, :user_id)
            """), {
                "id": media2_id,
                "exercise_id": str(exercise.id),
                "user_id": str(user.id)
            })
            await async_db.flush()
        
        error_str = str(exc_info.value).lower()
        assert 'uq_exercise_media_exercise_order' in error_str or 'unique' in error_str or 'duplicate' in error_str
    
    @pytest.mark.asyncio
    async def test_invalid_media_type_rejected(self, async_db: AsyncSession, exercise, user):
        """Media type invalido deve ser rejeitado."""
        media_id = str(uuid4())
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(text("""
                INSERT INTO exercise_media (id, exercise_id, media_type, url, order_index, created_by_user_id)
                VALUES (:id, :exercise_id, 'audio', 'https://example.com/audio.mp3', 1, :user_id)
            """), {
                "id": media_id,
                "exercise_id": str(exercise.id),
                "user_id": str(user.id)
            })
            await async_db.flush()
        
        error_str = str(exc_info.value).lower()
        assert 'ck_exercise_media_type' in error_str or 'media_type' in error_str
