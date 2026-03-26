from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID

from ..domain.entities import NotificationDelivery, UserNotificationPreferences
from ..domain.rules import (
    RoleLabel, InsufficientPrivilege, NotificationDeliveryNotFound,
    assert_can_create_intent, assert_can_list_deliveries,
    assert_can_get_delivery, assert_can_access_preferences,
    assert_can_update_preferences,
)
from ..infrastructure.repository import NotificationRepository


class CreateNotificationIntent:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    def execute(
        self, role: RoleLabel,
        recipient_user_id: UUID,
        channel_label: str,
        notification_template_ref: Optional[str] = None,
        event_envelope_ref: Optional[str] = None,
        preference_label: Optional[str] = None,
    ) -> NotificationDelivery:
        assert_can_create_intent(role)
        delivery = NotificationDelivery(
            id=uuid.uuid4(),
            recipient_user_id=recipient_user_id,
            channel_label=channel_label,
            notification_template_ref=notification_template_ref,
            event_envelope_ref=event_envelope_ref,
            preference_label=preference_label,
            delivery_status_label="queued",
            retry_count=0,
            requested_at=datetime.now(timezone.utc),
        )
        delivery.validate_invariants()
        return self.repo.save_delivery(delivery)


class ListDeliveries:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    def execute(
        self, role: RoleLabel,
        requesting_user_id: UUID,
        recipient_user_id: Optional[str] = None,
        channel_label: Optional[str] = None,
        delivery_status_label: Optional[str] = None,
        requested_at_from: Optional[datetime] = None,
        requested_at_to: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        assert_can_list_deliveries(role)
        # BOLA: coach/athlete can only see their own deliveries
        if role not in {RoleLabel.ADMIN, RoleLabel.COORDINATOR}:
            recipient_user_id = str(requesting_user_id)
        items, total = self.repo.list_deliveries(
            recipient_user_id=recipient_user_id,
            channel_label=channel_label,
            delivery_status_label=delivery_status_label,
            requested_at_from=requested_at_from,
            requested_at_to=requested_at_to,
            page=page,
            page_size=page_size,
        )
        return {"data": items, "page": page, "pageSize": page_size, "total": total}


class GetDelivery:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    def execute(self, role: RoleLabel, delivery_id: UUID, requesting_user_id: UUID) -> NotificationDelivery:
        delivery = self.repo.get_delivery_by_id(delivery_id)
        if delivery is None:
            raise NotificationDeliveryNotFound(f"Delivery {delivery_id} not found")
        assert_can_get_delivery(role, delivery, requesting_user_id)
        return delivery


class GetUserNotificationPreferences:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    def execute(
        self, role: RoleLabel, user_id: UUID, requesting_user_id: UUID
    ) -> UserNotificationPreferences:
        assert_can_access_preferences(role, user_id, requesting_user_id)
        return self.repo.get_preferences(user_id)


class UpdateUserNotificationPreferences:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    def execute(
        self, role: RoleLabel, user_id: UUID, requesting_user_id: UUID,
        push_enabled: Optional[bool] = None,
        email_enabled: Optional[bool] = None,
        in_app_enabled: Optional[bool] = None,
        sms_enabled: Optional[bool] = None,
        quiet_hours_start: Optional[str] = None,
        quiet_hours_end: Optional[str] = None,
    ) -> UserNotificationPreferences:
        assert_can_update_preferences(role, user_id, requesting_user_id)
        prefs = self.repo.get_preferences(user_id)
        if push_enabled is not None:
            prefs.push_enabled = push_enabled
        if email_enabled is not None:
            prefs.email_enabled = email_enabled
        if in_app_enabled is not None:
            prefs.in_app_enabled = in_app_enabled
        if sms_enabled is not None:
            prefs.sms_enabled = sms_enabled
        if quiet_hours_start is not None:
            prefs.quiet_hours_start = quiet_hours_start
        if quiet_hours_end is not None:
            prefs.quiet_hours_end = quiet_hours_end
        return self.repo.save_preferences(prefs)
