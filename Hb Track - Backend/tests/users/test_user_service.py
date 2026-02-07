"""Testes do UserService."""
import pytest
from app.services.user_service import UserService
from app.schemas.rbac import UserCreate, UserUpdate


class TestUserServiceCreate:
    """Testes de criação."""
    
    def test_create_user(self, db, person_id):
        """Criar user via service."""
        service = UserService(db)
        
        data = UserCreate(
            email="new@example.com",
            full_name="New User",
            password="Senha123!",
        )
        user = service.create(data, person_id=person_id, password_hash="hashed")
        
        assert user.id is not None
        assert user.email == "new@example.com"
    
    def test_create_duplicate_email_fails_R3(self, db, person_id, user):
        """R3: Email duplicado deve falhar."""
        service = UserService(db)
        
        data = UserCreate(
            email=user.email,
            full_name="Another",
            password="Senha123!",
        )
        
        with pytest.raises(ValueError, match="email_already_exists"):
            service.create(data, person_id=person_id, password_hash="hashed")


class TestUserServiceList:
    """Testes de listagem."""
    
    def test_list_users(self, db, user):
        """Lista usuários ativos."""
        service = UserService(db)
        
        items, total = service.list_users()
        
        assert total >= 1
        user_ids = [u.id for u in items]
        assert user.id in user_ids


class TestUserServiceSoftDelete:
    """Testes de soft delete."""
    
    def test_soft_delete_RDB4(self, db, user):
        """RDB4: Soft delete define deleted_at e status=arquivado."""
        service = UserService(db)
        
        deleted = service.soft_delete(user, reason="Teste")
        
        assert deleted.deleted_at is not None
        assert deleted.is_active is False
        assert deleted.status == "arquivado"
    
    def test_change_status_inativo(self, db, user):
        """Desativar usuário sem deletar."""
        service = UserService(db)
        
        deactivated = service.change_status(user, "inativo")
        
        assert deactivated.is_active is False
        assert deactivated.status == "inativo"
        assert deactivated.deleted_at is None
