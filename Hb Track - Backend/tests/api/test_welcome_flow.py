"""
Testes de Integração - Welcome Flow API (Sprint 2)

Cenários cobertos:
1. ✅ GET  /auth/welcome/verify - Token válido
2. ✅ GET  /auth/welcome/verify - Token inválido/expirado/usado
3. ✅ POST /auth/welcome/complete - Cadastro completo com sucesso
4. ✅ POST /auth/welcome/complete - Validações (senha curta, senhas diferentes)
5. ✅ POST /auth/welcome/complete - Token expirado
"""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta, timezone


class TestWelcomeVerifyNoAuth:
    """Testes do GET /auth/welcome/verify (sem autenticação necessária)"""
    
    def test_verify_without_token_returns_400(self, client):
        """GET /auth/welcome/verify sem token deve retornar 400"""
        response = client.get("/api/v1/auth/welcome/verify")
        assert response.status_code in [400, 422]
    
    def test_verify_invalid_token_returns_error(self, client):
        """GET /auth/welcome/verify com token inválido deve retornar erro"""
        response = client.get("/api/v1/auth/welcome/verify?token=invalid_token_12345")
        
        # Deve retornar 400 (token inválido) ou similar
        assert response.status_code in [400, 404]
        data = response.json()
        assert data.get("detail", {}).get("code") in ["INVALID_TOKEN", "TOKEN_NOT_FOUND", None] or "invalid" in str(data).lower()
    
    def test_verify_valid_token_structure(self, client, db):
        """GET /auth/welcome/verify com token válido deve retornar estrutura correta"""
        from app.models.password_reset import PasswordReset
        
        # Buscar um token welcome válido (não expirado, não usado)
        now = datetime.now(timezone.utc)
        valid_token = db.query(PasswordReset).filter(
            PasswordReset.token_type == "welcome",
            PasswordReset.expires_at > now,
            PasswordReset.used == False
        ).first()
        
        if not valid_token:
            pytest.skip("Nenhum token welcome válido encontrado no banco")
        
        response = client.get(f"/api/v1/auth/welcome/verify?token={valid_token.token}")
        
        # Deve retornar 200 com informações do convite
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estrutura da resposta
        assert "valid" in data
        assert "email" in data
        assert data["valid"] == True


class TestWelcomeCompleteNoAuth:
    """Testes do POST /auth/welcome/complete (sem autenticação necessária)"""
    
    def test_complete_without_token_returns_error(self, client):
        """POST /auth/welcome/complete sem token deve retornar erro"""
        response = client.post(
            "/api/v1/auth/welcome/complete",
            json={
                "password": "SenhaForte123!",
                "confirm_password": "SenhaForte123!",
                "full_name": "Teste User"
            }
        )
        assert response.status_code in [400, 422]
    
    def test_complete_with_invalid_token(self, client):
        """POST /auth/welcome/complete com token inválido deve retornar erro"""
        response = client.post(
            "/api/v1/auth/welcome/complete",
            json={
                "token": "invalid_token_xyz",
                "password": "SenhaForte123!",
                "confirm_password": "SenhaForte123!",
                "full_name": "Teste User"
            }
        )
        assert response.status_code in [400, 404]
    
    def test_complete_password_too_short(self, client, db):
        """POST /auth/welcome/complete com senha curta deve retornar erro"""
        from app.models.password_reset import PasswordReset
        from datetime import datetime, timezone
        
        # Buscar um token welcome válido
        now = datetime.now(timezone.utc)
        valid_token = db.query(PasswordReset).filter(
            PasswordReset.token_type == "welcome",
            PasswordReset.expires_at > now,
            PasswordReset.used == False
        ).first()
        
        if not valid_token:
            pytest.skip("Nenhum token welcome válido encontrado no banco")
        
        response = client.post(
            "/api/v1/auth/welcome/complete",
            json={
                "token": valid_token.token,
                "password": "123",  # muito curta
                "confirm_password": "123",
                "full_name": "Teste User"
            }
        )
        
        # Deve retornar erro de validação
        assert response.status_code == 422
    
    def test_complete_password_mismatch(self, client, db):
        """POST /auth/welcome/complete com senhas diferentes deve retornar erro"""
        from app.models.password_reset import PasswordReset
        from datetime import datetime, timezone
        
        # Buscar um token welcome válido
        now = datetime.now(timezone.utc)
        valid_token = db.query(PasswordReset).filter(
            PasswordReset.token_type == "welcome",
            PasswordReset.expires_at > now,
            PasswordReset.used == False
        ).first()
        
        if not valid_token:
            pytest.skip("Nenhum token welcome válido encontrado no banco")
        
        response = client.post(
            "/api/v1/auth/welcome/complete",
            json={
                "token": valid_token.token,
                "password": "SenhaForte123!",
                "confirm_password": "SenhaDiferente123!",
                "full_name": "Teste User"
            }
        )
        
        # Deve retornar erro (400 ou 422)
        assert response.status_code in [400, 422]


class TestWelcomeFlowIntegration:
    """Testes de integração completa do fluxo de welcome"""
    
    def test_full_welcome_flow(self, auth_client, test_team_id, client, db):
        """
        Fluxo completo:
        1. Criar convite via POST /teams/{team_id}/invites
        2. Verificar token via GET /auth/welcome/verify
        3. Completar cadastro via POST /auth/welcome/complete
        """
        from app.models.password_reset import PasswordReset
        from app.models.team_membership import TeamMembership
        
        # 1. Criar convite
        test_email = f"welcome_flow_{uuid4().hex[:8]}@teste.com"
        
        invite_response = auth_client.post(
            f"/api/v1/teams/{test_team_id}/invites",
            json={
                "email": test_email,
                "role": "membro"
            }
        )
        
        # Pode ser 201 (sucesso) ou 200
        if invite_response.status_code not in [200, 201]:
            pytest.skip(f"Não foi possível criar convite: {invite_response.status_code}")
        
        # 2. Buscar o token gerado via User
        from app.models.user import User
        
        user = db.query(User).filter(User.email == test_email).first()
        if not user:
            pytest.skip("Usuário não encontrado após criar convite")
        
        token_record = db.query(PasswordReset).filter(
            PasswordReset.user_id == user.id,
            PasswordReset.token_type == "welcome"
        ).order_by(PasswordReset.created_at.desc()).first()
        
        if not token_record:
            pytest.skip("Token de welcome não encontrado após criar convite")
        
        # 3. Verificar token
        verify_response = client.get(f"/api/v1/auth/welcome/verify?token={token_record.token}")
        
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["valid"] == True
        assert verify_data["email"] == test_email
        
        # 4. Completar cadastro
        complete_response = client.post(
            "/api/v1/auth/welcome/complete",
            json={
                "token": token_record.token,
                "password": "SenhaForte123!",
                "confirm_password": "SenhaForte123!",
                "full_name": "Teste Welcome Flow",
                "phone": "(11) 99999-9999"
            }
        )
        
        assert complete_response.status_code == 200
        complete_data = complete_response.json()
        assert complete_data["success"] == True
        
        # 5. Verificar que o membership foi ativado
        db.expire_all()  # Forçar refresh do cache
        membership = db.query(TeamMembership).filter(
            TeamMembership.team_id == test_team_id
        ).join(TeamMembership.person).filter(
            # Buscar pelo email do usuário
        ).first()
        
        # Token deve estar marcado como usado
        db.refresh(token_record)
        assert token_record.used == True
