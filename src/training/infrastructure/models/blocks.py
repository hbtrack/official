"""ORM do agregado SessionBlock."""
from __future__ import annotations

import uuid

from django.db import models


class SessionBlockModel(models.Model):
    """
    Bloco operacional de sessão.
    TRAIN-DEC-049. INV-TRAIN-083.
    """
    PHASE_CHOICES = [
        ("WARMUP", "Warmup"),
        ("ACTIVATION", "Activation"),
        ("TECHNICAL", "Technical"),
        ("DECISION_MAKING", "Decision Making"),
        ("TACTICAL", "Tactical"),
        ("REDUCED_GAME", "Reduced Game"),
        ("COOLDOWN", "Cooldown"),
    ]
    INTENSITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("MAXIMUM", "Maximum"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(db_index=True)
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES)
    order_index = models.IntegerField()
    duration_minutes = models.IntegerField()
    block_objective = models.CharField(max_length=300)
    intensity = models.CharField(max_length=10, choices=INTENSITY_CHOICES)
    is_optional = models.BooleanField(default=False)
    exercise_id = models.UUIDField(null=True, blank=True)
    exercise_version_id = models.UUIDField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "training_session_blocks"
        app_label = "training"
        unique_together = [("session_id", "order_index")]

    def __str__(self) -> str:
        return f"SessionBlock({self.id}, session={self.session_id}, phase={self.phase})"


__all__ = ["SessionBlockModel"]
