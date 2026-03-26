import uuid
from datetime import datetime, timezone
import pytest

from audit.domain.entities import AuditEntry
from audit.domain.rules import (
    RoleLabel,
    InsufficientPrivilege,
    AuditEntryNotFound,
    assert_can_list_entries,
    assert_can_create_entry,
    assert_can_get_entry,
    assert_can_export_entries,
    assert_coordinator_context,
)
from audit.application.use_cases import (
    ListAuditEntries,
    CreateAuditEntry,
    GetAuditEntry,
    ExportAuditEntries,
)


def make_entry(**kwargs):
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        actor_user_id=uuid.uuid4(),
        action="training_session.updated",
        occurred_at=now,
    )
    defaults.update(kwargs)
    return AuditEntry(**defaults)


# ---- INV-AUD-001: required fields ----

def test_entry_valid():
    e = make_entry()
    e.validate_invariants()


def test_entry_missing_actor_user_id():
    e = make_entry(actor_user_id=None)
    with pytest.raises(ValueError, match="INV-AUD-001"):
        e.validate_invariants()


def test_entry_missing_action():
    e = make_entry(action="")
    with pytest.raises(ValueError, match="INV-AUD-001"):
        e.validate_invariants()


def test_entry_missing_occurred_at():
    e = make_entry(occurred_at=None)
    with pytest.raises(ValueError, match="INV-AUD-001"):
        e.validate_invariants()


# ---- INV-AUD-003: targetResourceId <-> targetResourceType ----

def test_target_resource_id_without_type_fails():
    e = make_entry(target_resource_id=uuid.uuid4(), target_resource_type=None)
    with pytest.raises(ValueError, match="INV-AUD-003"):
        e.validate_invariants()


def test_target_resource_type_without_id_fails():
    e = make_entry(target_resource_id=None, target_resource_type="training_session")
    with pytest.raises(ValueError, match="INV-AUD-003"):
        e.validate_invariants()


def test_both_target_fields_present_ok():
    e = make_entry(target_resource_id=uuid.uuid4(), target_resource_type="training_session")
    e.validate_invariants()


def test_both_target_fields_absent_ok():
    e = make_entry(target_resource_id=None, target_resource_type=None)
    e.validate_invariants()


# ---- PERM-AUD: only admin/coordinator ----

def test_assert_list_admin_ok():
    assert_can_list_entries(RoleLabel.ADMIN)


def test_assert_list_coordinator_with_team_ok():
    assert_can_list_entries(RoleLabel.COORDINATOR, team_id="team-x")


def test_assert_list_coordinator_without_context_fails():
    with pytest.raises(ValueError, match="PERM-AUD-001"):
        assert_can_list_entries(RoleLabel.COORDINATOR)


def test_assert_list_coach_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_list_entries(RoleLabel.COACH)


def test_assert_list_athlete_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_list_entries(RoleLabel.ATHLETE)


def test_assert_list_member_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_list_entries(RoleLabel.MEMBER)


def test_assert_create_admin_ok():
    assert_can_create_entry(RoleLabel.ADMIN)


def test_assert_create_coordinator_ok():
    assert_can_create_entry(RoleLabel.COORDINATOR)


def test_assert_create_coach_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_create_entry(RoleLabel.COACH)


def test_assert_get_admin_ok():
    assert_can_get_entry(RoleLabel.ADMIN)


def test_assert_get_member_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_get_entry(RoleLabel.MEMBER)


def test_assert_export_admin_ok():
    now = datetime.now(timezone.utc)
    assert_can_export_entries(RoleLabel.ADMIN)


def test_assert_export_coordinator_org_ok():
    assert_can_export_entries(RoleLabel.COORDINATOR, organization_id="org-x")


def test_assert_export_coordinator_no_context_fails():
    with pytest.raises(ValueError, match="PERM-AUD-001"):
        assert_can_export_entries(RoleLabel.COORDINATOR)


def test_assert_export_athlete_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_export_entries(RoleLabel.ATHLETE)


# ---- Fake repo ----

class FakeRepo:
    def __init__(self, entries=None):
        self._entries = {e.id: e for e in (entries or [])}

    def save(self, entry):
        self._entries[entry.id] = entry
        return entry

    def get_by_id(self, entry_id):
        return self._entries.get(entry_id)

    def list_entries(self, **kwargs):
        items = list(self._entries.values())
        page_size = kwargs.get("page_size", 50)
        return items[:page_size], None

    def export_entries(self, occurred_after, occurred_before, **kwargs):
        items = [
            e for e in self._entries.values()
            if occurred_after <= e.occurred_at <= occurred_before
        ]
        return items[:10000], len(items) > 10000


# ---- ListAuditEntries ----

def test_list_returns_dict():
    e1 = make_entry()
    result = ListAuditEntries(FakeRepo([e1])).execute(role=RoleLabel.ADMIN)
    assert isinstance(result, dict)
    assert "items" in result
    assert len(result["items"]) == 1


def test_list_forbidden_for_coach():
    with pytest.raises(InsufficientPrivilege):
        ListAuditEntries(FakeRepo()).execute(role=RoleLabel.COACH)


def test_list_coordinator_without_context_raises_400():
    with pytest.raises(ValueError, match="PERM-AUD-001"):
        ListAuditEntries(FakeRepo()).execute(role=RoleLabel.COORDINATOR)


# ---- CreateAuditEntry ----

def test_create_entry_ok():
    repo = FakeRepo()
    now = datetime.now(timezone.utc)
    entry = CreateAuditEntry(repo).execute(
        role=RoleLabel.ADMIN,
        actor_user_id=uuid.uuid4(),
        action="user.login",
        occurred_at=now,
    )
    assert entry.action == "user.login"


def test_create_entry_missing_action_raises():
    repo = FakeRepo()
    with pytest.raises(ValueError, match="INV-AUD-001"):
        CreateAuditEntry(repo).execute(
            role=RoleLabel.ADMIN,
            actor_user_id=uuid.uuid4(),
            action="",
            occurred_at=datetime.now(timezone.utc),
        )


def test_create_entry_target_mismatch_raises():
    repo = FakeRepo()
    with pytest.raises(ValueError, match="INV-AUD-003"):
        CreateAuditEntry(repo).execute(
            role=RoleLabel.ADMIN,
            actor_user_id=uuid.uuid4(),
            action="session.updated",
            occurred_at=datetime.now(timezone.utc),
            target_resource_id=uuid.uuid4(),
            target_resource_type=None,
        )


def test_create_entry_forbidden_for_athlete():
    with pytest.raises(InsufficientPrivilege):
        CreateAuditEntry(FakeRepo()).execute(
            role=RoleLabel.ATHLETE,
            actor_user_id=uuid.uuid4(),
            action="x",
            occurred_at=datetime.now(timezone.utc),
        )


# ---- GetAuditEntry ----

def test_get_entry_found():
    e = make_entry()
    result = GetAuditEntry(FakeRepo([e])).execute(role=RoleLabel.ADMIN, entry_id=e.id)
    assert result.id == e.id


def test_get_entry_not_found():
    with pytest.raises(AuditEntryNotFound):
        GetAuditEntry(FakeRepo()).execute(role=RoleLabel.ADMIN, entry_id=uuid.uuid4())


def test_get_entry_forbidden_for_coach():
    e = make_entry()
    with pytest.raises(InsufficientPrivilege):
        GetAuditEntry(FakeRepo([e])).execute(role=RoleLabel.COACH, entry_id=e.id)


# ---- ExportAuditEntries ----

def test_export_ok():
    now = datetime.now(timezone.utc)
    e = make_entry(occurred_at=now)
    from datetime import timedelta
    after = now - timedelta(hours=1)
    before = now + timedelta(hours=1)
    result = ExportAuditEntries(FakeRepo([e])).execute(
        role=RoleLabel.ADMIN,
        occurred_after=after,
        occurred_before=before,
    )
    assert "entries" in result
    assert result["exportedCount"] >= 0


def test_export_coordinator_no_context_fails():
    now = datetime.now(timezone.utc)
    from datetime import timedelta
    with pytest.raises(ValueError, match="PERM-AUD-001"):
        ExportAuditEntries(FakeRepo()).execute(
            role=RoleLabel.COORDINATOR,
            occurred_after=now - timedelta(hours=1),
            occurred_before=now,
        )


def test_export_forbidden_for_member():
    now = datetime.now(timezone.utc)
    from datetime import timedelta
    with pytest.raises(InsufficientPrivilege):
        ExportAuditEntries(FakeRepo()).execute(
            role=RoleLabel.MEMBER,
            occurred_after=now - timedelta(hours=1),
            occurred_before=now,
        )
