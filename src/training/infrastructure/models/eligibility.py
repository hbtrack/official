"""ORM do agregado AthleteIneligibilityDeclaration."""
from __future__ import annotations

import uuid

from django.db import models


class AthleteIneligibilityDeclarationModel(models.Model):
    """Declaração de indisponibilidade do atleta no check-in de training."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(db_index=True)
    athlete_id = models.UUIDField(db_index=True)
    reason_flags = models.JSONField(default=list)
    reason_other = models.TextField(blank=True, default="")
    acknowledged_by_coach = models.BooleanField(default=False)
    coach_note = models.TextField(blank=True, default="")
    declared_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "training_athlete_ineligibility_declarations"
        app_label = "training"
        constraints = [
            models.UniqueConstraint(
                fields=["session_id", "athlete_id"],
                name="training_ineligibility_session_athlete_uniq",
            ),
        ]


__all__ = ["AthleteIneligibilityDeclarationModel"]
