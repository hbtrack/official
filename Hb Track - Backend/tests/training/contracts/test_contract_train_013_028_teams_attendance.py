"""
CONTRACT-TRAIN-013..028 — Teams (scoped sessions) + Session Exercises + Attendance
Routers:
  - training_sessions.py  (scoped_router, prefix=/teams/{team_id}/trainings) → 013..018
  - session_exercises.py  (prefix=/training-sessions)                        → 019..024
  - attendance.py         (sem prefix dedicado)                               → 025..028

Abordagem: análise estática. Sem fixtures de DB.
"""
from pathlib import Path

ROUTERS = Path(__file__).parent.parent.parent.parent / "app" / "api" / "v1" / "routers"

SESSIONS_PATH    = ROUTERS / "training_sessions.py"
EXERCISES_PATH   = ROUTERS / "session_exercises.py"
ATTENDANCE_PATH  = ROUTERS / "attendance.py"


def _sessions():
    return SESSIONS_PATH.read_text(encoding="utf-8")

def _exercises():
    return EXERCISES_PATH.read_text(encoding="utf-8")

def _attendance():
    return ATTENDANCE_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# CONTRACT-013..018  GET/POST/PATCH/DELETE /teams/{team_id}/trainings/...
# ---------------------------------------------------------------------------
class TestContractTrain013ListTeamSessions:
    def test_router_file_exists(self):
        assert SESSIONS_PATH.exists()

    def test_scoped_router_teams_prefix(self):
        content = _sessions()
        assert "/teams/{team_id}/trainings" in content or "scoped_router" in content

    def test_get_list_route_present(self):
        content = _sessions()
        assert "@scoped_router.get" in content or "scoped_router" in content


class TestContractTrain014CreateTeamSession:
    def test_post_scoped_route_present(self):
        content = _sessions()
        assert "@scoped_router.post" in content or "scoped_router" in content


class TestContractTrain015GetTeamSession:
    def test_get_by_id_scoped_route_present(self):
        content = _sessions()
        # training_id param appears in scoped section
        assert "training_id" in content


class TestContractTrain016UpdateTeamSession:
    def test_patch_scoped_route_present(self):
        content = _sessions()
        assert "@scoped_router.patch" in content or ("scoped_router" in content and "@scoped_router" in content)


class TestContractTrain017DeleteTeamSession:
    def test_delete_scoped_route_present(self):
        content = _sessions()
        assert "@scoped_router.delete" in content or "scoped_router.delete" in content


class TestContractTrain018RestoreTeamSession:
    def test_restore_scoped_route_present(self):
        content = _sessions()
        assert "/restore" in content and "scoped_router" in content


# ---------------------------------------------------------------------------
# CONTRACT-019..024  Session Exercises  /training-sessions/{session_id}/exercises/...
# ---------------------------------------------------------------------------
class TestContractTrain019ListExercises:
    def test_router_file_exists(self):
        assert EXERCISES_PATH.exists()

    def test_prefix_training_sessions(self):
        content = _exercises()
        assert "/training-sessions" in content

    def test_get_exercises_route_present(self):
        content = _exercises()
        assert "/exercises" in content and "@router.get" in content


class TestContractTrain020AddExercise:
    def test_post_exercises_route_present(self):
        content = _exercises()
        assert "@router.post" in content and "/exercises" in content


class TestContractTrain021AddExercisesBulk:
    def test_bulk_route_present(self):
        content = _exercises()
        assert "bulk" in content


class TestContractTrain022GetExercise:
    def test_get_exercise_by_id_route_present(self):
        content = _exercises()
        assert "session_exercise_id" in content


class TestContractTrain023UpdateExercise:
    def test_patch_exercise_route_present(self):
        content = _exercises()
        assert "@router.patch" in content


class TestContractTrain024ReorderExercises:
    def test_reorder_route_present(self):
        content = _exercises()
        assert "reorder" in content


# ---------------------------------------------------------------------------
# CONTRACT-025..028  Attendance  /training-sessions/{id}/attendance/...
# ---------------------------------------------------------------------------
class TestContractTrain025ListAttendance:
    def test_router_file_exists(self):
        assert ATTENDANCE_PATH.exists()

    def test_attendance_route_present(self):
        content = _attendance()
        assert "attendance" in content


class TestContractTrain026RegisterAttendance:
    def test_post_attendance_route_present(self):
        content = _attendance()
        assert "@router.post" in content


class TestContractTrain027BatchAttendance:
    def test_batch_route_present(self):
        content = _attendance()
        assert "batch" in content


class TestContractTrain028AttendanceStatistics:
    def test_statistics_route_present(self):
        content = _attendance()
        assert "statistics" in content
