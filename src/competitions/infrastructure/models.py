"""
ORM models Django — módulo competitions.
Fonte: domain/entities.py, contracts/openapi/paths/competitions.yaml
ADR-031: Django 5 + PostgreSQL 16
"""
from __future__ import annotations

import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models


class CompetitionModel(models.Model):
    """
    Tabela principal de competições.
    DR-COMP-002: season_id obrigatório.
    DR-COMP-003: registration_team_ids = inscrições formais (ArrayField).
    DR-COMP-004: stage_labels = fases explícitas (ArrayField).
    INV-COMP-002: start_date, end_date validados no domínio.
    """

    class StatusChoice(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    season_id = models.UUIDField(null=False, db_index=True)
    organization_id = models.UUIDField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=140)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    format_label = models.CharField(max_length=80, null=True, blank=True)
    status_label = models.CharField(
        max_length=20,
        choices=StatusChoice.choices,
        default=StatusChoice.DRAFT,
        db_index=True,
    )
    # INV-COMP-003: arrayfiled com uniqueItems — garantido no domínio
    stage_labels = ArrayField(
        models.CharField(max_length=80),
        default=list,
        blank=True,
    )
    registration_team_ids = ArrayField(
        models.UUIDField(),
        default=list,
        blank=True,
    )
    standings_summary = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "competitions"
        db_table = "competitions_competition"
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return f"Competition({self.name}, season={self.season_id})"
