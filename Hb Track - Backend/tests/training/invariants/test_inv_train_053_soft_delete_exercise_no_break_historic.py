"""
INV-TRAIN-053: Soft delete de exercício NÃO deve quebrar sessões históricas.
Classe A+B — DB Integration + Service Guard
Evidência: exercise_service.py — soft_delete_exercise() (sets deleted_at, não apaga FK)

Regra: Ao aplicar soft delete em um exercício, as referências em session_exercises
(histórico de treinos) permanecem íntegras — apenas deleted_at é preenchido no
registro do exercício. Nenhuma exclusão em cascata.
"""
import pytest
import pytest_asyncio
from uuid import uuid4, UUID
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.exercise_service import ExerciseService
from app.core.exceptions import ExerciseImmutableError


class TestInvTrain053SoftDeleteNoBreakHistoric:
    """
    INV-TRAIN-053: soft_delete_exercise() NUNCA remove fisicamente.
    session_exercise rows históricas continuam referenciando o exercício via FK.
    """

    @pytest_asyncio.fixture
    async def inv053_setup(self, async_db: AsyncSession, organization, user, training_session, category):
        """
        Cria exercício ORG, session_exercise referenciando-o.
        Retorna IDs para uso nos testes.
        """
        exercise_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Exercicio INV053', 'ORG', :org_id, :user_id, 'org_wide')
        """), {
            "id": exercise_id,
            "org_id": str(organization.id),
            "user_id": str(user.id),
        })
        await async_db.flush()

        # Inserir session_exercise referenciando o exercício
        se_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO training_session_exercises (id, session_id, exercise_id, order_index)
            VALUES (:id, :session_id, :exercise_id, 0)
        """), {
            "id": se_id,
            "session_id": str(training_session.id),
            "exercise_id": exercise_id,
        })
        await async_db.flush()

        return {
            "exercise_id": UUID(exercise_id),
            "session_exercise_id": se_id,
            "user_id": user.id,
        }

    @pytest.mark.asyncio
    async def test_soft_delete_sets_deleted_at_not_physical_delete(
        self, async_db: AsyncSession, inv053_setup
    ):
        """Happy: soft_delete seta deleted_at, exercício ainda exists no DB."""
        service = ExerciseService(async_db)
        exercise = await service.soft_delete_exercise(
            exercise_id=inv053_setup["exercise_id"],
            reason="Não mais necessário",
            user_id=inv053_setup["user_id"],
        )

        assert exercise.deleted_at is not None, "deleted_at deve ser preenchido após soft delete"
        assert exercise.deleted_reason is not None

        # Exercício ainda existe na tabela (não foi DELETE)
        result = await async_db.execute(text(
            "SELECT id, deleted_at FROM exercises WHERE id = :id"
        ), {"id": str(inv053_setup["exercise_id"])})
        row = result.fetchone()
        assert row is not None, "Exercício deve continuar existindo na tabela após soft delete"
        assert row[1] is not None, "deleted_at deve estar preenchido"

    @pytest.mark.asyncio
    async def test_session_exercise_intact_after_soft_delete(
        self, async_db: AsyncSession, inv053_setup
    ):
        """Invariante principal: session_exercise permanece intacto após soft delete do exercício referenciado."""
        service = ExerciseService(async_db)
        await service.soft_delete_exercise(
            exercise_id=inv053_setup["exercise_id"],
            reason="Soft delete - teste INV053",
            user_id=inv053_setup["user_id"],
        )

        # session_exercise ainda referencia o exercício (deleted_at no exercício não cascadeou)
        result = await async_db.execute(text("""
            SELECT se.id, e.deleted_at
            FROM training_session_exercises se
            JOIN exercises e ON se.exercise_id = e.id
            WHERE se.id = :se_id
        """), {"se_id": inv053_setup["session_exercise_id"]})
        row = result.fetchone()
        assert row is not None, (
            "session_exercise deve continuar existindo após soft delete do exercício — "
            "INV-053 garantia: histórico não é quebrado"
        )
        # O join ainda funciona — o exercício existe na tabela (apenas marcado como deleted)
        assert row[1] is not None, "exercício deve ter deleted_at preenchido (soft delete)"
