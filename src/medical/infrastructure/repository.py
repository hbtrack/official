from __future__ import annotations
import uuid
from datetime import date, datetime
from typing import List, Optional

from medical.domain.entities import MedicalRecord
from medical.infrastructure.models import MedicalRecordModel


def _to_domain(m: MedicalRecordModel) -> MedicalRecord:
    return MedicalRecord(
        id=m.id,
        athlete_user_id=m.athlete_user_id,
        team_id=m.team_id,
        record_date=m.record_date,
        record_label=m.record_label,
        assessment_summary=m.assessment_summary,
        restriction_summary=m.restriction_summary,
        return_to_training_authorized=m.return_to_training_authorized,
        return_to_play_authorized=m.return_to_play_authorized,
        clinical_notes=m.clinical_notes,
        is_deleted=m.is_deleted,
        deleted_at=m.deleted_at,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class MedicalRecordRepository:
    """Repositório de registros médicos — somente ORM Django."""

    def save(self, record: MedicalRecord) -> MedicalRecord:
        obj, _ = MedicalRecordModel.objects.update_or_create(
            id=record.id,
            defaults={
                "athlete_user_id": record.athlete_user_id,
                "team_id": record.team_id,
                "record_date": record.record_date,
                "record_label": record.record_label,
                "assessment_summary": record.assessment_summary,
                "restriction_summary": record.restriction_summary,
                "return_to_training_authorized": record.return_to_training_authorized,
                "return_to_play_authorized": record.return_to_play_authorized,
                "clinical_notes": record.clinical_notes,
                "is_deleted": record.is_deleted,
                "deleted_at": record.deleted_at,
            },
        )
        return _to_domain(obj)

    def get_by_id(self, record_id: uuid.UUID) -> Optional[MedicalRecord]:
        try:
            return _to_domain(MedicalRecordModel.objects.get(id=record_id, is_deleted=False))
        except MedicalRecordModel.DoesNotExist:
            return None

    def list_records(
        self,
        athlete_user_id: Optional[uuid.UUID] = None,
        team_id: Optional[uuid.UUID] = None,
        record_date_from: Optional[date] = None,
        record_date_to: Optional[date] = None,
        authorization_status: Optional[str] = None,
        page_token: Optional[str] = None,
        page_size: int = 20,
    ) -> tuple[List[MedicalRecord], Optional[str]]:
        qs = MedicalRecordModel.objects.filter(is_deleted=False)
        if athlete_user_id:
            qs = qs.filter(athlete_user_id=athlete_user_id)
        if team_id:
            qs = qs.filter(team_id=team_id)
        if record_date_from:
            qs = qs.filter(record_date__gte=record_date_from)
        if record_date_to:
            qs = qs.filter(record_date__lte=record_date_to)
        if authorization_status == "authorized_both":
            qs = qs.filter(return_to_training_authorized=True, return_to_play_authorized=True)
        elif authorization_status == "authorized_training_only":
            qs = qs.filter(return_to_training_authorized=True, return_to_play_authorized__ne=True)
        elif authorization_status == "not_authorized":
            qs = qs.filter(return_to_training_authorized__ne=True)

        # Simple cursor-based pagination using offset encoded in page_token
        offset = 0
        if page_token:
            try:
                offset = int(page_token)
            except ValueError:
                offset = 0

        items = list(qs.order_by("-record_date")[offset : offset + page_size])
        next_token = str(offset + page_size) if len(items) == page_size else None
        return [_to_domain(m) for m in items], next_token

    def soft_delete(self, record_id: uuid.UUID) -> bool:
        updated = MedicalRecordModel.objects.filter(id=record_id, is_deleted=False).update(
            is_deleted=True,
            deleted_at=datetime.now(),
        )
        return updated > 0
