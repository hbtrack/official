"""
WebSocket Connection Manager com métricas Prometheus.

Step 12: Gerenciamento de conexões WebSocket para notificações em tempo real.
Inclui métricas para monitoramento via Prometheus/Grafana.
"""

import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from prometheus_client import Counter, Gauge, Histogram

from app.core.config import settings


# ═══════════════════════════════════════════════════════════════════
# Métricas Prometheus
# ═══════════════════════════════════════════════════════════════════

# Gauge: número de conexões ativas
active_connections_gauge = Gauge(
    'websocket_active_connections',
    'Number of active WebSocket connections',
    ['user_id']
)

# Counter: total de reconexões
reconnections_counter = Counter(
    'websocket_reconnections_total',
    'Total number of WebSocket reconnections'
)

# Histogram: latência de entrega de mensagens (em segundos)
message_latency_histogram = Histogram(
    'websocket_message_latency_seconds',
    'Latency of WebSocket message delivery',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# Counter: falhas de handshake
handshake_failures_counter = Counter(
    'websocket_handshake_failures_total',
    'Total number of WebSocket handshake failures',
    ['reason']
)

# Gauge: contagem total de conexões (sem labels)
total_connections_gauge = Gauge(
    'websocket_total_connections',
    'Total number of active WebSocket connections'
)


# ═══════════════════════════════════════════════════════════════════
# Connection Manager
# ═══════════════════════════════════════════════════════════════════

class ConnectionManager:
    """
    Gerenciador de conexões WebSocket com suporte a múltiplas conexões por usuário.
    
    Features:
    - Múltiplas conexões por usuário (multi-device)
    - Métricas Prometheus para monitoramento
    - Cleanup automático de conexões mortas
    - Broadcast para usuários e organizações
    """
    
    def __init__(self):
        # Dict: user_id → list[WebSocket]
        self.active_connections: Dict[UUID, List[WebSocket]] = defaultdict(list)
        # Lock para thread safety
        self._lock = asyncio.Lock()
    
    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        """
        Adiciona nova conexão WebSocket para usuário.
        
        Args:
            user_id: UUID do usuário
            websocket: Instância WebSocket
        """
        async with self._lock:
            await websocket.accept()
            self.active_connections[user_id].append(websocket)
            
            # Atualizar métricas
            active_connections_gauge.labels(user_id=str(user_id)).set(
                len(self.active_connections[user_id])
            )
            total_connections_gauge.set(self._count_total_connections())
    
    async def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        """
        Remove conexão WebSocket de usuário.
        
        Args:
            user_id: UUID do usuário
            websocket: Instância WebSocket a remover
        """
        async with self._lock:
            if user_id in self.active_connections:
                try:
                    self.active_connections[user_id].remove(websocket)
                except ValueError:
                    pass  # Conexão já foi removida
                
                # Limpar entry se lista vazia
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    active_connections_gauge.labels(user_id=str(user_id)).set(0)
                else:
                    active_connections_gauge.labels(user_id=str(user_id)).set(
                        len(self.active_connections[user_id])
                    )
                
                total_connections_gauge.set(self._count_total_connections())
    
    async def send_to_user(self, user_id: UUID, message: dict) -> None:
        """
        Envia mensagem para todas as conexões de um usuário.
        
        Args:
            user_id: UUID do usuário destinatário
            message: Dict a ser enviado como JSON
        """
        if user_id not in self.active_connections:
            return
        
        start_time = datetime.now(timezone.utc)
        
        # Lista de conexões mortas para remover
        dead_connections = []
        
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(message)
            except WebSocketDisconnect:
                dead_connections.append(websocket)
            except Exception:
                dead_connections.append(websocket)
        
        # Remover conexões mortas
        for dead_ws in dead_connections:
            await self.disconnect(user_id, dead_ws)
        
        # Registrar latência
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        message_latency_histogram.observe(elapsed)
    
    async def broadcast_to_org(self, org_id: UUID, message: dict) -> None:
        """
        Envia mensagem para todos os usuários de uma organização.
        
        Args:
            org_id: UUID da organização
            message: Dict a ser enviado como JSON
        
        Note:
            Requer consulta ao banco para buscar user_ids da org.
            Usar com moderação para evitar overhead.
        """
        # TODO: Implementar quando necessário
        # Requer query: SELECT DISTINCT user_id FROM org_memberships WHERE organization_id = org_id
        pass
    
    def get_connection_count(self, user_id: UUID) -> int:
        """
        Retorna número de conexões ativas de um usuário.
        
        Args:
            user_id: UUID do usuário
        
        Returns:
            Número de conexões ativas
        """
        return len(self.active_connections.get(user_id, []))
    
    async def cleanup_dead_connections(self) -> int:
        """
        Remove conexões WebSocket que estão fechadas/mortas.
        
        Returns:
            Número de conexões removidas
        """
        removed_count = 0
        
        async with self._lock:
            for user_id in list(self.active_connections.keys()):
                connections = self.active_connections[user_id]
                alive_connections = []
                
                for ws in connections:
                    # Verificar se WebSocket está vivo
                    try:
                        # Tentar enviar ping
                        await ws.send_json({"type": "ping"})
                        alive_connections.append(ws)
                    except Exception:
                        # Conexão morta
                        removed_count += 1
                
                if alive_connections:
                    self.active_connections[user_id] = alive_connections
                    active_connections_gauge.labels(user_id=str(user_id)).set(
                        len(alive_connections)
                    )
                else:
                    # Nenhuma conexão viva, remover user
                    del self.active_connections[user_id]
                    active_connections_gauge.labels(user_id=str(user_id)).set(0)
            
            total_connections_gauge.set(self._count_total_connections())
        
        return removed_count
    
    def _count_total_connections(self) -> int:
        """Conta total de conexões ativas (todas os usuários)."""
        return sum(len(connections) for connections in self.active_connections.values())
    
    def register_reconnection(self) -> None:
        """Registra métrica de reconexão."""
        reconnections_counter.inc()
    
    def register_handshake_failure(self, reason: str) -> None:
        """
        Registra falha de handshake.
        
        Args:
            reason: Motivo da falha (invalid_token, expired_token, etc)
        """
        handshake_failures_counter.labels(reason=reason).inc()


# Singleton global
connection_manager = ConnectionManager()
