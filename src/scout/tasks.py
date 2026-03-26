"""
Tasks Celery — módulo scout.
Consolidação assíncrona de relatórios de scouting.
"""
from __future__ import annotations

from celery import shared_task


@shared_task(name="scout.consolidate_match_report", bind=True, max_retries=3)
def consolidate_match_report(self, match_id: str) -> dict:
    """
    Consolida todos os ScoutEvents de uma partida em um sumário agregado.
    match_id: UUID da partida cujos eventos devem ser consolidados.
    """
    from uuid import UUID
    from scout.infrastructure.models import ScoutEventModel

    try:
        events_qs = ScoutEventModel.objects.filter(match_id=UUID(match_id))
        count = events_qs.count()

        # Agrupa por event_label para o sumário
        from django.db.models import Count
        breakdown = list(
            events_qs.values("event_label")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        return {
            "status": "consolidated",
            "match_id": match_id,
            "total_events": count,
            "breakdown": breakdown,
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries))
