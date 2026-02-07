"""
Validação de escopo para Ficha Única

FASE 3 - FICHA.MD Seção 3.2

Valida permissões de criação/seleção baseado no papel do usuário.

Regras implementadas (REGRAS.md):
- R3: Superadmin bypass total
- R25: Permissões por papel
- R33: Nada acontece fora de vínculo
- R34: Escopo organizacional
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.context import ExecutionContext
from app.core.permissions import require_org_scope, require_team_scope, require_roles
from app.schemas.intake.ficha_unica import FichaUnicaRequest


# =============================================================================
# CONSTANTES DE PAPÉIS
# =============================================================================

# Papéis que podem criar organização
ROLES_CREATE_ORGANIZATION = ["dirigente"]

# Papéis que podem criar equipe
ROLES_CREATE_TEAM = ["dirigente", "coordenador"]

# Papéis que podem cadastrar atleta
ROLES_CREATE_ATHLETE = ["dirigente", "coordenador", "treinador"]

# Papéis que podem criar membership
ROLES_CREATE_MEMBERSHIP = ["dirigente", "coordenador"]


# =============================================================================
# ERROS
# =============================================================================

def _forbidden(message: str, constraint: str, details: Optional[dict] = None) -> HTTPException:
    """Gera exceção de acesso negado."""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error_code": "FORBIDDEN",
            "message": message,
            "constraint": constraint,
            "details": details or {},
        },
    )


def _unprocessable(message: str, constraint: str) -> HTTPException:
    """Gera exceção de validação."""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "error_code": "VALIDATION_ERROR",
            "message": message,
            "constraint": constraint,
        },
    )


# =============================================================================
# VALIDAÇÃO DE ESCOPO
# =============================================================================

def validate_ficha_scope(
    payload: FichaUnicaRequest,
    ctx: ExecutionContext,
    db: Session
) -> None:
    """
    Valida escopo de criação/seleção baseado no papel do usuário.
    
    Args:
        payload: Payload da Ficha Única
        ctx: Contexto de execução (usuário, papel, organização)
        db: Sessão do banco
    
    Raises:
        HTTPException 403: Se escopo não permitido
        HTTPException 422: Se validação falhar
    
    Regras:
        - Superadmin: bypass total (R3)
        - Dirigente: pode criar org, equipe, atleta, membership
        - Coordenador: pode criar equipe, atleta, membership (mesma org)
        - Treinador: pode criar atleta (apenas equipes que treina)
        - Atleta: não pode criar nada
    """
    
    # Superadmin: bypass total (R3)
    if ctx.is_superadmin:
        return
    
    # ========= VALIDAÇÃO DE ORGANIZAÇÃO =========
    if payload.organization:
        _validate_organization_scope(payload, ctx, db)
    
    # ========= VALIDAÇÃO DE EQUIPE =========
    if payload.team:
        _validate_team_scope(payload, ctx, db)
    
    # ========= VALIDAÇÃO DE ATLETA =========
    if payload.athlete and payload.athlete.create:
        _validate_athlete_scope(payload, ctx, db)
    
    # ========= VALIDAÇÃO DE MEMBERSHIP =========
    if payload.membership:
        _validate_membership_scope(payload, ctx, db)


def _validate_organization_scope(
    payload: FichaUnicaRequest,
    ctx: ExecutionContext,
    db: Session
) -> None:
    """Valida escopo de criação/seleção de organização."""
    
    if payload.organization.mode == "create":
        # Apenas dirigente pode criar organização
        if ctx.role_code not in ROLES_CREATE_ORGANIZATION:
            raise _forbidden(
                f"Papel '{ctx.role_code}' não pode criar organização",
                "R25",
                {"allowed_roles": ROLES_CREATE_ORGANIZATION}
            )
    
    elif payload.organization.mode == "select":
        org_id = payload.organization.organization_id
        
        if ctx.role_code in ["dirigente", "coordenador"]:
            # Dirigente/Coordenador: deve pertencer à organização
            require_org_scope(org_id, ctx)
        
        elif ctx.role_code == "treinador":
            # Treinador: precisa ter vínculo com equipe da organização
            if not payload.team or payload.team.mode != "select":
                raise _forbidden(
                    "Treinador deve selecionar equipe existente da organização",
                    "R25",
                    {"role": ctx.role_code}
                )
            # A validação de equipe fará a verificação
        
        else:
            # Outros papéis não podem selecionar organização
            raise _forbidden(
                f"Papel '{ctx.role_code}' não pode selecionar organização",
                "R25"
            )


def _validate_team_scope(
    payload: FichaUnicaRequest,
    ctx: ExecutionContext,
    db: Session
) -> None:
    """Valida escopo de criação/seleção de equipe."""
    
    if payload.team.mode == "create":
        # Apenas dirigente e coordenador podem criar equipe
        if ctx.role_code not in ROLES_CREATE_TEAM:
            raise _forbidden(
                f"Papel '{ctx.role_code}' não pode criar equipe",
                "R25",
                {"allowed_roles": ROLES_CREATE_TEAM}
            )
        
        # Validar organização (obrigatória para criar equipe)
        if not payload.organization:
            raise _unprocessable(
                "Organização é obrigatória para criar equipe",
                "R33"
            )
        
        # Se selecionando organização, validar escopo
        if payload.organization.mode == "select":
            org_id = payload.organization.organization_id
            require_org_scope(org_id, ctx)
    
    elif payload.team.mode == "select":
        # Validar que usuário tem acesso à equipe
        team_id = payload.team.team_id
        require_team_scope(team_id, ctx, db)


def _validate_athlete_scope(
    payload: FichaUnicaRequest,
    ctx: ExecutionContext,
    db: Session
) -> None:
    """Valida escopo de criação de atleta."""
    
    # Apenas dirigente, coordenador e treinador podem cadastrar atleta
    if ctx.role_code not in ROLES_CREATE_ATHLETE:
        raise _forbidden(
            f"Papel '{ctx.role_code}' não pode cadastrar atleta",
            "R25",
            {"allowed_roles": ROLES_CREATE_ATHLETE}
        )
    
    # Atleta precisa de equipe para vínculo (R33)
    # NOTA: Permitimos atleta sem equipe (fase captação) mas com warning
    if not payload.team:
        # Atleta sem equipe é permitido (captação)
        # Mas não cria team_registration
        pass
    else:
        # Com equipe: validar escopo
        if payload.team.mode == "select":
            team_id = payload.team.team_id
            require_team_scope(team_id, ctx, db)


def _validate_membership_scope(
    payload: FichaUnicaRequest,
    ctx: ExecutionContext,
    db: Session
) -> None:
    """Valida escopo de criação de membership."""
    
    # Apenas dirigente e coordenador podem criar membership
    if ctx.role_code not in ROLES_CREATE_MEMBERSHIP:
        raise _forbidden(
            f"Papel '{ctx.role_code}' não pode criar vínculo organizacional",
            "R25",
            {"allowed_roles": ROLES_CREATE_MEMBERSHIP}
        )
    
    # Membership precisa de organização
    if not payload.organization:
        raise _unprocessable(
            "Organização é obrigatória para criar vínculo",
            "R33"
        )
    
    # Validar escopo da organização
    if payload.organization.mode == "select":
        org_id = payload.organization.organization_id
        require_org_scope(org_id, ctx)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "validate_ficha_scope",
    "ROLES_CREATE_ORGANIZATION",
    "ROLES_CREATE_TEAM",
    "ROLES_CREATE_ATHLETE",
    "ROLES_CREATE_MEMBERSHIP",
]
