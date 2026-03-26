"""
ORM models Django — módulo wellness.
ADR-031: Django 5 + PostgreSQL 16
"""
from __future__ import annotations
import uuid
from django.db import models


class WellnessEntryModel(models.Model):
    """
    Tabela de entradas de wellness diário.
    INV-WELL-001: id, athlete_user_id, questionnaire_date, readiness_score.
    INV-WELL-002/003: ranges validados no domínio.
    INV-WELL-004: sem campos clínicos.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    athlete_user_id = models.UUIDField(null=False, db_index=True)
    training_session_id = models.UUIDField(null=True, blank=True, db_index=True)
    questionnaire_date = models.DateField(db_index=True)
    questionnaire_label = models.CharField(max_length=80, null=True, blank=True)
    readiness_score = models.SmallIntegerField()
    fatigue_score = models.SmallIntegerField(null=True, blank=True)
    pain_score = models.SmallIntegerField(null=True, blank=True)
    recovery_score = models.SmallIntegerField(null=True, blank=True)
    sleep_hours = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    notes = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "wellness"
        db_table = "wellness_entry"
        ordering = ["-questionnaire_date"]
        indexes = [
            models.Index(fields=["athlete_user_id", "questionnaire_date"]),
        ]

    def __str__(self) -> str:
        return f"WellnessEntry(athlete={self.athlete_user_id}, date={self.questionnaire_date})"
