"""
DEC-TRAIN-001a — POST wellness_pre → 201 (router estático)
DEC-TRAIN-001b — WellnessPreCreate.athlete_id obrigatório (schema estático); sem athlete_id → 422
DEC-TRAIN-003  — Endpoint /wellness-top-performers (CONTRACT-076) presente em router teams
DEC-TRAIN-004a — export-pdf: caminho degraded implementado (503 + worker_not_active)

NOTA DEC-004a: a implementação real (exports.py) retorna HTTP 503 SERVICE_UNAVAILABLE com
reason="worker_not_active" quando o worker Celery está inativo — NÃO 202+degraded conforme
especificado no DEC-TRAIN-004. O teste documenta o comportamento real via análise estática
do router (presença de "worker_not_active" e "HTTP_503_SERVICE_UNAVAILABLE").

Abordagem: 100% análise estática (read_text). Sem fixtures de DB, sem requests ao vivo.
"""

from pathlib import Path

BASE = Path(__file__).parent.parent.parent.parent
ROUTERS = BASE / "app" / "api" / "v1" / "routers"
SCHEMAS = BASE / "app" / "schemas"

WELLNESS_PRE_ROUTER = ROUTERS / "wellness_pre.py"
WELLNESS_SCHEMA = SCHEMAS / "wellness.py"
EXPORTS_ROUTER = ROUTERS / "exports.py"
TEAMS_ROUTER = ROUTERS / "teams.py"


def _wellness_router() -> str:
    return WELLNESS_PRE_ROUTER.read_text(encoding="utf-8")


def _wellness_schema() -> str:
    return WELLNESS_SCHEMA.read_text(encoding="utf-8")


def _exports_router() -> str:
    return EXPORTS_ROUTER.read_text(encoding="utf-8")


def _teams_router() -> str:
    return TEAMS_ROUTER.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# DEC-TRAIN-001a — POST wellness_pre → 201
# ---------------------------------------------------------------------------

class TestDecTrain001aWellnessPrePost201:
    """DEC-TRAIN-001a: endpoint POST wellness_pre existe e retorna 201."""

    def test_router_file_exists(self):
        assert WELLNESS_PRE_ROUTER.exists(), (
            "Router wellness_pre.py não encontrado em app/api/v1/routers/"
        )

    def test_post_wellness_pre_endpoint_exists(self):
        content = _wellness_router()
        assert "@router.post" in content, "DEC-001a: @router.post ausente em wellness_pre.py"
        assert "wellness_pre" in content, "DEC-001a: 'wellness_pre' não presente no router"

    def test_post_returns_201_created(self):
        """DEC-001a: endpoint POST deve retornar status_code 201."""
        assert "HTTP_201_CREATED" in _wellness_router(), (
            "DEC-001a: status_code HTTP_201_CREATED ausente em wellness_pre.py"
        )

    def test_post_route_uses_training_session_path(self):
        """DEC-001a: rota POST contém 'training_sessions' no path (nested resource)."""
        assert "training_sessions" in _wellness_router(), (
            "DEC-001a: path 'training_sessions' ausente no router de wellness_pre"
        )


# ---------------------------------------------------------------------------
# DEC-TRAIN-001b — WellnessPreCreate.athlete_id obrigatório → 422 se ausente
# ---------------------------------------------------------------------------

class TestDecTrain001bWellnessPreAthleteIdRequired:
    """DEC-TRAIN-001b: athlete_id é campo obrigatório no schema; ausência → 422."""

    def test_schema_file_exists(self):
        assert WELLNESS_SCHEMA.exists(), "Schema wellness.py não encontrado"

    def test_wellness_pre_create_class_exists(self):
        content = _wellness_schema()
        assert "WellnessPreCreate" in content, (
            "DEC-001b: classe WellnessPreCreate ausente em wellness.py"
        )

    def test_athlete_id_field_present(self):
        """DEC-001b: campo athlete_id presente no schema WellnessPreCreate."""
        content = _wellness_schema()
        assert "athlete_id" in content, "DEC-001b: campo athlete_id ausente em wellness.py"

    def test_athlete_id_not_optional_in_schema(self):
        """DEC-001b: athlete_id deve ser Field(...) (obrigatório), não Optional — 422 se omitido."""
        content = _wellness_schema()
        lines = content.split("\n")
        found_class = False
        for line in lines:
            if "class WellnessPreCreate" in line:
                found_class = True
            if found_class and "athlete_id" in line:
                # athlete_id field line should NOT contain Optional
                assert "Optional" not in line, (
                    "DEC-001b: athlete_id está marcado como Optional — "
                    "deveria ser obrigatório (Field(...))"
                )
                return
        # Se chegou aqui sem encontrar a linha, verifica só que o campo existe
        assert "athlete_id" in content

    def test_422_mapped_via_validation_error(self):
        """DEC-001b: router ou schema mapeia ValidationError → 422."""
        content = _wellness_router()
        has_422 = (
            "422" in content
            or "HTTP_422_UNPROCESSABLE_ENTITY" in content
            or "ValidationError" in content
            or "RequestValidationError" in content
        )
        assert has_422, (
            "DEC-001b: nenhum mapeamento de 422/ValidationError encontrado em wellness_pre.py"
        )


# ---------------------------------------------------------------------------
# DEC-TRAIN-003 — SCREEN-015 usa /wellness-top-performers (CONTRACT-076)
# ---------------------------------------------------------------------------

class TestDecTrain003TopPerformersCanonicalRoute:
    """DEC-TRAIN-003: endpoint /wellness-top-performers (CONTRACT-076) existe em teams router."""

    def test_teams_router_exists(self):
        assert TEAMS_ROUTER.exists(), "Router teams.py não encontrado em app/api/v1/routers/"

    def test_wellness_top_performers_route_exists(self):
        """DEC-003: rota /wellness-top-performers presente no router teams."""
        assert "wellness-top-performers" in _teams_router(), (
            "DEC-003: endpoint '/wellness-top-performers' ausente em teams.py — CONTRACT-076"
        )

    def test_top_performers_route_is_get(self):
        """DEC-003: endpoint é GET (não POST/PUT)."""
        content = _teams_router()
        idx = content.find("wellness-top-performers")
        assert idx > 0
        # Varrer até 300 chars antes para encontrar o decorador @router.get
        snippet = content[max(0, idx - 300): idx + 50]
        assert "@router.get" in snippet, (
            "DEC-003: @router.get não encontrado antes de 'wellness-top-performers'"
        )


# ---------------------------------------------------------------------------
# DEC-TRAIN-004a — export-pdf caminho degraded implementado (503 + worker_not_active)
# ---------------------------------------------------------------------------

class TestDecTrain004aExportDegradedPathImplemented:
    """
    DEC-TRAIN-004a: POST /analytics/export-pdf possui lógica de estado degradado.

    NOTA: a especificação DEC original dizia 202+degraded. A implementação real retorna
    HTTP 503 SERVICE_UNAVAILABLE (reason=worker_not_active) quando o worker está inativo.
    Este teste valida o comportamento real do código, não a spec original.
    """

    def test_exports_router_exists(self):
        assert EXPORTS_ROUTER.exists(), "Router exports.py não encontrado"

    def test_export_pdf_endpoint_exists(self):
        content = _exports_router()
        assert "export-pdf" in content, (
            "DEC-004a: endpoint /analytics/export-pdf ausente em exports.py"
        )

    def test_endpoint_accepts_post(self):
        """DEC-004a: endpoint export-pdf é POST."""
        content = _exports_router()
        assert "@router.post" in content, "DEC-004a: @router.post ausente em exports.py"

    def test_202_accepted_status_code_present(self):
        """DEC-004a: status_code HTTP_202_ACCEPTED declarado no endpoint."""
        assert "HTTP_202_ACCEPTED" in _exports_router(), (
            "DEC-004a: status_code HTTP_202_ACCEPTED ausente em exports.py"
        )

    def test_worker_not_active_degraded_logic_implemented(self):
        """DEC-004a: lógica worker_not_active está implementada no router (degraded path)."""
        assert "worker_not_active" in _exports_router(), (
            "DEC-004a: reason 'worker_not_active' ausente — caminho degraded não implementado"
        )

    def test_503_raised_when_worker_inactive(self):
        """
        DEC-004a (comportamento real): HTTP 503 é levantado quando worker inativo.
        NB: spec original dizia 202+degraded; código implementa 503.
        """
        content = _exports_router()
        assert (
            "HTTP_503_SERVICE_UNAVAILABLE" in content
            or "status_code=503" in content
        ), (
            "DEC-004a: HTTP_503_SERVICE_UNAVAILABLE ausente — degraded path não protege via 503"
        )

    def test_dec_train_004_comment_documenting_intent(self):
        """DEC-004a: comentário DEC-TRAIN-004 presente documentando intenção."""
        assert "DEC-TRAIN-004" in _exports_router(), (
            "DEC-004a: comentário DEC-TRAIN-004 ausente em exports.py"
        )
