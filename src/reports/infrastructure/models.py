import uuid
from django.db import models


class ReportJobModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_user_id = models.UUIDField()
    report_type = models.CharField(max_length=120)
    format_label = models.CharField(max_length=40, null=True, blank=True)
    parameter_summary = models.TextField(max_length=1000, null=True, blank=True)
    source_metric_names = models.JSONField(default=list)
    generated_artifact_ref = models.CharField(max_length=255, null=True, blank=True)
    retention_label = models.CharField(max_length=60, null=True, blank=True)
    status_label = models.CharField(max_length=20, default="queued")
    requested_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "reports"
        db_table = "report_job"
        ordering = ["-requested_at"]
