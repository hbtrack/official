"""
Router Notifications - Endpoints REST e WebSocket para notificações em tempo real.

Steps 13 e 14: WebSocket stream + REST endpoints para notificações.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.core.auth import ExecutionContext
from app.core.security import decode_access_token
from app.api.v1.deps.auth import get_current_context
from app.services.notification_service import NotificationService
from app.schemas.notifications import NotificationResponse, NotificationListResponse
from app.core.websocket_manager import connection_manager
from app.core.config import settings

import asyncio


router = APIRouter()


# ═══════════════════════════════════════════════════════════════════
# WebSocket Stream (Step 13)
# ═══════════════════════════════════════════════════════════════════

@router.websocket("/stream")
async def websocket_notifications_stream(
    websocket: WebSocket,
    token: str = Query(..., description="JWT token para autenticação"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Stream de notificações em tempo real via WebSocket.
    
    Fluxo:
    1. Cliente conecta com ?token={jwt}
    2. Servidor valida token e extrai user_id
    3. Servidor envia notificações não lidas automaticamente
    4. Loop infinito aguardando heartbeat do client
    5. Servidor envia notificações quando NotificationService.broadcast_to_user() é chamado
    
    Mensagens enviadas:
    - {"type": "initial", "notifications": [...]} - ao conectar
    - {"type": "notification", "data": {...}} - nova notificação
    - {"type": "pong"} - resposta ao ping do client
    
    Mensagens recebidas:
    - {"type": "ping"} - heartbeat do client
    """
    user_id = None
    
    try:
        # Validar token
        try:
            payload = decode_access_token(token)
            user_id = payload.get("user_id")
            if not user_id:
                connection_manager.register_handshake_failure("missing_user_id")
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        except Exception as e:
            connection_manager.register_handshake_failure("invalid_token")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Conectar WebSocket
        await connection_manager.connect(user_id, websocket)
        
        # Step 13: Enviar notificações não lidas automaticamente ao conectar
        service = NotificationService(db)
        unread_notifications = await service.get_unread(user_id, limit=50)
        
        initial_message = {
            "type": "initial",
            "notifications": [
                {
                    "id": str(n.id),
                    "type": n.type,
                    "message": n.message,
                    "notification_data": n.notification_data,
                    "is_read": n.is_read,
                    "read_at": n.read_at.isoformat() if n.read_at else None,
                    "created_at": n.created_at.isoformat(),
                }
                for n in unread_notifications
            ]
        }
        await websocket.send_json(initial_message)
        
        # Loop infinito aguardando mensagens do client (heartbeat)
        while True:
            try:
                # Aguardar mensagem do client com timeout
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=settings.WEBSOCKET_HEARTBEAT_INTERVAL * 2
                )
                
                # Processar heartbeat
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                
            except asyncio.TimeoutError:
                # Cliente não enviou heartbeat, desconectar
                break
            except WebSocketDisconnect:
                break
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        # Log erro mas não quebrar
        pass
    finally:
        # Desconectar WebSocket
        if user_id:
            await connection_manager.disconnect(user_id, websocket)


# ═══════════════════════════════════════════════════════════════════
# REST Endpoints (Step 14)
# ═══════════════════════════════════════════════════════════════════

@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    unread_only: bool = Query(False, description="Retornar apenas não lidas"),
    page: int = Query(1, ge=1, description="Página (1-indexed)"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Lista notificações do usuário logado com paginação.
    
    Query params:
    - unread_only: bool (default False)
    - page: int (default 1)
    - limit: int (default 50, max 100)
    
    Returns:
        NotificationListResponse com items, total, unread_count, page, limit
    """
    service = NotificationService(db)
    notifications, total, unread_count = await service.get_all(
        user_id=ctx.user_id,
        page=page,
        limit=limit,
        unread_only=unread_only,
    )
    
    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        unread_count=unread_count,
        page=page,
        limit=limit,
    )


@router.patch("/{notification_id}/read", response_model=dict)
async def mark_notification_as_read(
    notification_id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Marca notificação como lida.
    
    Returns:
        {"success": true}
    """
    from uuid import UUID
    
    try:
        notification_uuid = UUID(notification_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid_notification_id")
    
    service = NotificationService(db)
    notification = await service.mark_as_read(notification_uuid)
    
    if not notification:
        raise HTTPException(status_code=404, detail="notification_not_found")
    
    # Verificar ownership
    if notification.user_id != ctx.user_id:
        raise HTTPException(status_code=403, detail="not_your_notification")
    
    await db.commit()
    
    return {"success": True}


@router.post("/read-all", response_model=dict)
async def mark_all_notifications_as_read(
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Marca todas as notificações do usuário logado como lidas.
    
    Returns:
        {"success": true, "count": <número de notificações marcadas>}
    """
    service = NotificationService(db)
    count = await service.mark_all_as_read(ctx.user_id)
    await db.commit()
    
    return {"success": True, "count": count}
