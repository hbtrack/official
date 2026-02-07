"""
Router Metrics - Endpoint para métricas Prometheus.

Step 15: Expor métricas do sistema para scraping Prometheus/Grafana.
"""

from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST


router = APIRouter()


@router.get("/metrics")
async def prometheus_metrics():
    """
    Endpoint de métricas Prometheus.
    
    Expõe métricas:
    - websocket_active_connections (gauge por user_id)
    - websocket_total_connections (gauge)
    - websocket_reconnections_total (counter)
    - websocket_message_latency_seconds (histogram)
    - websocket_handshake_failures_total (counter por reason)
    
    Segurança:
        Endpoint sem autenticação, mas deve ser acessível apenas internamente
        via firewall/network policy (não expor publicamente).
    
    Content-Type:
        text/plain; version=0.0.4; charset=utf-8
    
    Returns:
        Métricas no formato Prometheus
    """
    metrics_output = generate_latest()
    return Response(
        content=metrics_output,
        media_type=CONTENT_TYPE_LATEST,
    )
