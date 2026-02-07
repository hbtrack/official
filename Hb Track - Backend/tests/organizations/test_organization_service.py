"""Testes do OrganizationService."""
import pytest
from app.services.organization_service import OrganizationService
from app.schemas.rbac import OrganizationCreate, OrganizationUpdate


class TestOrganizationService:
    """Testes do service."""
    
    def test_create_organization(self, db, owner_user_id):
        """Criar organization via service."""
        service = OrganizationService(db)
        
        data = OrganizationCreate(
            name="Novo Clube",
        )
        
        org = service.create(data, owner_user_id=owner_user_id)
        
        assert org.id is not None
        assert org.name == "Novo Clube"
    
    def test_list_organizations(self, db, organization):
        """Listar organizations."""
        service = OrganizationService(db)
        
        items, total = service.list_organizations()
        
        assert total >= 1
        assert any(o.id == organization.id for o in items)
    
    def test_soft_delete_RDB4(self, db, organization):
        """RDB4: Soft delete define deleted_at."""
        service = OrganizationService(db)
        
        deleted = service.soft_delete(organization, reason="Teste de exclusão")
        
        assert deleted.deleted_at is not None
    
    def test_list_excludes_deleted(self, db, organization):
        """Lista exclui deletados por padrão."""
        service = OrganizationService(db)
        service.soft_delete(organization, reason="Teste de exclusão")
        
        items, total = service.list_organizations()
        
        assert not any(o.id == organization.id for o in items)
