"""
Infrastructure models — módulo seasons.
ORM Django sem ArrayField (portável — usa JSONField para listas).
Contrato: contracts/schemas/seasons/season.schema.json
ADR-031: Django stack.
"""
from __future__ import annotations

from django.db import models


class SeasonModel(models.Model):
    """
    Modelo ORM da entidade Season.
    Usa JSONField para listas (phase_labels, team_ids, competition_ids)
    para manter portabilidade sem depender do ArrayField do PostgreSQL.
    """
    id = models.UUIDField(primary_key=True)
    organization_id = models.UUIDField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=120)
    sport_cycle_label = models.CharField(max_length=80, null=True, blank=True)
    status_label = models.CharField(
        max_length=20,
        default="DRAFT",
        db_index=True,
    )
    start_date = models.DateField()
    end_date = models.DateField()

    # Listas canônicas (DR-SEAS-003) — JSONField portável
    phase_labels = models.JSONField(default=list)
    team_ids = models.JSONField(default=list)
    competition_ids = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "seasons"
        db_table = "seasons_season"
        ordering = ["-start_date"]
