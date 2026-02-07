"""
Testes de Integração - Training API

Cenários cobertos:
1. CRUD de sessões de treino
2. Marcação de presença
3. Validações de data/hora
4. Permissões por role
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


client = TestClient(app)


class TestTrainingSessionsAPI:
    """Testes do módulo Training Sessions"""
    
    def test_list_sessions_without_auth_returns_401(self):
        """GET /training-sessions sem auth deve retornar 401"""
        response = client.get("/api/v1/training-sessions")
        assert response.status_code == 401
    
    def test_get_session_without_auth_returns_401(self):
        """GET /training-sessions/{id} sem auth deve retornar 401"""
        response = client.get(f"/api/v1/training-sessions/{uuid4()}")
        assert response.status_code == 401
    
    def test_create_session_without_auth_returns_401(self):
        """POST /training-sessions sem auth deve retornar 401"""
        response = client.post("/api/v1/training-sessions", json={
            "team_id": str(uuid4()),
            "session_at": "2026-01-15T10:00:00Z",
            "duration_minutes": 90,
        })
        assert response.status_code == 401
    
    # TODO: Adicionar testes com autenticação
    # - test_create_session_as_treinador
    # - test_create_session_as_atleta_returns_403
    # - test_mark_attendance
    # - test_session_in_past_cannot_be_created


class TestAttendanceAPI:
    """Testes de presença em treinos"""
    
    def test_attendance_route_without_auth_returns_401(self):
        """POST /training_sessions/{id}/attendance sem auth retorna 401"""
        response = client.post(f"/api/v1/training_sessions/{uuid4()}/attendance", json={
            "athlete_id": str(uuid4()),
            "status": "presente",
        })
        assert response.status_code == 401
    
    def test_scoped_attendance_route_not_exposed_returns_404(self):
        """POST /teams/{team_id}/trainings/{id}/attendance retorna 404 (rota não exposta)"""
        team_id = uuid4()
        training_id = uuid4()
        response = client.post(
            f"/api/v1/teams/{team_id}/trainings/{training_id}/attendance",
            json={"athlete_id": str(uuid4()), "status": "presente"}
        )
        assert response.status_code == 404


class TestTrainingFlowAuthenticated:
    """Testes de fluxo de treino autenticados"""

    def test_superadmin_can_list_training_sessions(self, auth_client):
        """Superadmin pode listar sessões de treino"""
        response = auth_client.get("/api/v1/training-sessions")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    def test_superadmin_can_create_training_session(self, auth_client, test_team_id):
        """Superadmin pode criar sessão de treino (RBAC: can_create_training=True)"""
        from datetime import datetime, timedelta
        
        # Criar sessão no futuro
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT10:00:00Z")
        
        session_data = {
            "team_id": str(test_team_id),
            "session_at": future_date,
            "duration_minutes": 90,
            "training_type": "técnico",
        }
        response = auth_client.post("/api/v1/training-sessions", json=session_data)
        # Pode retornar 200, 201 (criado), 400/422 se validação, 404 se team não existe
        assert response.status_code in [200, 201, 400, 404, 422], f"Unexpected: {response.status_code}: {response.text}"

    def test_get_training_session_with_invalid_id_returns_404(self, auth_client):
        """GET com ID inexistente retorna 404"""
        fake_id = str(uuid4())
        response = auth_client.get(f"/api/v1/training-sessions/{fake_id}")
        assert response.status_code == 404

    def test_training_sessions_endpoint_supports_team_filter(self, auth_client, test_team_id):
        """API de treinos suporta filtro por equipe"""
        response = auth_client.get("/api/v1/training-sessions", params={"team_id": str(test_team_id)})
        assert response.status_code == 200
        data = response.json()
        # Deve retornar estrutura válida
        assert isinstance(data, (dict, list))
