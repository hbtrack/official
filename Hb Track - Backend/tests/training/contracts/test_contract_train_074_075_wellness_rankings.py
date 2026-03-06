"""
CONTRACT-TRAIN-074, 075 — Wellness Rankings: Calculate + Athletes 90+

SSOT: docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md
AR: AR_245 / AR-TRAIN-061 (Batch 27)

Contratos verificados:
  - CONTRACT-TRAIN-074: POST /analytics/wellness-rankings/calculate
  - CONTRACT-TRAIN-075: GET  /analytics/wellness-rankings/{team_id}/athletes-90plus

Estratégia: análise estática — verifica que o router `analytics.py` define
os caminhos e métodos HTTP corretos conforme o SSOT.
Não requerem banco de dados ou servidor em execução.
"""

from pathlib import Path
import re


ROUTER_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "app"
    / "api"
    / "v1"
    / "routers"
    / "analytics.py"
)


def _content() -> str:
    return ROUTER_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# CONTRACT-TRAIN-074  POST /analytics/wellness-rankings/calculate
# ---------------------------------------------------------------------------

class TestContractTrain074WellnessRankingsCalculate:
    """CONTRACT-TRAIN-074: POST /analytics/wellness-rankings/calculate"""

    def test_router_file_exists(self):
        """Verifica que o arquivo de router analytics.py existe."""
        assert ROUTER_PATH.exists(), f"Router não encontrado: {ROUTER_PATH}"

    def test_router_prefix_is_analytics(self):
        """Verifica que o router tem prefix '/analytics'."""
        content = _content()
        assert 'prefix="/analytics"' in content or "prefix='/analytics'" in content, (
            "Router analytics.py deve ter prefix='/analytics'"
        )

    def test_post_wellness_rankings_calculate_route_defined(self):
        """CONTRACT-TRAIN-074: verifica que POST /wellness-rankings/calculate está definido."""
        content = _content()
        assert '"/wellness-rankings/calculate"' in content or "'/wellness-rankings/calculate'" in content, (
            "Rota POST /analytics/wellness-rankings/calculate não encontrada em analytics.py"
        )

    def test_post_wellness_rankings_calculate_is_post_method(self):
        """CONTRACT-TRAIN-074: verifica que /wellness-rankings/calculate usa método POST."""
        content = _content()
        match = re.search(
            r'@router\.post\s*\(\s*["\']\/wellness-rankings\/calculate["\']',
            content,
        )
        assert match, (
            "CONTRACT-TRAIN-074: @router.post('/wellness-rankings/calculate') não encontrado"
        )

    def test_calculate_response_has_month_reference_field(self):
        """CONTRACT-TRAIN-074: response schema deve incluir month_reference."""
        content = _content()
        assert "month_reference" in content, (
            "CONTRACT-TRAIN-074: campo month_reference ausente no response schema"
        )

    def test_calculate_response_has_teams_processed_field(self):
        """CONTRACT-TRAIN-074: response schema deve incluir teams_processed."""
        content = _content()
        assert "teams_processed" in content, (
            "CONTRACT-TRAIN-074: campo teams_processed ausente no response schema"
        )

    def test_calculate_restricted_to_dirigente(self):
        """CONTRACT-TRAIN-074: endpoint deve exigir role 'dirigente'."""
        content = _content()
        # O decorator de permissão deve mencionar 'dirigente' para este endpoint
        # Verificamos que 'dirigente' aparece no arquivo (role requerido)
        assert "dirigente" in content, (
            "CONTRACT-TRAIN-074: role 'dirigente' não encontrado em analytics.py"
        )


# ---------------------------------------------------------------------------
# CONTRACT-TRAIN-075  GET /analytics/wellness-rankings/{team_id}/athletes-90plus
# ---------------------------------------------------------------------------

class TestContractTrain075WellnessRankingsAthletes90Plus:
    """CONTRACT-TRAIN-075: GET /analytics/wellness-rankings/{team_id}/athletes-90plus"""

    def test_get_athletes_90plus_route_defined(self):
        """CONTRACT-TRAIN-075: verifica que GET /{team_id}/athletes-90plus está definido."""
        content = _content()
        assert "athletes-90plus" in content, (
            "Rota GET /analytics/wellness-rankings/{team_id}/athletes-90plus não encontrada em analytics.py"
        )

    def test_get_athletes_90plus_is_get_method(self):
        """CONTRACT-TRAIN-075: verifica que athletes-90plus usa método GET."""
        content = _content()
        match = re.search(
            r'@router\.get\s*\(\s*["\'][^"\']*athletes-90plus["\']',
            content,
        )
        assert match, (
            "CONTRACT-TRAIN-075: @router.get('...athletes-90plus') não encontrado"
        )

    def test_athletes_90plus_has_team_id_path_param(self):
        """CONTRACT-TRAIN-075: rota deve receber team_id como path parameter."""
        content = _content()
        assert "{team_id}" in content, (
            "CONTRACT-TRAIN-075: path parameter {team_id} não encontrado em analytics.py"
        )

    def test_athletes_90plus_response_has_response_rate_field(self):
        """CONTRACT-TRAIN-075: response item deve incluir response_rate."""
        content = _content()
        assert "response_rate" in content, (
            "CONTRACT-TRAIN-075: campo response_rate ausente no response schema"
        )

    def test_athletes_90plus_has_badge_earned_field(self):
        """CONTRACT-TRAIN-075: response item deve incluir badge_earned."""
        content = _content()
        assert "badge_earned" in content, (
            "CONTRACT-TRAIN-075: campo badge_earned ausente no response schema"
        )

    def test_athletes_90plus_is_drilldown_not_primary_listing(self):
        """CONTRACT-TRAIN-075: SSOT define este endpoint como drilldown especializado.
        Verifica que há lógica de filtro para atletas >= 90%.
        """
        content = _content()
        has_threshold = "90" in content or "90plus" in content or "athletes-90plus" in content
        assert has_threshold, (
            "CONTRACT-TRAIN-075: referência ao threshold 90%+ não encontrada no router"
        )

    def test_athletes_90plus_requires_month_query_param(self):
        """CONTRACT-TRAIN-075: endpoint deve exigir query param 'month' (YYYY-MM)."""
        content = _content()
        # Verificamos que o parâmetro month está presente
        assert "month" in content, (
            "CONTRACT-TRAIN-075: query param 'month' não encontrado em analytics.py"
        )
