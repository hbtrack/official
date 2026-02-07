"""
Service PasswordReset - Lógica de negócio para tokens de recuperação de senha.

Responsabilidades:
- Criar tokens de reset/welcome
- Validar tokens
- Marcar tokens como utilizados
- Limpar tokens expirados
"""

import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset import PasswordReset
from app.models.user import User


class PasswordResetService:
    """
    Service para operações de PasswordReset.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_reset_token(
        self,
        user_id: UUID,
        token_type: str = "reset",
        expires_in_hours: int = 1,
    ) -> PasswordReset:
        """
        Cria um novo token de reset/welcome.

        Args:
            user_id: ID do usuário
            token_type: 'reset' ou 'welcome'
            expires_in_hours: Horas até expiração

        Returns:
            PasswordReset object
        """
        # Gerar token seguro
        token = secrets.token_urlsafe(32)

        # Calcular expiração
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)

        # Invalidar tokens anteriores do mesmo tipo
        stmt = select(PasswordReset).where(
            PasswordReset.user_id == str(user_id),
            PasswordReset.token_type == token_type,
            PasswordReset.used == False,
            PasswordReset.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        old_tokens = result.scalars().all()
        for old_token in old_tokens:
            old_token.deleted_at = datetime.now(timezone.utc)
            old_token.deleted_reason = "new_token_created"
        await self.db.commit()

        # Criar novo token
        reset = PasswordReset(
            user_id=str(user_id),
            token=token,
            token_type=token_type,
            expires_at=expires_at,
            used=False,
        )

        self.db.add(reset)
        await self.db.commit()
        await self.db.refresh(reset)

        return reset

    async def get_by_token(
        self,
        token: str,
        *,
        include_expired: bool = False,
        include_used: bool = False,
    ) -> Optional[PasswordReset]:
        """
        Busca um token de reset.

        Args:
            token: Token para buscar
            include_expired: Incluir tokens expirados
            include_used: Incluir tokens já utilizados

        Returns:
            PasswordReset or None
        """
        query = select(PasswordReset).where(
            PasswordReset.token == token,
            PasswordReset.deleted_at.is_(None),
        )

        if not include_used:
            query = query.where(PasswordReset.used == False)

        if not include_expired:
            query = query.where(
                PasswordReset.expires_at > datetime.now(timezone.utc)
            )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def mark_as_used(self, reset: PasswordReset) -> PasswordReset:
        """
        Marca um token como utilizado.

        Args:
            reset: PasswordReset object

        Returns:
            Updated PasswordReset
        """
        reset.used = True
        reset.used_at = datetime.now(timezone.utc)
        reset.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(reset)
        return reset

    async def cleanup_expired_tokens(self, days_to_keep: int = 30) -> int:
        """
        Remove tokens expirados (soft delete).

        Args:
            days_to_keep: Manter registros dos últimos N dias

        Returns:
            Número de tokens deletados
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

        stmt = select(PasswordReset).where(
            PasswordReset.expires_at < cutoff_date,
            PasswordReset.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        expired_tokens = result.scalars().all()
        count = 0
        for token in expired_tokens:
            token.deleted_at = datetime.now(timezone.utc)
            token.deleted_reason = "expired_cleanup"
            count += 1

        await self.db.commit()
        return count
