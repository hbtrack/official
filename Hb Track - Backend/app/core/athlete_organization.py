"""
Utilitários para gerenciamento de organization_id derivado em Athletes

Implementação da decisão canônica Q2-C:
- organization_id é campo opcional e DERIVADO automaticamente
- Quando atleta tem team_registration ativo: organization_id = teams.organization_id
- Quando atleta NÃO tem team_registration ativo: organization_id = NULL

Data de canonização: 31/12/2025
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.athlete import Athlete
from app.models.team import Team
from app.models.team_registration import TeamRegistration


def derive_organization_id_from_registrations(
    athlete_id: UUID,
    db: Session
) -> Optional[UUID]:
    """
    Deriva organization_id da atleta baseado em seus team_registrations ativos.
    
    Lógica:
    1. Se atleta tem team_registrations ativos, pegar organization_id da equipe
    2. Se múltiplos vínculos ativos, pegar o mais recente (start_at DESC)
    3. Se nenhum vínculo ativo, retornar NULL
    
    Args:
        athlete_id: ID da atleta
        db: Sessão do banco de dados
        
    Returns:
        UUID da organização ou None
    """
    # Buscar team_registrations ativos (end_at IS NULL)
    stmt = (
        select(TeamRegistration)
        .where(
            TeamRegistration.athlete_id == athlete_id,
            TeamRegistration.end_at.is_(None)
        )
        .order_by(TeamRegistration.start_at.desc())
    )
    
    active_registrations = db.execute(stmt).scalars().all()
    
    if not active_registrations:
        return None
    
    # Pegar primeiro registration (mais recente)
    first_registration = active_registrations[0]
    
    # Buscar organization_id da equipe
    team = db.get(Team, first_registration.team_id)
    
    if not team:
        return None
    
    return team.organization_id


def update_athlete_organization_id(
    athlete_id: UUID,
    db: Session,
    commit: bool = True
) -> Optional[UUID]:
    """
    Atualiza automaticamente o organization_id da atleta baseado em vínculos ativos.
    
    Esta função deve ser chamada:
    - Após criar team_registration
    - Após encerrar team_registration (end_at != NULL)
    - Após deletar team_registration
    - Ao mudar estado da atleta para 'dispensada'
    
    Args:
        athlete_id: ID da atleta
        db: Sessão do banco de dados
        commit: Se True, faz commit após atualização
        
    Returns:
        Novo organization_id (ou None)
    """
    athlete = db.get(Athlete, athlete_id)
    
    if not athlete:
        return None
    
    # Derivar organization_id dos vínculos ativos
    new_org_id = derive_organization_id_from_registrations(athlete_id, db)
    
    # Atualizar se mudou
    if athlete.organization_id != new_org_id:
        athlete.organization_id = new_org_id
        
        if commit:
            db.commit()
            db.refresh(athlete)
    
    return new_org_id


def handle_team_registration_created(
    athlete_id: UUID,
    team_id: UUID,
    db: Session
) -> None:
    """
    Handler para quando team_registration é criado.
    
    Atualiza automaticamente athletes.organization_id.
    
    Args:
        athlete_id: ID da atleta
        team_id: ID da equipe vinculada
        db: Sessão do banco de dados
    """
    athlete = db.get(Athlete, athlete_id)
    team = db.get(Team, team_id)
    
    if not athlete or not team:
        return
    
    # Atualizar organization_id para o da equipe
    athlete.organization_id = team.organization_id
    db.commit()
    db.refresh(athlete)


def handle_team_registration_ended(
    athlete_id: UUID,
    db: Session
) -> None:
    """
    Handler para quando team_registration é encerrado (end_at preenchido).
    
    Recalcula organization_id baseado em vínculos restantes ativos.
    
    Args:
        athlete_id: ID da atleta
        db: Sessão do banco de dados
    """
    update_athlete_organization_id(athlete_id, db, commit=True)


def handle_athlete_dispensed(
    athlete_id: UUID,
    db: Session
) -> None:
    """
    Handler para quando atleta é dispensada (state='dispensada').
    
    Comportamento canônico:
    1. Encerrar TODOS os team_registrations ativos (end_at = NOW())
    2. Atualizar organization_id = NULL
    
    Args:
        athlete_id: ID da atleta
        db: Sessão do banco de dados
    """
    from datetime import datetime, timezone
    
    # 1. Encerrar todos os team_registrations ativos
    stmt = (
        select(TeamRegistration)
        .where(
            TeamRegistration.athlete_id == athlete_id,
            TeamRegistration.end_at.is_(None)
        )
    )
    
    active_registrations = db.execute(stmt).scalars().all()
    
    for registration in active_registrations:
        registration.end_at = datetime.now(timezone.utc)
    
    # 2. Atualizar organization_id para NULL
    athlete = db.get(Athlete, athlete_id)
    if athlete:
        athlete.organization_id = None
    
    db.commit()


def get_athletes_without_organization(
    db: Session,
    limit: int = 100
) -> list[Athlete]:
    """
    Lista atletas sem organization_id (em fase de captação/avaliação).
    
    Útil para:
    - Identificar atletas em processo de captação
    - Listagens administrativas de atletas "sem vínculo"
    
    Args:
        db: Sessão do banco de dados
        limit: Limite de resultados
        
    Returns:
        Lista de atletas com organization_id = NULL
    """
    stmt = (
        select(Athlete)
        .where(
            Athlete.organization_id.is_(None),
            Athlete.deleted_at.is_(None)  # Apenas não excluídas
        )
        .order_by(Athlete.created_at.desc())
        .limit(limit)
    )
    
    return db.execute(stmt).scalars().all()


def get_athletes_by_organization(
    organization_id: UUID,
    db: Session,
    include_without_team: bool = False
) -> list[Athlete]:
    """
    Lista atletas de uma organização.
    
    Args:
        organization_id: ID da organização
        db: Sessão do banco de dados
        include_without_team: Se True, inclui atletas com team_registrations inativos
        
    Returns:
        Lista de atletas da organização
    """
    if include_without_team:
        # Incluir atletas com organization_id mesmo sem vínculo ativo
        # (útil para listar "banco" de atletas da organização)
        stmt = (
            select(Athlete)
            .where(
                Athlete.organization_id == organization_id,
                Athlete.deleted_at.is_(None)
            )
            .order_by(Athlete.athlete_name)
        )
    else:
        # Apenas atletas com vínculo ativo (padrão)
        stmt = (
            select(Athlete)
            .join(TeamRegistration, TeamRegistration.athlete_id == Athlete.id)
            .join(Team, Team.id == TeamRegistration.team_id)
            .where(
                Team.organization_id == organization_id,
                TeamRegistration.end_at.is_(None),
                Athlete.deleted_at.is_(None)
            )
            .order_by(Athlete.athlete_name)
        )
    
    return db.execute(stmt).scalars().all()
