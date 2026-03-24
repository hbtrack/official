"""
WebSocket Consumer — módulo notifications
Entrega notificações em tempo real para usuários conectados.
Canal: notifications.<user_id>
"""
from __future__ import annotations

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope.get("user_id")
        if not user_id:
            await self.close(code=4001)
            return
        self.group_name = f"notifications.{user_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name, self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        # Clientes só recebem; não enviam mensagens por este canal.
        pass

    async def notification_message(self, event):
        """Handler para mensagens enviadas ao grupo via channel_layer."""
        await self.send(text_data=json.dumps(event["payload"]))
