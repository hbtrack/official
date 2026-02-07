"""Testes para contexto de execução"""
import pytest
from uuid import uuid4, UUID
from datetime import datetime
from app.core.context import ExecutionContext, get_mock_context


def test_execution_context_creation():
    """Valida criação de contexto"""
    ctx = ExecutionContext(
        user_id=uuid4(),
        person_id=uuid4(),
        membership_id=uuid4(),
        organization_id=uuid4(),
        role_code="coordenador",
        is_superadmin=False,
        request_id=str(uuid4()),
        timestamp=datetime.utcnow()
    )
    assert isinstance(ctx.user_id, UUID)
    assert ctx.role_code == "coordenador"
    assert ctx.is_superadmin is False


def test_superadmin_can_bypass_rules():
    """Valida que superadmin pode ignorar travas (R3)"""
    ctx_super = ExecutionContext(
        user_id=uuid4(),
        person_id=uuid4(),
        membership_id=None,  # Superadmin pode não ter membership (R2)
        organization_id=uuid4(),
        role_code="dirigente",
        is_superadmin=True,
        request_id=str(uuid4()),
        timestamp=datetime.utcnow()
    )
    assert ctx_super.can_bypass_rules() is True

    ctx_normal = ExecutionContext(
        user_id=uuid4(),
        person_id=uuid4(),
        membership_id=uuid4(),
        organization_id=uuid4(),
        role_code="treinador",
        is_superadmin=False,
        request_id=str(uuid4()),
        timestamp=datetime.utcnow()
    )
    assert ctx_normal.can_bypass_rules() is False


def test_has_active_membership():
    """Valida verificação de vínculo ativo (R42, RF3)"""
    # Superadmin sem membership (ok)
    ctx_super = ExecutionContext(
        user_id=uuid4(),
        person_id=uuid4(),
        membership_id=None,
        organization_id=uuid4(),
        role_code="dirigente",
        is_superadmin=True,
        request_id=str(uuid4()),
        timestamp=datetime.utcnow()
    )
    assert ctx_super.has_active_membership() is True

    # Usuário normal com membership (ok)
    ctx_with_membership = ExecutionContext(
        user_id=uuid4(),
        person_id=uuid4(),
        membership_id=uuid4(),
        organization_id=uuid4(),
        role_code="treinador",
        is_superadmin=False,
        request_id=str(uuid4()),
        timestamp=datetime.utcnow()
    )
    assert ctx_with_membership.has_active_membership() is True

    # Usuário normal sem membership (NÃO ok - violaria R42)
    ctx_without_membership = ExecutionContext(
        user_id=uuid4(),
        person_id=uuid4(),
        membership_id=None,
        organization_id=uuid4(),
        role_code="treinador",
        is_superadmin=False,
        request_id=str(uuid4()),
        timestamp=datetime.utcnow()
    )
    assert ctx_without_membership.has_active_membership() is False


def test_to_audit_dict():
    """Valida conversão para dict de auditoria (R31, R32)"""
    ctx = get_mock_context()
    audit_dict = ctx.to_audit_dict()

    assert "actor_user_id" in audit_dict
    assert "actor_person_id" in audit_dict
    assert "actor_role" in audit_dict
    assert "request_id" in audit_dict
    assert "timestamp" in audit_dict
    assert isinstance(audit_dict["timestamp"], str)  # ISO format


def test_get_mock_context():
    """Valida contexto mock para desenvolvimento"""
    ctx = get_mock_context()
    assert ctx.role_code == "coordenador"  # Acesso total (R26)
    assert ctx.has_active_membership() is True
