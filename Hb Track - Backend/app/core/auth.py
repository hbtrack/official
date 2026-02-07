"""
Autenticação e permissões.

FASE 6: Implementação real com JWT

Re-exporta funções de app.core.context para compatibilidade com imports antigos.

Referências RAG:
- R3: Super Admin pode ignorar travas operacionais
- R42: Vínculo ativo obrigatório (exceto superadmin)
- R25/R26: Permissões por papel
"""
from app.core.context import (
    ExecutionContext,
    get_current_context,
    require_role,
    get_mock_context,
)


# Re-export para compatibilidade com imports existentes (FASE 2)
__all__ = [
    "ExecutionContext",
    "get_current_context",
    "require_role",
    "get_mock_context",
]


# Mantém MockUser para compatibilidade com código antigo
class MockUser:
    """
    DEPRECATED: Usar ExecutionContext
    
    Mantido para compatibilidade com código de FASE 2.
    
    Step 8: Compatibilidade com dict | list para permissions
    Aceita tanto Dict[str, bool] (novo formato) quanto list[str] (antigo formato)
    """
    def __init__(
        self,
        user_id: str = "09cd9e07-3a95-4d1e-8f19-d3d81e1dd8b4",
        person_id: str = "8a99ff63-66e9-4d1b-b288-60332667467f",
        membership_id: str = "11111111-1111-1111-1111-111111111111",
        organization_id: str = "85b5a651-6677-4a6a-a08f-60e657a624a2",
        role: str = "coordenador",
        permissions: dict[str, bool] | list[str] = None,
    ):
        self.user_id = user_id
        self.person_id = person_id
        self.membership_id = membership_id
        self.organization_id = organization_id
        self.role = role
        
        # Step 8: Converter list[str] para dict[str, bool] se necessário
        if permissions is None:
            self.permissions = {"*": True}
        elif isinstance(permissions, list):
            # Formato antigo: ["perm1", "perm2"] -> {"perm1": True, "perm2": True}
            self.permissions = {perm: True for perm in permissions}
        else:
            # Formato novo: já é dict[str, bool]
            self.permissions = permissions

    def has_permission(self, permission: str) -> bool:
        # Verificar wildcard
        if self.permissions.get("*", False):
            return True
        return self.permissions.get(permission, False)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "person_id": self.person_id,
            "membership_id": self.membership_id,
            "organization_id": self.organization_id,
            "role": self.role,
            "permissions": self.permissions,
        }


# Alias para compatibilidade com código existente que usa get_current_user
# A função get_current_context é a implementação real
get_current_user = get_current_context
