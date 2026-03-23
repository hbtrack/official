import uuid
from datetime import datetime, timezone, timedelta
import pytest

from notifications.domain.entities import NotificationDelivery, UserNotificationPreferences
from notifications.domain.rules import (
    RoleLabel,
    InsufficientPrivilege,
    NotificationDeliveryNotFound,
    assert_can_create_intent,
    assert_can_list_deliveries,
    assert_can_get_delivery,
    assert_can_access_preferences,
    assert_can_update_preferences,
)
from notifications.application.use_cases import (
    CreateNotificationIntent,
    ListDeliveries,
    GetDelivery,
    GetUserNotificationPreferences,
    UpdateUserNotificationPreferences,
)


def make_delivery(**kwargs):
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        recipient_user_id=uuid.uuid4(),
        channel_label="push",
        requested_at=now,
        notification_template_ref="template://session-reminder",
    )
    defaults.update(kwargs)
    return NotificationDelivery(**defaults)


# ---- INV-NTF-001: required fields ----

def test_delivery_valid():
    d = make_delivery()
    d.validate_invariants()


def test_delivery_missing_recipient():
    d = make_delivery(recipient_user_id=None)
    with pytest.raises(ValueError, match="INV-NTF-001"):
        d.validate_invariants()


def test_delivery_missing_channel():
    d = make_delivery(channel_label="")
    with pytest.raises(ValueError, match="INV-NTF-001"):
        d.validate_invariants()


def test_delivery_missing_requested_at():
    d = make_delivery(requested_at=None)
    with pytest.raises(ValueError, match="INV-NTF-001"):
        d.validate_invariants()


# ---- INV-NTF-002: retryCount in [0..10] ----

def test_retry_count_zero_ok():
    d = make_delivery(retry_count=0)
    d.validate_invariants()


def test_retry_count_10_ok():
    d = make_delivery(retry_count=10)
    d.validate_invariants()


def test_retry_count_negative_fails():
    d = make_delivery(retry_count=-1)
    with pytest.raises(ValueError, match="INV-NTF-002"):
        d.validate_invariants()


def test_retry_count_11_fails():
    d = make_delivery(retry_count=11)
    with pytest.raises(ValueError, match="INV-NTF-002"):
        d.validate_invariants()


# ---- INV-NTF-003: deliveredAt >= requestedAt ----

def test_delivered_at_before_requested_at_fails():
    now = datetime.now(timezone.utc)
    d = make_delivery(requested_at=now, delivered_at=now - timedelta(seconds=1))
    with pytest.raises(ValueError, match="INV-NTF-003"):
        d.validate_invariants()


def test_delivered_at_after_requested_at_ok():
    now = datetime.now(timezone.utc)
    d = make_delivery(requested_at=now, delivered_at=now + timedelta(seconds=10))
    d.validate_invariants()


# ---- INV-NTF-004: at least one of templateRef or eventEnvelopeRef ----

def test_both_refs_absent_fails():
    d = make_delivery(notification_template_ref=None, event_envelope_ref=None)
    with pytest.raises(ValueError, match="INV-NTF-004"):
        d.validate_invariants()


def test_template_ref_only_ok():
    d = make_delivery(notification_template_ref="template://x", event_envelope_ref=None)
    d.validate_invariants()


def test_event_envelope_ref_only_ok():
    d = make_delivery(notification_template_ref=None, event_envelope_ref="event://y")
    d.validate_invariants()


def test_both_refs_present_ok():
    d = make_delivery(notification_template_ref="template://x", event_envelope_ref="event://y")
    d.validate_invariants()


# ---- PERM-NOT-001: create intent ----

def test_create_intent_admin_ok():
    assert_can_create_intent(RoleLabel.ADMIN)


def test_create_intent_coordinator_ok():
    assert_can_create_intent(RoleLabel.COORDINATOR)


def test_create_intent_coach_ok():
    assert_can_create_intent(RoleLabel.COACH)


def test_create_intent_athlete_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_create_intent(RoleLabel.ATHLETE)


def test_create_intent_member_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_create_intent(RoleLabel.MEMBER)


# ---- listDeliveries BOLA ----

def test_list_deliveries_admin_ok():
    assert_can_list_deliveries(RoleLabel.ADMIN)


def test_list_deliveries_member_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_list_deliveries(RoleLabel.MEMBER)


# ---- getDelivery BOLA ----

def test_get_delivery_admin_any_ok():
    d = make_delivery()
    other_id = uuid.uuid4()
    assert_can_get_delivery(RoleLabel.ADMIN, d, other_id)  # admin can see any


def test_get_delivery_coach_own_ok():
    own_id = uuid.uuid4()
    d = make_delivery(recipient_user_id=own_id)
    assert_can_get_delivery(RoleLabel.COACH, d, own_id)


def test_get_delivery_coach_other_forbidden():
    d = make_delivery(recipient_user_id=uuid.uuid4())
    with pytest.raises(InsufficientPrivilege):
        assert_can_get_delivery(RoleLabel.COACH, d, uuid.uuid4())


def test_get_delivery_member_forbidden():
    d = make_delivery()
    with pytest.raises(InsufficientPrivilege):
        assert_can_get_delivery(RoleLabel.MEMBER, d, uuid.uuid4())


# ---- Preferences BOLA ----

def test_access_preferences_admin_any_ok():
    user_id = uuid.uuid4()
    other_id = uuid.uuid4()
    assert_can_access_preferences(RoleLabel.ADMIN, user_id, other_id)


def test_access_preferences_athlete_own_ok():
    own_id = uuid.uuid4()
    assert_can_access_preferences(RoleLabel.ATHLETE, own_id, own_id)


def test_access_preferences_athlete_other_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_access_preferences(RoleLabel.ATHLETE, uuid.uuid4(), uuid.uuid4())


def test_update_preferences_admin_any_ok():
    user_id = uuid.uuid4()
    other_id = uuid.uuid4()
    assert_can_update_preferences(RoleLabel.ADMIN, user_id, other_id)


def test_update_preferences_coach_own_ok():
    own_id = uuid.uuid4()
    assert_can_update_preferences(RoleLabel.COACH, own_id, own_id)


def test_update_preferences_coordinator_other_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_update_preferences(RoleLabel.COORDINATOR, uuid.uuid4(), uuid.uuid4())


def test_update_preferences_member_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_update_preferences(RoleLabel.MEMBER, uuid.uuid4(), uuid.uuid4())


# ---- Fake repo ----

class FakeRepo:
    def __init__(self, deliveries=None, preferences=None):
        self._deliveries = {d.id: d for d in (deliveries or [])}
        self._preferences = dict(preferences or {})

    def save_delivery(self, delivery):
        self._deliveries[delivery.id] = delivery
        return delivery

    def get_delivery_by_id(self, delivery_id):
        return self._deliveries.get(delivery_id)

    def list_deliveries(self, recipient_user_id=None, channel_label=None,
                       delivery_status_label=None, requested_at_from=None,
                       requested_at_to=None, page=1, page_size=20):
        items = list(self._deliveries.values())
        if recipient_user_id:
            items = [d for d in items if str(d.recipient_user_id) == recipient_user_id]
        total = len(items)
        offset = (page - 1) * page_size
        return items[offset:offset + page_size], total

    def get_preferences(self, user_id):
        if user_id not in self._preferences:
            prefs = UserNotificationPreferences(user_id=user_id)
            self._preferences[user_id] = prefs
        return self._preferences[user_id]

    def save_preferences(self, prefs):
        self._preferences[prefs.user_id] = prefs
        return prefs


# ---- CreateNotificationIntent use case ----

def test_create_intent_use_case_ok():
    repo = FakeRepo()
    delivery = CreateNotificationIntent(repo).execute(
        role=RoleLabel.ADMIN,
        recipient_user_id=uuid.uuid4(),
        channel_label="push",
        notification_template_ref="template://reminder",
    )
    assert delivery.delivery_status_label == "queued"
    assert delivery.retry_count == 0


def test_create_intent_both_refs_absent_raises():
    repo = FakeRepo()
    with pytest.raises(ValueError, match="INV-NTF-004"):
        CreateNotificationIntent(repo).execute(
            role=RoleLabel.ADMIN,
            recipient_user_id=uuid.uuid4(),
            channel_label="push",
        )


def test_create_intent_athlete_forbidden():
    with pytest.raises(InsufficientPrivilege):
        CreateNotificationIntent(FakeRepo()).execute(
            role=RoleLabel.ATHLETE,
            recipient_user_id=uuid.uuid4(),
            channel_label="push",
            notification_template_ref="template://x",
        )


# ---- ListDeliveries use case ----

def test_list_deliveries_use_case_admin():
    user_id = uuid.uuid4()
    d = make_delivery(recipient_user_id=user_id)
    result = ListDeliveries(FakeRepo([d])).execute(
        role=RoleLabel.ADMIN,
        requesting_user_id=user_id,
    )
    assert result["total"] == 1


def test_list_deliveries_coach_bola():
    own_id = uuid.uuid4()
    other_id = uuid.uuid4()
    d1 = make_delivery(recipient_user_id=own_id)
    d2 = make_delivery(recipient_user_id=other_id)
    result = ListDeliveries(FakeRepo([d1, d2])).execute(
        role=RoleLabel.COACH,
        requesting_user_id=own_id,
    )
    assert result["total"] == 1
    assert result["data"][0].recipient_user_id == own_id


# ---- GetDelivery use case ----

def test_get_delivery_use_case_ok():
    d = make_delivery()
    delivery = GetDelivery(FakeRepo([d])).execute(
        role=RoleLabel.ADMIN,
        delivery_id=d.id,
        requesting_user_id=uuid.uuid4(),
    )
    assert delivery.id == d.id


def test_get_delivery_not_found():
    with pytest.raises(NotificationDeliveryNotFound):
        GetDelivery(FakeRepo()).execute(
            role=RoleLabel.ADMIN,
            delivery_id=uuid.uuid4(),
            requesting_user_id=uuid.uuid4(),
        )


# ---- Preferences use cases ----

def test_get_preferences_creates_default():
    user_id = uuid.uuid4()
    prefs = GetUserNotificationPreferences(FakeRepo()).execute(
        role=RoleLabel.ADMIN,
        user_id=user_id,
        requesting_user_id=user_id,
    )
    assert prefs.push_enabled is True


def test_update_preferences_partial():
    user_id = uuid.uuid4()
    repo = FakeRepo()
    updated = UpdateUserNotificationPreferences(repo).execute(
        role=RoleLabel.ADMIN,
        user_id=user_id,
        requesting_user_id=user_id,
        push_enabled=False,
    )
    assert updated.push_enabled is False
    assert updated.email_enabled is True  # unchanged
