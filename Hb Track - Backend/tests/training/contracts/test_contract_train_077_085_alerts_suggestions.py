"""
CONTRACT-TRAIN-077..085 — Training Alerts & Suggestions Endpoints

SSOT: docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md

Status no SSOT: DIVERGENTE_DO_SSOT
  - CONTRACT-TRAIN-077: GET  /training/alerts-suggestions/alerts/team/{team_id}/active
  - CONTRACT-TRAIN-078: GET  /training/alerts-suggestions/alerts/team/{team_id}/history
  - CONTRACT-TRAIN-079: GET  /training/alerts-suggestions/alerts/team/{team_id}/stats
  - CONTRACT-TRAIN-080: POST /training/alerts-suggestions/alerts/{alert_id}/dismiss
  - CONTRACT-TRAIN-081: GET  /training/alerts-suggestions/suggestions/team/{team_id}/pending
  - CONTRACT-TRAIN-082: GET  /training/alerts-suggestions/suggestions/team/{team_id}/history
  - CONTRACT-TRAIN-083: GET  /training/alerts-suggestions/suggestions/team/{team_id}/stats
  - CONTRACT-TRAIN-084: POST /training/alerts-suggestions/suggestions/{suggestion_id}/apply
  - CONTRACT-TRAIN-085: POST /training/alerts-suggestions/suggestions/{suggestion_id}/dismiss

Estratégia: Testes estruturais DIVERGENTE_DO_SSOT — verificam que o router
`training_alerts_step18.py` define os caminhos conforme o SSOT. Servem como
sentinelas de drift: qualquer remoção ou renomeação de rota quebrará estes testes.
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
    / "training_alerts_step18.py"
)


class TestContractTrain077AlertsTeamActive:
    """CONTRACT-TRAIN-077: GET /training/alerts-suggestions/alerts/team/{team_id}/active"""

    def test_router_file_exists(self):
        """Verifica que o arquivo de router training_alerts_step18.py existe."""
        assert ROUTER_PATH.exists(), f"Router não encontrado: {ROUTER_PATH}"

    def test_router_prefix_is_alerts_suggestions(self):
        """Verifica que o router tem prefix '/training/alerts-suggestions'."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert "/training/alerts-suggestions" in content, (
            "Router training_alerts_step18.py deve ter prefix='/training/alerts-suggestions'"
        )

    def test_get_alerts_team_active_route_defined(self):
        """CONTRACT-TRAIN-077: verifica que /alerts/team/{team_id}/active está definido."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert '"/alerts/team/{team_id}/active"' in content or "'/alerts/team/{team_id}/active'" in content, (
            "CONTRACT-TRAIN-077: rota /alerts/team/{team_id}/active não encontrada"
        )

    def test_get_alerts_team_active_is_get_method(self):
        """CONTRACT-TRAIN-077: verifica que a rota usa método GET."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        match = re.search(
            r'@router\.get\s*\(\s*["\']\/alerts\/team\/\{team_id\}\/active["\']',
            content,
        )
        assert match, (
            "CONTRACT-TRAIN-077: @router.get('/alerts/team/{team_id}/active') não encontrado"
        )


class TestContractTrain078AlertsTeamHistory:
    """CONTRACT-TRAIN-078: GET /training/alerts-suggestions/alerts/team/{team_id}/history"""

    def test_get_alerts_team_history_route_defined(self):
        """CONTRACT-TRAIN-078: verifica que /alerts/team/{team_id}/history está definido."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert '"/alerts/team/{team_id}/history"' in content or "'/alerts/team/{team_id}/history'" in content, (
            "CONTRACT-TRAIN-078: rota /alerts/team/{team_id}/history não encontrada"
        )

    def test_get_alerts_team_history_is_get_method(self):
        """CONTRACT-TRAIN-078: verifica que a rota usa método GET."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        match = re.search(
            r'@router\.get\s*\(\s*["\']\/alerts\/team\/\{team_id\}\/history["\']',
            content,
        )
        assert match, (
            "CONTRACT-TRAIN-078: @router.get('/alerts/team/{team_id}/history') não encontrado"
        )


class TestContractTrain079AlertsTeamStats:
    """CONTRACT-TRAIN-079: GET /training/alerts-suggestions/alerts/team/{team_id}/stats"""

    def test_get_alerts_team_stats_route_defined(self):
        """CONTRACT-TRAIN-079: verifica que /alerts/team/{team_id}/stats está definido."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert '"/alerts/team/{team_id}/stats"' in content or "'/alerts/team/{team_id}/stats'" in content, (
            "CONTRACT-TRAIN-079: rota /alerts/team/{team_id}/stats não encontrada"
        )

    def test_get_alerts_team_stats_is_get_method(self):
        """CONTRACT-TRAIN-079: verifica que a rota usa método GET."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        match = re.search(
            r'@router\.get\s*\(\s*["\']\/alerts\/team\/\{team_id\}\/stats["\']',
            content,
        )
        assert match, (
            "CONTRACT-TRAIN-079: @router.get('/alerts/team/{team_id}/stats') não encontrado"
        )


class TestContractTrain080AlertsDismiss:
    """CONTRACT-TRAIN-080: POST /training/alerts-suggestions/alerts/{alert_id}/dismiss"""

    def test_post_alerts_dismiss_route_defined(self):
        """CONTRACT-TRAIN-080: verifica que /alerts/{alert_id}/dismiss está definido."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert '"/alerts/{alert_id}/dismiss"' in content or "'/alerts/{alert_id}/dismiss'" in content, (
            "CONTRACT-TRAIN-080: rota /alerts/{alert_id}/dismiss não encontrada"
        )

    def test_post_alerts_dismiss_is_post_method(self):
        """CONTRACT-TRAIN-080: verifica que a rota usa método POST."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        match = re.search(
            r'@router\.post\s*\(\s*["\']\/alerts\/\{alert_id\}\/dismiss["\']',
            content,
        )
        assert match, (
            "CONTRACT-TRAIN-080: @router.post('/alerts/{alert_id}/dismiss') não encontrado"
        )


class TestContractTrain081SuggestionsTeamPending:
    """CONTRACT-TRAIN-081: GET /training/alerts-suggestions/suggestions/team/{team_id}/pending"""

    def test_get_suggestions_team_pending_route_defined(self):
        """CONTRACT-TRAIN-081: verifica que /suggestions/team/{team_id}/pending está definido."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert '"/suggestions/team/{team_id}/pending"' in content or "'/suggestions/team/{team_id}/pending'" in content, (
            "CONTRACT-TRAIN-081: rota /suggestions/team/{team_id}/pending não encontrada"
        )

    def test_get_suggestions_team_pending_is_get_method(self):
        """CONTRACT-TRAIN-081: verifica que a rota usa método GET."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        match = re.search(
            r'@router\.get\s*\(\s*["\']\/suggestions\/team\/\{team_id\}\/pending["\']',
            content,
        )
        assert match, (
            "CONTRACT-TRAIN-081: @router.get('/suggestions/team/{team_id}/pending') não encontrado"
        )


class TestContractTrain082SuggestionsTeamHistory:
    """CONTRACT-TRAIN-082: GET /training/alerts-suggestions/suggestions/team/{team_id}/history"""

    def test_get_suggestions_team_history_route_defined(self):
        """CONTRACT-TRAIN-082: verifica que /suggestions/team/{team_id}/history está definido."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert '"/suggestions/team/{team_id}/history"' in content or "'/suggestions/team/{team_id}/history'" in content, (
            "CONTRACT-TRAIN-082: rota /suggestions/team/{team_id}/history não encontrada"
        )

    def test_get_suggestions_team_history_is_get_method(self):
        """CONTRACT-TRAIN-082: verifica que a rota usa método GET."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        match = re.search(
            r'@router\.get\s*\(\s*["\']\/suggestions\/team\/\{team_id\}\/history["\']',
            content,
        )
        assert match, (
            "CONTRACT-TRAIN-082: @router.get('/suggestions/team/{team_id}/history') não encontrado"
        )


class TestContractTrain083SuggestionsTeamStats:
    """CONTRACT-TRAIN-083: GET /training/alerts-suggestions/suggestions/team/{team_id}/stats"""

    def test_get_suggestions_team_stats_route_defined(self):
        """CONTRACT-TRAIN-083: verifica que /suggestions/team/{team_id}/stats está definido."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert '"/suggestions/team/{team_id}/stats"' in content or "'/suggestions/team/{team_id}/stats'" in content, (
            "CONTRACT-TRAIN-083: rota /suggestions/team/{team_id}/stats não encontrada"
        )

    def test_get_suggestions_team_stats_is_get_method(self):
        """CONTRACT-TRAIN-083: verifica que a rota usa método GET."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        match = re.search(
            r'@router\.get\s*\(\s*["\']\/suggestions\/team\/\{team_id\}\/stats["\']',
            content,
        )
        assert match, (
            "CONTRACT-TRAIN-083: @router.get('/suggestions/team/{team_id}/stats') não encontrado"
        )


class TestContractTrain084SuggestionsApply:
    """CONTRACT-TRAIN-084: POST /training/alerts-suggestions/suggestions/{suggestion_id}/apply"""

    def test_post_suggestions_apply_route_defined(self):
        """CONTRACT-TRAIN-084: verifica que /suggestions/{suggestion_id}/apply está definido."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert '"/suggestions/{suggestion_id}/apply"' in content or "'/suggestions/{suggestion_id}/apply'" in content, (
            "CONTRACT-TRAIN-084: rota /suggestions/{suggestion_id}/apply não encontrada"
        )

    def test_post_suggestions_apply_is_post_method(self):
        """CONTRACT-TRAIN-084: verifica que a rota usa método POST."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        match = re.search(
            r'@router\.post\s*\(\s*["\']\/suggestions\/\{suggestion_id\}\/apply["\']',
            content,
        )
        assert match, (
            "CONTRACT-TRAIN-084: @router.post('/suggestions/{suggestion_id}/apply') não encontrado"
        )


class TestContractTrain085SuggestionsDismiss:
    """CONTRACT-TRAIN-085: POST /training/alerts-suggestions/suggestions/{suggestion_id}/dismiss"""

    def test_post_suggestions_dismiss_route_defined(self):
        """CONTRACT-TRAIN-085: verifica que /suggestions/{suggestion_id}/dismiss está definido."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        assert '"/suggestions/{suggestion_id}/dismiss"' in content or "'/suggestions/{suggestion_id}/dismiss'" in content, (
            "CONTRACT-TRAIN-085: rota /suggestions/{suggestion_id}/dismiss não encontrada"
        )

    def test_post_suggestions_dismiss_is_post_method(self):
        """CONTRACT-TRAIN-085: verifica que a rota usa método POST."""
        content = ROUTER_PATH.read_text(encoding="utf-8")
        match = re.search(
            r'@router\.post\s*\(\s*["\']\/suggestions\/\{suggestion_id\}\/dismiss["\']',
            content,
        )
        assert match, (
            "CONTRACT-TRAIN-085: @router.post('/suggestions/{suggestion_id}/dismiss') não encontrado"
        )
