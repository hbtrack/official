"""ORM do agregado AttendanceRecord (append-only)."""
from __future__ import annotations

import uuid

from django.db import models


class AttendanceRecordModel(models.Model):
    """Fato append-only de presença em sessão de treino."""

    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("JUSTIFIED", "Justified"),
        ("PRECONFIRMED", "Preconfirmed"),
    ]
    SOURCE_CHOICES = [
        ("coach_input", "Coach Input"),
        ("athlete_selfcheck", "Athlete Selfcheck"),
        ("correction", "Correction"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(db_index=True)
    athlete_id = models.UUIDField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    source = models.CharField(max_length=32, choices=SOURCE_CHOICES, default="coach_input")
    recorded_at = models.DateTimeField(db_index=True)
    correction_by_user_id = models.UUIDField(null=True, blank=True)
    correction_at = models.DateTimeField(null=True, blank=True)
    justification_reason = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "training_attendance_records"
        app_label = "training"
        indexes = [
            models.Index(fields=["session_id", "athlete_id"], name="training_attend_sess_ath_idx"),
            models.Index(fields=["session_id", "recorded_at"], name="training_attend_sess_rec_idx"),
        ]

    def __str__(self) -> str:
        return f"AttendanceRecord(session={self.session_id}, athlete={self.athlete_id}, status={self.status})"


__all__ = ["AttendanceRecordModel"]
