"""
Schemas Pydantic para Memberships (alias para rbac.py).

Este módulo re-exporta os schemas de Membership do módulo rbac.py
para manter compatibilidade com imports existentes.

Para novos imports, preferir:
    from app.schemas.rbac import Membership, MembershipCreate, ...

Conforme definido em:
- docs/openapi/rbac.yaml (OpenAPI 3.1)
- docs/fluxo-backend-oficial_Version12.md (Contrato de erros por regra)
"""

# Re-export tudo do módulo rbac para manter compatibilidade
from app.schemas.rbac import (
    # Enums
    RoleCode,
    RoleCodeCreate,
    MembershipOrderBy,
    OrderDirection,
    # Membership schemas
    Membership,
    MembershipCreate,
    MembershipUpdate,
    MembershipPaginatedResponse,
)

__all__ = [
    "RoleCode",
    "RoleCodeCreate",
    "MembershipOrderBy",
    "OrderDirection",
    "Membership",
    "MembershipCreate",
    "MembershipUpdate",
    "MembershipPaginatedResponse",
]
