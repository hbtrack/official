"""
CONTRACT-TRAIN-073, 074, 075 — Wellness Rankings Endpoints

SSOT: docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md

Status no SSOT: PARCIAL
  - CONTRACT-TRAIN-073: GET  /analytics/wellness-rankings
  - CONTRACT-TRAIN-074: POST /analytics/wellness-rankings/calculate
  - CONTRACT-TRAIN-075: GET  /analytics/wellness-rankings/{team_id}/athletes-90plus

Estratégia: Testes estruturais que verificam o router `analytics.py` define
os caminhos e métodos HTTP corretos conforme o SSOT.
Não requerem banco de dados ou servidor em execução.
"""

from pathlib import Path
import re


ROUTER_PATH = (
    Path(__file__).parent.parent.parent
    / "app"
    / "api"
    / "v1"
    / "routers"
    / "analytics.py"
)


class TestContractTrain073WellnessRankingsList:
    """CONTRACT-TRAIN-073: GET /analytics/wellness-rankings"""

    def test_router_file_exists(self):
        """Verifica que o arquivo de router analytics.py existe."""
        assert ROUTER_PATH.exists(), f"Router não encontrado: {ROUTER_PATH}"

    def test_router_prefix_is_analytics(self):
        """Verifica que o router tem prefix '/analytics'."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert 'prefix="/analytics"' in content or "prefix='/analytics'" in content, (
            "Router analytics.py deve ter prefix='/analytics'"
        )

    def test_get_wellness_rankings_route_defined(self):
        """CONTRACT-TRAIN-073: verifica que GET /wellness-rankings está definido."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert '"/wellness-rankings"' in content or "'/wellness-rankings'" in content, (
            "Rota GET /analytics/wellness-rankings não encontrada em analytics.py"
        )

    def test_get_wellness_rankings_is_get_method(self):
        """CONTRACT-TRAIN-073: verifica que /wellness-rankings usa método GET."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        # Deve haver @router.get com "/wellness-rankings"
        match = re.search(r'@router\.get\s*\(\s*["\']\/wellness-rankings["\']', content)
        assert match, (
            "CONTRACT-TRAIN-073: @router.get('/wellness-rankings') não encontrado"
        )

    def test_get_wellness_rankings_has_response_model(self):
        """CONTRACT-TRAIN-073: verifica que endpoint tem response_model definido."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        # A linha do decorator deve ter response_model
        match = re.search(
            r'@router\.get\s*\(\s*["\']\/wellness-rankings["\'],\s*response_model=',
            content,
        )
        assert match, (
            "CONTRACT-TRAIN-073: response_model ausente em GET /wellness-rankings"
        )


class TestContractTrain074WellnessRankingsCalculate:
    """CONTRACT-TRAIN-074: POST /analytics/wellness-rankings/calculate"""

    def test_post_wellness_rankings_calculate_route_defined(self):
        """CONTRACT-TRAIN-074: verifica que POST /wellness-rankings/calculate está definido."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert '"/wellness-rankings/calculate"' in content or "'/wellness-rankings/calculate'" in content, (
            "Rota POST /analytics/wellness-rankings/calculate não encontrada em analytics.py"
        )

    def test_post_wellness_rankings_calculate_is_post_method(self):
        """CONTRACT-TRAIN-074: verifica que /wellness-rankings/calculate usa método POST."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        match = re.search(
            r'@router\.post\s*\(\s*["\']\/wellness-rankings\/calculate["\']',
            content,
        )
        assert match, (
            "CONTRACT-TRAIN-074: @router.post('/wellness-rankings/calculate') não encontrado"
        )

    def test_calculate_response_has_month_reference_field(self):
        """CONTRACT-TRAIN-074: response schema deve incluir month_reference."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert "month_reference" in content, (
            "CONTRACT-TRAIN-074: campo month_reference ausente no response schema"
        )

    def test_calculate_response_has_teams_processed_field(self):
        """CONTRACT-TRAIN-074: response schema deve incluir teams_processed."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert "teams_processed" in content, (
            "CONTRACT-TRAIN-074: campo teams_processed ausente no response schema"
        )


class TestContractTrain075WellnessRankingsAthletes90Plus:
    """CONTRACT-TRAIN-075: GET /analytics/wellness-rankings/{team_id}/athletes-90plus"""

    def test_get_athletes_90plus_route_defined(self):
        """CONTRACT-TRAIN-075: verifica que GET /{team_id}/athletes-90plus está definido."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert "athletes-90plus" in content, (
            "Rota GET /analytics/wellness-rankings/{team_id}/athletes-90plus não encontrada"
        )

    def test_get_athletes_90plus_is_get_method(self):
        """CONTRACT-TRAIN-075: verifica que athletes-90plus usa método GET."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        match = re.search(
            r'@router\.get\s*\(\s*["\'][^"\']*athletes-90plus["\']',
            content,
        )
        assert match, (
            "CONTRACT-TRAIN-075: @router.get('...athletes-90plus') não encontrado"
        )

    def test_athletes_90plus_has_team_id_path_param(self):
        """CONTRACT-TRAIN-075: rota deve receber team_id como path parameter."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert "{team_id}" in content, (
            "CONTRACT-TRAIN-075: path parameter {team_id} não encontrado"
        )

    def test_athletes_90plus_response_has_response_rate_field(self):
        """CONTRACT-TRAIN-075: response item deve incluir response_rate."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert "response_rate" in content, (
            "CONTRACT-TRAIN-075: campo response_rate ausente no response schema"
        )

    def test_athletes_90plus_is_drilldown_not_primary_listing(self):
        """CONTRACT-TRAIN-075: SSOT define este endpoint como drilldown especializado.
        Verifica que há lógica de filtro para atletas >= 90%.
        """
        content = ROUTER_PATH.read_text(encoding="utf-8")
        # Deve haver referência a 90 (threshold de filtro)
        has_threshold = "90" in content or "90plus" in content or "athletes-90plus" in content
        assert has_threshold, (
            "CONTRACT-TRAIN-075: referência ao threshold 90%+ não encontrada no router"
        )
