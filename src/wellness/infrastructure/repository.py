from __future__ import annotations
import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple

from wellness.domain.entities import WellnessEntry, WellnessSummary


class WellnessEntryRepository:
    def _model(self):
        from wellness.infrastructure.models import WellnessEntryModel
        return WellnessEntryModel

    def _to_domain(self, obj) -> WellnessEntry:
        return WellnessEntry(
            id=obj.id,
            athlete_user_id=obj.athlete_user_id,
            training_session_id=obj.training_session_id,
            questionnaire_date=obj.questionnaire_date,
            questionnaire_label=obj.questionnaire_label,
            readiness_score=obj.readiness_score,
            fatigue_score=obj.fatigue_score,
            pain_score=obj.pain_score,
            recovery_score=obj.recovery_score,
            sleep_hours=Decimal(str(obj.sleep_hours)) if obj.sleep_hours is not None else None,
            notes=obj.notes,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    def save(self, entry: WellnessEntry) -> WellnessEntry:
        M = self._model()
        obj, _ = M.objects.update_or_create(
            id=entry.id,
            defaults=dict(
                athlete_user_id=entry.athlete_user_id,
                training_session_id=entry.training_session_id,
                questionnaire_date=entry.questionnaire_date,
                questionnaire_label=entry.questionnaire_label,
                readiness_score=entry.readiness_score,
                fatigue_score=entry.fatigue_score,
                pain_score=entry.pain_score,
                recovery_score=entry.recovery_score,
                sleep_hours=entry.sleep_hours,
                notes=entry.notes,
            ),
        )
        return self._to_domain(obj)

    def get_by_id(self, entry_id: uuid.UUID) -> Optional[WellnessEntry]:
        M = self._model()
        try:
            return self._to_domain(M.objects.get(id=entry_id))
        except M.DoesNotExist:
            return None

    def list_entries(
        self,
        *,
        athlete_user_id: Optional[uuid.UUID] = None,
        questionnaire_date: Optional[date] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        questionnaire_label: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[WellnessEntry], int]:
        M = self._model()
        qs = M.objects.all()
        if athlete_user_id is not None:
            qs = qs.filter(athlete_user_id=athlete_user_id)
        if questionnaire_date is not None:
            qs = qs.filter(questionnaire_date=questionnaire_date)
        if date_from is not None:
            qs = qs.filter(questionnaire_date__gte=date_from)
        if date_to is not None:
            qs = qs.filter(questionnaire_date__lte=date_to)
        if questionnaire_label is not None:
            qs = qs.filter(questionnaire_label=questionnaire_label)
        total = qs.count()
        offset = (page - 1) * page_size
        return [self._to_domain(o) for o in qs[offset:offset + page_size]], total

    def compute_summary(
        self,
        athlete_user_id: uuid.UUID,
        date_from: date,
        date_to: date,
    ) -> WellnessSummary:
        from django.db.models import Avg
        M = self._model()
        qs = M.objects.filter(
            athlete_user_id=athlete_user_id,
            questionnaire_date__gte=date_from,
            questionnaire_date__lte=date_to,
        )
        count = qs.count()
        agg = qs.aggregate(
            avg_r=Avg("readiness_score"),
            avg_f=Avg("fatigue_score"),
            avg_p=Avg("pain_score"),
            avg_rec=Avg("recovery_score"),
            avg_s=Avg("sleep_hours"),
        )

        # trend: comparar médias primeira e segunda metade do período
        trend = None
        if count >= 4:
            mid = date_from + (date_to - date_from) / 2
            first_avg = qs.filter(questionnaire_date__lte=mid).aggregate(Avg("readiness_score"))["readiness_score__avg"]
            second_avg = qs.filter(questionnaire_date__gt=mid).aggregate(Avg("readiness_score"))["readiness_score__avg"]
            if first_avg is not None and second_avg is not None:
                diff = second_avg - first_avg
                if diff > 0.5:
                    trend = "improving"
                elif diff < -0.5:
                    trend = "declining"
                else:
                    trend = "stable"

        high_pain = qs.filter(pain_score__gte=7).exists()
        return WellnessSummary(
            athlete_user_id=athlete_user_id,
            date_from=date_from,
            date_to=date_to,
            entry_count=count,
            avg_readiness=Decimal(str(round(agg["avg_r"], 2))) if agg["avg_r"] is not None else None,
            avg_fatigue=Decimal(str(round(agg["avg_f"], 2))) if agg["avg_f"] is not None else None,
            avg_pain=Decimal(str(round(agg["avg_p"], 2))) if agg["avg_p"] is not None else None,
            avg_recovery=Decimal(str(round(agg["avg_rec"], 2))) if agg["avg_rec"] is not None else None,
            avg_sleep_hours=Decimal(str(round(agg["avg_s"], 2))) if agg["avg_s"] is not None else None,
            readiness_trend=trend,
            high_pain_alert=high_pain,
        )
