"""Testes do Model User."""
import pytest
from app.models.user import User


class TestUserModel:
    """Testes do modelo User."""
    
    def test_create_user(self, db, person_id):
        """Criar user com sucesso."""
        user = User(
            person_id=str(person_id),
            email="test@example.com",
            status="ativo",
        )
        db.add(user)
        db.flush()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_active is True
    
    def test_email_unique_R3(self, db, person_id, user):
        """R3: Email deve ser único."""
        from sqlalchemy.exc import IntegrityError
        
        user2 = User(
            person_id=str(person_id),
            email=user.email,  # mesmo email
            status="ativo",
        )
        db.add(user2)
        
        with pytest.raises(IntegrityError):
            db.flush()
