"""
INV-TRAIN-058 — session_structure_mutable_until_close

SERVICE TEST (Classe C2) - Testa que operações de alteração de estrutura de exercícios
estão bloqueadas para sessões readonly/in_progress.

Enunciado: Estrutura de exercícios de uma sessão só pode ser alterada enquanto
sessão NÃO estiver encerrada (status != readonly e status != in_progress).

Evidência (service layer):
- app/services/training_session_service.py:495-497 (readonly → ForbiddenError)
- app/services/training_session_service.py:499-500 (in_progress → ForbiddenError)
- GAP: session_exercise_service.py NÃO valida status da sessão antes de add/remove/update

Teste: Verifica:
  1) CASO POSITIVO: Pode adicionar exercício a sessão draft (sucesso)
  2) CASO NEGATIVO: Sessão readonly deveria rejeitar add_exercise_to_session
     (SKIP: guard não implementado em session_exercise_service)

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
from app.services.session_exercise_service import SessionExerciseService
from app.schemas.session_exercises import SessionExerciseCreate


# ============================================
# FIXTURES LOCAIS (isoladas para este teste)
# ============================================

@pytest_asyncio.fixture
async def inv058_organization(async_db: AsyncSession) -> Organization:
    """Organização de teste para INV-TRAIN-058."""
    org = Organization(
        id=str(uuid4()),
        name="Org INV-TRAIN-058",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest_asyncio.fixture
async def inv058_person(async_db: AsyncSession) -> Person:
    """Pessoa de teste para INV-TRAIN-058."""
    person = Person(
        id=str(uuid4()),
        full_name="Teste INV-058",
        first_name="Teste",
        last_name="INV-058",
        birth_date=date(1990, 1, 1),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv058_user(async_db: AsyncSession, inv058_person: Person) -> User:
    """Usuário de teste para INV-TRAIN-058."""
    user = User(
        id=str(uuid4()),
        person_id=inv058_person.id,
        email=f"inv058_{uuid4().hex[:8]}@hbtrack.com",
    )
    async_db.add(user)
    await async_db.flush()
    return user


@pytest_asyncio.fixture
async def inv058_category(async_db: AsyncSession):
    """Categoria de teste para INV-TRAIN-058."""
    cid = 9998
    await async_db.execute(text("""
        INSERT INTO categories (id, name, max_age, is_active)
        VALUES (:id, 'Test Category INV-058', 19, true)
        ON CONFLICT (id) DO NOTHING
    """), {"id": cid})
    await async_db.flush()
    return type('Category', (), {'id': cid})()


@pytest_asyncio.fixture
async def inv058_team(
    async_db: AsyncSession,
    inv058_organization: Organization,
    inv058_category,
) -> Team:
    """Time de teste para INV-TRAIN-058."""
    team = Team(
        id=uuid4(),
        organization_id=UUID(inv058_organization.id),
        category_id=inv058_category.id,
        name="Time INV-058",
        gender="masculino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


@pytest_asyncio.fixture
async def inv058_season(
    async_db: AsyncSession,
    inv058_team: Team,
) -> Season:
    """Season de teste para INV-TRAIN-058."""
    season = Season(
        id=uuid4(),
        team_id=inv058_team.id,
        year=2026,
        name="Temporada 2026 INV-058",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
    )
    async_db.add(season)
    await async_db.flush()
    return season


@pytest_asyncio.fixture
async def inv058_session_draft(
    async_db: AsyncSession,
    inv058_organization: Organization,
    inv058_team: Team,
    inv058_user: User,
) -> TrainingSession:
    """Sessão de treino DRAFT para INV-TRAIN-058."""
    session = TrainingSession(
        id=uuid4(),
        organization_id=UUID(inv058_organization.id),
        team_id=inv058_team.id,
        session_at=datetime(2026, 2, 1, 10, 0, 0, tzinfo=timezone.utc),
        session_type="quadra",
        created_by_user_id=UUID(inv058_user.id),
        status="draft",
    )
    async_db.add(session)
    await async_db.flush()
    return session


@pytest_asyncio.fixture
async def inv058_session_readonly(
    async_db: AsyncSession,
    inv058_organization: Organization,
    inv058_team: Team,
    inv058_user: User,
) -> TrainingSession:
    """Sessão de treino READONLY (encerrada) para INV-TRAIN-058."""
    session = TrainingSession(
        id=uuid4(),
        organization_id=UUID(inv058_organization.id),
        team_id=inv058_team.id,
        session_at=datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
        session_type="quadra",
        created_by_user_id=UUID(inv058_user.id),
        status="readonly",  # sessão encerrada/congelada
    )
    async_db.add(session)
    await async_db.flush()
    return session


@pytest_asyncio.fixture
async def inv058_exercise(
    async_db: AsyncSession,
    inv058_organization: Organization,
    inv058_user: User,
) -> Exercise:
    """Exercício de teste para INV-TRAIN-058."""
    exercise = Exercise(
        id=uuid4(),
        organization_id=UUID(inv058_organization.id),
        name="Exercício INV-058",
        created_by_user_id=UUID(inv058_user.id),
    )
    async_db.add(exercise)
    await async_db.flush()
    return exercise


# ============================================
# TESTES SERVICE LAYER
# ============================================

class TestInvTrain058SessionStructureMutable:
    """
    Testes SERVICE para INV-TRAIN-058: session_structure_mutable_until_close.

    Prova que:
    1) Sessão draft aceita alterações de estrutura de exercícios
    2) Sessão readonly/in_progress DEVERIA rejeitar (guard faltando)

    Evidência:
    - training_session_service.py:495-500 (guards readonly/in_progress)
    - GAP: session_exercise_service.py não valida status da sessão
    """

    @pytest.mark.asyncio
    async def test_valid_session_draft_allows_add_exercise(
        self,
        async_db: AsyncSession,
        inv058_session_draft: TrainingSession,
        inv058_exercise: Exercise,
        inv058_user: User,
    ):
        """
        CASO POSITIVO: Sessão draft deve permitir adicionar exercícios.

        Evidência: status == "draft" não tem restrições (training_session_service.py)
        """
        service = SessionExerciseService(async_db)

        # Criar payload para adicionar exercício
        payload = SessionExerciseCreate(
            exercise_id=inv058_exercise.id,
            order_index=1,
            duration_minutes=15,
            notes="Exercício de aquecimento",
        )

        # Adicionar exercício à sessão draft - deve suceder
        result = await service.add_exercise(
            session_id=inv058_session_draft.id,
            data=payload,
            user_id=UUID(inv058_user.id),
        )

        # Validar que o exercício foi adicionado
        assert result.id is not None
        assert result.exercise_id == inv058_exercise.id
        assert result.order_index == 1
        assert result.duration_minutes == 15

    @pytest.mark.skip(
        reason="PENDING: session_exercise_service não valida status da sessão antes de add/update/delete"
    )
    @pytest.mark.asyncio
    async def test_invalid_session_readonly_rejects_add_exercise(
        self,
        async_db: AsyncSession,
        inv058_session_readonly: TrainingSession,
        inv058_exercise: Exercise,
        inv058_user: User,
    ):
        """
        CASO NEGATIVO: Sessão readonly NÃO deve permitir adicionar exercícios.

        SKIP: Guard não implementado em session_exercise_service.py

        Evidência esperada: 
        - session_exercise_service.add_exercise deveria chamar _validate_session_mutable()
        - _validate_session_mutable() deveria rejeitar se status in ["readonly", "in_progress"]
        - Erro esperado: ForbiddenError("Sessão encerrada. Estrutura não pode ser alterada.")

        Gap atual: session_exercise_service.py:117-127 NÃO verifica session.status
        """
        from app.core.exceptions import ForbiddenError

        service = SessionExerciseService(async_db)

        payload = SessionExerciseCreate(
            exercise_id=inv058_exercise.id,
            order_index=1,
            duration_minutes=15,
            notes="Tentativa de adicionar exercício a sessão readonly",
        )

        # Tentar adicionar exercício à sessão readonly - deveria falhar
        with pytest.raises(ForbiddenError) as exc_info:
            await service.add_exercise(
                session_id=inv058_session_readonly.id,
                data=payload,
                user_id=UUID(inv058_user.id),
            )

        # Validar mensagem de erro
        assert "encerrada" in str(exc_info.value).lower() or "readonly" in str(exc_info.value).lower()
