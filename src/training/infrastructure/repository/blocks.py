"""Repositório do agregado SessionBlock."""
from __future__ import annotations

import uuid
from typing import Optional

from ...domain.entities.blocks import SessionBlock
from ...domain.common.enums import SessionBlockIntensity, SessionBlockPhase
from ..models.blocks import SessionBlockModel


class SessionBlockRepository:
    def get_by_id(self, id: uuid.UUID) -> Optional[SessionBlock]:
        try:
            m = SessionBlockModel.objects.get(pk=id)
            return self._to_domain(m)
        except SessionBlockModel.DoesNotExist:
            return None

    def list_by_session(self, session_id: uuid.UUID) -> list[SessionBlock]:
        return [
            self._to_domain(m)
            for m in SessionBlockModel.objects.filter(session_id=session_id).order_by("order_index")
        ]

    def save(self, block: SessionBlock) -> SessionBlock:
        defaults = {
            "session_id": block.session_id,
            "phase": block.phase.value,
            "order_index": block.order_index,
            "duration_minutes": block.duration_minutes,
            "block_objective": block.block_objective,
            "intensity": block.intensity.value,
            "is_optional": block.is_optional,
            "exercise_id": block.exercise_id,
            "exercise_version_id": block.exercise_version_id,
            "notes": block.notes or "",
        }
        m, _ = SessionBlockModel.objects.update_or_create(pk=block.id, defaults=defaults)
        return self._to_domain(m)

    def delete(self, id: uuid.UUID) -> None:
        SessionBlockModel.objects.filter(pk=id).delete()

    def total_duration_for_session(self, session_id: uuid.UUID, exclude_id: Optional[uuid.UUID] = None) -> int:
        qs = SessionBlockModel.objects.filter(session_id=session_id)
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return sum(b.duration_minutes for b in qs)

    def _to_domain(self, m: SessionBlockModel) -> SessionBlock:
        return SessionBlock(
            id=m.id,
            session_id=m.session_id,
            phase=SessionBlockPhase(m.phase),
            order_index=m.order_index,
            duration_minutes=m.duration_minutes,
            block_objective=m.block_objective,
            intensity=SessionBlockIntensity(m.intensity),
            is_optional=m.is_optional,
            exercise_id=m.exercise_id,
            exercise_version_id=m.exercise_version_id,
            notes=m.notes or None,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


__all__ = ["SessionBlockRepository"]
