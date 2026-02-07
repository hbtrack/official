"""
NotificationService - Gerenciamento de notificações em tempo real.

Step 11: Service para criar, buscar e gerenciar notificações de usuários.
Integração com WebSocket manager para envio em tempo real.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.core.config import settings


class NotificationService:
    """
    Service para gerenciamento de notificações.
    
    Funcionalidades:
    - Criar notificações
    - Marcar como lidas (individual ou todas)
    - Buscar não lidas
    - Buscar com paginação
    - Broadcast via WebSocket (se conectado)
    - Cleanup de notificações antigas
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        user_id: UUID,
        type: str,
        message: str,
        notification_data: Optional[dict] = None,
    ) -> Notification:
        """
        Cria uma notificação.
        
        Args:
            user_id: UUID do usuário destinatário
            type: Tipo da notificação (team_assignment, coach_removal, etc)
            message: Mensagem de texto
            notification_data: Dados adicionais em JSON (opcional)
        
        Returns:
            Notification criada (não commitada)
        """
        notification = Notification(
            user_id=user_id,
            type=type,
            message=message,
            notification_data=notification_data or {},
        )
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification
    
    async def mark_as_read(self, notification_id: UUID) -> Optional[Notification]:
        """
        Marca notificação como lida.
        
        Returns:
            Notification atualizada ou None se não encontrada
        """
        notification = await self.db.get(Notification, notification_id)
        if notification and notification.read_at is None:
            notification.read_at = datetime.now(timezone.utc)
            await self.db.flush()
            await self.db.refresh(notification)
        return notification
    
    async def mark_all_as_read(self, user_id: UUID) -> int:
        """
        Marca todas as notificações não lidas do usuário como lidas.
        
        Returns:
            Número de notificações marcadas
        """
        result = await self.db.execute(
            select(Notification).filter(
                Notification.user_id == user_id,
                Notification.read_at.is_(None)
            )
        )
        notifications = result.scalars().all()
        
        now = datetime.now(timezone.utc)
        count = 0
        for notification in notifications:
            notification.read_at = now
            count += 1
        
        if count > 0:
            await self.db.flush()
        
        return count
    
    async def get_unread(self, user_id: UUID, limit: int = 50) -> list[Notification]:
        """
        Busca notificações não lidas do usuário.
        
        Args:
            user_id: UUID do usuário
            limit: Máximo de notificações (default 50)
        
        Returns:
            Lista de notificações não lidas (mais recentes primeiro)
        """
        result = await self.db.execute(
            select(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.read_at.is_(None)
            )
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_all(
        self,
        user_id: UUID,
        page: int = 1,
        limit: int = 50,
        unread_only: bool = False,
    ) -> tuple[list[Notification], int, int]:
        """
        Busca notificações do usuário com paginação.
        
        Args:
            user_id: UUID do usuário
            page: Página (1-indexed)
            limit: Itens por página
            unread_only: Se True, retorna apenas não lidas
        
        Returns:
            Tupla (notificações, total, unread_count)
        """
        # Query base
        query = select(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.read_at.is_(None))
        
        # Total count
        from sqlalchemy import func
        count_query = select(func.count()).select_from(Notification).filter(
            Notification.user_id == user_id
        )
        if unread_only:
            count_query = count_query.filter(Notification.read_at.is_(None))
        total = await self.db.scalar(count_query) or 0
        
        # Unread count (sempre calcular)
        unread_count_query = select(func.count()).select_from(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.read_at.is_(None)
            )
        )
        unread_count = await self.db.scalar(unread_count_query) or 0
        
        # Paginação
        offset = (page - 1) * limit
        query = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        notifications = list(result.scalars().all())
        
        return notifications, total, unread_count
    
    async def broadcast_to_user(self, user_id: UUID, notification: Notification) -> None:
        """
        Envia notificação via WebSocket se usuário estiver conectado.
        
        Args:
            user_id: UUID do usuário
            notification: Notification a enviar
        
        Note:
            Lazy import do ConnectionManager para evitar dependência circular.
            Se WebSocket não estiver disponível, falha silenciosamente.
        """
        try:
            from app.core.websocket_manager import connection_manager
            
            message = {
                "type": "notification",
                "data": {
                    "id": str(notification.id),
                    "type": notification.type,
                    "message": notification.message,
                    "notification_data": notification.notification_data,
                    "is_read": notification.is_read,
                    "read_at": notification.read_at.isoformat() if notification.read_at else None,
                    "created_at": notification.created_at.isoformat(),
                }
            }
            
            await connection_manager.send_to_user(user_id, message)
        except Exception as e:
            # Falha silenciosa se WebSocket não disponível
            # Usuário receberá ao reconectar ou via polling
            pass
    
    async def cleanup_old_notifications(self) -> int:
        """
        Deleta notificações lidas com read_at > NOTIFICATION_RETENTION_DAYS.
        
        Returns:
            Número de notificações deletadas
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=settings.NOTIFICATION_RETENTION_DAYS)
        
        result = await self.db.execute(
            select(Notification).filter(
                and_(
                    Notification.read_at.isnot(None),
                    Notification.read_at < cutoff_date
                )
            )
        )
        notifications_to_delete = result.scalars().all()
        
        count = 0
        for notification in notifications_to_delete:
            await self.db.delete(notification)
            count += 1
        
        if count > 0:
            await self.db.flush()
        
        return count
    
    async def broadcast_permissions_changed(
        self,
        user_id: UUID,
        permissions: dict[str, bool],
        reason: Optional[str] = None
    ) -> None:
        """
        Envia evento permissions-changed via WebSocket.
        
        Step 4: Enviar evento quando permissões mudam (role alterado).
        
        Args:
            user_id: UUID do usuário
            permissions: Dict de permissões atualizadas
            reason: Razão opcional da mudança (ex: "role_changed_to_coordenador")
        
        Note:
            Frontend escutará este evento e invalidará cache de permissões.
        """
        try:
            from app.core.websocket_manager import connection_manager
            
            message = {
                "type": "permissions-changed",
                "data": {
                    "user_id": str(user_id),
                    "permissions": permissions,
                    "reason": reason,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            }
            
            await connection_manager.send_to_user(user_id, message)
        except Exception as e:
            # Falha silenciosa se WebSocket não disponível
            # Permissões serão atualizadas no próximo login ou refetch manual
            pass
