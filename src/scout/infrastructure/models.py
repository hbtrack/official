from django.db import models
import uuid


class ScoutEventModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match_id = models.UUIDField(db_index=True)
    event_label = models.CharField(max_length=120)
    recorded_at = models.DateTimeField(db_index=True)
    athlete_user_id = models.UUIDField(null=True, blank=True, db_index=True)
    team_id = models.UUIDField(null=True, blank=True, db_index=True)
    tag_labels = models.JSONField(default=list)
    clip_asset_refs = models.JSONField(default=list)
    coding_schema_label = models.CharField(max_length=120, null=True, blank=True)
    tactical_aggregation_label = models.CharField(max_length=120, null=True, blank=True)
    session_id = models.UUIDField(null=True, blank=True, db_index=True)
    position_x = models.FloatField(null=True, blank=True)
    position_y = models.FloatField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "scout"
        db_table = "scout_event"
        ordering = ["-recorded_at"]
