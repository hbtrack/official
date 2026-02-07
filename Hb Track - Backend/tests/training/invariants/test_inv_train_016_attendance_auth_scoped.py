"""
INV-TRAIN-016 — Attendance: rota base exige auth; rota scoped não exposta

Enunciado: Rota base de attendance exige autenticação obrigatória (HTTPBearer).
Rota scoped (teams/{team_id}/trainings/{id}/attendance) não deve estar exposta.

Evidência:
- Router: app/api/v1/routers/attendance.py:57 (Depends(get_current_user))
- OpenAPI: security=[{"HTTPBearer": []}] para endpoint attendance
- Agregador: app/api/v1/api.py:184-186 (inclui attendance.router, não attendance_scoped)

Obrigação A: Analisei o router e agregador. Para testar:
  1. Endpoint: /api/v1/training_sessions/{training_session_id}/attendance
  2. Guard: Depends(get_current_user) (Âncora: attendance.py linha 57)
  3. Rota scoped: /api/v1/teams/{team_id}/trainings/{id}/attendance (não exposta)
  4. Evidência: api.py não inclui attendance_scoped.router

Obrigação B: Invariante alvo: list_attendance_by_session_api_v1_training_sessions__training_session_id__attendance_get (Router/Auth).
  * OperationId: list_attendance_by_session_api_v1_training_sessions__training_session_id__attendance_get
  * Oráculo: 401 (sem auth), 404 (rota scoped não exposta), autenticado retorna !=401 (200 ou 404 por ID inexistente)
  * Estratégia: TestClient sem/com auth, assert status_code
"""
import pytest
from uuid import uuid4


class TestInvTrain016AttendanceAuthScoped:
    """
    INV-TRAIN-016: Attendance base route requires auth; scoped route not exposed
    """
    
    def test_attendance_route_without_auth_returns_401(self, client):
        """
        Caso 1 (inválido): POST /training_sessions/{id}/attendance sem auth deve retornar 401
        
        Validação: Rota base exige autenticação obrigatória
        """
        response = client.post(
            f"/api/v1/training_sessions/{uuid4()}/attendance",
            json={
                "athlete_id": str(uuid4()),
                "status": "presente",
            }
        )
        assert response.status_code == 401, \
            f"Expected 401 Unauthorized, got {response.status_code}"
    
    def test_scoped_attendance_route_not_exposed_returns_404(self, client):
        """
        Caso 2 (inválido): POST /teams/{team_id}/trainings/{id}/attendance deve retornar 404
        
        Validação: Rota scoped definida mas não exposta no agregador
        """
        team_id = uuid4()
        training_id = uuid4()
        response = client.post(
            f"/api/v1/teams/{team_id}/trainings/{training_id}/attendance",
            json={
                "athlete_id": str(uuid4()),
                "status": "presente"
            }
        )
        assert response.status_code == 404, \
            f"Expected 404 Not Found (route not exposed), got {response.status_code}"
    
    def test_authenticated_request_bypasses_auth_guard(self, auth_client):
        """
        Caso 3 (válido com auth): POST /training_sessions/{id}/attendance com auth não retorna 401
        
        Validação: Com autenticação, o guard é ultrapassado.
        Oráculo: status_code != 401 (pode ser 404 por session inexistente, ou 422, mas não 401)
        """
        response = auth_client.post(
            f"/api/v1/training_sessions/{uuid4()}/attendance",
            json={
                "athlete_id": str(uuid4()),
                "status": "presente",
            }
        )
        assert response.status_code != 401, \
            f"Expected auth to bypass 401, got {response.status_code}"
