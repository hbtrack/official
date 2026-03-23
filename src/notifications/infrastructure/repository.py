from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from ..domain.entities import NotificationDelivery, UserNotificationPreferences
from .models import NotificationDeliveryModel, UserNotificationPreferencesModel


def _delivery_from_model(m: NotificationDeliveryModel) -> NotificationDelivery:
    return NotificationDelivery(
        id=m.id,
        recipient_user_id=m.recipient_user_id,
        channel_label=m.channel_label,
        notification_template_ref=m.notification_template_ref,
        event_envelope_ref=m.event_envelope_ref,
        preference_label=m.preference_label,
        delivery_status_label=m.delivery_status_label,
        retry_count=m.retry_count,
        requested_at=m.requested_at,
        delivered_at=m.delivered_at,
    )


def _prefs_from_model(m: UserNotificationPreferencesModel) -> UserNotificationPreferences:
    return UserNotificationPreferences(
        user_id=m.user_id,
        push_enabled=m.push_enabled,
        email_enabled=m.email_enabled,
        in_app_enabled=m.in_app_enabled,
        sms_enabled=m.sms_enabled,
        quiet_hours_start=m.quiet_hours_start,
        quiet_hours_end=m.quiet_hours_end,
    )


class NotificationRepository:
    def save_delivery(self, delivery: NotificationDelivery) -> NotificationDelivery:
        obj, _ = NotificationDeliveryModel.objects.update_or_create(
            id=delivery.id,
            defaults={
                "recipient_user_id": delivery.recipient_user_id,
                "channel_label": delivery.channel_label,
                "notification_template_ref": delivery.notification_template_ref,
                "event_envelope_ref": delivery.event_envelope_ref,
                "preference_label": delivery.preference_label,
                "delivery_status_label": delivery.delivery_status_label,
                "retry_count": delivery.retry_count,
                "requested_at": delivery.requested_at,
                "delivered_at": delivery.delivered_at,
            },
        )
        return _delivery_from_model(obj)

    def get_delivery_by_id(self, delivery_id: UUID) -> Optional[NotificationDelivery]:
        try:
            return _delivery_from_model(
                NotificationDeliveryModel.objects.get(id=delivery_id)
            )
        except NotificationDeliveryModel.DoesNotExist:
            return None

    def list_deliveries(
        self,
        recipient_user_id: Optional[str] = None,
        channel_label: Optional[str] = None,
        delivery_status_label: Optional[str] = None,
        requested_at_from: Optional[datetime] = None,
        requested_at_to: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[NotificationDelivery], int]:
        qs = NotificationDeliveryModel.objects.all()
        if recipient_user_id:
            qs = qs.filter(recipient_user_id=recipient_user_id)
        if channel_label:
            qs = qs.filter(channel_label=channel_label)
        if delivery_status_label:
            qs = qs.filter(delivery_status_label=delivery_status_label)
        if requested_at_from:
            qs = qs.filter(requested_at__gte=requested_at_from)
        if requested_at_to:
            qs = qs.filter(requested_at__lte=requested_at_to)
        total = qs.count()
        offset = (page - 1) * page_size
        items = qs[offset:offset + page_size]
        return [_delivery_from_model(m) for m in items], total

    def get_preferences(self, user_id: UUID) -> UserNotificationPreferences:
        prefs, _ = UserNotificationPreferencesModel.objects.get_or_create(
            user_id=user_id,
            defaults={
                "push_enabled": True,
                "email_enabled": True,
                "in_app_enabled": True,
                "sms_enabled": False,
            },
        )
        return _prefs_from_model(prefs)

    def save_preferences(
        self, prefs: UserNotificationPreferences
    ) -> UserNotificationPreferences:
        obj, _ = UserNotificationPreferencesModel.objects.update_or_create(
            user_id=prefs.user_id,
            defaults={
                "push_enabled": prefs.push_enabled,
                "email_enabled": prefs.email_enabled,
                "in_app_enabled": prefs.in_app_enabled,
                "sms_enabled": prefs.sms_enabled,
                "quiet_hours_start": prefs.quiet_hours_start,
                "quiet_hours_end": prefs.quiet_hours_end,
            },
        )
        return _prefs_from_model(obj)
