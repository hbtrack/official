from django.db import models
import uuid


class MedicalRecordModel(models.Model):
    """
    ORM Django para MedicalRecord.
    INV-MED-001: id, athlete_user_id, record_date, record_label obrigatórios.
    INV-MED-004: PHI/PII — dados clínicos sensíveis.
    Soft-delete via is_deleted + deleted_at para conformidade LGPD/PERM-MED-003.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    athlete_user_id = models.UUIDField(db_index=True)
    team_id = models.UUIDField(null=True, blank=True, db_index=True)
    record_date = models.DateField(db_index=True)
    record_label = models.CharField(max_length=120)

    assessment_summary = models.TextField(max_length=1000, blank=True, null=True)
    restriction_summary = models.TextField(max_length=1000, blank=True, null=True)
    return_to_training_authorized = models.BooleanField(null=True, blank=True)
    return_to_play_authorized = models.BooleanField(null=True, blank=True)
    clinical_notes = models.TextField(max_length=2000, blank=True, null=True)

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "medical"
        db_table = "medical_record"
        ordering = ["-record_date"]
        indexes = [
            models.Index(fields=["athlete_user_id", "record_date"]),
        ]

    def __str__(self):
        return f"MedicalRecord({self.id}, athlete={self.athlete_user_id}, date={self.record_date})"
