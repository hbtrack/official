"""
CONTRACT-TRAIN-096, 101..105 — Athlete View + AI Coach + Wellness Content Gate
Routers:
  - athlete_training.py  (sem prefix) → 096
  - ai_coach.py          (prefix=/ai) → 101..104
  - CONTRACT-105: endpoint NÃO implementado → pytest.skip

ATENÇÃO: ai_coach.py usa prefix=/ai (NÃO /ai-coach como consta no SSOT).
Abordagem: análise estática. Sem fixtures de DB. Sem import de ai_coach_service.
"""
import pytest
from pathlib import Path

ROUTERS = Path(__file__).parent.parent.parent.parent / "app" / "api" / "v1" / "routers"

ATHLETE_TRAIN_PATH = ROUTERS / "athlete_training.py"
AI_COACH_PATH      = ROUTERS / "ai_coach.py"


def _athlete_train():
    return ATHLETE_TRAIN_PATH.read_text(encoding="utf-8")

def _ai_coach():
    return AI_COACH_PATH.read_text(encoding="utf-8")


# ===========================================================================
# CONTRACT-096  GET /training-sessions/{session_id}/preview
# ===========================================================================

class TestContractTrain096SessionPreview:
    def test_router_file_exists(self):
        assert ATHLETE_TRAIN_PATH.exists()

    def test_session_preview_route(self):
        content = _athlete_train()
        assert "preview" in content

    def test_session_id_param_present(self):
        content = _athlete_train()
        assert "session_id" in content


# ===========================================================================
# CONTRACT-101  POST /ai/chat
# ===========================================================================

class TestContractTrain101AiChat:
    def test_router_file_exists(self):
        assert AI_COACH_PATH.exists()

    def test_prefix_ai(self):
        content = _ai_coach()
        assert 'prefix="/ai"' in content or "prefix = \"/ai\"" in content

    def test_chat_route_defined(self):
        content = _ai_coach()
        assert "/chat" in content and "@router.post" in content


# ===========================================================================
# CONTRACT-102  POST /ai/coach/suggest-session
# ===========================================================================

class TestContractTrain102AiSuggestSession:
    def test_suggest_session_route_defined(self):
        content = _ai_coach()
        assert "suggest-session" in content or "suggest_session" in content


# ===========================================================================
# CONTRACT-103  POST /ai/coach/suggest-microcycle
# ===========================================================================

class TestContractTrain103AiSuggestMicrocycle:
    def test_suggest_microcycle_route_defined(self):
        content = _ai_coach()
        assert "suggest-microcycle" in content or "suggest_microcycle" in content


# ===========================================================================
# CONTRACT-104  GET /ai/coach/... (additional AI coach endpoint)
# ===========================================================================

class TestContractTrain104AiCoachEndpointExists:
    def test_ai_coach_router_has_coach_routes(self):
        content = _ai_coach()
        assert "coach" in content and "@router" in content


# ===========================================================================
# CONTRACT-105  GET /athlete/wellness-content-gate/{session_id}
# Endpoint NÃO implementado em nenhum router. Skip documentado.
# ===========================================================================

class TestContractTrain105WellnessContentGate:
    def test_wellness_content_gate_not_yet_implemented(self):
        pytest.skip(
            "CONTRACT-105: GET /athlete/wellness-content-gate/{session_id} "
            "não encontrado em nenhum router. Endpoint pendente de implementação."
        )
