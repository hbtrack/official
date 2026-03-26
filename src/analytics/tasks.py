"""Tasks Celery — módulo analytics. Cálculo de métricas periódicas."""
from celery import shared_task


@shared_task(name="analytics.compute_metrics")
def compute_metrics(season_id: str) -> dict:
    """Recalcula métricas de performance de uma temporada."""
    # Stub — lógica de cálculo real vai aqui
    return {"status": "computed", "season_id": season_id}


@shared_task(name="analytics.aggregate_daily_stats")
def aggregate_daily_stats() -> dict:
    """Agrega estatísticas diárias de todos os módulos (chamada periódica)."""
    return {"status": "aggregated"}
