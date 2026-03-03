"""
INV-TRAIN-051: Filtro de visibilidade do catálogo de exercícios.
Classe C2 — Service+DB (ExerciseService.list_exercises())
Evidência: exercise_service.py — list_exercises()

Regras:
- SYSTEM exercises: sempre visíveis (independente de org)
- ORG exercises: visíveis apenas para a mesma organização
- Deleted exercises (deleted_at IS NOT NULL): excluídos do catálogo
"""
import pytest
import pytest_asyncio
from uuid import uuid4, UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.exercise_service import ExerciseService


class TestInvTrain051CatalogVisibility:
    """
    INV-TRAIN-051: ExerciseService.list_exercises() filtra exercícios
    por scope/org e exclui deletados.
    """

    @pytest_asyncio.fixture
    async def inv051_setup(self, async_db: AsyncSession, organization, user):
        """Cria SYSTEM, ORG-A, ORG-B e deleted exercises para comparação."""
        org_a_id = str(organization.id)
        org_b_str = str(uuid4())

        # Cria org B inline
        await async_db.execute(text("""
            INSERT INTO organizations (id, name)
            VALUES (:id, 'Org B INV051')
        """), {"id": org_b_str})

        system_id = str(uuid4())
        org_a_ex_id = str(uuid4())
        org_b_ex_id = str(uuid4())
        deleted_id = str(uuid4())

        # SYSTEM exercise: scope='SYSTEM', organization_id=NULL
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'System Exercise INV051', 'SYSTEM', NULL, :user_id, 'org_wide')
        """), {"id": system_id, "user_id": str(user.id)})

        # ORG A exercise
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Org A Exercise INV051', 'ORG', :org_id, :user_id, 'org_wide')
        """), {"id": org_a_ex_id, "org_id": org_a_id, "user_id": str(user.id)})

        # ORG B exercise (deve ser invisível para org A)
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Org B Exercise INV051', 'ORG', :org_id, :user_id, 'org_wide')
        """), {"id": org_b_ex_id, "org_id": org_b_str, "user_id": str(user.id)})

        # Deleted exercise da org A (deleted_at preenchido)
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, scope, organization_id, created_by_user_id, visibility_mode, deleted_at, deleted_reason)
            VALUES (:id, 'Deleted Exercise INV051', 'ORG', :org_id, :user_id, 'org_wide', now(), 'Teste INV051')
        """), {"id": deleted_id, "org_id": org_a_id, "user_id": str(user.id)})

        await async_db.flush()
        return {
            "org_a_uuid": organization.id,
            "system_id": system_id,
            "org_a_ex_id": org_a_ex_id,
            "org_b_ex_id": org_b_ex_id,
            "deleted_id": deleted_id,
        }

    @pytest.mark.asyncio
    async def test_system_exercise_visible_for_org(
        self, async_db: AsyncSession, inv051_setup
    ):
        """SYSTEM exercises devem aparecer no catálogo de qualquer org."""
        service = ExerciseService(async_db)
        result = await service.list_exercises(
            organization_id=inv051_setup["org_a_uuid"]
        )
        ids = [str(e.id) for e in result["exercises"]]
        assert inv051_setup["system_id"] in ids

    @pytest.mark.asyncio
    async def test_org_exercise_hidden_from_other_org(
        self, async_db: AsyncSession, inv051_setup
    ):
        """ORG exercise de org B não deve aparecer no catálogo da org A."""
        service = ExerciseService(async_db)
        result = await service.list_exercises(
            organization_id=inv051_setup["org_a_uuid"]
        )
        ids = [str(e.id) for e in result["exercises"]]
        assert inv051_setup["org_b_ex_id"] not in ids

    @pytest.mark.asyncio
    async def test_deleted_exercise_excluded_from_catalog(
        self, async_db: AsyncSession, inv051_setup
    ):
        """Exercise com deleted_at preenchido não deve aparecer no catálogo."""
        service = ExerciseService(async_db)
        result = await service.list_exercises(
            organization_id=inv051_setup["org_a_uuid"]
        )
        ids = [str(e.id) for e in result["exercises"]]
        assert inv051_setup["deleted_id"] not in ids
