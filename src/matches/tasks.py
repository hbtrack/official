"""
Tasks Celery — módulo matches.
Cálculo assíncrono de estatísticas de partida após encerramento.
"""
from __future__ import annotations

from celery import shared_task


@shared_task(name="matches.compute_match_stats", bind=True, max_retries=3)
def compute_match_stats(self, match_id: str) -> dict:
    """
    Consolida estatísticas da partida após encerramento (status COMPLETED).
    match_id: UUID da MatchModel a processar.
    """
    from uuid import UUID
    from matches.infrastructure.models import MatchModel

    try:
        match = MatchModel.objects.get(pk=UUID(match_id))
        if match.status_label != "COMPLETED":
            return {"status": "skipped", "reason": "match not COMPLETED", "match_id": match_id}

        # Consolida home_score/away_score e incidents do JSON
        incidents = match.official_incident_ids or []
        lineup = match.lineup_user_ids or []

        stats = {
            "match_id": match_id,
            "status": "computed",
            "home_score": match.home_score,
            "away_score": match.away_score,
            "incident_count": len(incidents),
            "lineup_size": len(lineup),
        }
        return stats
    except MatchModel.DoesNotExist:
        return {"status": "not_found", "match_id": match_id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries))
