"""AccessContext — contexto de ator para use cases do módulo training.

Substitui o par solto (actor_role, actor_id) em todos os inputs de use cases.
Preparado na Fase 2 da refatoração; os use cases existentes continuam aceitando
actor_role/actor_id diretamente até a Fase 3, quando migrarão para AccessContext.

Intencionalmente sem imports de Django ou Ninja — camada de domínio pura.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

from ...domain.rules import RoleLabel, STAFF_ROLES


@dataclass(frozen=True)
class AccessContext:
    """Contexto completo de autorização de um ator HTTP autenticado.

    Campos:
        actor_id        -- UUID do usuário autenticado (obtido do JWT).
        role            -- papel canônico do ator (RoleLabel).
        organization_id -- organização principal do ator; pode ser None
                           para superadmins ou tokens de serviço.
        team_ids        -- times aos quais o ator pertence; usado para
                           filtros de visibilidade (Fase 3+).
        athlete_ids     -- perfis de atleta vinculados ao ator; relevante
                           quando role == ATHLETE. Resolvido pela integração
                           com identity_access (TODO Fase 3).
    """

    actor_id: uuid.UUID
    role: RoleLabel
    organization_id: Optional[uuid.UUID] = None
    team_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)
    athlete_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Helpers de consulta (sem lógica de domínio — só conveniência)
    # ------------------------------------------------------------------

    def is_coach(self) -> bool:
        return self.role == RoleLabel.COACH

    def is_athlete(self) -> bool:
        return self.role == RoleLabel.ATHLETE

    def is_staff(self) -> bool:
        return self.role in STAFF_ROLES
