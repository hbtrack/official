"""ORM do agregado TrainingSession (raiz + SessionObjective)."""
from __future__ import annotations

import uuid

from django.db import models


class TrainingSessionModel(models.Model):
    """
    Persiste TrainingSession.
    db_table: training_sessions
    INV-TRAIN-006: status FSM — 7 estados canônicos (ADR-017).
    INV-TRAIN-008: soft delete auditável.
    """
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("SCHEDULED", "Scheduled"),
        ("PUBLISHED", "Published"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
        ("ARCHIVED", "Archived"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.UUIDField(db_index=True)
    team_id = models.UUIDField(null=True, blank=True, db_index=True)
    season_id = models.UUIDField(null=True, blank=True, db_index=True)
    microcycle_id = models.UUIDField(null=True, blank=True)
    session_at = models.DateTimeField(db_index=True)
    duration_planned_minutes = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=120, blank=True, default="")
    session_type = models.CharField(max_length=32)
    main_objective = models.CharField(max_length=255, blank=True, default="")
    secondary_objective = models.TextField(blank=True, default="")
    planned_load = models.SmallIntegerField(null=True, blank=True)
    intensity_target = models.SmallIntegerField(null=True, blank=True)
    session_block = models.CharField(max_length=32, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    group_climate = models.SmallIntegerField(null=True, blank=True)
    standalone = models.BooleanField(null=True, blank=True)
    individualization_mode = models.CharField(max_length=40, blank=True, default="")

    focus_attack_positional_pct = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    focus_defense_positional_pct = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    focus_transition_offense_pct = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    focus_transition_defense_pct = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    focus_attack_technical_pct = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    focus_defense_technical_pct = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    focus_physical_pct = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    phase_focus_defense = models.BooleanField(null=True, blank=True)
    phase_focus_attack = models.BooleanField(null=True, blank=True)
    phase_focus_transition_offense = models.BooleanField(null=True, blank=True)
    phase_focus_transition_defense = models.BooleanField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    created_by_user_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_reason = models.TextField(blank=True, default="")

    # ── Campos de execução / resultado (migration 0007) ───────────────────────
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by_user_id = models.UUIDField(null=True, blank=True)
    deviation_justification = models.TextField(null=True, blank=True)
    planning_deviation_flag = models.BooleanField(null=True, blank=True)
    duration_actual_minutes = models.IntegerField(null=True, blank=True)
    execution_outcome = models.CharField(max_length=40, null=True, blank=True)
    delay_minutes = models.IntegerField(null=True, blank=True)
    cancellation_reason = models.TextField(null=True, blank=True)
    actual_load_recorded = models.SmallIntegerField(null=True, blank=True)
    post_review_completed_at = models.DateTimeField(null=True, blank=True)
    post_review_completed_by_user_id = models.UUIDField(null=True, blank=True)
    post_review_deadline_at = models.DateTimeField(null=True, blank=True)
    post_review_completed = models.BooleanField(null=True, blank=True)

    planned_content_snapshot = models.JSONField(null=True, blank=True)
    objective_origin = models.CharField(max_length=60, null=True, blank=True)
    continuity_notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "training_sessions"
        app_label = "training"
        indexes = [
            models.Index(fields=["organization_id", "status"]),
            models.Index(fields=["team_id", "session_at"]),
        ]

    def __str__(self) -> str:
        return f"TrainingSession({self.id}, status={self.status})"


class SessionObjectiveModel(models.Model):
    """Objetivo operacional de sessão. TRAIN-DEC-004/005."""
    ORIGIN_CHOICES = [
        ("NEED_DETECTED", "Need Detected"),
        ("COMPETITIVE_FOCUS", "Competitive Focus"),
        ("DEVELOPMENT_GOAL", "Development Goal"),
        ("MANUAL_COACH_RATIONALE", "Manual Coach Rationale"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(db_index=True)
    origin = models.CharField(max_length=30, choices=ORIGIN_CHOICES)
    objective_type = models.CharField(max_length=60)
    description = models.TextField()
    origin_notes = models.TextField(blank=True, default="")
    priority = models.SmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "training_session_objectives"
        app_label = "training"


__all__ = ["TrainingSessionModel", "SessionObjectiveModel"]
