"""
INV-TRAIN-061: Para adaptar exercício SYSTEM, deve-se criar cópia ORG — não editar o original.
Classe B — Service Guard (ExerciseService)
Evidência: exercise_service.py — copy_system_exercise_to_org() + update_exercise()

Regra: Exercícios SYSTEM são imutáveis. O fluxo correto é:
- copy_system_exercise_to_org() → cria NOVO exercício scope='ORG' baseado no SYSTEM
- O original SYSTEM permanece inalterado
- Tentativa de update_exercise() em SYSTEM levanta ExerciseImmutableError (INV-048, reforça INV-061)
"""
import pytest
import pytest_asyncio
from uuid import uuid4, UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.exercise_service import ExerciseService
from app.core.exceptions import ExerciseImmutableError


class TestInvTrain061SystemExerciseCopyNotEdit:
    """
    INV-TRAIN-061: copy_system_exercise_to_org() cria cópia ORG, não edita o SYSTEM.
    """

    @pytest_asyncio.fixture
    async def inv061_setup(self, async_db: AsyncSession, organization, user):
        """Cria um SYSTEM exercise para usar nos testes."""
        system_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'SYSTEM Exercicio INV061', 'Exercicio SYSTEM original', 'SYSTEM', NULL, :user_id, 'org_wide')
        """), {"id": system_id, "user_id": str(user.id)})
        await async_db.flush()
        return {
            "system_id": UUID(system_id),
            "original_name": "SYSTEM Exercicio INV061",
        }

    @pytest.mark.asyncio
    async def test_copy_system_creates_new_org_exercise(
        self, async_db: AsyncSession, organization, user, inv061_setup
    ):
        """Happy: copy_system_exercise_to_org() cria exercício ORG, original SYSTEM imutável."""
        service = ExerciseService(async_db)

        clone = await service.copy_system_exercise_to_org(
            exercise_id=inv061_setup["system_id"],
            organization_id=organization.id,
            user_id=user.id,
        )

        # Clone deve ser ORG
        assert clone.scope == "ORG", f"Clone deve ser scope='ORG', obtido: {clone.scope}"
        assert clone.organization_id == organization.id
        assert clone.id != inv061_setup["system_id"], "Clone deve ter UUID diferente do original"

        # Original SYSTEM permanece inalterado
        result = await async_db.execute(text(
            "SELECT scope, name FROM exercises WHERE id = :id"
        ), {"id": str(inv061_setup["system_id"])})
        row = result.fetchone()
        assert row is not None
        assert row[0] == "SYSTEM", "Original deve continuar com scope='SYSTEM'"
        assert row[1] == inv061_setup["original_name"], "Nome do SYSTEM original não deve ter mudado"

    @pytest.mark.asyncio
    async def test_copy_default_visibility_is_restricted(
        self, async_db: AsyncSession, organization, user, inv061_setup
    ):
        """Cópia ORG criada por copy_system_exercise_to_org() deve defaultar para 'restricted'."""
        service = ExerciseService(async_db)
        clone = await service.copy_system_exercise_to_org(
            exercise_id=inv061_setup["system_id"],
            organization_id=organization.id,
            user_id=user.id,
        )
        assert clone.visibility_mode == "restricted", (
            f"Cópia ORG criada de SYSTEM deve ser 'restricted' por default (INV-060), "
            f"obtido: {clone.visibility_mode}"
        )

    @pytest.mark.asyncio
    async def test_direct_update_system_raises_immutable_error(
        self, async_db: AsyncSession, inv061_setup
    ):
        """Violation: tentar editar exercício SYSTEM diretamente lança ExerciseImmutableError."""
        service = ExerciseService(async_db)

        with pytest.raises(ExerciseImmutableError):
            await service.update_exercise(
                exercise_id=inv061_setup["system_id"],
                data={"name": "Tentativa de edição direta"},
                organization_id=None,
            )
