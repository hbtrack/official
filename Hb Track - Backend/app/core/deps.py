"""
Dependências reutilizáveis de autorização.

Uso típico em rotas:
    @router.get("/{team_id}")
    def get_team(
        team_id: UUID,
        ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador"], require_team=True)),
    ):
        ...
"""
from typing import Iterable, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.context import ExecutionContext, get_current_context
from app.core.db import get_db
from app.core.permissions import (
    require_roles,
    require_membership,
    require_org_scope,
    require_team_scope as _require_team_scope,
    require_team_registration as _require_team_registration,
)
from app.schemas.error import ErrorCode


def permission_dep(
    roles: Optional[Iterable[str]] = None,
    *,
    require_org: bool = False,
    require_team: bool = False,
    require_team_registration: bool = False,
):
    """
    Fabrica uma dependência que valida papel e vínculo/escopo.

    Args:
        roles: lista de papéis permitidos (None = não checa papel)
        require_org: se True, exige membership ativo e escopo de organização
        require_team: se True, exige escopo de equipe (usa team_id do path/query)
    """

    async def _dep(
        ctx: ExecutionContext = Depends(get_current_context),
        db: Session = Depends(get_db),
        organization_id: Optional[UUID] = None,  # capturado se rota tem path/query "organization_id"
        team_id: Optional[UUID] = None,  # capturado se rota tem path/query "team_id"
        athlete_id: Optional[UUID] = None,  # capturado se rota tiver atleta no path/query
    ) -> ExecutionContext:
        if roles:
            require_roles(ctx, roles)

        if require_org:
            require_membership(ctx)
            # Se a rota informar org_id, validar; caso contrário, apenas exige vínculo ativo.
            target_org = organization_id if organization_id is not None else None
            require_org_scope(target_org, ctx)

        if require_team:
            if team_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_code": ErrorCode.VALIDATION_ERROR.value,
                        "message": "team_id é obrigatório para validação de escopo",
                    },
                )
            _require_team_scope(team_id, ctx, db)

        if require_team_registration:
            if team_id is None or athlete_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_code": ErrorCode.VALIDATION_ERROR.value,
                        "message": "team_id e athlete_id são obrigatórios para validar registro de equipe",
                    },
                )
            _require_team_registration(
                team_id=team_id,
                athlete_id=athlete_id,
                ctx=ctx,
                db=db,
                ensure_active=True,
            )

        return ctx

    return _dep


__all__ = [
    "permission_dep",
]
