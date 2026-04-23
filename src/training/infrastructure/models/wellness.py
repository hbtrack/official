"""ORM do agregado Wellness (pré e pós treino)."""
from __future__ import annotations

import uuid

from django.db import models


class WellnessPreModel(models.Model):
    """
    Wellness pré-treino por atleta.
    INV-TRAIN-009: único ativo por (session_id, athlete_id).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(db_index=True)
    athlete_id = models.UUIDField(db_index=True)
    readiness = models.SmallIntegerField(null=True, blank=True)
    sleep_quality = models.SmallIntegerField(null=True, blank=True)
    sleep_hours = models.FloatField(null=True, blank=True)
    mood = models.SmallIntegerField(null=True, blank=True)
    fatigue = models.SmallIntegerField(null=True, blank=True)
    muscle_soreness = models.SmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_reason = models.TextField(blank=True, default="")

    class Meta:
        db_table = "training_wellness_pre"
        app_label = "training"

    def __str__(self) -> str:
        return f"WellnessPre(session={self.session_id}, athlete={self.athlete_id})"


class WellnessPostModel(models.Model):
    """
    Wellness pós-treino por atleta.
    INV-TRAIN-010: único ativo por (session_id, athlete_id).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(db_index=True)
    athlete_id = models.UUIDField(db_index=True)
    perceived_exertion = models.SmallIntegerField(null=True, blank=True)
    enjoyment = models.SmallIntegerField(null=True, blank=True)
    technical_learning = models.SmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_reason = models.TextField(blank=True, default="")

    class Meta:
        db_table = "training_wellness_post"
        app_label = "training"

    def __str__(self) -> str:
        return f"WellnessPost(session={self.session_id}, athlete={self.athlete_id})"


__all__ = ["WellnessPreModel", "WellnessPostModel"]
