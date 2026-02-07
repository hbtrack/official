"""Testes do Model Organization."""
import pytest
from app.models.organization import Organization


class TestOrganizationModel:
    """Testes do modelo Organization."""
    
    def test_create_organization(self, db, owner_user_id):
        """Criar organization com sucesso."""
        org = Organization(
            name="Clube ABC",
            owner_user_id=owner_user_id,
        )
        db.add(org)
        db.flush()
        
        assert org.id is not None
        assert org.name == "Clube ABC"
        assert org.deleted_at is None
    
    def test_name_duplicate(self, db, owner_user_id, organization):
        """Duas orgs podem ter o mesmo nome (sem constraint unique)."""
        org2 = Organization(
            name=organization.name,  # mesmo nome
            owner_user_id=owner_user_id,
        )
        db.add(org2)
        db.flush()  # Deve funcionar pois name não é unique
        
        assert org2.id is not None
        assert org2.name == organization.name
