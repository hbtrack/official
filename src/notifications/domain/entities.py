from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

VALID_CHANNELS = frozenset(["push", "email", "in_app", "sms"])
VALID_STATUSES = frozenset(["queued", "sent", "failed", "retrying"])


@dataclass
class NotificationDelivery:
    id: UUID
    recipient_user_id: UUID
    channel_label: str
    requested_at: datetime
    notification_template_ref: Optional[str] = None
    event_envelope_ref: Optional[str] = None
    preference_label: Optional[str] = None
    delivery_status_label: str = "queued"
    retry_count: int = 0
    delivered_at: Optional[datetime] = None

    def validate_invariants(self) -> None:
        # INV-NTF-001: required fields
        if not self.id:
            raise ValueError("INV-NTF-001: id is required")
        if not self.recipient_user_id:
            raise ValueError("INV-NTF-001: recipientUserId is required")
        if not self.channel_label:
            raise ValueError("INV-NTF-001: channelLabel is required")
        if not self.requested_at:
            raise ValueError("INV-NTF-001: requestedAt is required")
        # INV-NTF-002: retryCount in [0..10]
        if not (0 <= self.retry_count <= 10):
            raise ValueError("INV-NTF-002: retryCount must be between 0 and 10")
        # INV-NTF-003: deliveredAt >= requestedAt
        if self.delivered_at and self.delivered_at < self.requested_at:
            raise ValueError("INV-NTF-003: deliveredAt must be >= requestedAt")
        # INV-NTF-004: at least one of notificationTemplateRef or eventEnvelopeRef
        if not self.notification_template_ref and not self.event_envelope_ref:
            raise ValueError(
                "INV-NTF-004: at least one of notificationTemplateRef or "
                "eventEnvelopeRef must be present"
            )


@dataclass
class UserNotificationPreferences:
    user_id: UUID
    push_enabled: bool = True
    email_enabled: bool = True
    in_app_enabled: bool = True
    sms_enabled: bool = False
    quiet_hours_start: Optional[str] = None  # HH:MM
    quiet_hours_end: Optional[str] = None    # HH:MM
