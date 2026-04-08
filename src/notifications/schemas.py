from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from ninja import Schema

# CODEGEN CUTOVER — generated layer linked
from .generated import schemas as _gen_schemas  # noqa: F401


class NotificationDeliveryOut(Schema):
    id: UUID
    recipient_user_id: UUID
    channel_label: str
    notification_template_ref: Optional[str] = None
    event_envelope_ref: Optional[str] = None
    preference_label: Optional[str] = None
    delivery_status_label: str
    retry_count: int
    requested_at: datetime
    delivered_at: Optional[datetime] = None

    @classmethod
    def from_domain(cls, d) -> "NotificationDeliveryOut":
        return cls(
            id=d.id,
            recipient_user_id=d.recipient_user_id,
            channel_label=d.channel_label,
            notification_template_ref=d.notification_template_ref,
            event_envelope_ref=d.event_envelope_ref,
            preference_label=d.preference_label,
            delivery_status_label=d.delivery_status_label,
            retry_count=d.retry_count,
            requested_at=d.requested_at,
            delivered_at=d.delivered_at,
        )

class DeliveryListOut(Schema):
    data: List[NotificationDeliveryOut]
    page: int
    pageSize: int
    total: int

class CreateNotificationIntentIn(Schema):
    recipientUserId: UUID
    channelLabel: str
    notificationTemplateRef: Optional[str] = None
    eventEnvelopeRef: Optional[str] = None
    preferenceLabel: Optional[str] = None

class UserNotificationPreferencesOut(Schema):
    user_id: UUID
    push_enabled: bool
    email_enabled: bool
    in_app_enabled: bool
    sms_enabled: bool
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None

    @classmethod
    def from_domain(cls, p) -> "UserNotificationPreferencesOut":
        return cls(
            user_id=p.user_id,
            push_enabled=p.push_enabled,
            email_enabled=p.email_enabled,
            in_app_enabled=p.in_app_enabled,
            sms_enabled=p.sms_enabled,
            quiet_hours_start=p.quiet_hours_start,
            quiet_hours_end=p.quiet_hours_end,
        )

class UpdateNotificationPreferencesIn(Schema):
    pushEnabled: Optional[bool] = None
    emailEnabled: Optional[bool] = None
    inAppEnabled: Optional[bool] = None
    smsEnabled: Optional[bool] = None
    quietHoursStart: Optional[str] = None
    quietHoursEnd: Optional[str] = None

class ErrorOut(Schema):
    detail: str
