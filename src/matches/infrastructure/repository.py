from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from matches.domain.entities import Match
from matches.infrastructure.models import MatchModel


def _to_domain(m: MatchModel) -> Match:
    return Match(
        id=m.id,
        competition_id=m.competition_id,
        home_team_id=m.home_team_id,
        away_team_id=m.away_team_id,
        status_label=m.status_label,
        venue_label=m.venue_label,
        scheduled_at=m.scheduled_at,
        started_at=m.started_at,
        ended_at=m.ended_at,
        home_score=m.home_score,
        away_score=m.away_score,
        referee_names=list(m.referee_names or []),
        lineup_user_ids=[uuid.UUID(str(uid)) for uid in (m.lineup_user_ids or [])],
        official_incident_ids=[uuid.UUID(str(iid)) for iid in (m.official_incident_ids or [])],
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class MatchRepository:
    def save(self, match: Match) -> Match:
        obj, _ = MatchModel.objects.update_or_create(
            id=match.id,
            defaults={
                "competition_id": match.competition_id,
                "home_team_id": match.home_team_id,
                "away_team_id": match.away_team_id,
                "status_label": match.status_label,
                "venue_label": match.venue_label,
                "scheduled_at": match.scheduled_at,
                "started_at": match.started_at,
                "ended_at": match.ended_at,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "referee_names": match.referee_names,
                "lineup_user_ids": [str(u) for u in match.lineup_user_ids],
                "official_incident_ids": [str(i) for i in match.official_incident_ids],
            },
        )
        return _to_domain(obj)

    def get_by_id(self, match_id: uuid.UUID) -> Optional[Match]:
        try:
            return _to_domain(MatchModel.objects.get(id=match_id))
        except MatchModel.DoesNotExist:
            return None

    def list_matches(
        self,
        competition_id: Optional[uuid.UUID] = None,
        status_label: Optional[str] = None,
        home_team_id: Optional[uuid.UUID] = None,
        away_team_id: Optional[uuid.UUID] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Match], int]:
        qs = MatchModel.objects.all()
        if competition_id:
            qs = qs.filter(competition_id=competition_id)
        if status_label:
            qs = qs.filter(status_label=status_label)
        if home_team_id:
            qs = qs.filter(home_team_id=home_team_id)
        if away_team_id:
            qs = qs.filter(away_team_id=away_team_id)
        total = qs.count()
        offset = (page - 1) * page_size
        items = list(qs.order_by("-scheduled_at")[offset : offset + page_size])
        return [_to_domain(m) for m in items], total
