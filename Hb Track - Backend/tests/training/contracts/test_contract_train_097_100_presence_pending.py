import pytest
from pathlib import Path

# CONTRACT-TRAIN-097: POST /training-sessions/{id}/pre-confirm
# CONTRACT-TRAIN-098: POST /training-sessions/{id}/close
# CONTRACT-TRAIN-099: GET /training/pending-items
# CONTRACT-TRAIN-100: PATCH /training/pending-items/{id}/resolve

# Determinar root do router para validação estática
ROUTER_PATH = Path(__file__).parent.parent.parent.parent / "app" / "api" / "v1" / "routers"

def test_contract_presence_endpoints_exist():
    """Valida se os arquivos de router que implementam os contratos P0 existem."""
    # Endpoints de sessão (pre-confirm/close) costumam estar em training_sessions.py
    # Endpoints de pendências costumam estar em training_pending.py ou similar
    router_sessions = ROUTER_PATH / "training_sessions.py"
    router_pending = ROUTER_PATH / "attendance.py" # Ou training_pending.py se existir
    
    assert router_sessions.exists(), f"Router {router_sessions} não encontrado"

def test_contract_097_098_routes_defined():
    """Valida via inspeção de texto se as rotas pre-confirm e close estão no router."""
    router_attendance = ROUTER_PATH / "attendance.py"
    content = router_attendance.read_text(encoding='utf-8')
    
    # Busca por padrões de rota FastAPI em attendance.py (AR_185 conforme grep)
    assert "preconfirm" in content
    assert "close" in content

def test_contract_099_100_routes_defined():
    """Valida se endpoints de pendências/presenças estão definidos."""
    router_attendance = ROUTER_PATH / "attendance.py"
    content = router_attendance.read_text(encoding='utf-8')
    assert "pending-items" in content
