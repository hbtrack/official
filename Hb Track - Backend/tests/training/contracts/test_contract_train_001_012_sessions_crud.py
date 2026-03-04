"""
CONTRACT-TRAIN-001..012 — Training Sessions CRUD
Router: training_sessions.py (unscoped router, montado em /training-sessions)

Abordagem: análise estática — verifica existência do arquivo e presença
dos padrões de rota. Sem fixtures de DB.
"""
from pathlib import Path

ROUTER_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "app" / "api" / "v1" / "routers" / "training_sessions.py"
)


def _content() -> str:
    return ROUTER_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# CONTRACT-001  GET /training-sessions
# ---------------------------------------------------------------------------
class TestContractTrain001ListSessions:
    def test_router_file_exists(self):
        assert ROUTER_PATH.exists(), f"Router não encontrado: {ROUTER_PATH}"

    def test_get_list_route_defined(self):
        content = _content()
        assert "@router.get" in content
        # rota raiz "" (lista)
        assert '""' in content or "\"\"" in content


# ---------------------------------------------------------------------------
# CONTRACT-002  POST /training-sessions
# ---------------------------------------------------------------------------
class TestContractTrain002CreateSession:
    def test_post_create_route_defined(self):
        content = _content()
        assert "@router.post" in content


# ---------------------------------------------------------------------------
# CONTRACT-003  GET /training-sessions/{id}
# ---------------------------------------------------------------------------
class TestContractTrain003GetSession:
    def test_get_by_id_route_defined(self):
        content = _content()
        assert "training_session_id" in content or "/{id}" in content or "/{training_session_id}" in content


# ---------------------------------------------------------------------------
# CONTRACT-004  PATCH /training-sessions/{id}
# ---------------------------------------------------------------------------
class TestContractTrain004UpdateSession:
    def test_patch_route_defined(self):
        content = _content()
        assert "@router.patch" in content


# ---------------------------------------------------------------------------
# CONTRACT-005  DELETE /training-sessions/{id}
# ---------------------------------------------------------------------------
class TestContractTrain005DeleteSession:
    def test_delete_route_defined(self):
        content = _content()
        assert "@router.delete" in content


# ---------------------------------------------------------------------------
# CONTRACT-006  POST /training-sessions/{id}/restore
# ---------------------------------------------------------------------------
class TestContractTrain006RestoreSession:
    def test_restore_route_defined(self):
        content = _content()
        assert "/restore" in content


# ---------------------------------------------------------------------------
# CONTRACT-007  POST /training-sessions/{id}/publish
# ---------------------------------------------------------------------------
class TestContractTrain007PublishSession:
    def test_publish_route_defined(self):
        content = _content()
        assert "/publish" in content


# ---------------------------------------------------------------------------
# CONTRACT-008  POST /training-sessions/{id}/close
# ---------------------------------------------------------------------------
class TestContractTrain008CloseSession:
    def test_close_route_defined(self):
        content = _content()
        assert "/close" in content


# ---------------------------------------------------------------------------
# CONTRACT-009  GET /training-sessions/{id}/deviation
# ---------------------------------------------------------------------------
class TestContractTrain009DeviationSession:
    def test_deviation_route_defined(self):
        content = _content()
        assert "/deviation" in content


# ---------------------------------------------------------------------------
# CONTRACT-010  GET /training-sessions/{id}/wellness-status
# ---------------------------------------------------------------------------
class TestContractTrain010WellnessStatus:
    def test_wellness_status_route_defined(self):
        content = _content()
        assert "wellness-status" in content


# ---------------------------------------------------------------------------
# CONTRACT-011  POST /training-sessions/{id}/duplicate
# ---------------------------------------------------------------------------
class TestContractTrain011DuplicateSession:
    def test_duplicate_route_defined(self):
        content = _content()
        assert "/duplicate" in content


# ---------------------------------------------------------------------------
# CONTRACT-012  POST /training-sessions/copy-week
# ---------------------------------------------------------------------------
class TestContractTrain012CopyWeek:
    def test_copy_week_route_defined(self):
        content = _content()
        assert "copy-week" in content
