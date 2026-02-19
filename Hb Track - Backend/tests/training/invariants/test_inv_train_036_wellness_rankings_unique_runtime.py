"""
INV-TRAIN-036 — Ranking de wellness é único por equipe e mês

RUNTIME DB TEST - Testa constraint real no Postgres via IntegrityError.

Evidência:
- Constraint: `uq_team_wellness_rankings_team_month UNIQUE (team_id, month_reference)`
- Schema: `Hb Track - Backend/docs/ssot/schema.sql:3653`
- Table: `team_wellness_rankings`

Este teste NÃO usa string match. Ele insere registros no DB e verifica
que a constraint é imposta pelo Postgres (SQLSTATE 23505 para UNIQUE).

NOTA: Como não há modelo SQLAlchemy para team_wellness_rankings,
usamos SQL raw para inserção via async_db.execute(text(...)).
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4, UUID

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.organization import Organization
from app.models.team import Team


# ============================================
# FIXTURES LOCAIS (isoladas para este teste)
# ============================================

@pytest_asyncio.fixture
async def inv036_category(async_db: AsyncSession) -> Category:
    """Categoria de teste para INV-TRAIN-036."""
    category = Category(
        id=9936,
        name="Categoria INV-036",
        max_age=19,
        is_active=True,
    )
    async_db.add(category)
    await async_db.flush()
    return category


@pytest_asyncio.fixture
async def inv036_organization(async_db: AsyncSession) -> Organization:
    """Organização de teste para INV-TRAIN-036."""
    org = Organization(
        id=str(uuid4()),
        name="Org INV-TRAIN-036",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest_asyncio.fixture
async def inv036_team_a(
    async_db: AsyncSession,
    inv036_category: Category,
    inv036_organization: Organization,
) -> Team:
    """Equipe A de teste para INV-TRAIN-036."""
    team = Team(
        id=uuid4(),
        organization_id=UUID(inv036_organization.id),
        name="Equipe A INV-036",
        category_id=inv036_category.id,
        gender="feminino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


@pytest_asyncio.fixture
async def inv036_team_b(
    async_db: AsyncSession,
    inv036_category: Category,
    inv036_organization: Organization,
) -> Team:
    """Equipe B de teste para INV-TRAIN-036."""
    team = Team(
        id=uuid4(),
        organization_id=UUID(inv036_organization.id),
        name="Equipe B INV-036",
        category_id=inv036_category.id,
        gender="masculino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


# ============================================
# TESTES RUNTIME
# ============================================

class TestInvTrain036WellnessRankingsUniqueRuntime:
    """
    Testes RUNTIME para INV-TRAIN-036: uq_team_wellness_rankings_team_month.

    Prova que o Postgres impõe unicidade (team_id, month_reference).
    """

    @pytest.mark.asyncio
    async def test_same_team_different_months_accepted(
        self,
        async_db: AsyncSession,
        inv036_team_a: Team,
    ):
        """
        CASO POSITIVO: Mesmo team com meses diferentes.

        Evidência: schema.sql:3653 - UNIQUE (team_id, month_reference)
        """
        # Inserir ranking para janeiro
        await async_db.execute(
            text("""
                INSERT INTO team_wellness_rankings (
                    id, team_id, month_reference, response_rate_pre,
                    response_rate_post, avg_rate, rank, athletes_90plus
                ) VALUES (
                    gen_random_uuid(), :team_id, :month_ref, 85.0,
                    75.0, 80.0, 1, 5
                )
            """),
            {"team_id": str(inv036_team_a.id), "month_ref": date(2026, 1, 1)}
        )

        # Inserir ranking para fevereiro - deve passar
        await async_db.execute(
            text("""
                INSERT INTO team_wellness_rankings (
                    id, team_id, month_reference, response_rate_pre,
                    response_rate_post, avg_rate, rank, athletes_90plus
                ) VALUES (
                    gen_random_uuid(), :team_id, :month_ref, 90.0,
                    80.0, 85.0, 1, 6
                )
            """),
            {"team_id": str(inv036_team_a.id), "month_ref": date(2026, 2, 1)}  # Mês diferente
        )
        await async_db.flush()

        # Verificar que ambos foram inseridos
        result = await async_db.execute(
            text("SELECT COUNT(*) FROM team_wellness_rankings WHERE team_id = :team_id"),
            {"team_id": str(inv036_team_a.id)}
        )
        count = result.scalar()
        assert count == 2

    @pytest.mark.asyncio
    async def test_different_teams_same_month_accepted(
        self,
        async_db: AsyncSession,
        inv036_team_a: Team,
        inv036_team_b: Team,
    ):
        """
        CASO POSITIVO: Teams diferentes no mesmo mês.

        Evidência: schema.sql:3653 - UNIQUE (team_id, month_reference)
        A unicidade é por team, não global.
        """
        month_ref = date(2026, 3, 1)

        # Inserir ranking para team A
        await async_db.execute(
            text("""
                INSERT INTO team_wellness_rankings (
                    id, team_id, month_reference, response_rate_pre,
                    response_rate_post, avg_rate, rank, athletes_90plus
                ) VALUES (
                    gen_random_uuid(), :team_id, :month_ref, 85.0,
                    75.0, 80.0, 1, 5
                )
            """),
            {"team_id": str(inv036_team_a.id), "month_ref": month_ref}
        )

        # Inserir ranking para team B no mesmo mês - deve passar
        await async_db.execute(
            text("""
                INSERT INTO team_wellness_rankings (
                    id, team_id, month_reference, response_rate_pre,
                    response_rate_post, avg_rate, rank, athletes_90plus
                ) VALUES (
                    gen_random_uuid(), :team_id, :month_ref, 90.0,
                    80.0, 85.0, 2, 6
                )
            """),
            {"team_id": str(inv036_team_b.id), "month_ref": month_ref}  # Team diferente
        )
        await async_db.flush()

        # Verificar que ambos foram inseridos
        result = await async_db.execute(
            text("SELECT COUNT(*) FROM team_wellness_rankings WHERE month_reference = :month_ref"),
            {"month_ref": month_ref}
        )
        count = result.scalar()
        assert count == 2

    @pytest.mark.asyncio
    async def test_duplicate_team_month_rejected(
        self,
        async_db: AsyncSession,
        inv036_team_a: Team,
    ):
        """
        CASO NEGATIVO: Mesmo team + mesmo mês deve ser rejeitado.

        Evidência: schema.sql:3653 - UNIQUE (team_id, month_reference)
        """
        month_ref = date(2026, 4, 1)

        # Inserir primeiro ranking
        await async_db.execute(
            text("""
                INSERT INTO team_wellness_rankings (
                    id, team_id, month_reference, response_rate_pre,
                    response_rate_post, avg_rate, rank, athletes_90plus
                ) VALUES (
                    gen_random_uuid(), :team_id, :month_ref, 85.0,
                    75.0, 80.0, 1, 5
                )
            """),
            {"team_id": str(inv036_team_a.id), "month_ref": month_ref}
        )
        await async_db.flush()

        # Tentar inserir segundo ranking com mesma combinação - deve falhar
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(
                text("""
                    INSERT INTO team_wellness_rankings (
                        id, team_id, month_reference, response_rate_pre,
                        response_rate_post, avg_rate, rank, athletes_90plus
                    ) VALUES (
                        gen_random_uuid(), :team_id, :month_ref, 95.0,
                        90.0, 92.5, 1, 8
                    )
                """),
                {"team_id": str(inv036_team_a.id), "month_ref": month_ref}  # DUPLICADO
            )
            await async_db.flush()

        assert "uq_team_wellness_rankings_team_month" in str(exc_info.value).lower()
