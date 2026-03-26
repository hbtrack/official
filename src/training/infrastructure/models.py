"""
Django ORM models — módulo training.
Alinhados com:
  - contracts/schemas/training/training_session.schema.json
  - contracts/schemas/training/session_block.schema.json
  - contracts/schemas/training/execution_record.schema.json
  - docs/hbtrack/modulos/training/INVARIANTS_TRAINING.md
"""
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

    # Focus percentages — INV-TRAIN-001
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

    # Phase focus booleans
    phase_focus_defense = models.BooleanField(null=True, blank=True)
    phase_focus_attack = models.BooleanField(null=True, blank=True)
    phase_focus_transition_offense = models.BooleanField(null=True, blank=True)
    phase_focus_transition_defense = models.BooleanField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    created_by_user_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Soft delete — INV-TRAIN-008
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_reason = models.TextField(blank=True, default="")

    class Meta:
        db_table = "training_sessions"
        app_label = "training"
        indexes = [
            models.Index(fields=["organization_id", "status"]),
            models.Index(fields=["team_id", "session_at"]),
        ]

    def __str__(self) -> str:
        return f"TrainingSession({self.id}, status={self.status})"


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
    # Sem FK cross-module; sem FK para TrainingSessionModel para evitar acoplamento
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


class ExecutionRecordModel(models.Model):
    """
    Registro de execução — append-only. TRAIN-DEC-007/008/009.
    """
    TYPE_CHOICES = [
        ("SESSION_EXECUTION", "Session Execution"),
        ("BLOCK_EXECUTION", "Block Execution"),
        ("LIVE_ADJUSTMENT", "Live Adjustment"),
        ("CONSTRAINT_OVERRIDE", "Constraint Override"),
        ("ALTERNATE_EXERCISE", "Alternate Exercise"),
        ("LOAD_RECALCULATION", "Load Recalculation"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(db_index=True)
    block_id = models.UUIDField(null=True, blank=True)
    execution_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    recorded_at = models.DateTimeField()
    planned_value = models.FloatField(null=True, blank=True)
    actual_value = models.FloatField(null=True, blank=True)
    planned_unit = models.CharField(max_length=32, blank=True, default="")
    actual_unit = models.CharField(max_length=32, blank=True, default="")
    adjustment_reason_type = models.CharField(max_length=40, blank=True, default="")
    coach_rationale = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    created_by_user_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "training_execution_records"
        app_label = "training"

    def __str__(self) -> str:
        return f"ExecutionRecord({self.id}, type={self.execution_type})"


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


class FeedbackThreadModel(models.Model):
    """Thread de feedback técnico. TRAIN-DEC-010/015."""
    OUTCOME_CHOICES = [
        ("REFLECTION_DOCUMENTED", "Reflection Documented"),
        ("COMMITMENT_MADE", "Commitment Made"),
        ("FOLLOWUP_SCHEDULED", "Followup Scheduled"),
        ("DECISION_RECORDED", "Decision Recorded"),
        ("PENDING_FOLLOWUP", "Pending Followup"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(db_index=True)
    block_id = models.UUIDField(null=True, blank=True)
    athlete_id = models.UUIDField(null=True, blank=True)
    objective_id = models.UUIDField(null=True, blank=True)
    created_by_user_id = models.UUIDField()
    subject = models.CharField(max_length=200, blank=True, default="")
    body = models.TextField(blank=True, default="")
    conversation_outcome = models.CharField(max_length=30, choices=OUTCOME_CHOICES)
    follow_up_at = models.DateTimeField(null=True, blank=True)
    commitment_text = models.TextField(blank=True, default="")
    decision_text = models.TextField(blank=True, default="")
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "training_feedback_threads"
        app_label = "training"


class AttentionQueueItemModel(models.Model):
    """Item da fila de atenção técnica."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(db_index=True)
    athlete_id = models.UUIDField()
    reason = models.TextField()
    severity = models.CharField(max_length=20)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.UUIDField(null=True, blank=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    escalated_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "training_attention_queue_items"
        app_label = "training"


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
