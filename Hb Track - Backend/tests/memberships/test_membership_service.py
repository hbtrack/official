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

    def test_create_membership_success(self, db, organization, user):
        """Criar membership via service."""
        service = MembershipService(db)

        membership = service.create(
            organization_id=organization.id,
            user_id=user.id,
            role_id=ROLE_COACH,
        )

        assert membership.id is not None
        assert membership.role_id == ROLE_COACH

    def test_create_membership_athlete(self, db, organization, user):
        """Criar membership de atleta."""
        service = MembershipService(db)

        membership = service.create(
            organization_id=organization.id,
            user_id=user.id,
            role_id=ROLE_ATHLETE,
        )

        assert membership.role_id == ROLE_ATHLETE

    def test_create_membership_coordinator(self, db, organization, user):
        """Criar membership de coordenador."""
        service = MembershipService(db)

        membership = service.create(
            organization_id=organization.id,
            user_id=user.id,
            role_id=ROLE_COORDINATOR,
        )

        assert membership.role_id == ROLE_COORDINATOR


class TestMembershipServiceRead:
    """Testes de leitura de memberships."""

    def test_list_memberships(self, db, membership):
        """Listar memberships."""
        service = MembershipService(db)
        memberships = service.list_memberships()

        assert len(memberships) >= 1
        assert any(m.id == membership.id for m in memberships)

    def test_list_memberships_by_organization(self, db, membership, organization):
        """Listar memberships por organização."""
        service = MembershipService(db)
        memberships = service.list_memberships(organization_id=organization.id)

        assert len(memberships) >= 1
        assert all(m.organization_id == organization.id for m in memberships)

    def test_get_by_id_found(self, db, membership):
        """Buscar membership por ID existente."""
        service = MembershipService(db)
        found = service.get_by_id(membership.id)

        assert found is not None
        assert found.id == membership.id

    def test_get_by_id_not_found(self, db):
        """Buscar membership por ID inexistente."""
        service = MembershipService(db)
        found = service.get_by_id(uuid4())

        assert found is None


class TestMembershipServiceGetActive:
    """Testes de busca por membership ativo."""

    def test_get_active_by_user_found(self, db, membership, user):
        """Buscar membership ativo por user."""
        service = MembershipService(db)
        active = service.get_active_by_user(user.id)

        assert active is not None
        assert active.user_id == user.id

    def test_get_active_by_user_not_found(self, db):
        """Buscar membership ativo para user sem vínculo."""
        service = MembershipService(db)
        active = service.get_active_by_user(uuid4())

        assert active is None


class TestMembershipServiceEnd:
    """Testes de encerramento de membership."""

    def test_end_membership_success(self, db, membership):
        """Encerrar membership."""
        service = MembershipService(db)

        ended = service.end_membership(membership.id)

        assert ended is not None
        assert ended.is_active is False

    def test_end_membership_not_found(self, db):
        """Encerrar membership inexistente retorna None."""
        service = MembershipService(db)

        result = service.end_membership(uuid4())

        assert result is None
