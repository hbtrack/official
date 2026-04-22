"""Repositório do agregado AthleteIneligibilityDeclaration."""
from __future__ import annotations

import uuid
from typing import Optional

from ...domain.entities import AthleteIneligibilityDeclaration
from ..models import AthleteIneligibilityDeclarationModel


class AthleteIneligibilityDeclarationRepository:
    def get_by_session_athlete(
        self,
        session_id: uuid.UUID,
        athlete_id: uuid.UUID,
    ) -> Optional[AthleteIneligibilityDeclaration]:
        try:
            return self._to_domain(
                AthleteIneligibilityDeclarationModel.objects.get(
                    session_id=session_id,
                    athlete_id=athlete_id,
                )
            )
        except AthleteIneligibilityDeclarationModel.DoesNotExist:
            return None

    def save(
        self,
        declaration: AthleteIneligibilityDeclaration,
    ) -> AthleteIneligibilityDeclaration:
        m, _ = AthleteIneligibilityDeclarationModel.objects.update_or_create(
            session_id=declaration.session_id,
            athlete_id=declaration.athlete_id,
            defaults={
                "id": declaration.id,
                "reason_flags": declaration.reason_flags,
                "reason_other": declaration.reason_other or "",
                "acknowledged_by_coach": declaration.acknowledged_by_coach,
                "coach_note": declaration.coach_note or "",
                "declared_at": declaration.declared_at,
            },
        )
        return self._to_domain(m)

    def _to_domain(self, m: AthleteIneligibilityDeclarationModel) -> AthleteIneligibilityDeclaration:
        return AthleteIneligibilityDeclaration(
            id=m.id,
            session_id=m.session_id,
            athlete_id=m.athlete_id,
            reason_flags=list(m.reason_flags or []),
            reason_other=m.reason_other or None,
            acknowledged_by_coach=m.acknowledged_by_coach,
            coach_note=m.coach_note or None,
            declared_at=m.declared_at,
            created_at=m.created_at,
        )


__all__ = ["AthleteIneligibilityDeclarationRepository"]
