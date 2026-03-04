"""
INV-TRAIN-060: Exercício ORG criado sem visibility_mode explícito deve defaultar para 'restricted'.
Classe B — Service Guard (ExerciseService)
Evidência: exercise_service.py:342-351 — INV-060 default logic

Regra: Ao criar exercício com scope='ORG' sem especificar visibility_mode,
o serviço deve automaticamente definir visibility_mode='restricted'.
Isso garante que por padrão exercícios organizacionais não ficam públicos dentro
da org sem decisão explícita do criador.

ATENÇÃO: canonical é 'restricted' (não 'org_wide') — conforme v1.3.0 amendment e INV-TRAIN-060.
"""
import pytest
import pytest_asyncio
from uuid import uuid4, UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.exercise_service import ExerciseService


class TestInvTrain060OrgExerciseDefaultRestricted:
    """
    INV-TRAIN-060: ExerciseService.create_exercise() com scope='ORG'
    sem visibility_mode → deve definir visibility_mode='restricted'.
    """

    @pytest.mark.asyncio
    async def test_org_exercise_defaults_to_restricted_when_not_specified(
        self, async_db: AsyncSession, organization, user
    ):
        """Happy: ORG exercise sem visibility_mode → visibility_mode='restricted'."""
        service = ExerciseService(async_db)

        exercise = await service.create_exercise(
            data={
                "name": f"Exercicio ORG INV060 {uuid4().hex[:6]}",
                "description": "Teste INV-060 default restricted",
                # scope='ORG' é o default — não passamos para evitar duplicação no Exercise()
                # NÃO especificamos visibility_mode — deve defaultar para 'restricted'
            },
            user_id=user.id,
            organization_id=organization.id,
        )

        assert exercise.visibility_mode == "restricted", (
            f"INV-060: ORG exercise sem visibility_mode deve defaultar para 'restricted', "
            f"obtido: '{exercise.visibility_mode}'"
        )
        assert exercise.scope == "ORG"
        assert exercise.organization_id == organization.id

    @pytest.mark.asyncio
    async def test_org_exercise_explicit_org_wide_is_respected(
        self, async_db: AsyncSession, organization, user
    ):
        """Quando visibility_mode='org_wide' é explicitamente especificado, deve ser aceito."""
        service = ExerciseService(async_db)

        exercise = await service.create_exercise(
            data={
                "name": f"Exercicio ORG orgwide INV060 {uuid4().hex[:6]}",
                "description": "Teste INV-060 explicit org_wide",
                # scope='ORG' é o default — não passamos para evitar duplicação no Exercise()
                "visibility_mode": "org_wide",  # Explícito — deve ser respeitado
            },
            user_id=user.id,
            organization_id=organization.id,
        )

        assert exercise.visibility_mode == "org_wide", (
            "Quando org_wide for explicitamente especificado, deve ser aceito"
        )

    @pytest.mark.asyncio
    async def test_org_exercise_explicit_restricted_is_accepted(
        self, async_db: AsyncSession, organization, user
    ):
        """Violation check: visibility_mode='restricted' explícito deve permanecer restricted."""
        service = ExerciseService(async_db)

        exercise = await service.create_exercise(
            data={
                "name": f"Exercicio ORG restricted INV060 {uuid4().hex[:6]}",
                "description": "Teste INV-060 explicit restricted",
                # scope='ORG' é o default — não passamos para evitar duplicação no Exercise()
                "visibility_mode": "restricted",  # Explícito
            },
            user_id=user.id,
            organization_id=organization.id,
        )

        assert exercise.visibility_mode == "restricted"
        assert exercise.scope == "ORG"
