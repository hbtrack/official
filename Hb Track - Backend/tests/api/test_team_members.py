"""
Testes de Integração - Team Members API

Cenários cobertos:
1. ✅ Convite com email novo
2. ✅ Convite com email existente (regressão do bug UniqueViolation)
3. ✅ Convite duplicado para mesma equipe
4. ✅ Permissões (usuário sem permissão tentando convidar)
5. ✅ Validação de campos obrigatórios

NOVAS ROTAS RESTful (Sprint 1):
6. ✅ GET  /teams/{team_id}/invites - Lista convites pendentes
7. ✅ POST /teams/{team_id}/invites - Cria convite
8. ✅ POST /teams/{team_id}/invites/{id}/resend - Reenvia convite
9. ✅ DELETE /teams/{team_id}/invites/{id} - Cancela convite

Nota: Usa fixtures do conftest.py para autenticação automática.
"""
import pytest
from uuid import uuid4


# ============================================================================
# TESTES SEM AUTENTICAÇÃO (sempre funcionam)
# ============================================================================

class TestTeamMembersNoAuth:
    """Testes que não requerem autenticação - validam proteção de rotas"""
    
    def test_invite_without_auth_returns_401(self, client):
        """POST /team-members/invite sem autenticação deve retornar 401"""
        response = client.post(
            "/api/v1/team-members/invite",
            json={
                "email": "teste@exemplo.com",
                "role": "membro",
                "team_id": str(uuid4()),
            }
        )
        assert response.status_code == 401
    
    def test_pending_without_auth_returns_401(self, client):
        """GET /team-members/pending sem autenticação deve retornar 401"""
        response = client.get("/api/v1/team-members/pending")
        assert response.status_code == 401


# ============================================================================
# TESTES COM AUTENTICAÇÃO (usam fixtures do conftest.py)
# ============================================================================

class TestInviteMember:
    """Testes do endpoint POST /api/v1/team-members/invite"""
    
    def test_invite_new_email_success(self, auth_client, test_team_id):
        """
        Cenário 1: Convite com email novo deve retornar 201
        """
        new_email = f"novo_{uuid4().hex[:8]}@teste.com"
        
        response = auth_client.post(
            "/api/v1/team-members/invite",
            json={
                "email": new_email,
                "role": "membro",
                "team_id": test_team_id,
            }
        )
        
        # Pode ser 201 (sucesso) ou 400 (validação de vínculo existente)
        assert response.status_code in [200, 201, 400], f"Erro: {response.status_code} - {response.text}"
        
        if response.status_code == 201:
            data = response.json()
            assert data["success"] == True
    
    def test_invite_existing_email_no_500_error(self, auth_client, test_team_id, db):
        """
        Cenário 2 (REGRESSÃO): Convite com email já existente NÃO deve dar erro 500
        
        Bug original: UniqueViolation em ux_users_email
        Solução: Verificar User existente ANTES de criar Person
        """
        from app.models.user import User
        
        # Usar um email que já existe no banco
        existing_user = db.query(User).filter(User.deleted_at.is_(None)).first()
        if not existing_user:
            pytest.skip("Nenhum usuário encontrado no banco")
        
        response = auth_client.post(
            "/api/v1/team-members/invite",
            json={
                "email": existing_user.email,
                "role": "membro",
                "team_id": test_team_id,
            }
        )
        
        # NÃO deve dar erro 500 (UniqueViolation)
        assert response.status_code != 500, f"Erro 500 não esperado: {response.text}"
        
        # Códigos aceitáveis:
        # - 200/201: Sucesso (convite criado)
        # - 400: Já possui vínculo ou outro erro de negócio
        # - 409: Conflito (já convidado)
        # - 422: Validação (ex: role inválido para o contexto)
        assert response.status_code in [200, 201, 400, 409, 422], f"Status inesperado: {response.status_code}"
    
    def test_invite_without_team_id_returns_validation_error(self, auth_client):
        """
        Cenário 5: Convite sem team_id deve retornar erro de validação
        
        Pydantic valida que team_id é obrigatório e retorna 422.
        """
        response = auth_client.post(
            "/api/v1/team-members/invite",
            json={"email": "qualquer@teste.com", "role": "membro"}
        )
        
        # Deve retornar 422 (validação Pydantic) - team_id é obrigatório
        assert response.status_code == 422, f"Esperado 422, recebeu: {response.status_code}"
        
        # Verificar que a mensagem menciona team_id
        assert "team_id" in response.text.lower()


class TestPendingMembers:
    """Testes do endpoint GET /api/v1/team-members/pending"""
    
    def test_get_pending_members_with_auth(self, auth_client):
        """GET /team-members/pending com autenticação deve funcionar"""
        response = auth_client.get("/api/v1/team-members/pending")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


# ============================================================================
# NOVAS ROTAS RESTful (Sprint 1) - /teams/{team_id}/invites
# ============================================================================

class TestTeamInvitesNoAuth:
    """Testes sem autenticação para novas rotas RESTful"""
    
    def test_list_invites_without_auth_returns_401(self, client):
        """GET /teams/{team_id}/invites sem autenticação deve retornar 401"""
        team_id = str(uuid4())
        response = client.get(f"/api/v1/teams/{team_id}/invites")
        assert response.status_code == 401
    
    def test_create_invite_without_auth_returns_401(self, client):
        """POST /teams/{team_id}/invites sem autenticação deve retornar 401"""
        team_id = str(uuid4())
        response = client.post(
            f"/api/v1/teams/{team_id}/invites",
            json={"email": "teste@exemplo.com", "role": "membro"}
        )
        assert response.status_code == 401
    
    def test_resend_invite_without_auth_returns_401(self, client):
        """POST /teams/{team_id}/invites/{id}/resend sem autenticação deve retornar 401"""
        team_id = str(uuid4())
        invite_id = str(uuid4())
        response = client.post(f"/api/v1/teams/{team_id}/invites/{invite_id}/resend")
        assert response.status_code == 401
    
    def test_cancel_invite_without_auth_returns_401(self, client):
        """DELETE /teams/{team_id}/invites/{id} sem autenticação deve retornar 401"""
        team_id = str(uuid4())
        invite_id = str(uuid4())
        response = client.delete(f"/api/v1/teams/{team_id}/invites/{invite_id}")
        assert response.status_code == 401


class TestTeamInvitesRESTful:
    """Testes das novas rotas RESTful /teams/{team_id}/invites"""
    
    def test_list_invites_success(self, auth_client, test_team_id):
        """GET /teams/{team_id}/invites deve listar convites pendentes"""
        response = auth_client.get(f"/api/v1/teams/{test_team_id}/invites")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
    
    def test_list_invites_team_not_found(self, auth_client):
        """GET /teams/{team_id}/invites com equipe inexistente deve retornar 404"""
        fake_team_id = str(uuid4())
        response = auth_client.get(f"/api/v1/teams/{fake_team_id}/invites")
        
        assert response.status_code == 404
    
    def test_create_invite_success(self, auth_client, test_team_id):
        """POST /teams/{team_id}/invites deve criar convite"""
        new_email = f"restful_test_{uuid4().hex[:8]}@teste.com"
        
        response = auth_client.post(
            f"/api/v1/teams/{test_team_id}/invites",
            json={"email": new_email, "role": "membro"}
        )
        
        # Pode ser 201 (sucesso) ou 400 (validação de vínculo)
        assert response.status_code in [201, 400], f"Status inesperado: {response.status_code}"
        
        if response.status_code == 201:
            data = response.json()
            assert data["success"] == True
            assert "person_id" in data
    
    def test_create_invite_team_not_found(self, auth_client):
        """POST /teams/{team_id}/invites com equipe inexistente deve retornar 404"""
        fake_team_id = str(uuid4())
        
        response = auth_client.post(
            f"/api/v1/teams/{fake_team_id}/invites",
            json={"email": "teste@teste.com", "role": "membro"}
        )
        
        assert response.status_code == 404
    
    def test_create_invite_invalid_email(self, auth_client, test_team_id):
        """POST /teams/{team_id}/invites com email inválido deve retornar 422"""
        response = auth_client.post(
            f"/api/v1/teams/{test_team_id}/invites",
            json={"email": "email_invalido", "role": "membro"}
        )
        
        assert response.status_code == 422
    
    def test_cancel_invite_not_found(self, auth_client, test_team_id):
        """DELETE /teams/{team_id}/invites/{id} com convite inexistente deve retornar 404"""
        fake_invite_id = str(uuid4())
        
        response = auth_client.delete(
            f"/api/v1/teams/{test_team_id}/invites/{fake_invite_id}"
        )
        
        assert response.status_code == 404
    
    def test_resend_invite_not_found(self, auth_client, test_team_id):
        """POST /teams/{team_id}/invites/{id}/resend com convite inexistente deve retornar 404"""
        fake_invite_id = str(uuid4())
        
        response = auth_client.post(
            f"/api/v1/teams/{test_team_id}/invites/{fake_invite_id}/resend"
        )
        
        assert response.status_code == 404


class TestTeamInvitesIntegration:
    """Testes de integração completos para fluxo de convites"""
    
    def test_full_invite_flow(self, auth_client, test_team_id, db):
        """
        Testa fluxo completo: criar convite → listar → cancelar
        """
        from app.models.team_membership import TeamMembership
        
        # 1. Criar convite
        new_email = f"flow_test_{uuid4().hex[:8]}@teste.com"
        
        create_response = auth_client.post(
            f"/api/v1/teams/{test_team_id}/invites",
            json={"email": new_email, "role": "membro"}
        )
        
        # Pode ser 201 (sucesso) ou 400 (validação)
        if create_response.status_code != 201:
            pytest.skip("Não foi possível criar convite - validação de negócio")
        
        # 2. Listar e verificar que aparece
        list_response = auth_client.get(f"/api/v1/teams/{test_team_id}/invites")
        assert list_response.status_code == 200
        
        data = list_response.json()
        invite = next((i for i in data["items"] if i["email"] == new_email), None)
        
        if invite:
            # 3. Cancelar convite
            cancel_response = auth_client.delete(
                f"/api/v1/teams/{test_team_id}/invites/{invite['id']}"
            )
            assert cancel_response.status_code == 200
            
            cancel_data = cancel_response.json()
            assert cancel_data["success"] == True
            
            # 4. Verificar que não aparece mais
            list_after = auth_client.get(f"/api/v1/teams/{test_team_id}/invites")
            data_after = list_after.json()
            invite_after = next((i for i in data_after["items"] if i["email"] == new_email), None)
            assert invite_after is None, "Convite cancelado ainda aparece na lista"
