"""
CONTRACT-TRAIN-029..039 — Wellness Pré-treino e Pós-treino
Routers:
  - wellness_pre.py  (sem prefix dedicado) → 029..034
  - wellness_post.py (sem prefix dedicado) → 035..039

Abordagem: análise estática. Sem fixtures de DB. INV-057/058: DB não disponível em CI.
"""
from pathlib import Path

ROUTERS = Path(__file__).parent.parent.parent.parent / "app" / "api" / "v1" / "routers"

WELLNESS_PRE_PATH  = ROUTERS / "wellness_pre.py"
WELLNESS_POST_PATH = ROUTERS / "wellness_post.py"


def _pre():
    return WELLNESS_PRE_PATH.read_text(encoding="utf-8")

def _post():
    return WELLNESS_POST_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# CONTRACT-029  GET /training_sessions/{id}/wellness_pre
# ---------------------------------------------------------------------------
class TestContractTrain029ListWellnessPre:
    def test_router_file_exists(self):
        assert WELLNESS_PRE_PATH.exists()

    def test_get_list_wellness_pre_route(self):
        content = _pre()
        assert "wellness_pre" in content
        assert "@router.get" in content
        assert "/training_sessions/" in content


# ---------------------------------------------------------------------------
# CONTRACT-030  POST /training_sessions/{id}/wellness_pre
# ---------------------------------------------------------------------------
class TestContractTrain030CreateWellnessPre:
    def test_post_wellness_pre_route(self):
        content = _pre()
        assert "@router.post" in content
        assert "/training_sessions/" in content and "wellness_pre" in content


# ---------------------------------------------------------------------------
# CONTRACT-031  GET /wellness_pre/{wellness_pre_id}
# ---------------------------------------------------------------------------
class TestContractTrain031GetWellnessPre:
    def test_get_by_id_wellness_pre_route(self):
        content = _pre()
        assert "/wellness_pre/{wellness_pre_id}" in content


# ---------------------------------------------------------------------------
# CONTRACT-031 IMPL — GET /wellness_pre/{wellness_pre_id} — impl quality guard
# ---------------------------------------------------------------------------
class TestContractTrain031ImplWellnessPre:
    def test_get_by_id_is_async(self):
        """Endpoint nao pode ser def sync (bug pre-AR_253)."""
        content = _pre()
        assert "async def get_wellness_pre_by_id" in content

    def test_get_by_id_has_auth(self):
        """Endpoint deve exigir autenticacao (get_current_user)."""
        content = _pre()
        assert "get_current_user" in content

    def test_get_by_id_calls_service(self):
        """Endpoint deve delegar ao WellnessPreService.get_wellness_pre_by_id."""
        content = _pre()
        assert "get_wellness_pre_by_id" in content
        assert "WellnessPreService" in content


# ---------------------------------------------------------------------------
# CONTRACT-032  PATCH /wellness_pre/{wellness_pre_id}
# ---------------------------------------------------------------------------
class TestContractTrain032UpdateWellnessPre:
    def test_patch_wellness_pre_route(self):
        content = _pre()
        assert "@router.patch" in content
        assert "wellness_pre_id" in content


# ---------------------------------------------------------------------------
# CONTRACT-032 IMPL — PATCH /wellness_pre/{wellness_pre_id} — impl quality guard
# ---------------------------------------------------------------------------
class TestContractTrain032ImplUpdateWellnessPre:
    def test_update_is_async(self):
        """Endpoint nao pode ser def sync (bug pre-AR_253)."""
        content = _pre()
        assert "async def update_wellness_pre" in content

    def test_update_has_auth(self):
        """Endpoint deve exigir autenticacao."""
        content = _pre()
        assert "get_current_user" in content

    def test_update_calls_service(self):
        """Endpoint deve delegar ao WellnessPreService.update_wellness_pre_by_id."""
        content = _pre()
        assert "update_wellness_pre_by_id" in content

    def test_update_commits(self):
        """Endpoint PATCH deve fazer commit apos edicao bem sucedida."""
        content = _pre()
        assert "await db.commit()" in content or "db.commit()" in content


# ---------------------------------------------------------------------------
# CONTRACT-033  GET /training_sessions/{id}/wellness_pre/status
# ---------------------------------------------------------------------------
class TestContractTrain033WellnessPreStatus:
    def test_wellness_pre_status_route(self):
        content = _pre()
        assert "wellness_pre/status" in content or "/wellness_pre/status" in content


# ---------------------------------------------------------------------------
# CONTRACT-034  POST /wellness_pre/{id}/request-unlock
# ---------------------------------------------------------------------------
class TestContractTrain034WellnessPreRequestUnlock:
    def test_request_unlock_route(self):
        content = _pre()
        assert "request-unlock" in content


# ---------------------------------------------------------------------------
# CONTRACT-035  GET /training_sessions/{id}/wellness_post
# ---------------------------------------------------------------------------
class TestContractTrain035ListWellnessPost:
    def test_router_file_exists(self):
        assert WELLNESS_POST_PATH.exists()

    def test_get_list_wellness_post_route(self):
        content = _post()
        assert "wellness_post" in content
        assert "@router.get" in content
        assert "/training_sessions/" in content


# ---------------------------------------------------------------------------
# CONTRACT-036  POST /training_sessions/{id}/wellness_post
# ---------------------------------------------------------------------------
class TestContractTrain036CreateWellnessPost:
    def test_post_wellness_post_route(self):
        content = _post()
        assert "@router.post" in content
        assert "/training_sessions/" in content and "wellness_post" in content


# ---------------------------------------------------------------------------
# CONTRACT-037  GET /wellness_post/{wellness_post_id}
# ---------------------------------------------------------------------------
class TestContractTrain037GetWellnessPost:
    def test_get_by_id_wellness_post_route(self):
        content = _post()
        assert "/wellness_post/{wellness_post_id}" in content


# ---------------------------------------------------------------------------
# CONTRACT-037 IMPL — GET /wellness_post/{wellness_post_id} — impl quality guard
# ---------------------------------------------------------------------------
class TestContractTrain037ImplWellnessPost:
    def test_get_by_id_is_async(self):
        """Endpoint deve ser async def."""
        content = _post()
        assert "async def get_wellness_post_by_id" in content

    def test_get_by_id_has_auth(self):
        """Endpoint deve exigir autenticacao."""
        content = _post()
        assert "get_current_user" in content

    def test_get_by_id_calls_service(self):
        """Endpoint deve delegar ao WellnessPostService.get_wellness_post_by_id."""
        content = _post()
        assert "get_wellness_post_by_id" in content
        assert "WellnessPostService" in content


# ---------------------------------------------------------------------------
# CONTRACT-038  PATCH /wellness_post/{wellness_post_id}
# ---------------------------------------------------------------------------
class TestContractTrain038UpdateWellnessPost:
    def test_patch_wellness_post_route(self):
        content = _post()
        assert "@router.patch" in content
        assert "wellness_post_id" in content


# ---------------------------------------------------------------------------
# CONTRACT-038 IMPL — PATCH /wellness_post/{wellness_post_id} — impl quality guard
# ---------------------------------------------------------------------------
class TestContractTrain038ImplUpdateWellnessPost:
    def test_update_is_async(self):
        """Endpoint nao pode ser def sync (bug pre-AR_253)."""
        content = _post()
        assert "async def update_wellness_post" in content

    def test_update_has_auth(self):
        """Endpoint deve exigir autenticacao."""
        content = _post()
        assert "get_current_user" in content

    def test_update_calls_service(self):
        """Endpoint deve delegar ao WellnessPostService.update_wellness_post_by_id."""
        content = _post()
        assert "update_wellness_post_by_id" in content

    def test_update_commits(self):
        """Endpoint PATCH deve fazer commit."""
        content = _post()
        assert "await db.commit()" in content or "db.commit()" in content


# ---------------------------------------------------------------------------
# CONTRACT-039  GET /training_sessions/{id}/wellness_post/status
# ---------------------------------------------------------------------------
class TestContractTrain039WellnessPostStatus:
    def test_wellness_post_status_route(self):
        content = _post()
        assert "wellness_post/status" in content or "/wellness_post/status" in content
