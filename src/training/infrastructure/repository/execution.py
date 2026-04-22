"""Repositório do agregado ExecutionRecord (append-only)."""
from __future__ import annotations

import uuid
from typing import Optional

from ...domain.entities import ExecutionRecord, ExecutionType
from ..models import ExecutionRecordModel


class ExecutionRecordRepository:
    def list_by_session(self, session_id: uuid.UUID) -> list[ExecutionRecord]:
        return [
            self._to_domain(m)
            for m in ExecutionRecordModel.objects.filter(session_id=session_id).order_by("recorded_at")
        ]

    def get_by_id(self, id: uuid.UUID) -> Optional[ExecutionRecord]:
        try:
            return self._to_domain(ExecutionRecordModel.objects.get(pk=id))
        except ExecutionRecordModel.DoesNotExist:
            return None

    def save(self, record: ExecutionRecord) -> ExecutionRecord:
        defaults = {
            "session_id": record.session_id,
            "block_id": record.block_id,
            "execution_type": record.execution_type.value,
            "recorded_at": record.recorded_at,
            "planned_value": record.planned_value,
            "actual_value": record.actual_value,
            "planned_unit": record.planned_unit or "",
            "actual_unit": record.actual_unit or "",
            "adjustment_reason_type": record.adjustment_reason_type or "",
            "coach_rationale": record.coach_rationale or "",
            "notes": record.notes or "",
            "created_by_user_id": record.created_by_user_id,
        }
        m, _ = ExecutionRecordModel.objects.update_or_create(pk=record.id, defaults=defaults)
        return self._to_domain(m)

    def _to_domain(self, m: ExecutionRecordModel) -> ExecutionRecord:
        return ExecutionRecord(
            id=m.id,
            session_id=m.session_id,
            block_id=m.block_id,
            execution_type=ExecutionType(m.execution_type),
            recorded_at=m.recorded_at,
            planned_value=m.planned_value,
            actual_value=m.actual_value,
            planned_unit=m.planned_unit or None,
            actual_unit=m.actual_unit or None,
            adjustment_reason_type=m.adjustment_reason_type or None,
            coach_rationale=m.coach_rationale or None,
            notes=m.notes or None,
            created_by_user_id=m.created_by_user_id,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


__all__ = ["ExecutionRecordRepository"]
