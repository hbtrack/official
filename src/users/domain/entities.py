"""
Domain entities — módulo users.
Contrato: contracts/schemas/users/user_profile.schema.json
Invariantes: docs/hbtrack/modulos/users/INVARIANTS_USERS.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID


class UserStatus(StrEnum):
    """
    Lifecycle status do UserProfile (DEC-USERS-002).
    x-domain-enum-ref: user_account_status
    """
    ACTIVE = "ACTIVE"
    PENDING_ACTIVATION = "PENDING_ACTIVATION"
    SUSPENDED = "SUSPENDED"


class RoleLabel(StrEnum):
    """
    5 atores canônicos do sistema (ADR-008).
    Papel funcional/esportivo — não confundir com JWT roles (identity_access).
    DR-USR-002 / DR-USR-004.
    """
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    COACH = "coach"
    ATHLETE = "athlete"
    MEMBER = "member"


@dataclass
class UserProfile:
    """
    Entidade central do módulo users.
    Módulo: users
    Contrato: contracts/schemas/users/user_profile.schema.json
    Boundary: credenciais, sessão e JWT nunca pertencem a esta entidade (INV-USR-003, INV-USR-004).
    """
    id: UUID
    display_name: str
    role_label: RoleLabel

    # Opcional
    organization_id: UUID | None = None
    first_name: str | None = None
    last_name: str | None = None
    status_label: UserStatus = UserStatus.PENDING_ACTIVATION
    position_label: str | None = None
    preferred_language: str | None = None
    preference_tags: list[str] = field(default_factory=list)
    team_ids: list[UUID] = field(default_factory=list)
    season_ids: list[UUID] = field(default_factory=list)

    def validate_invariants(self) -> None:
        """
        Enforce invariantes conforme INVARIANTS_USERS.md.
        Nunca chamar no router; chamar nos use cases.
        """
        # INV-USR-001: id, displayName, roleLabel obrigatórios
        if not self.id:
            raise ValueError("INV-USR-001: id é obrigatório")
        if not self.display_name or not self.display_name.strip():
            raise ValueError("INV-USR-001: displayName é obrigatório")
        if not self.role_label:
            raise ValueError("INV-USR-001: roleLabel é obrigatório")

        # INV-USR-001: roleLabel deve ser um dos 5 canônicos
        if self.role_label not in list(RoleLabel):
            raise ValueError(f"INV-USR-001: roleLabel '{self.role_label}' inválido — usar: {list(RoleLabel)}")

        # INV-USR-002: conjuntos sem duplicidade
        if len(self.team_ids) != len(set(self.team_ids)):
            raise ValueError("INV-USR-002: teamIds deve ter uniqueItems")
        if len(self.season_ids) != len(set(self.season_ids)):
            raise ValueError("INV-USR-002: seasonIds deve ter uniqueItems")
        if len(self.preference_tags) != len(set(self.preference_tags)):
            raise ValueError("INV-USR-002: preferenceTags deve ter uniqueItems")

        # INV-USR-003: campos de authn nunca permitidos (verificado pelo schema boundary, mas defensivo)
        # (Este campo não existe no dataclass por design — boundary enforced estruturalmente)
