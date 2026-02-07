"""
INV-TRAIN-045 — Unicidade de order_index por sessão de treino

RUNTIME DB TEST - Testa constraint UNIQUE INDEX (partial) real no Postgres via IntegrityError.

Obrigação A:
- Tabela: training_session_exercises
- Colunas: training_session_exercises.session_id (UUID, NOT NULL FK),
           training_session_exercises.order_index (INTEGER, NOT NULL DEFAULT 0)
- Constraint: idx_session_exercises_session_order_unique UNIQUE (session_id, order_index) WHERE deleted_at IS NULL
- Schema: schema.sql:3917

Obrigação B:
- SQLSTATE: 23505 (unique_violation)
- constraint_name: idx_session_exercises_session_order_unique

Este teste NÃO usa string match. Ele insere registros no DB e verifica
que a constraint é imposta pelo Postgres.

Nota: O UNIQUE INDEX é partial (WHERE deleted_at IS NULL), então exercícios
soft-deleted podem ter o mesmo order_index na mesma sessão.
"""

from datetime import date, datetime, timezone
from uuid import uuid4, UUID

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tests._helpers.pg_error import assert_pg_constraint_violation
from app.models.organization import Organization
from app.models.person import Person
from app.models.user import User
from app.models.training_session import TrainingSession
from app.models.exercise import Exercise
from app.models.session_exercise import SessionExercise


# ============================================
# FIXTURES LOCAIS (isoladas para este teste)
# ============================================

@pytest_asyncio.fixture
async def inv045_organization(async_db: AsyncSession) -> Organization:
    """Organização de teste para INV-TRAIN-045."""
    org = Organization(
        id=str(uuid4()),
        name="Org INV-TRAIN-045",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest_asyncio.fixture
async def inv045_person(async_db: AsyncSession) -> Person:
    """Pessoa de teste para INV-TRAIN-045."""
    person = Person(
        id=str(uuid4()),
        full_name="Teste INV-045",
        first_name="Teste",
        last_name="INV-045",
        birth_date=date(1990, 1, 1),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv045_user(async_db: AsyncSession, inv045_person: Person) -> User:
    """Usuário de teste para INV-TRAIN-045."""
    user = User(
        id=str(uuid4()),
        person_id=inv045_person.id,
        email=f"inv045_{uuid4().hex[:8]}@hbtrack.com",
    )
    async_db.add(user)
    await async_db.flush()
    return user


@pytest_asyncio.fixture
async def inv045_session(
    async_db: AsyncSession,
    inv045_organization: Organization,
    inv045_user: User,
) -> TrainingSession:
    """Sessão de treino de teste para INV-TRAIN-045."""
    session = TrainingSession(
        id=uuid4(),
        organization_id=UUID(inv045_organization.id),
        session_at=datetime(2026, 2, 1, 10, 0, 0, tzinfo=timezone.utc),
        session_type="quadra",
        created_by_user_id=UUID(inv045_user.id),
        status="draft",
    )
    async_db.add(session)
    await async_db.flush()
    return session


@pytest_asyncio.fixture
async def inv045_exercise(
    async_db: AsyncSession,
    inv045_organization: Organization,
    inv045_user: User,
) -> Exercise:
    """Exercício de teste para INV-TRAIN-045."""
    exercise = Exercise(
        id=uuid4(),
        organization_id=UUID(inv045_organization.id),
        name="Exercício INV-045",
        created_by_user_id=UUID(inv045_user.id),
    )
    async_db.add(exercise)
    await async_db.flush()
    return exercise


@pytest_asyncio.fixture
async def inv045_exercise_2(
    async_db: AsyncSession,
    inv045_organization: Organization,
    inv045_user: User,
) -> Exercise:
    """Segundo exercício de teste para INV-TRAIN-045."""
    exercise = Exercise(
        id=uuid4(),
        organization_id=UUID(inv045_organization.id),
        name="Exercício 2 INV-045",
        created_by_user_id=UUID(inv045_user.id),
    )
    async_db.add(exercise)
    await async_db.flush()
    return exercise


# ============================================
# TESTES RUNTIME
# ============================================

class TestInvTrain045SessionExercisesOrderUnique:
    """
    Testes RUNTIME para INV-TRAIN-045: idx_session_exercises_session_order_unique.

    Prova que o Postgres impõe unicidade (session_id, order_index) WHERE deleted_at IS NULL.

    Obrigação A:
    - Tabela: training_session_exercises
    - Colunas: training_session_exercises.session_id, training_session_exercises.order_index
    - Constraint: idx_session_exercises_session_order_unique UNIQUE (session_id, order_index) WHERE deleted_at IS NULL
    - Schema: schema.sql:3917

    Obrigação B:
    - SQLSTATE: 23505 (unique_violation)
    - constraint_name: idx_session_exercises_session_order_unique
    """

    @pytest.mark.asyncio
    async def test_valid_case__unique_order_index_accepted(
        self,
        async_db: AsyncSession,
        inv045_session: TrainingSession,
        inv045_exercise: Exercise,
        inv045_exercise_2: Exercise,
    ):
        """
        CASO POSITIVO: Exercícios com order_index diferentes na mesma sessão devem ser aceitos.

        Evidência: schema.sql:3917 - UNIQUE (session_id, order_index) WHERE deleted_at IS NULL
        """
        # Exercício 1: order_index = 0
        se1 = SessionExercise(
            id=uuid4(),
            session_id=inv045_session.id,
            exercise_id=inv045_exercise.id,
            order_index=0,
        )
        async_db.add(se1)
        await async_db.flush()

        # Exercício 2: order_index = 1 (diferente - OK)
        se2 = SessionExercise(
            id=uuid4(),
            session_id=inv045_session.id,
            exercise_id=inv045_exercise_2.id,
            order_index=1,
        )
        async_db.add(se2)
        await async_db.flush()

        assert se1.id is not None
        assert se2.id is not None

    @pytest.mark.asyncio
    async def test_invalid_case_1__duplicate_order_index_same_session(
        self,
        async_db: AsyncSession,
        inv045_session: TrainingSession,
        inv045_exercise: Exercise,
        inv045_exercise_2: Exercise,
    ):
        """
        CASO NEGATIVO 1: Dois exercícios com mesmo order_index na mesma sessão devem ser rejeitados.

        Evidência: schema.sql:3917 - UNIQUE (session_id, order_index) WHERE deleted_at IS NULL
        """
        # Exercício original: order_index = 0
        se1 = SessionExercise(
            id=uuid4(),
            session_id=inv045_session.id,
            exercise_id=inv045_exercise.id,
            order_index=0,
        )
        async_db.add(se1)
        await async_db.flush()

        # Duplicata: mesmo order_index (0) na mesma sessão
        se_dup = SessionExercise(
            id=uuid4(),
            session_id=inv045_session.id,  # mesma sessão
            exercise_id=inv045_exercise_2.id,  # exercício diferente, mas...
            order_index=0,  # mesmo order_index - VIOLAÇÃO
        )
        async_db.add(se_dup)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Verifica SQLSTATE e constraint via helper canônico
        assert_pg_constraint_violation(
            exc_info,
            "23505",
            "idx_session_exercises_session_order_unique"
        )

        await async_db.rollback()

    @pytest.mark.asyncio
    async def test_invalid_case_2__duplicate_same_exercise_same_order(
        self,
        async_db: AsyncSession,
        inv045_session: TrainingSession,
        inv045_exercise: Exercise,
    ):
        """
        CASO NEGATIVO 2: Mesmo exercício duplicado com mesmo order_index deve ser rejeitado.

        Nota: A tabela permite duplicatas de exercise_id (circuitos), mas não do order_index.

        Evidência: schema.sql:3917 - UNIQUE (session_id, order_index) WHERE deleted_at IS NULL
        """
        # Exercício original: order_index = 5
        se1 = SessionExercise(
            id=uuid4(),
            session_id=inv045_session.id,
            exercise_id=inv045_exercise.id,
            order_index=5,
        )
        async_db.add(se1)
        await async_db.flush()

        # Duplicata: mesmo exercício E mesmo order_index
        se_dup = SessionExercise(
            id=uuid4(),
            session_id=inv045_session.id,  # mesma sessão
            exercise_id=inv045_exercise.id,  # mesmo exercício
            order_index=5,  # mesmo order_index - VIOLAÇÃO
        )
        async_db.add(se_dup)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Verifica SQLSTATE e constraint via helper canônico
        assert_pg_constraint_violation(
            exc_info,
            "23505",
            "idx_session_exercises_session_order_unique"
        )

        await async_db.rollback()

    @pytest.mark.asyncio
    async def test_valid_case__same_order_different_session(
        self,
        async_db: AsyncSession,
        inv045_organization: Organization,
        inv045_user: User,
        inv045_exercise: Exercise,
    ):
        """
        CASO POSITIVO: Mesmo order_index em sessões diferentes deve ser aceito.

        Evidência: schema.sql:3917 - UNIQUE (session_id, order_index) - session_id é parte da chave
        """
        # Sessão 1
        session1 = TrainingSession(
            id=uuid4(),
            organization_id=UUID(inv045_organization.id),
            session_at=datetime(2026, 2, 2, 10, 0, 0, tzinfo=timezone.utc),
            session_type="quadra",
            created_by_user_id=UUID(inv045_user.id),
            status="draft",
        )
        async_db.add(session1)
        await async_db.flush()

        # Sessão 2
        session2 = TrainingSession(
            id=uuid4(),
            organization_id=UUID(inv045_organization.id),
            session_at=datetime(2026, 2, 3, 10, 0, 0, tzinfo=timezone.utc),
            session_type="quadra",
            created_by_user_id=UUID(inv045_user.id),
            status="draft",
        )
        async_db.add(session2)
        await async_db.flush()

        # Exercício na sessão 1: order_index = 0
        se1 = SessionExercise(
            id=uuid4(),
            session_id=session1.id,
            exercise_id=inv045_exercise.id,
            order_index=0,
        )
        async_db.add(se1)
        await async_db.flush()

        # Exercício na sessão 2: order_index = 0 (mesmo index, mas sessão diferente - OK)
        se2 = SessionExercise(
            id=uuid4(),
            session_id=session2.id,  # sessão diferente
            exercise_id=inv045_exercise.id,
            order_index=0,  # mesmo order_index - OK pois sessão diferente
        )
        async_db.add(se2)
        await async_db.flush()

        assert se1.id is not None
        assert se2.id is not None

    @pytest.mark.asyncio
    async def test_valid_case__soft_deleted_allows_reuse(
        self,
        async_db: AsyncSession,
        inv045_session: TrainingSession,
        inv045_exercise: Exercise,
        inv045_exercise_2: Exercise,
    ):
        """
        CASO POSITIVO: Order_index pode ser reutilizado se o registro original foi soft-deleted.

        Evidência: schema.sql:3917 - UNIQUE ... WHERE deleted_at IS NULL (partial index)
        """
        # Exercício original: order_index = 3, depois soft-delete
        se1 = SessionExercise(
            id=uuid4(),
            session_id=inv045_session.id,
            exercise_id=inv045_exercise.id,
            order_index=3,
            deleted_at=datetime.now(timezone.utc),  # soft-deleted
        )
        async_db.add(se1)
        await async_db.flush()

        # Novo exercício com mesmo order_index - OK pois o outro está deletado
        se2 = SessionExercise(
            id=uuid4(),
            session_id=inv045_session.id,  # mesma sessão
            exercise_id=inv045_exercise_2.id,
            order_index=3,  # mesmo order_index - OK pois original está soft-deleted
        )
        async_db.add(se2)
        await async_db.flush()

        assert se1.id is not None
        assert se2.id is not None
