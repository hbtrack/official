import pytest
from uuid import uuid4
from exercises.domain.entities import Exercise, ExerciseVersion, ExerciseRelation
from exercises.domain.rules import (
    RoleLabel, InsufficientPrivilege, ExerciseConflict,
    assert_can_create_exercise, assert_can_modify_exercise, assert_can_delete_exercise,
    can_read_exercise, assert_can_manage_acl, assert_can_manage_relations,
)


def _make_version(**kw):
    defaults = dict(
        id=uuid4(), exercise_id=uuid4(), version_number=1, name="Test",
        session_phase="WARMUP", primary_objective="TECHNICAL", physical_load="LOW",
        space_required="HALF_COURT", skill_level="BEGINNER", complexity=2,
        min_athletes=2, max_athletes=10, estimated_duration_minutes=20,
        age_categories=["ADULT"],
    )
    defaults.update(kw)
    return ExerciseVersion(**defaults)


def _make_exercise(**kw):
    defaults = dict(id=uuid4(), scope="ORG", created_by_user_id=uuid4(),
                    organization_id=uuid4())
    defaults.update(kw)
    return Exercise(**defaults)


# ─── INV-EXB-001 / 002 ───

class TestInvExb001And002:
    def test_valid_org_exercise(self):
        e = _make_exercise()
        e.validate_invariants()

    def test_invalid_scope_raises(self):
        e = _make_exercise(scope="INVALID")
        with pytest.raises(ValueError, match="scope"):
            e.validate_invariants()

    def test_org_without_organization_id_raises(self):
        e = _make_exercise(scope="ORG", organization_id=None)
        with pytest.raises(ValueError, match="organization_id"):
            e.validate_invariants()

    def test_system_with_organization_id_raises(self):
        e = _make_exercise(scope="SYSTEM", organization_id=uuid4())
        with pytest.raises(ValueError, match="organization_id"):
            e.validate_invariants()

    def test_system_without_organization_id_ok(self):
        e = _make_exercise(scope="SYSTEM", organization_id=None)
        e.validate_invariants()


# ─── INV-EXB-003 / 004 ───

class TestInvExb003And004:
    def test_max_less_than_min_raises(self):
        v = _make_version(min_athletes=10, max_athletes=5)
        with pytest.raises(ValueError, match="maxAthletes"):
            v.validate_invariants()

    def test_min_zero_raises(self):
        v = _make_version(min_athletes=0, max_athletes=5)
        with pytest.raises(ValueError, match="minAthletes"):
            v.validate_invariants()

    def test_max_over_50_raises(self):
        v = _make_version(min_athletes=1, max_athletes=51)
        with pytest.raises(ValueError, match="maxAthletes"):
            v.validate_invariants()

    def test_valid_athletes_range(self):
        v = _make_version(min_athletes=5, max_athletes=10)
        v.validate_invariants()


# ─── INV-EXB-013 / 014 ───

class TestInvExb013And014:
    def test_reflexive_relation_raises(self):
        eid = uuid4()
        rel = ExerciseRelation(id=uuid4(), from_exercise_id=eid, to_exercise_id=eid,
                                relation_type="PROGRESSION", created_by_user_id=uuid4())
        with pytest.raises(ValueError, match="reflexiva"):
            rel.validate_invariants()

    def test_invalid_relation_type_raises(self):
        rel = ExerciseRelation(id=uuid4(), from_exercise_id=uuid4(), to_exercise_id=uuid4(),
                                relation_type="INVALID", created_by_user_id=uuid4())
        with pytest.raises(ValueError, match="relationType"):
            rel.validate_invariants()

    def test_valid_relation(self):
        for rt in ["PROGRESSION", "REGRESSION", "VARIATION", "CONTRAINDICATION"]:
            rel = ExerciseRelation(id=uuid4(), from_exercise_id=uuid4(), to_exercise_id=uuid4(),
                                    relation_type=rt, created_by_user_id=uuid4())
            rel.validate_invariants()


# ─── INV-EXB-015 / 016 ───

class TestInvExb015And016:
    def test_complexity_zero_raises(self):
        v = _make_version(complexity=0)
        with pytest.raises(ValueError, match="complexity"):
            v.validate_invariants()

    def test_complexity_six_raises(self):
        v = _make_version(complexity=6)
        with pytest.raises(ValueError, match="complexity"):
            v.validate_invariants()

    def test_complexity_five_ok(self):
        v = _make_version(complexity=5)
        v.validate_invariants()

    def test_duration_zero_raises(self):
        v = _make_version(estimated_duration_minutes=0)
        with pytest.raises(ValueError, match="estimatedDurationMinutes"):
            v.validate_invariants()

    def test_duration_181_raises(self):
        v = _make_version(estimated_duration_minutes=181)
        with pytest.raises(ValueError, match="estimatedDurationMinutes"):
            v.validate_invariants()

    def test_duration_180_ok(self):
        v = _make_version(estimated_duration_minutes=180)
        v.validate_invariants()


# ─── PERM rules ───

class TestPermExercises:
    def test_athlete_cannot_create(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_exercise(RoleLabel.ATHLETE)

    def test_member_cannot_create(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_exercise(RoleLabel.MEMBER)

    def test_coach_can_create(self):
        assert_can_create_exercise(RoleLabel.COACH)

    def test_admin_can_create(self):
        assert_can_create_exercise(RoleLabel.ADMIN)

    def test_non_admin_cannot_modify_system(self):
        cid = uuid4()
        with pytest.raises(InsufficientPrivilege):
            assert_can_modify_exercise(RoleLabel.COACH, cid, "SYSTEM", cid)

    def test_admin_can_modify_system(self):
        assert_can_modify_exercise(RoleLabel.ADMIN, uuid4(), "SYSTEM", uuid4())

    def test_coach_can_modify_own_org_exercise(self):
        cid = uuid4()
        assert_can_modify_exercise(RoleLabel.COACH, cid, "ORG", cid)

    def test_coach_cannot_modify_others_org_exercise(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_modify_exercise(RoleLabel.COACH, uuid4(), "ORG", uuid4())

    def test_system_exercise_visible_to_all(self):
        assert can_read_exercise(RoleLabel.ATHLETE, uuid4(), "SYSTEM", "RESTRICTED",
                                  None, None, uuid4(), []) is True

    def test_org_restricted_visible_to_creator(self):
        cid = uuid4()
        org = uuid4()
        assert can_read_exercise(RoleLabel.COACH, cid, "ORG", "RESTRICTED",
                                  org, org, cid, []) is True

    def test_org_restricted_not_visible_to_outsider(self):
        org = uuid4()
        assert can_read_exercise(RoleLabel.COACH, uuid4(), "ORG", "RESTRICTED",
                                  org, org, uuid4(), []) is False

    def test_org_wide_visible_to_org_member(self):
        org = uuid4()
        assert can_read_exercise(RoleLabel.COACH, uuid4(), "ORG", "ORG_WIDE",
                                  org, org, uuid4(), []) is True

    def test_acl_cannot_be_managed_for_system_exercise(self):
        with pytest.raises(ExerciseConflict):
            assert_can_manage_acl(RoleLabel.ADMIN, uuid4(), "SYSTEM", uuid4(), "RESTRICTED")

    def test_acl_cannot_be_managed_for_org_wide(self):
        with pytest.raises(ExerciseConflict):
            assert_can_manage_acl(RoleLabel.ADMIN, uuid4(), "ORG", uuid4(), "ORG_WIDE")
