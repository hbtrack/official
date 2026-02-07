"""
Helpers de autorização baseados em papel e vínculo.

Regras implementadas (REGRAS.md / REGRAS_GERENCIAMENTO_ATLETAS.md):
- R3: Superadmin pode bypassar travas
- R25/R26: Permissões por papel
- R34/R42: Contexto organizacional obrigatório
- Vínculo por equipe quando o recurso é team-scoped
"""

from typing import Iterable, Optional
from uuid import UUID
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.models.team import Team
from app.models.team_registration import TeamRegistration
from app.models.team_membership import TeamMembership
from app.schemas.error import ErrorCode


def _forbidden(message: str, details: Optional[dict] = None) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error_code": ErrorCode.FORBIDDEN.value,
            "message": message,
            "details": details or {},
        },
    )


def require_roles(ctx, allowed_roles: Iterable[str]) -> None:
    """Valida papel (bypass para superadmin)."""
    if ctx.is_superadmin:
        return
    if ctx.role_code not in allowed_roles:
        raise _forbidden(
            f"Papel '{ctx.role_code}' não autorizado",
            {"constraint": "R25", "allowed_roles": list(allowed_roles)},
        )


def require_membership(ctx) -> None:
    """Garante vínculo organizacional ativo (bypass superadmin)."""
    if ctx.is_superadmin:
        return
    if ctx.membership_id is None:
        raise _forbidden(
            "Vínculo organizacional ativo é obrigatório",
            {"constraint": "R42"},
        )


def require_org_scope(resource_org_id: Optional[UUID], ctx) -> None:
    """
    Garante que o recurso pertence à mesma organização do contexto (bypass superadmin).
    Se org_id não for fornecido (rota não traz org no path/query), não valida escopo.
    """
    if ctx.is_superadmin:
        return
    if resource_org_id is None:
        return
    if str(resource_org_id) != str(ctx.organization_id):
        raise _forbidden(
            "Recurso fora do contexto da organização",
            {
                "constraint": "R34",
                "resource_org_id": str(resource_org_id),
                "context_org_id": str(ctx.organization_id),
            },
        )


def require_team_scope(team_id: UUID, ctx, db: Session) -> Team:
    """
    Valida que a equipe pertence à organização do contexto (bypass superadmin).
    
    Step 20: Também valida que o usuário possui vínculo ativo via team_memberships,
    garantindo revogação imediata de permissões para coaches removidos (end_at preenchido)
    ou pendentes (status != 'ativo').

    Returns:
        Team carregada (para reuso em rota).
    """
    if ctx.is_superadmin:
        team = db.get(Team, str(team_id))
        return team

    team = db.get(Team, str(team_id))
    if not team or getattr(team, "deleted_at", None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ErrorCode.RESOURCE_NOT_FOUND.value,
                "message": "Equipe não encontrada",
            },
        )

    if str(team.organization_id) != str(ctx.organization_id):
        raise _forbidden(
            "Equipe fora do contexto da organização",
            {
                "constraint": "R34",
                "team_id": str(team_id),
                "team_org_id": str(team.organization_id),
                "context_org_id": str(ctx.organization_id),
            },
        )
    
    # Step 20: Validar team_membership ativo (revogação imediata de permissões)
    # Apenas para usuários não-superadmin que possuem membership_id (usuários logados com org)
    if ctx.membership_id:
        stmt = select(TeamMembership).where(
            TeamMembership.team_id == team_id,
            TeamMembership.org_membership_id == ctx.membership_id,
            TeamMembership.status == 'ativo',
            TeamMembership.end_at.is_(None),
            TeamMembership.deleted_at.is_(None),
        )
        membership = db.execute(stmt).scalar_one_or_none()
        
        if not membership:
            raise _forbidden(
                "Acesso revogado: vínculo com equipe inativo, encerrado ou pendente",
                {
                    "constraint": "R34-TEAM-MEMBERSHIP",
                    "team_id": str(team_id),
                    "membership_id": str(ctx.membership_id),
                    "reason": "team_membership não encontrado ou inativo (end_at preenchido / status != 'ativo')",
                },
            )

    return team


def require_team_registration(
    *,
    team_id: UUID,
    athlete_id: UUID,
    ctx,
    db: Session,
    ensure_active: bool = True,
    season_start=None,
    season_end=None,
) -> TeamRegistration:
    """
    Valida que o atleta possui vínculo com a equipe (RDB10) e que o escopo da org confere.

    Regras:
    - 403 se vínculo não existir ou estiver fora da organização do contexto
    - ensure_active: exige end_at NULL (e deleted_at NULL)
    - Se season_start/season_end informados, o vínculo deve cobrir o período
    """
    # Valida equipe pertence à org
    team = require_team_scope(team_id, ctx, db)

    stmt = (
        select(TeamRegistration)
        .where(
            TeamRegistration.team_id == team_id,
            TeamRegistration.athlete_id == athlete_id,
        )
    )
    if ensure_active:
        stmt = stmt.where(
            TeamRegistration.deleted_at.is_(None),
            TeamRegistration.end_at.is_(None),
        )
    if season_start is not None:
        stmt = stmt.where(TeamRegistration.start_at <= season_start)
    if season_end is not None:
        stmt = stmt.where(
            (TeamRegistration.end_at.is_(None)) | (TeamRegistration.end_at >= season_end)
        )

    reg = db.scalar(stmt)
    if not reg:
        raise _forbidden(
            "Atleta sem vínculo ativo com a equipe",
            {
                "constraint": "RDB10",
                "team_id": str(team_id),
                "athlete_id": str(athlete_id),
            },
        )

    return reg


def require_team_registration_in_season(
    *,
    team_id: UUID,
    athlete_id: UUID,
    season_start: date,
    season_end: date,
    db: Session,
    ctx=None,
) -> TeamRegistration:
    """
    Variante para rotas que exigem janela (temporada).

    Regras:
    - Vínculo deve existir e não estar deletado.
    - start_at <= season_end e (end_at is NULL ou end_at >= season_start).
    - Se ctx for fornecido, reaproveita validação de escopo da equipe.
    """
    if ctx:
        require_team_scope(team_id, ctx, db)

    stmt = (
        select(TeamRegistration)
        .where(
            TeamRegistration.team_id == team_id,
            TeamRegistration.athlete_id == athlete_id,
            TeamRegistration.deleted_at.is_(None),
            TeamRegistration.start_at <= season_end,
            or_(
                TeamRegistration.end_at.is_(None),
                TeamRegistration.end_at >= season_start,
            ),
        )
    )

    reg = db.scalar(stmt)
    if not reg:
        raise _forbidden(
            "Atleta sem vínculo válido para a temporada",
            {
                "constraint": "RDB10",
                "team_id": str(team_id),
                "athlete_id": str(athlete_id),
                "season_start": season_start.isoformat(),
                "season_end": season_end.isoformat(),
            },
        )
    return reg
