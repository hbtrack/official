from django.db import models
import uuid


class MatchModel(models.Model):
    """
    ORM Django para Match.
    INV-MATCH-001..005 enforced em domain/entities.py.
    lineup_user_ids, official_incident_ids, referee_names: JSON arrays.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    competition_id = models.UUIDField(db_index=True)
    home_team_id = models.UUIDField(db_index=True)
    away_team_id = models.UUIDField(db_index=True)
    status_label = models.CharField(max_length=20, default="SCHEDULED", db_index=True)
    venue_label = models.CharField(max_length=200, blank=True, null=True)
    scheduled_at = models.DateTimeField(db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    away_score = models.PositiveSmallIntegerField(null=True, blank=True)
    referee_names = models.JSONField(default=list, blank=True)
    lineup_user_ids = models.JSONField(default=list, blank=True)
    official_incident_ids = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "matches"
        db_table = "match"
        ordering = ["-scheduled_at"]
        indexes = [
            models.Index(fields=["competition_id", "scheduled_at"]),
        ]
