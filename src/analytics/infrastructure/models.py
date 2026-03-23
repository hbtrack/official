import uuid
from django.db import models


class AnalyticsSnapshotModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric_key = models.CharField(max_length=50)
    source_module_labels = models.JSONField(default=list)
    time_window_label = models.CharField(max_length=80, null=True, blank=True)
    granularity_label = models.CharField(max_length=40, null=True, blank=True)
    filter_summary = models.TextField(max_length=500, null=True, blank=True)
    projection_key = models.CharField(max_length=80, null=True, blank=True)
    refresh_mode_label = models.CharField(max_length=40, null=True, blank=True)
    computed_at = models.DateTimeField()
    created_by_user_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "analytics"
        db_table = "analytics_snapshot"
        ordering = ["-computed_at"]
