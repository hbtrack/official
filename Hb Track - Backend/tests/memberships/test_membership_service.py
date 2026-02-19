"""
Testes do MembershipService.
Ref: R5-R8, RDB9, R25/R26
"""
import pytest
from uuid import uuid4

from app.services.membership_service import (
    MembershipService,
    ROLE_ATHLETE,
    ROLE_COACH,
    ROLE_COORDINATOR,
    ROLE_DIRECTOR,
)


class TestMembershipServiceCreate:
    """Testes de criação de membership."""

    @pytest.mark.asyncio
    async def test_create_membership_success(self, async_db, organization, user, person_id):
        """Criar membership via service."""
        service = MembershipService(async_db)

        membership = await service.create(
            organization_id=organization.id,
            person_id=person_id,
            role_id=ROLE_COACH,
        )

        assert membership.id is not None
        assert membership.role_id == ROLE_COACH

    @pytest.mark.asyncio
    async def test_create_membership_athlete(self, async_db, organization, user, person_id):
        """Criar membership de atleta."""
        service = MembershipService(async_db)

        membership = await service.create(
            organization_id=organization.id,
            person_id=person_id,
            role_id=ROLE_ATHLETE,
        )

        assert membership.role_id == ROLE_ATHLETE

    @pytest.mark.asyncio
    async def test_create_membership_coordinator(self, async_db, organization, user, person_id):
        """Criar membership de coordenador."""
        service = MembershipService(async_db)

        membership = await service.create(
            organization_id=organization.id,
            person_id=person_id,
            role_id=ROLE_COORDINATOR,
        )

        assert membership.role_id == ROLE_COORDINATOR


class TestMembershipServiceRead:
    """Testes de leitura de memberships."""

    @pytest.mark.asyncio
    async def test_list_memberships(self, async_db, membership):
        """Listar memberships."""
        service = MembershipService(async_db)
        memberships, total = await service.list_memberships(
            organization_id=membership.organization_id
        )

        assert len(memberships) >= 1
        assert any(m.id == membership.id for m in memberships)

    @pytest.mark.asyncio
    async def test_list_memberships_by_organization(self, async_db, membership, organization):
        """Listar memberships por organização."""
        service = MembershipService(async_db)
        memberships, total = await service.list_memberships(organization_id=organization.id)

        assert len(memberships) >= 1
        assert all(str(m.organization_id) == str(organization.id) for m in memberships)

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, async_db, membership):
        """Buscar membership por ID existente."""
        service = MembershipService(async_db)
        found = await service.get_by_id(membership.id)

        assert found is not None
        assert found.id == membership.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, async_db):
        """Buscar membership por ID inexistente."""
        service = MembershipService(async_db)
        found = await service.get_by_id(uuid4())

        assert found is None


class TestMembershipServiceGetActive:
    """Testes de busca por membership ativo."""

    @pytest.mark.asyncio
    async def test_get_active_by_user_found(self, async_db, membership, person_id):
        """Buscar membership ativo por person."""
        service = MembershipService(async_db)
        active = await service.get_active_by_person(person_id)

        assert active is not None
        assert str(active.person_id) == str(person_id)

    @pytest.mark.asyncio
    async def test_get_active_by_user_not_found(self, async_db):
        """Buscar membership ativo para person sem vínculo."""
        service = MembershipService(async_db)
        active = await service.get_active_by_person(uuid4())

        assert active is None


class TestMembershipServiceEnd:
    """Testes de encerramento de membership."""

    @pytest.mark.skip(reason="end_membership não implementado no service V1.2")
    @pytest.mark.asyncio
    async def test_end_membership_success(self, async_db, membership):
        """Encerrar membership."""
        service = MembershipService(async_db)

        ended = await service.end_membership(membership.id)

        assert ended is not None
        assert ended.end_at is not None

    @pytest.mark.skip(reason="end_membership não implementado no service V1.2")
    @pytest.mark.asyncio
    async def test_end_membership_not_found(self, async_db):
        """Encerrar membership inexistente retorna None."""
        service = MembershipService(async_db)

        result = await service.end_membership(uuid4())

        assert result is None
