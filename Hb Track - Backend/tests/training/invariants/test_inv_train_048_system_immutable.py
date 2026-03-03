"""
INV-TRAIN-048: Exercícios SYSTEM são imutáveis por usuários não-plataforma.
Classe B — Service Guard (ExerciseService)
Evidência: exercise_service.py — update_exercise() e soft_delete_exercise()
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.exercise_service import ExerciseService
from app.core.exceptions import ExerciseImmutableError


class TestInvTrain048SystemImmutable:
    """
    INV-TRAIN-048: ExerciseService.update_exercise() e soft_delete_exercise()
    levantam ExerciseImmutableError quando exercise.scope == 'SYSTEM'.
    """

    @pytest_asyncio.fixture
    async def inv048_setup(self, async_db: AsyncSession, organization, user):
        """Cria um SYSTEM exercise e um ORG exercise para comparação."""
        system_id = str(uuid4())
        org_id = str(uuid4())

        # SYSTEM exercise: scope='SYSTEM', organization_id=NULL
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'System Exercise INV048', 'SYSTEM', NULL, :user_id, 'org_wide')
        """), {"id": system_id, "user_id": str(user.id)})

        # ORG exercise: scope='ORG'
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Org Exercise INV048', 'ORG', :org_id, :user_id, 'restricted')
        """), {"id": org_id, "org_id": str(organization.id), "user_id": str(user.id)})

        await async_db.flush()
        return {"system_id": system_id, "org_id": org_id, "user_id": user.id, "org_uuid": organization.id}

    @pytest.mark.asyncio
    async def test_update_system_exercise_raises_immutable(
        self, async_db: AsyncSession, inv048_setup
    ):
        """PATCH em exercise SYSTEM deve levantar ExerciseImmutableError."""
        service = ExerciseService(async_db)
        from uuid import UUID

        with pytest.raises(ExerciseImmutableError):
            await service.update_exercise(
                exercise_id=UUID(inv048_setup["system_id"]),
                data={"name": "Tentativa de mudança"},
                organization_id=None
            )

    @pytest.mark.asyncio
    async def test_delete_system_exercise_raises_immutable(
        self, async_db: AsyncSession, inv048_setup
    ):
        """DELETE em exercise SYSTEM deve levantar ExerciseImmutableError."""
        service = ExerciseService(async_db)
        from uuid import UUID

        with pytest.raises(ExerciseImmutableError):
            await service.soft_delete_exercise(
                exercise_id=UUID(inv048_setup["system_id"]),
                reason="Tentativa de deletar SYSTEM",
                user_id=inv048_setup["user_id"]
            )

    @pytest.mark.asyncio
    async def test_update_org_exercise_allowed(
        self, async_db: AsyncSession, inv048_setup
    ):
        """PATCH em exercise ORG deve ser permitido (sem ExerciseImmutableError)."""
        service = ExerciseService(async_db)
        from uuid import UUID

        # Should NOT raise ExerciseImmutableError
        result = await service.update_exercise(
            exercise_id=UUID(inv048_setup["org_id"]),
            data={"name": "ORG Exercise Atualizado INV048"},
            organization_id=inv048_setup["org_uuid"]
        )
        assert result.name == "ORG Exercise Atualizado INV048"
