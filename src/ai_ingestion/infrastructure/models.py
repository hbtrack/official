import uuid
from django.db import models


class IngestionJobModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_label = models.CharField(max_length=120)
    ingestion_mode = models.CharField(max_length=40)
    payload_schema_ref = models.CharField(max_length=255, null=True, blank=True)
    mapping_profile = models.CharField(max_length=120, null=True, blank=True)
    idempotency_key = models.CharField(max_length=120, null=True, blank=True, unique=True)
    execution_binding_label = models.CharField(max_length=80, null=True, blank=True)
    status_label = models.CharField(max_length=20, default="queued")
    received_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    origin_job_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "ai_ingestion"
        db_table = "ingestion_job"
        ordering = ["-received_at"]
