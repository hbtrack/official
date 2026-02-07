"""
Dependências de autenticação

FASE 6: Implementação real com JWT

Re-exporta funções de app.core.context para compatibilidade.
"""
from app.core.context import (
    ExecutionContext,
    get_current_context,
    require_role,
    get_mock_context,
)
from app.core.deps import permission_dep

# Re-export para compatibilidade com imports existentes
__all__ = [
    "ExecutionContext",
    "get_current_context",
    "require_role",
    "get_mock_context",
    "permission_dep",
]
