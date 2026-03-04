"""
INV-TRAIN-062: Exercício com visibility_mode='restricted' só pode ser adicionado a sessão
               pelo criador ou por usuário com entrada na tabela exercise_acl.
Classe B — Service Guard (SessionExerciseService._verify_exercise_visibility)
Evidência: session_exercise_service.py — _verify_exercise_visibility()

Regra: Tentativa de add_exercise() com exercício restricted + sem ACL/não-criador
       deve lançar ExerciseNotVisibleError.
"""
import pytest
import pytest_asyncio
from uuid import uuid4, UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.session_exercise_service import SessionExerciseService
from app.core.exceptions import ExerciseNotVisibleError
from app.schemas.session_exercises import SessionExerciseCreate


class TestInvTrain062ExerciseVisibilityRequired:
    """
    INV-TRAIN-062: restricted exercise bloqueia add_exercise() para não-criador sem ACL.
    """

    @pytest_asyncio.fixture
    async def inv062_setup(
        self, async_db: AsyncSession, organization, user, training_session
    ):
        """
        Cria:
        - exercício restricted criado por `user`
        - outsider_id: UUID aleatório sem ACL (não precisa existir no DB — o serviço
          só compara UUID e consulta exercise_acl, não faz lookup de user)
        """
        exercise_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO exercises (id, name, description, scope, organization_id, created_by_user_id, visibility_mode)
            VALUES (:id, 'Exercicio Restricted INV062', 'Desc', 'ORG', :org_id, :user_id, 'restricted')
        """), {
            "id": exercise_id,
            "org_id": str(organization.id),
            "user_id": str(user.id),
        })
        await async_db.flush()
        return {
            "exercise_id": UUID(exercise_id),
            "session": training_session,
            "creator_id": user.id,
            # UUID aleatório — não-criador sem ACL (serviço não faz lookup)
            "outsider_id": uuid4(),
        }

    @pytest.mark.asyncio
    async def test_creator_can_add_restricted_exercise(
        self, async_db: AsyncSession, inv062_setup
    ):
        """Happy: criador do exercício pode adicionar exercício restricted à sessão."""
        service = SessionExerciseService(async_db)
        data = SessionExerciseCreate(
            exercise_id=inv062_setup["exercise_id"],
            order_index=0,
        )
        # Não deve lançar ExerciseNotVisibleError para o criador
        try:
            result = await service.add_exercise(
                session_id=inv062_setup["session"].id,
                data=data,
                user_id=inv062_setup["creator_id"],
            )
            assert result is not None
        except ExerciseNotVisibleError:
            pytest.fail("ExerciseNotVisibleError levantado para o criador — violação INV-062")

    @pytest.mark.asyncio
    async def test_non_creator_without_acl_cannot_add_restricted_exercise(
        self, async_db: AsyncSession, inv062_setup
    ):
        """Violation: não-criador sem ACL lança ExerciseNotVisibleError ao tentar add_exercise()."""
        service = SessionExerciseService(async_db)
        data = SessionExerciseCreate(
            exercise_id=inv062_setup["exercise_id"],
            order_index=1,
        )
        with pytest.raises(ExerciseNotVisibleError):
            await service.add_exercise(
                session_id=inv062_setup["session"].id,
                data=data,
                user_id=inv062_setup["outsider_id"],
            )
