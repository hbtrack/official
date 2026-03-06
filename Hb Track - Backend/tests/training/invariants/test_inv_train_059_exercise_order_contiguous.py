"""
INV-TRAIN-059 — exercise_order_contiguous_starting_1

SERVICE TEST (Classe C2) - Testa que order_index de session_exercises deve ser
contíguo começando em 1 (sem gaps: 1,2,3... não 1,2,4).

Enunciado: A ordem dos exercícios de uma sessão deve ser sequencial e contígua
começando em 1, sem lacunas/gaps. Ao reordenar ou remover exercícios, o service
deve normalizar a sequência.

Evidência (service layer):
- app/services/session_exercise_service.py:320-420 (método reorder_exercises)
- GAP: reorder_exercises permite [1,2,4] sem validar contiguidade
- IDEAL: criar _normalize_order() que garante [1,2,3...] após add/remove/reorder

Teste: Verifica:
  1) CASO POSITIVO: Adicionar 3 exercícios resulta em order_index [1,2,3]
  2) CASO NEGATIVO: Tentar setar [1,2,4] via reorder (SKIP: validação não implementada)

Classe: C2 (Service com DB, Runtime Integration)
"""

from datetime import date, datetime, timezone
from uuid import uuid4, UUID

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.person import Person
from app.models.user import User
from app.models.team import Team
from app.models.season import Season
from app.models.training_session import TrainingSession
from app.models.exercise import Exercise
from app.models.session_exercise import SessionExercise
from app.services.session_exercise_service import SessionExerciseService
from app.schemas.session_exercises import (
    SessionExerciseCreate,
    SessionExerciseReorder,
    SessionExerciseReorderItem,
)


# ============================================
# FIXTURES LOCAIS (isoladas para este teste)
# ============================================

@pytest_asyncio.fixture
async def inv059_organization(async_db: AsyncSession) -> Organization:
    """Organização de teste para INV-TRAIN-059."""
    org = Organization(
        id=str(uuid4()),
        name="Org INV-TRAIN-059",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest_asyncio.fixture
async def inv059_person(async_db: AsyncSession) -> Person:
    """Pessoa de teste para INV-TRAIN-059."""
    person = Person(
        id=str(uuid4()),
        full_name="Teste INV-059",
        first_name="Teste",
        last_name="INV-059",
        birth_date=date(1990, 1, 1),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv059_user(async_db: AsyncSession, inv059_person: Person) -> User:
    """Usuário de teste para INV-TRAIN-059."""
    user = User(
        id=str(uuid4()),
        person_id=inv059_person.id,
        email=f"inv059_{uuid4().hex[:8]}@hbtrack.com",
    )
    async_db.add(user)
    await async_db.flush()
    return user


@pytest_asyncio.fixture
async def inv059_category(async_db: AsyncSession):
    """Categoria de teste para INV-TRAIN-059."""
    cid = 9997
    await async_db.execute(text("""
        INSERT INTO categories (id, name, max_age, is_active)
        VALUES (:id, 'Test Category INV-059', 19, true)
        ON CONFLICT (id) DO NOTHING
    """), {"id": cid})
    await async_db.flush()
    return type('Category', (), {'id': cid})()


@pytest_asyncio.fixture
async def inv059_team(
    async_db: AsyncSession,
    inv059_organization: Organization,
    inv059_category,
) -> Team:
    """Time de teste para INV-TRAIN-059."""
    team = Team(
        id=uuid4(),
        organization_id=UUID(inv059_organization.id),
        category_id=inv059_category.id,
        name="Time INV-059",
        gender="masculino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


@pytest_asyncio.fixture
async def inv059_season(
    async_db: AsyncSession,
    inv059_team: Team,
) -> Season:
    """Season de teste para INV-TRAIN-059."""
    season = Season(
        id=uuid4(),
        team_id=inv059_team.id,
        year=2026,
        name="Temporada 2026 INV-059",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
    )
    async_db.add(season)
    await async_db.flush()
    return season


@pytest_asyncio.fixture
async def inv059_session(
    async_db: AsyncSession,
    inv059_organization: Organization,
    inv059_team: Team,
    inv059_user: User,
) -> TrainingSession:
    """Sessão de treino para INV-TRAIN-059."""
    session = TrainingSession(
        id=uuid4(),
        organization_id=UUID(inv059_organization.id),
        team_id=inv059_team.id,
        session_at=datetime(2026, 2, 1, 10, 0, 0, tzinfo=timezone.utc),
        session_type="quadra",
        created_by_user_id=UUID(inv059_user.id),
        status="draft",
    )
    async_db.add(session)
    await async_db.flush()
    return session


@pytest_asyncio.fixture
async def inv059_exercise_1(
    async_db: AsyncSession,
    inv059_organization: Organization,
    inv059_user: User,
) -> Exercise:
    """Primeiro exercício de teste para INV-TRAIN-059."""
    exercise = Exercise(
        id=uuid4(),
        organization_id=UUID(inv059_organization.id),
        name="Exercício 1 INV-059",
        created_by_user_id=UUID(inv059_user.id),
    )
    async_db.add(exercise)
    await async_db.flush()
    return exercise


@pytest_asyncio.fixture
async def inv059_exercise_2(
    async_db: AsyncSession,
    inv059_organization: Organization,
    inv059_user: User,
) -> Exercise:
    """Segundo exercício de teste para INV-TRAIN-059."""
    exercise = Exercise(
        id=uuid4(),
        organization_id=UUID(inv059_organization.id),
        name="Exercício 2 INV-059",
        created_by_user_id=UUID(inv059_user.id),
    )
    async_db.add(exercise)
    await async_db.flush()
    return exercise


@pytest_asyncio.fixture
async def inv059_exercise_3(
    async_db: AsyncSession,
    inv059_organization: Organization,
    inv059_user: User,
) -> Exercise:
    """Terceiro exercício de teste para INV-TRAIN-059."""
    exercise = Exercise(
        id=uuid4(),
        organization_id=UUID(inv059_organization.id),
        name="Exercício 3 INV-059",
        created_by_user_id=UUID(inv059_user.id),
    )
    async_db.add(exercise)
    await async_db.flush()
    return exercise


# ============================================
# TESTES SERVICE LAYER
# ============================================

class TestInvTrain059ExerciseOrderContiguous:
    """
    Testes SERVICE para INV-TRAIN-059: exercise_order_contiguous_starting_1.

    Prova que:
    1) Ao adicionar exercícios, order_index deve seguir [1,2,3...]
    2) Ao reordenar, não deveria permitir gaps como [1,2,4]

    Evidência:
    - session_exercise_service.py:320-420 (reorder_exercises)
    - GAP: não há validação de contiguidade (permite [1,2,4])
    """

    @pytest.mark.asyncio
    async def test_valid_contiguous_order_1_2_3(
        self,
        async_db: AsyncSession,
        inv059_session: TrainingSession,
        inv059_exercise_1: Exercise,
        inv059_exercise_2: Exercise,
        inv059_exercise_3: Exercise,
        inv059_user: User,
    ):
        """
        CASO POSITIVO: Adicionar 3 exercícios deve resultar em order_index [1,2,3].

        Evidência: session_exercise_service.py:127 (order_index do payload)
        """
        service = SessionExerciseService(async_db)

        # Adicionar exercício 1
        payload1 = SessionExerciseCreate(
            exercise_id=inv059_exercise_1.id,
            order_index=1,
            duration_minutes=10,
        )
        result1 = await service.add_exercise(
            session_id=inv059_session.id,
            data=payload1,
            user_id=UUID(inv059_user.id),
        )

        # Adicionar exercício 2
        payload2 = SessionExerciseCreate(
            exercise_id=inv059_exercise_2.id,
            order_index=2,
            duration_minutes=15,
        )
        result2 = await service.add_exercise(
            session_id=inv059_session.id,
            data=payload2,
            user_id=UUID(inv059_user.id),
        )

        # Adicionar exercício 3
        payload3 = SessionExerciseCreate(
            exercise_id=inv059_exercise_3.id,
            order_index=3,
            duration_minutes=20,
        )
        result3 = await service.add_exercise(
            session_id=inv059_session.id,
            data=payload3,
            user_id=UUID(inv059_user.id),
        )

        # Validar ordem contígua [1,2,3]
        assert result1.order_index == 1
        assert result2.order_index == 2
        assert result3.order_index == 3

        # Buscar todos exercícios da sessão e verificar ordem
        session_exercises = await service.get_session_exercises(
            session_id=inv059_session.id,
            user_id=UUID(inv059_user.id),
        )

        assert len(session_exercises.exercises) == 3
        orders = [ex.order_index for ex in session_exercises.exercises]
        assert orders == [1, 2, 3], f"Ordem esperada [1,2,3], obtida {orders}"

    @pytest.mark.asyncio
    async def test_invalid_gap_in_order_2_4(
        self,
        async_db: AsyncSession,
        inv059_session: TrainingSession,
        inv059_exercise_1: Exercise,
        inv059_exercise_2: Exercise,
        inv059_exercise_3: Exercise,
        inv059_user: User,
    ):
        """
        CASO NEGATIVO: Reordenar para [1,2,4] NÃO deveria ser permitido (gap no 3).

        SKIP: Guard não implementado em session_exercise_service.reorder_exercises

        Evidência esperada:
        - reorder_exercises deveria chamar _validate_order_contiguity()
        - Erro esperado: BusinessError("Order index deve ser contíguo começando em 1")

        Gap atual: session_exercise_service.py:376-420 permite qualquer order_index sem validar gaps
        """
        from app.core.exceptions import BusinessError

        service = SessionExerciseService(async_db)

        # Criar 3 exercícios com ordem inicial [1,2,3]
        se1 = SessionExercise(
            id=uuid4(),
            session_id=inv059_session.id,
            exercise_id=inv059_exercise_1.id,
            order_index=1,
        )
        se2 = SessionExercise(
            id=uuid4(),
            session_id=inv059_session.id,
            exercise_id=inv059_exercise_2.id,
            order_index=2,
        )
        se3 = SessionExercise(
            id=uuid4(),
            session_id=inv059_session.id,
            exercise_id=inv059_exercise_3.id,
            order_index=3,
        )
        async_db.add_all([se1, se2, se3])
        await async_db.flush()

        # Tentar reordenar para [1,2,4] - deveria falhar (gap no 3)
        reorder_payload = SessionExerciseReorder(
            reorders=[
                SessionExerciseReorderItem(id=se1.id, order_index=1),
                SessionExerciseReorderItem(id=se2.id, order_index=2),
                SessionExerciseReorderItem(id=se3.id, order_index=4),  # GAP!
            ]
        )

        with pytest.raises(BusinessError) as exc_info:
            await service.reorder_exercises(
                session_id=inv059_session.id,
                data=reorder_payload,
                user_id=UUID(inv059_user.id),
            )

        # Validar mensagem de erro
        assert "contíguo" in str(exc_info.value).lower() or "gap" in str(exc_info.value).lower()
