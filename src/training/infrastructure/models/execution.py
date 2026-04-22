"""ORM do agregado ExecutionRecord (append-only)."""
from __future__ import annotations

import uuid

from django.db import models


class ExecutionRecordModel(models.Model):
    """
    Registro de execução — append-only. TRAIN-DEC-007/008/009.
    """
    TYPE_CHOICES = [
        ("SESSION_EXECUTION", "Session Execution"),
        ("BLOCK_EXECUTION", "Block Execution"),
        ("LIVE_ADJUSTMENT", "Live Adjustment"),
        ("CONSTRAINT_OVERRIDE", "Constraint Override"),
        ("ALTERNATE_EXERCISE", "Alternate Exercise"),
        ("LOAD_RECALCULATION", "Load Recalculation"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(db_index=True)
    block_id = models.UUIDField(null=True, blank=True)
    execution_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    recorded_at = models.DateTimeField()
    planned_value = models.FloatField(null=True, blank=True)
    actual_value = models.FloatField(null=True, blank=True)
    planned_unit = models.CharField(max_length=32, blank=True, default="")
    actual_unit = models.CharField(max_length=32, blank=True, default="")
    adjustment_reason_type = models.CharField(max_length=40, blank=True, default="")
    coach_rationale = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    created_by_user_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "training_execution_records"
        app_label = "training"

    def __str__(self) -> str:
        return f"ExecutionRecord({self.id}, type={self.execution_type})"


__all__ = ["ExecutionRecordModel"]
