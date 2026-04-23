"""Repositórios do agregado Wellness (pré e pós treino)."""
from __future__ import annotations

import uuid
from typing import Optional

from ...domain.entities import WellnessPost, WellnessPre
from ..models import WellnessPostModel, WellnessPreModel


class WellnessPreRepository:
    def get_active(self, session_id: uuid.UUID, athlete_id: uuid.UUID) -> Optional[WellnessPre]:
        try:
            m = WellnessPreModel.objects.get(
                session_id=session_id, athlete_id=athlete_id, deleted_at__isnull=True
            )
            return self._to_domain(m)
        except WellnessPreModel.DoesNotExist:
            return None

    def save(self, wellness: WellnessPre) -> WellnessPre:
        defaults = {
            "session_id": wellness.session_id,
            "athlete_id": wellness.athlete_id,
            "readiness": wellness.readiness,
            "sleep_quality": wellness.sleep_quality,
            "sleep_hours": wellness.sleep_hours,
            "mood": wellness.mood,
            "fatigue": wellness.fatigue,
            "muscle_soreness": wellness.muscle_soreness,
            "notes": wellness.notes or "",
            "deleted_at": wellness.deleted_at,
            "deleted_reason": wellness.deleted_reason or "",
        }
        m, _ = WellnessPreModel.objects.update_or_create(pk=wellness.id, defaults=defaults)
        return self._to_domain(m)

    def _to_domain(self, m: WellnessPreModel) -> WellnessPre:
        return WellnessPre(
            id=m.id,
            session_id=m.session_id,
            athlete_id=m.athlete_id,
            readiness=m.readiness,
            sleep_quality=m.sleep_quality,
            sleep_hours=m.sleep_hours,
            mood=m.mood,
            fatigue=m.fatigue,
            muscle_soreness=m.muscle_soreness,
            notes=m.notes or None,
            created_at=m.created_at,
            updated_at=m.updated_at,
            deleted_at=m.deleted_at,
            deleted_reason=m.deleted_reason or None,
        )


class WellnessPostRepository:
    def get_active(self, session_id: uuid.UUID, athlete_id: uuid.UUID) -> Optional[WellnessPost]:
        try:
            m = WellnessPostModel.objects.get(
                session_id=session_id, athlete_id=athlete_id, deleted_at__isnull=True
            )
            return self._to_domain(m)
        except WellnessPostModel.DoesNotExist:
            return None

    def save(self, wellness: WellnessPost) -> WellnessPost:
        defaults = {
            "session_id": wellness.session_id,
            "athlete_id": wellness.athlete_id,
            "perceived_exertion": wellness.perceived_exertion,
            "enjoyment": wellness.enjoyment,
            "technical_learning": wellness.technical_learning,
            "notes": wellness.notes or "",
            "deleted_at": wellness.deleted_at,
            "deleted_reason": wellness.deleted_reason or "",
        }
        m, _ = WellnessPostModel.objects.update_or_create(pk=wellness.id, defaults=defaults)
        return self._to_domain(m)

    def _to_domain(self, m: WellnessPostModel) -> WellnessPost:
        return WellnessPost(
            id=m.id,
            session_id=m.session_id,
            athlete_id=m.athlete_id,
            perceived_exertion=m.perceived_exertion,
            enjoyment=m.enjoyment,
            technical_learning=m.technical_learning,
            notes=m.notes or None,
            created_at=m.created_at,
            updated_at=m.updated_at,
            deleted_at=m.deleted_at,
            deleted_reason=m.deleted_reason or None,
        )


__all__ = ["WellnessPreRepository", "WellnessPostRepository"]
