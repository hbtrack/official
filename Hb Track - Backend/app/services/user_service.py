"""
Service User - Lógica de negócio para usuários.
Regras: R2, R3, R29, RDB4
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.rbac import UserCreate, UserUpdate
from app.core.cache import cache_user, invalidate_user_cache


class UserService:
    """
    Service para operações de User.

    Regras:
    - R2: Autenticação obrigatória
    - R3: Email único
    - R29: Sem delete físico
    - RDB4: Soft delete

    Nota: Relação user ↔ organization é via membership (não há FK direta).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_users(
        self,
        *,
        page: int = 1,
        limit: int = 50,
        include_inactive: bool = False,
        include_deleted: bool = False,
    ) -> tuple[list[User], int]:
        """Lista usuários com paginação."""
        query = select(User)

        if not include_inactive:
            query = query.where(User.status == "ativo")

        if not include_deleted:
            query = query.where(User.deleted_at.is_(None))

        # Count - usar with_only_columns para evitar produto cartesiano
        count_query = query.with_only_columns(func.count()).order_by(None)
        total = await self.db.scalar(count_query) or 0

        # Paginate
        query = query.order_by(User.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        results = await self.db.scalars(query)
        return list(results.all()), total

    @cache_user
    async def get_by_id(
        self,
        user_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> Optional[User]:
        """Busca usuário por ID (com cache)."""
        user = await self.db.get(User, str(user_id))
        if user and not include_deleted and user.deleted_at is not None:
            return None
        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        """Busca usuǭrio por email (R3 - ǧnico)."""
        normalized = _normalize_email(email)
        query = select(User).where(
            func.lower(User.email) == normalized,
            User.deleted_at.is_(None),
        )
        return await self.db.scalar(query)

    async def create(
        self,
        data: UserCreate,
        *,
        person_id: UUID,
        password_hash: Optional[str] = None,
    ) -> User:
        """
        Cria novo usuário.

        Args:
            data: Dados do usuário
            person_id: ID da pessoa associada
            password_hash: Hash da senha (opcional, definido pela camada de auth)

        Regras:
        - R3: Email deve ser único
        - R1: full_name pertence a Person, não a User

        Raises:
            ValueError("email_already_exists"): se email já existe
        """
        # Verificar email único (R3)
        normalized_email = _normalize_email(data.email)
        existing = await self.get_by_email(normalized_email)
        if existing:
            raise ValueError("email_already_exists")

        # R1: User NÃO tem full_name - isso está em Person
        user = User(
            email=normalized_email,
            person_id=str(person_id),
            password_hash=password_hash,
            status="ativo",
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def update(
        self,
        user: User,
        data: UserUpdate,
    ) -> User:
        """
        Atualiza usuário.

        Raises:
            ValueError("user_deleted"): se já foi soft-deleted
            ValueError("email_already_exists"): se email já existe
        """
        if user.deleted_at is not None:
            raise ValueError("user_deleted")

        update_data = data.model_dump(exclude_unset=True)

        # Se email está sendo alterado, verificar unicidade (R3)
        if "email" in update_data and update_data["email"] != user.email:
            normalized_email = _normalize_email(update_data["email"])
            existing = await self.get_by_email(normalized_email)
            if existing:
                raise ValueError("email_already_exists")
            update_data["email"] = normalized_email

        if "full_name" in update_data and update_data["full_name"] is not None:
            update_data["full_name"] = update_data["full_name"].strip()

        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        await self.db.flush()

        # Invalidar cache após update
        invalidate_user_cache(str(user.id))

        return user

    async def change_status(
        self,
        user: User,
        new_status: str,
    ) -> User:
        """
        Altera status do usuário.

        Args:
            new_status: 'ativo', 'inativo', 'arquivado'

        Raises:
            ValueError("invalid_status"): se status inválido
            ValueError("user_deleted"): se já foi deletado
        """
        valid_statuses = {"ativo", "inativo", "arquivado"}
        if new_status not in valid_statuses:
            raise ValueError("invalid_status")

        if user.deleted_at is not None:
            raise ValueError("user_deleted")

        user.status = new_status
        await self.db.flush()

        # Invalidar cache após mudança de status
        invalidate_user_cache(str(user.id))

        return user

    async def lock(self, user: User) -> User:
        """Bloqueia usuário."""
        user.is_locked = True
        await self.db.flush()
        invalidate_user_cache(str(user.id))
        return user

    async def unlock(self, user: User) -> User:
        """Desbloqueia usuário."""
        user.is_locked = False
        await self.db.flush()
        invalidate_user_cache(str(user.id))
        return user

    async def soft_delete(
        self,
        user: User,
        *,
        reason: Optional[str] = None,
    ) -> User:
        """
        Soft delete (RDB4).

        Args:
            user: Usuário a deletar
            reason: Motivo do delete (opcional)

        Regras: R29 - sem delete físico
        """
        if user.deleted_at is not None:
            raise ValueError("already_deleted")

        user.deleted_at = datetime.now(timezone.utc)
        user.deleted_reason = reason
        user.status = "arquivado"
        await self.db.flush()

        # Invalidar cache após soft delete
        invalidate_user_cache(str(user.id))

        return user

    async def restore(self, user: User) -> User:
        """
        Restaura usuário soft-deleted.

        Raises:
            ValueError("not_deleted"): se não estava deletado
        """
        if user.deleted_at is None:
            raise ValueError("not_deleted")

        user.deleted_at = None
        user.deleted_reason = None
        user.status = "ativo"
        await self.db.flush()

        # Invalidar cache após restore
        invalidate_user_cache(str(user.id))

        return user


def _normalize_email(email: str) -> str:
    return email.strip().lower()
