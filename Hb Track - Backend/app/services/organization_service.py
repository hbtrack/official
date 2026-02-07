"""
Service Organization - Lógica de negócio para organizações.
Regras: R34, R29, RDB4
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.schemas.rbac import OrganizationCreate, OrganizationUpdate


class OrganizationService:
    """
    Service para operações de Organization.

    Regras:
    - R34: Clube único (V1 simplificado)
    - R29: Sem delete físico
    - RDB4: Soft delete com deleted_at
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_organizations(
        self,
        *,
        page: int = 1,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> tuple[list[Organization], int]:
        """Lista organizações com paginação."""
        query = select(Organization)

        if not include_deleted:
            query = query.where(Organization.deleted_at.is_(None))

        # Count - usar with_only_columns para evitar produto cartesiano
        count_query = query.with_only_columns(func.count()).order_by(None)
        total = await self.db.scalar(count_query) or 0

        # Paginate
        query = query.order_by(Organization.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        results = await self.db.scalars(query)
        return list(results.all()), total

    async def get_by_id(
        self,
        org_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> Optional[Organization]:
        """Busca organização por ID."""
        org = await self.db.get(Organization, str(org_id))
        if org and not include_deleted and org.deleted_at is not None:
            return None
        return org

    async def get_by_name(self, name: str) -> Optional[Organization]:
        """Busca organização por nome."""
        query = select(Organization).where(
            Organization.name == name,
            Organization.deleted_at.is_(None),
        )
        return await self.db.scalar(query)

    async def create(
        self,
        data: OrganizationCreate,
        *,
        owner_user_id: UUID,
    ) -> Organization:
        """
        Cria nova organização.

        Args:
            data: Dados da organização
            owner_user_id: ID do usuário proprietário (para futuro vínculo org_membership)

        Regras: R34
        """
        # Nota: O modelo Organization só tem os campos: id, name, created_at, updated_at, deleted_at, deleted_reason
        # O owner_user_id será usado para criar o org_membership posteriormente (RF1.1)
        org = Organization(
            name=data.name,
        )
        self.db.add(org)
        await self.db.flush()
        
        # TODO: Criar org_membership para owner_user_id como Dirigente (RF1.1)
        # Isso será implementado quando o modelo OrgMembership estiver disponível
        
        return org

    async def update(
        self,
        org: Organization,
        data: OrganizationUpdate,
    ) -> Organization:
        """
        Atualiza organização.

        Raises:
            ValueError("organization_deleted"): se já foi soft-deleted
        """
        if org.deleted_at is not None:
            raise ValueError("organization_deleted")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(org, field):
                setattr(org, field, value)

        await self.db.flush()
        return org

    async def soft_delete(
        self,
        org: Organization,
        *,
        reason: Optional[str] = None,
    ) -> Organization:
        """
        Soft delete (RDB4).

        Args:
            org: Organização a deletar
            reason: Motivo do delete (opcional)

        Regras: R29 - sem delete físico
        """
        if org.deleted_at is not None:
            raise ValueError("already_deleted")

        org.deleted_at = datetime.now(timezone.utc)
        org.deleted_reason = reason
        await self.db.flush()
        return org

    async def restore(self, org: Organization) -> Organization:
        """
        Restaura organização soft-deleted.

        Raises:
            ValueError("not_deleted"): se não estava deletada
        """
        if org.deleted_at is None:
            raise ValueError("not_deleted")

        org.deleted_at = None
        org.deleted_reason = None
        await self.db.flush()
        return org

    async def change_status(
        self,
        org: Organization,
        new_status: str,
    ) -> Organization:
        """
        Altera status da organização.

        Args:
            new_status: 'ativo', 'inativo', 'arquivado'

        Raises:
            ValueError("invalid_status"): se status inválido
            ValueError("organization_deleted"): se já foi deletada
        """
        valid_statuses = {"ativo", "inativo", "arquivado"}
        if new_status not in valid_statuses:
            raise ValueError("invalid_status")

        if org.deleted_at is not None:
            raise ValueError("organization_deleted")

        org.status = new_status
        await self.db.flush()
        return org
