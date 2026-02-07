"""
Helpers para aplicar escopo em queries SQLAlchemy.

São genéricos e só atuam se o modelo tiver os campos esperados.
"""
from sqlalchemy.orm import Query

from app.core.context import ExecutionContext


def apply_org_scope(query: Query, ctx: ExecutionContext, model) -> Query:
    """Filtra por organization_id quando disponível (bypass para superadmin)."""
    if ctx.is_superadmin:
        return query
    if hasattr(model, "organization_id") and ctx.organization_id:
        return query.filter(model.organization_id == str(ctx.organization_id))
    return query


def apply_team_scope(query: Query, ctx: ExecutionContext, model) -> Query:
    """
    Filtra por team_id ou organization_id para manter escopo de equipe.
    Se o modelo tiver team_id, usa ctx.team_ids; senão tenta organization_id.
    """
    if ctx.is_superadmin:
        return query

    if hasattr(model, "team_id") and ctx.team_ids:
        return query.filter(model.team_id.in_([str(tid) for tid in ctx.team_ids]))

    if hasattr(model, "organization_id") and ctx.organization_id:
        return query.filter(model.organization_id == str(ctx.organization_id))

    return query


def apply_self_scope(query: Query, ctx: ExecutionContext, model) -> Query:
    """
    Escopo de "self": para atletas, restringe por person_id quando existir no modelo.
    """
    if ctx.is_superadmin:
        return query

    if ctx.role_code == "atleta" and hasattr(model, "person_id") and ctx.person_id:
        return query.filter(model.person_id == str(ctx.person_id))

    return query
