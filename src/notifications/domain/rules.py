from enum import Enum
from uuid import UUID
from .entities import NotificationDelivery


class RoleLabel(str, Enum):
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    COACH = "coach"
    ATHLETE = "athlete"
    MEMBER = "member"


MANAGER_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR}
INTENT_CREATOR_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR, RoleLabel.COACH}


class InsufficientPrivilege(Exception):
    pass


class NotificationDeliveryNotFound(Exception):
    pass


def assert_can_create_intent(role: RoleLabel) -> None:
    """PERM-NOT-001: athlete/member cannot create intents."""
    if role not in INTENT_CREATOR_ROLES:
        raise InsufficientPrivilege(
            "notifications: requires admin, coordinator, or coach role to create intent"
        )


def assert_can_list_deliveries(role: RoleLabel) -> None:
    """listDeliveries: member forbidden; others need role check."""
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege(
            "notifications: member cannot list deliveries"
        )


def assert_can_get_delivery(
    role: RoleLabel, delivery: NotificationDelivery, requesting_user_id: UUID
) -> None:
    """BOLA: coach/athlete can only access own deliveries."""
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege("notifications: member cannot access delivery")
    if role not in MANAGER_ROLES:
        if str(delivery.recipient_user_id) != str(requesting_user_id):
            raise InsufficientPrivilege(
                "notifications: BOLA — can only access own deliveries"
            )


def assert_can_access_preferences(
    role: RoleLabel, target_user_id: UUID, requesting_user_id: UUID
) -> None:
    """PERM-NOT-002: non-managers can only access own preferences."""
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege(
            "notifications: member cannot access notification preferences"
        )
    if role not in MANAGER_ROLES:
        if str(target_user_id) != str(requesting_user_id):
            raise InsufficientPrivilege(
                "notifications: BOLA — can only access own notification preferences"
            )


def assert_can_update_preferences(
    role: RoleLabel, target_user_id: UUID, requesting_user_id: UUID
) -> None:
    """PERM-NOT-002: non-admins can only update own preferences."""
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege(
            "notifications: member cannot update notification preferences"
        )
    if role != RoleLabel.ADMIN:
        if str(target_user_id) != str(requesting_user_id):
            raise InsufficientPrivilege(
                "notifications: BOLA — can only update own notification preferences"
            )
