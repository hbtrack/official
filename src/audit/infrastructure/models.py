from django.db import models
import uuid


class AuditEntryModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor_user_id = models.UUIDField()
    action = models.CharField(max_length=120)
    occurred_at = models.DateTimeField()
    target_resource_id = models.UUIDField(null=True, blank=True)
    target_resource_type = models.CharField(max_length=80, blank=True, null=True)
    outcome_label = models.CharField(max_length=40, blank=True, null=True)
    origin_label = models.CharField(max_length=80, blank=True, null=True)
    correlation_id = models.UUIDField(null=True, blank=True)
    before_summary = models.CharField(max_length=1000, blank=True, null=True)
    after_summary = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        db_table = "audit_entry"
        ordering = ["-occurred_at"]

    def save(self, *args, **kwargs):
        # INV-AUD-002: append-only; block updates
        if not self._state.adding:
            raise RuntimeError(
                "INV-AUD-002: AuditEntry is append-only and cannot be modified"
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # INV-AUD-002: append-only; block deletes
        raise RuntimeError(
            "INV-AUD-002: AuditEntry is append-only and cannot be deleted"
        )
