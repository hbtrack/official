"""
Service para gerenciamento de Roles (Papéis).

Regras RAG aplicadas:
- R4: Papéis do sistema são fixos (catálogo)
- R25/R26: Permissões por papel e escopo
"""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import ExecutionContext
from app.core.exceptions import NotFoundError
from app.models.role import Role

logger = logging.getLogger(__name__)

# Catálogo de papéis V1 (R4)
ROLE_CATALOG = {
    1: {"id": 1, "name": "dirigente", "description": "Gestão administrativa do clube"},
    2: {"id": 2, "name": "coordenador", "description": "Coordenação técnica de equipes"},
    3: {"id": 3, "name": "treinador", "description": "Gestão de treinos e atletas"},
    4: {"id": 4, "name": "atleta", "description": "Acesso aos próprios dados"},
}


class RoleService:
    """
    Service de Roles (Papéis).
    Ref: R4, R25/R26
    
    Roles são um catálogo fixo no V1 - não há CRUD completo,
    apenas listagem e busca.
    """

    def __init__(self, db: AsyncSession, context: ExecutionContext):
        self.db = db
        self.context = context

    async def get_all(self) -> list[Role]:
        """
        Lista todos os papéis.
        Ref: R4 - Papéis são fixos
        """
        query = select(Role).order_by(Role.id)
        result = await self.db.execute(query)
        roles = list(result.scalars().all())

        logger.info(f"Listed {len(roles)} roles")
        return roles

    async def get_by_id(self, role_id: int) -> Role:
        """
        Busca papel por ID (smallint).
        Ref: R4
        """
        query = select(Role).where(Role.id == role_id)
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()

        if not role:
            raise NotFoundError(f"Role {role_id} not found")

        return role

    async def get_by_name(self, name: str) -> Optional[Role]:
        """
        Busca papel por nome.
        Ref: R4
        """
        query = select(Role).where(Role.name == name)
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()

        if not role:
            raise NotFoundError(f"Role '{name}' not found")

        return role

    async def get_by_code(self, code: str) -> Optional[Role]:
        """
        Busca papel por código.
        Ref: R4
        """
        query = select(Role).where(Role.code == code)
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()

        if not role:
            raise NotFoundError(f"Role com código '{code}' not found")

        return role

    def get_role_hierarchy(self) -> dict:
        """
        Retorna hierarquia de papéis.
        Ref: R26 - Hierarquia (dirigente > coordenador > treinador > atleta)
        """
        return {
            "dirigente": 4,      # Mais alto
            "coordenador": 3,
            "treinador": 2,
            "atleta": 1,         # Mais baixo
        }

    def is_superior(self, role_a: str, role_b: str) -> bool:
        """
        Verifica se role_a é superior a role_b na hierarquia.
        Ref: R26
        """
        hierarchy = self.get_role_hierarchy()
        return hierarchy.get(role_a, 0) > hierarchy.get(role_b, 0)

    def can_manage(self, manager_role: str, target_role: str) -> bool:
        """
        Verifica se manager_role pode gerenciar target_role.
        Ref: R25/R26 - Permissões por papel
        """
        # SuperAdmin pode tudo
        if self.context.is_superadmin:
            return True

        return self.is_superior(manager_role, target_role)
