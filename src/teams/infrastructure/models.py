"""
Infrastructure models — módulo teams.
ORM Django sem ArrayField (JSONField portável para listas).
ADR-031: Django stack.
"""
from __future__ import annotations

from django.db import models


class TeamModel(models.Model):
    """
    Modelo ORM da entidade Team.
    JSONField para listas de IDs — portável sem ArrayField do PostgreSQL.
    INV-TEAM-004: sem campos de credenciais, sessão ou prontuário.
    """
    id = models.UUIDField(primary_key=True)
    organization_id = models.UUIDField(db_index=True)
    season_id = models.UUIDField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=120)
    short_name = models.CharField(max_length=32, null=True, blank=True)
    category_label = models.CharField(max_length=80, db_index=True)
    status_label = models.CharField(max_length=20, default="DRAFT", db_index=True)

    # Vínculos explícitos (DR-TEAM-002, INV-TEAM-002) — JSONField portável
    athlete_ids = models.JSONField(default=list)
    staff_user_ids = models.JSONField(default=list)

    # Notas operacionais (DR-TEAM-005)
    roster_notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "teams"
        db_table = "teams_team"
        ordering = ["name"]
