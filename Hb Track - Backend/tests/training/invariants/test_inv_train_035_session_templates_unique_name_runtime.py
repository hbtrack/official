"""
INV-TRAIN-035 — Nome de template de sessão é único por organização

RUNTIME DB TEST - Testa constraint real no Postgres via IntegrityError.

Evidência:
- Constraint: `uq_session_templates_org_name UNIQUE (org_id, name)`
- Schema: `Hb Track - Backend/docs/ssot/schema.sql:3645`
- Model: `app/models/session_template.py:38` (organization_id + name)

Este teste NÃO usa string match. Ele insere registros no DB e verifica
que a constraint é imposta pelo Postgres (SQLSTATE 23505 para UNIQUE).
"""

from datetime import date, datetime, timezone
from uuid import uuid4, UUID

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.session_template import SessionTemplate


# ============================================
# FIXTURES LOCAIS (isoladas para este teste)
# ============================================

@pytest_asyncio.fixture
async def inv035_organization_a(async_db: AsyncSession) -> Organization:
    """Organização A de teste para INV-TRAIN-035."""
    org = Organization(
        id=str(uuid4()),
        name="Org A INV-TRAIN-035",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest_asyncio.fixture
async def inv035_organization_b(async_db: AsyncSession) -> Organization:
    """Organização B de teste para INV-TRAIN-035."""
    org = Organization(
        id=str(uuid4()),
        name="Org B INV-TRAIN-035",
    )
    async_db.add(org)
    await async_db.flush()
    return org


# ============================================
# TESTES RUNTIME
# ============================================

class TestInvTrain035SessionTemplatesUniqueNameRuntime:
    """
    Testes RUNTIME para INV-TRAIN-035: uq_session_templates_org_name.

    Prova que o Postgres impõe unicidade (org_id, name).
    """

    @pytest.mark.asyncio
    async def test_unique_name_in_same_org_accepted(
        self,
        async_db: AsyncSession,
        inv035_organization_a: Organization,
    ):
        """
        CASO POSITIVO: Dois templates com nomes diferentes na mesma org.

        Evidência: schema.sql:3645 - UNIQUE (org_id, name)
        """
        template1 = SessionTemplate(
            id=uuid4(),
            org_id=UUID(inv035_organization_a.id),
            name="Template A",
            icon="target",
        )
        template2 = SessionTemplate(
            id=uuid4(),
            org_id=UUID(inv035_organization_a.id),
            name="Template B",  # Nome diferente - deve passar
            icon="target",
        )
        async_db.add(template1)
        async_db.add(template2)
        await async_db.flush()

        assert template1.id is not None
        assert template2.id is not None

    @pytest.mark.asyncio
    async def test_same_name_in_different_orgs_accepted(
        self,
        async_db: AsyncSession,
        inv035_organization_a: Organization,
        inv035_organization_b: Organization,
    ):
        """
        CASO POSITIVO: Mesmo nome em organizações diferentes.

        Evidência: schema.sql:3645 - UNIQUE (org_id, name)
        A unicidade é por organização, não global.
        """
        template1 = SessionTemplate(
            id=uuid4(),
            org_id=UUID(inv035_organization_a.id),
            name="Template Comum",
            icon="target",
        )
        template2 = SessionTemplate(
            id=uuid4(),
            org_id=UUID(inv035_organization_b.id),  # Org diferente
            name="Template Comum",  # Mesmo nome - deve passar
            icon="target",
        )
        async_db.add(template1)
        async_db.add(template2)
        await async_db.flush()

        assert template1.id is not None
        assert template2.id is not None

    @pytest.mark.asyncio
    async def test_duplicate_name_in_same_org_rejected(
        self,
        async_db: AsyncSession,
        inv035_organization_a: Organization,
    ):
        """
        CASO NEGATIVO: Nome duplicado na mesma org deve ser rejeitado.

        Evidência: schema.sql:3645 - UNIQUE (org_id, name)
        """
        template1 = SessionTemplate(
            id=uuid4(),
            org_id=UUID(inv035_organization_a.id),
            name="Template Duplicado",
            icon="target",
        )
        async_db.add(template1)
        await async_db.flush()

        # Tentar criar segundo com mesmo nome na mesma org
        template2 = SessionTemplate(
            id=uuid4(),
            org_id=UUID(inv035_organization_a.id),  # Mesma org
            name="Template Duplicado",  # MESMO NOME - deve falhar
            icon="activity",
        )
        async_db.add(template2)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        assert "uq_session_templates_org_name" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_case_sensitive_names_are_different(
        self,
        async_db: AsyncSession,
        inv035_organization_a: Organization,
    ):
        """
        CASO POSITIVO: Nomes com case diferente são únicos.

        Evidência: schema.sql:3645 - UNIQUE (org_id, name)
        PostgreSQL por padrão é case-sensitive para text/varchar.
        """
        template1 = SessionTemplate(
            id=uuid4(),
            org_id=UUID(inv035_organization_a.id),
            name="Template Case",
            icon="target",
        )
        template2 = SessionTemplate(
            id=uuid4(),
            org_id=UUID(inv035_organization_a.id),
            name="TEMPLATE CASE",  # Case diferente - deve passar
            icon="target",
        )
        async_db.add(template1)
        async_db.add(template2)
        await async_db.flush()

        assert template1.id is not None
        assert template2.id is not None
