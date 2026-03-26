from django.db import models
import uuid


class NotificationDeliveryModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient_user_id = models.UUIDField()
    channel_label = models.CharField(max_length=40)
    notification_template_ref = models.CharField(max_length=160, blank=True, null=True)
    event_envelope_ref = models.CharField(max_length=160, blank=True, null=True)
    preference_label = models.CharField(max_length=40, blank=True, null=True)
    delivery_status_label = models.CharField(max_length=40, default="queued")
    retry_count = models.IntegerField(default=0)
    requested_at = models.DateTimeField()
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notification_delivery"
        ordering = ["-requested_at"]


class UserNotificationPreferencesModel(models.Model):
    user_id = models.UUIDField(unique=True)
    push_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.CharField(max_length=5, blank=True, null=True)  # HH:MM
    quiet_hours_end = models.CharField(max_length=5, blank=True, null=True)    # HH:MM

    class Meta:
        db_table = "user_notification_preferences"
