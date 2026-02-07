"""
Router Athlete - Endpoints de atletas (V1.2).

Regras RAG:
- R6: Atletas vinculam-se via team_registrations
- R7: Múltiplos team_registrations ativos simultâneos
- R12/R13/R14: Estados e flags de restrição
- R32/RF1.1: Atleta pode ser cadastrada sem equipe
- RD13: Goleiras não têm posição ofensiva
"""
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.core.context import ExecutionContext
from app.api.v1.deps.auth import permission_dep
from app.services.athlete_service_v1_2 import AthleteServiceV1_2
from app.schemas.athletes_v2 import (
    AthleteCreate,
    AthleteUpdate,
    AthleteResponse,
    AthletePaginatedResponse,
    AthleteStateEnum,
    AthleteStatsResponse,
)

router = APIRouter(prefix="/athletes", tags=["athletes"])


# ============================================================================
# ENDPOINTS ESTÁTICOS (devem vir ANTES dos endpoints com {athlete_id})
# ============================================================================

@router.get("/stats", response_model=AthleteStatsResponse)
async def get_athlete_stats(
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador"], require_org=True)),
):
    """
    Retorna estatísticas de atletas para dashboard (FASE 2).
    
    KPIs:
    - Total de atletas
    - Em captação (sem team_registration ativo)
    - Lesionadas (injured=true)
    - Suspensas (suspended_until >= hoje)
    - Por estado (ativa, dispensada, arquivada)
    - Por categoria
    """
    service = AthleteServiceV1_2(db)
    return await service.get_stats(organization_id=ctx.organization_id)


@router.get("/available-today")
async def get_available_today(
    team_id: Optional[UUID] = Query(None, description="Filtrar por equipe específica"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador"], require_org=True)),
):
    """
    Retorna atletas disponíveis para jogar hoje (FASE 5.5).
    
    Critérios de disponibilidade:
    - state = 'ativa'
    - injured = false
    - suspended_until IS NULL OR suspended_until < hoje
    - Tem team_registration ativo
    
    Regras RAG:
    - R12: Estado 'ativa' é obrigatório
    - R13: injured=true e suspended_until bloqueiam participação em jogos
    """
    from datetime import date
    from sqlalchemy import and_, or_, select
    from app.models.athlete import Athlete
    from app.models.team_registration import TeamRegistration
    from app.models.team import Team
    
    today = date.today()
    
    query = select(Athlete).join(
        TeamRegistration,
        and_(
            TeamRegistration.athlete_id == Athlete.id,
            TeamRegistration.end_at.is_(None),  # Vínculo ativo
            TeamRegistration.deleted_at.is_(None),
        )
    ).filter(
        Athlete.deleted_at.is_(None),
        Athlete.state == 'ativa',
        Athlete.injured == False,
        or_(
            Athlete.suspended_until.is_(None),
            Athlete.suspended_until < today,
        ),
    )
    
    # Filtrar por equipe
    if team_id:
        query = query.filter(TeamRegistration.team_id == team_id)
    else:
        # Filtrar por organização
        query = query.join(
            Team, TeamRegistration.team_id == Team.id
        ).filter(Team.organization_id == ctx.organization_id)
    
    result = await db.execute(query)
    athletes = result.scalars().all()
    
    # Formatar resposta
    result = []
    for athlete in athletes:
        result.append({
            "id": str(athlete.id),
            "full_name": athlete.athlete_name,
            "nickname": athlete.athlete_nickname,
            "defensive_position": athlete.main_defensive_position.name if athlete.main_defensive_position else None,
            "offensive_position": athlete.main_offensive_position.name if athlete.main_offensive_position else None,
            "has_medical_restriction": athlete.medical_restriction,
            "has_load_restriction": athlete.load_restricted,
        })
    
    return result


# ============================================================================
# ENDPOINTS DE LISTAGEM E CRIAÇÃO
# ============================================================================

@router.get("", response_model=AthletePaginatedResponse)
async def list_athletes(
    state: Optional[AthleteStateEnum] = Query(None),
    search: Optional[str] = Query(None),
    team_id: Optional[UUID] = Query(None, description="Filtrar por equipe específica"),
    has_team: Optional[bool] = Query(None, description="Filtrar: true=com equipe, false=sem equipe, null=todas"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador"], require_org=True)),
):
    """
    Lista atletas da organização.
    
    V1.2 (Opção B - REGRAS.md):
    - Por padrão mostra TODAS as atletas da organização (com ou sem equipe)
    - Filtro has_team:
      - true: apenas atletas COM team_registration ativo
      - false: apenas atletas SEM team_registration ativo
      - null/omitido: todas as atletas
    - RF1.1: Atleta pode existir sem equipe
    - R32: Atleta sem equipe não opera, mas aparece na lista
    """
    service = AthleteServiceV1_2(db)
    return await service.list_athletes(
        organization_id=ctx.organization_id,
        state=state,
        search=search,
        team_id=team_id,
        has_team=has_team,
        page=page,
        limit=limit,
    )


@router.post("", response_model=AthleteResponse, status_code=status.HTTP_201_CREATED)
async def create_athlete(
    data: AthleteCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador"], require_org=True)),
):
    """
    Cria atleta.
    
    RF1.1: Vínculo com equipe é OPCIONAL no cadastro.
    RD13: Goleiras não podem ter posição ofensiva.
    """
    service = AthleteServiceV1_2(db)

    try:
        return await service.create_athlete(
            organization_id=ctx.organization_id,
            data=data,
            created_by_membership_id=ctx.membership_id,
        )
    except ValueError as e:
        code = str(e)
        error_map = {
            "team_not_found": (404, "Equipe não encontrada ou não pertence à organização"),
            "goleira_no_offensive_position": (422, "Goleiras não podem ter posição ofensiva (RD13)"),
            "non_goalkeeper_requires_offensive_position": (422, "Atletas de linha devem ter posição ofensiva"),
        }
        if code in error_map:
            status_code, message = error_map[code]
            raise HTTPException(status_code=status_code, detail={"code": code, "message": message})
        raise HTTPException(status_code=422, detail={"code": "validation_error", "message": str(e)})


@router.get("/{athlete_id}", response_model=AthleteResponse)
async def get_athlete(
    athlete_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador"], require_org=True)),
):
    """Retorna atleta por ID."""
    service = AthleteServiceV1_2(db)
    athlete = await service.get_by_id(athlete_id)

    if not athlete:
        raise HTTPException(status_code=404, detail="Atleta não encontrada")

    return athlete


@router.patch("/{athlete_id}", response_model=AthleteResponse)
async def update_athlete(
    athlete_id: UUID,
    data: AthleteUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador"], require_org=True)),
):
    """Atualiza atleta."""
    service = AthleteServiceV1_2(db)
    try:
        updated = await service.update_athlete(
            athlete_id,
            data,
            updated_by_membership_id=ctx.membership_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"code": "validation_error", "message": str(e)})

    if not updated:
        raise HTTPException(status_code=404, detail="Atleta não encontrada")

    return updated


@router.delete("/{athlete_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_athlete(
    athlete_id: UUID,
    reason: str = Query("Exclusão manual", description="Motivo da exclusão"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador"], require_org=True)),
):
    """
    Exclui atleta (soft delete - RDB4).
    
    Comportamento:
    - Soft delete: marca deleted_at e deleted_reason
    - Encerra todos os team_registrations ativos
    """
    service = AthleteServiceV1_2(db)
    try:
        deleted = await service.soft_delete(
            athlete_id,
            reason=reason,
            deleted_by_membership_id=ctx.membership_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code": "error", "message": str(e)})

    if not deleted:
        raise HTTPException(status_code=404, detail="Atleta não encontrada")

    return None


# ============================================================================
# FASE 5: ENDPOINTS AVANÇADOS (com path params - devem vir por último)
# ============================================================================

@router.get("/{athlete_id}/badges")
async def get_athlete_badges(
    athlete_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador","atleta"], require_org=True)),
):
    """
    Retorna badges conquistados pelo atleta (Sistema de Gamificação).
    
    Badges disponíveis:
    - wellness_champion_monthly: Taxa de resposta >= 90% no mês
    - wellness_streak_3months: 3 meses consecutivos com badge monthly
    
    Resposta:
    [
        {
            "id": 1,
            "badge_type": "wellness_champion_monthly",
            "month_reference": "2026-01",
            "response_rate": 95.0,
            "earned_at": "2026-02-01T00:00:00"
        }
    ]
    
    Regras:
    - Atleta pode ver apenas próprios badges
    - Staff pode ver badges de qualquer atleta do time
    """
    from sqlalchemy import select
    from app.models.athlete import Athlete
    from app.services.wellness_gamification_service import WellnessGamificationService
    
    # Verificar se atleta existe
    stmt = select(Athlete).filter(
        Athlete.id == athlete_id,
        Athlete.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    athlete = result.scalar_one_or_none()
    
    if not athlete:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Se usuário é atleta, validar que está acessando próprios badges
    if "atleta" in ctx.roles:
        if not ctx.athlete_id or str(ctx.athlete_id) != str(athlete_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você pode ver apenas seus próprios badges"
            )
    
    # Buscar badges
    service = WellnessGamificationService(db)
    badges = await service.get_athlete_badges(
        athlete_id=int(athlete_id),
        limit=limit
    )
    
    return badges


@router.get("/{athlete_id}/history")
async def get_athlete_history(
    athlete_id: UUID,
    event_type: Optional[str] = Query(None, description="Filtrar por tipo de evento"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador"], require_org=True)),
):
    """
    Retorna histórico de eventos da atleta (FASE 5.4 - Timeline).
    
    Busca eventos de:
    - audit_logs (ações auditadas)
    - team_registrations (vínculos)
    - medical_cases (casos médicos - se existir)
    
    Regras RAG:
    - R30: Ações críticas auditáveis
    - R31: Log obrigatório (actor_id, timestamp, action, context, old_value, new_value)
    - R34: Imutabilidade dos logs
    """
    from sqlalchemy import select
    from app.models.audit_log import AuditLog
    from app.models.athlete import Athlete
    
    # Verificar se atleta existe
    stmt = select(Athlete).filter(
        Athlete.id == athlete_id,
        Athlete.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    athlete = result.scalar_one_or_none()
    
    if not athlete:
        raise HTTPException(status_code=404, detail="Atleta não encontrada")
    
    # Buscar logs de auditoria
    query = select(AuditLog).filter(
        AuditLog.entity_type == 'athletes',
        AuditLog.entity_id == str(athlete_id),
    )
    
    if event_type:
        query = query.filter(AuditLog.action == event_type)
    
    query = query.order_by(AuditLog.created_at.desc()).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    
    # Mapear para formato de timeline
    result = []
    for log in logs:
        event_type_map = {
            'create': 'created',
            'update': 'updated',
            'delete': 'state_changed',
            'state_change': 'state_changed',
            'injury_start': 'injury_start',
            'injury_end': 'injury_end',
        }
        
        result.append({
            "id": str(log.id),
            "type": event_type_map.get(log.action, 'updated'),
            "timestamp": log.created_at.isoformat(),
            "description": log.action,
            "actor_id": str(log.actor_id) if log.actor_id else None,
            "actor_name": None,  # TODO: Buscar nome do actor
            "old_value": log.old_value,
            "new_value": log.new_value,
            "metadata": log.context,
        })
    
    return result
