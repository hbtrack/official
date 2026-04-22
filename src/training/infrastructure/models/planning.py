"""ORM de periodização: Mesocycle + Microcycle."""
from __future__ import annotations

import uuid

from django.db import models


class MesocycleModel(models.Model):
    """Mesociclo — bloco médio de periodização."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.UUIDField(db_index=True)
    season_id = models.UUIDField(null=True, blank=True)
    team_id = models.UUIDField(null=True, blank=True)
    name = models.CharField(max_length=120)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    objective = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "training_mesocycles"
        app_label = "training"


class MicrocycleModel(models.Model):
    """Microciclo — unidade semanal de periodização."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.UUIDField(db_index=True)
    mesocycle_id = models.UUIDField(db_index=True)
    team_id = models.UUIDField(null=True, blank=True)
    week_number = models.SmallIntegerField()
    name = models.CharField(max_length=120, blank=True, default="")
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    objective = models.TextField(blank=True, default="")
    planned_sessions_count = models.SmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "training_microcycles"
        app_label = "training"


__all__ = ["MesocycleModel", "MicrocycleModel"]
