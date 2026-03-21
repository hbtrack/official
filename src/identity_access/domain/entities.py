"""
Entidades do módulo identity_access.
Derivadas de:
  - contracts/schemas/identity_access/auth_session.schema.json
  - docs/hbtrack/modulos/identity_access/DOMAIN_RULES_IDENTITY_ACCESS.md
  - docs/hbtrack/modulos/identity_access/INVARIANTS_IDENTITY_ACCESS.md

Boundary: este módulo NÃO modela perfil esportivo, dados clínicos ou posição.
DR-IAM-002: principalUserId referencia o módulo users — não duplicar atributos de perfil.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Optional


class RoleLabel(StrEnum):
    """5 roles canônicos — ADR-008."""
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    COACH = "coach"
    ATHLETE = "athlete"
    MEMBER = "member"


@dataclass
class AuthSession:
    """
    Sessão autenticada do usuário.
    Módulo: identity_access
    Contrato: contracts/schemas/identity_access/auth_session.schema.json
    INV-IAM-001: id, principalUserId e sessionScopeLabel são obrigatórios.
    """
    id: uuid.UUID
    principal_user_id: uuid.UUID
    session_scope_label: str
    role_labels: list[str] = field(default_factory=list)
    auth_method_label: Optional[str] = None
    mfa_required: Optional[bool] = None
    mfa_satisfied: Optional[bool] = None
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None

    def is_active(self) -> bool:
        """Sessão ativa = não revogada e não expirada."""
        from datetime import timezone
        now = datetime.now(tz=timezone.utc)
        if self.revoked_at is not None:
            return False
        if self.expires_at is not None and self.expires_at < now:
            return False
        return True

    def validate_invariants(self) -> None:
        """
        Enforce INVARIANTS_IDENTITY_ACCESS.md.
        INV-IAM-001: campos obrigatórios presentes.
        INV-IAM-002: roleLabels sem duplicatas.
        INV-IAM-003: issuedAt < expiresAt; revokedAt >= issuedAt quando presente.
        INV-IAM-004: nenhum campo de perfil físico nesta entidade.
        """
        if not self.session_scope_label or len(self.session_scope_label) > 80:
            raise ValueError(
                "INV-IAM-001: sessionScopeLabel obrigatório e máx 80 chars."
            )
        if len(self.role_labels) != len(set(self.role_labels)):
            raise ValueError("INV-IAM-002: roleLabels não pode ter duplicatas.")
        if self.issued_at and self.expires_at and self.issued_at >= self.expires_at:
            raise ValueError("INV-IAM-003: issuedAt deve ser anterior a expiresAt.")
        if self.issued_at and self.revoked_at and self.revoked_at < self.issued_at:
            raise ValueError("INV-IAM-003: revokedAt deve ser >= issuedAt.")


@dataclass
class UserRoleBinding:
    """
    Binding de role RBAC para um usuário.
    Módulo: identity_access
    DR-IAM-001: atribuição e revogação de role são soberania de identity_access.
    DR-IAM-003: roleLabel é contexto técnico — nunca derivado de posição esportiva.
    """
    id: uuid.UUID
    user_id: uuid.UUID
    role_label: str

    def validate_invariants(self) -> None:
        canonical = {r.value for r in RoleLabel}
        if self.role_label not in canonical:
            raise ValueError(
                f"DR-IAM-003: roleLabel '{self.role_label}' não é canônico. "
                f"Valores válidos: {canonical}"
            )
