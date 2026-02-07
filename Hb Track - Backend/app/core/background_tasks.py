"""
Background Tasks - Tarefas periódicas do sistema.

Step 17: Cleanup de conexões WebSocket e notificações antigas.
"""

import asyncio
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.websocket_manager import connection_manager
from app.services.notification_service import NotificationService
from app.core.config import settings
from app.core.db import get_async_db


async def cleanup_websocket_connections_task():
    """
    Task periódica para limpar conexões WebSocket mortas.
    Roda a cada WEBSOCKET_CLEANUP_INTERVAL segundos (default: 5 minutos).
    """
    while True:
        try:
            await asyncio.sleep(settings.WEBSOCKET_CLEANUP_INTERVAL)
            
            removed_count = await connection_manager.cleanup_dead_connections()
            
            if removed_count > 0:
                print(f"[WebSocket Cleanup] Removed {removed_count} dead connections at {datetime.now(timezone.utc).isoformat()}")
        
        except Exception as e:
            print(f"[WebSocket Cleanup] Error: {e}")
            # Continuar loop mesmo com erro
            await asyncio.sleep(60)


async def cleanup_old_notifications_task():
    """
    Task periódica para deletar notificações antigas lidas.
    Roda a cada 24 horas.
    Deleta notificações com read_at > NOTIFICATION_RETENTION_DAYS dias.
    """
    while True:
        try:
            # Aguardar 24 horas entre execuções
            await asyncio.sleep(86400)  # 24 * 60 * 60
            
            # Obter sessão do banco
            async for db in get_async_db():
                try:
                    service = NotificationService(db)
                    deleted_count = await service.cleanup_old_notifications()
                    await db.commit()
                    
                    print(f"[Notification Cleanup] Deleted {deleted_count} old notifications at {datetime.now(timezone.utc).isoformat()}")
                finally:
                    await db.close()
                break  # Apenas uma iteração
        
        except Exception as e:
            print(f"[Notification Cleanup] Error: {e}")
            # Continuar loop mesmo com erro
            await asyncio.sleep(3600)  # Tentar novamente em 1 hora


def start_background_tasks():
    """
    Inicia todas as background tasks.
    Deve ser chamado no startup do app em main.py.
    """
    asyncio.create_task(cleanup_websocket_connections_task())
    asyncio.create_task(cleanup_old_notifications_task())
