"""ORM dos agregados de comunicação: FeedbackThread, AttentionQueueItem, Recommendation."""
from __future__ import annotations

import uuid

from django.db import models


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


class RecommendationModel(models.Model):
    """Recommendation gerada por analytics/ai_ingestion e revisada no módulo training."""

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("DISMISSED", "Dismissed"),
    ]
    ACTION_TYPE_CHOICES = [
        ("MODIFY_FOCUS", "Modify Focus"),
        ("ADD_BLOCK", "Add Block"),
        ("REMOVE_BLOCK", "Remove Block"),
        ("ADJUST_DURATION", "Adjust Duration"),
        ("ADD_OBJECTIVE", "Add Objective"),
        ("ADJUST_LOAD", "Adjust Load"),
        ("REVIEW_ATHLETE", "Review Athlete"),
    ]
    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(db_index=True)
    generated_by_rule = models.CharField(max_length=128)
    action_type = models.CharField(max_length=32, choices=ACTION_TYPE_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="PENDING", db_index=True)
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, null=True, blank=True)
    generated_by_module = models.CharField(max_length=64)
    coach_note = models.TextField(blank=True, default="")
    dismissal_reason = models.TextField(blank=True, default="")
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by_user_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "training_recommendations"
        app_label = "training"
        indexes = [
            models.Index(fields=["session_id", "status"], name="training_reco_sess_status_idx"),
        ]


__all__ = ["FeedbackThreadModel", "AttentionQueueItemModel", "RecommendationModel"]
