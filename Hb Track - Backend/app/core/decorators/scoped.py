"""
Decorator para aplicar permissão e escopo de dados (leitura).

Quando usar:
- Endpoints de leitura/listagem com regra repetitiva de escopo.
- Permissões simples baseadas em ctx.can(...).

Não usar para:
- Fluxos transacionais complexos.
- Escrita com múltiplos efeitos colaterais (use require_permission direto).
"""

from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable, Optional

from fastapi import HTTPException, status

from app.core.context import ExecutionContext
from app.core.scope import apply_org_scope, apply_team_scope, apply_self_scope


def scoped_endpoint(
    permission: str,
    scope: Optional[str] = None,
    *,
    require_org: bool = False,
) -> Callable:
    """
    Aplica verificação de permissão + filtro de escopo no kwargs["query"] (se presente).

    Args:
        permission: nome da permissão a verificar em ctx.can(...)
        scope: "team" ou "self" para aplicar filtros adicionais
        require_org: se True, aplica escopo de organização antes do scope específico
    """

    def decorator(func: Callable):
        is_coro = iscoroutinefunction(func)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx: ExecutionContext = kwargs.get("ctx")
            query = kwargs.get("query")
            model = kwargs.get("model")

            if not ctx:
                raise RuntimeError("ExecutionContext não encontrado")

            if not ctx.can(permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissão necessária: {permission}",
                )

            if query is not None and model is not None:
                if require_org:
                    query = apply_org_scope(query, ctx, model)
                if scope == "team":
                    query = apply_team_scope(query, ctx, model)
                elif scope == "self":
                    query = apply_self_scope(query, ctx, model)
                kwargs["query"] = query

            if is_coro:
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
