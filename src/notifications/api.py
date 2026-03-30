from __future__ import annotations
from typing import Optional
from uuid import UUID
from datetime import datetime
from ninja import Router
from ninja.errors import HttpError
from django.http import HttpRequest

from notifications.application.use_cases import (
    CreateNotificationIntent,
    ListDeliveries,
    GetDelivery,
    GetUserNotificationPreferences,
    UpdateUserNotificationPreferences,
)
from notifications.infrastructure.repository import NotificationRepository
from notifications.domain.rules import (
    InsufficientPrivilege,
    NotificationDeliveryNotFound,
)
from notifications.schemas import (
    NotificationDeliveryOut,
    DeliveryListOut,
    CreateNotificationIntentIn,
    UserNotificationPreferencesOut,
    UpdateNotificationPreferencesIn,
    ErrorOut,
)

router = Router(tags=["notifications"])


def _get_role(request: HttpRequest) -> str:
    """Extrai role do JWT validado."""
    role = getattr(request, "_actor_role", None)
    if role:
        return role
    raise HttpError(401, "Unauthenticated")


def _get_user_id(request: HttpRequest) -> UUID:
    """Extrai user_id do JWT validado."""
    user_id = getattr(request, "_actor_id", None)
    if user_id:
        return UUID(str(user_id))
    raise HttpError(401, "Unauthenticated")


@router.post(
    "/intents",
    response={202: NotificationDeliveryOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut},
)
def create_notification_intent(request: HttpRequest, payload: CreateNotificationIntentIn):
    role = _get_role(request)
    repo = NotificationRepository()
    try:
        delivery = CreateNotificationIntent(repo).execute(
            role=role,
            recipient_user_id=payload.recipientUserId,
            channel_label=payload.channelLabel,
            notification_template_ref=payload.notificationTemplateRef,
            event_envelope_ref=payload.eventEnvelopeRef,
            preference_label=payload.preferenceLabel,
        )
        return 202, NotificationDeliveryOut.from_domain(delivery)
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 400, ErrorOut(detail=str(e))


@router.get(
    "/deliveries",
    response={200: DeliveryListOut, 401: ErrorOut, 403: ErrorOut},
)
def list_deliveries(
    request: HttpRequest,
    recipientUserId: Optional[UUID] = None,
    channelLabel: Optional[str] = None,
    deliveryStatusLabel: Optional[str] = None,
    requestedAtFrom: Optional[datetime] = None,
    requestedAtTo: Optional[datetime] = None,
    page: int = 1,
    pageSize: int = 20,
):
    role = _get_role(request)
    requesting_user_id = _get_user_id(request)
    repo = NotificationRepository()
    try:
        result = ListDeliveries(repo).execute(
            role=role,
            requesting_user_id=requesting_user_id,
            recipient_user_id=str(recipientUserId) if recipientUserId else None,
            channel_label=channelLabel,
            delivery_status_label=deliveryStatusLabel,
            requested_at_from=requestedAtFrom,
            requested_at_to=requestedAtTo,
            page=page,
            page_size=pageSize,
        )
        return 200, DeliveryListOut(
            data=[NotificationDeliveryOut.from_domain(d) for d in result["data"]],
            page=result["page"],
            pageSize=result["pageSize"],
            total=result["total"],
        )
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))


@router.get(
    "/deliveries/{delivery_id}",
    response={200: NotificationDeliveryOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
def get_delivery(request: HttpRequest, delivery_id: UUID):
    role = _get_role(request)
    requesting_user_id = _get_user_id(request)
    repo = NotificationRepository()
    try:
        delivery = GetDelivery(repo).execute(
            role=role,
            delivery_id=delivery_id,
            requesting_user_id=requesting_user_id,
        )
        return 200, NotificationDeliveryOut.from_domain(delivery)
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except NotificationDeliveryNotFound as e:
        return 404, ErrorOut(detail=str(e))


@router.get(
    "/users/{user_id}/preferences",
    response={200: UserNotificationPreferencesOut, 401: ErrorOut, 403: ErrorOut},
)
def get_user_notification_preferences(request: HttpRequest, user_id: UUID):
    role = _get_role(request)
    requesting_user_id = _get_user_id(request)
    repo = NotificationRepository()
    try:
        prefs = GetUserNotificationPreferences(repo).execute(
            role=role,
            user_id=user_id,
            requesting_user_id=requesting_user_id,
        )
        return 200, UserNotificationPreferencesOut.from_domain(prefs)
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))


@router.patch(
    "/users/{user_id}/preferences",
    response={200: UserNotificationPreferencesOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut},
)
def update_user_notification_preferences(
    request: HttpRequest, user_id: UUID, payload: UpdateNotificationPreferencesIn
):
    role = _get_role(request)
    requesting_user_id = _get_user_id(request)
    repo = NotificationRepository()
    try:
        prefs = UpdateUserNotificationPreferences(repo).execute(
            role=role,
            user_id=user_id,
            requesting_user_id=requesting_user_id,
            push_enabled=payload.pushEnabled,
            email_enabled=payload.emailEnabled,
            in_app_enabled=payload.inAppEnabled,
            sms_enabled=payload.smsEnabled,
            quiet_hours_start=payload.quietHoursStart,
            quiet_hours_end=payload.quietHoursEnd,
        )
        return 200, UserNotificationPreferencesOut.from_domain(prefs)
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 400, ErrorOut(detail=str(e))
