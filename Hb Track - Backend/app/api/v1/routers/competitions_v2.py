"""
Router para Competitions V2 — Módulo com IA para importação de PDF.

Endpoints V2 (novos):
- POST /v1/competitions/v2                           → createCompetitionV2
- POST /v1/competitions/v2/parse-pdf                 → parsePdfWithAI  
- POST /v1/competitions/v2/{id}/validate-and-save    → validateAndSaveFromAI
- GET  /v1/competitions/v2/{id}/full                 → getCompetitionWithRelations

Endpoints de Fases:
- GET    /v1/competitions/{id}/phases                → listPhases
- POST   /v1/competitions/{id}/phases                → createPhase
- PATCH  /v1/competitions/{id}/phases/{phase_id}     → updatePhase
- DELETE /v1/competitions/{id}/phases/{phase_id}     → deletePhase

Endpoints de Equipes Adversárias:
- GET    /v1/competitions/{id}/opponent-teams        → listOpponentTeams
- POST   /v1/competitions/{id}/opponent-teams        → createOpponentTeam
- PATCH  /v1/competitions/{id}/opponent-teams/{tid}  → updateOpponentTeam
- DELETE /v1/competitions/{id}/opponent-teams/{tid}  → deleteOpponentTeam
- POST   /v1/competitions/{id}/opponent-teams/bulk   → bulkCreateOpponentTeams

Endpoints de Jogos:
- GET    /v1/competitions/{id}/matches               → listCompetitionMatches
- POST   /v1/competitions/{id}/matches               → createCompetitionMatch
- PATCH  /v1/competitions/{id}/matches/{mid}         → updateCompetitionMatch
- PATCH  /v1/competitions/{id}/matches/{mid}/result  → updateMatchResult
- POST   /v1/competitions/{id}/matches/bulk          → bulkCreateMatches

Endpoints de Classificação:
- GET    /v1/competitions/{id}/standings             → getStandings
- POST   /v1/competitions/{id}/standings/recalculate → recalculateStandings
"""

import logging
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.api.v1.deps.auth import permission_dep
from app.core.context import ExecutionContext, get_current_context
from app.core.db import get_db
from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError
from app.models import (
    Competition,
    CompetitionPhase,
    CompetitionOpponentTeam,
    CompetitionMatch,
    CompetitionStanding,
    Team,
)
from app.schemas.competitions_v2 import (
    # Competition
    CompetitionV2Create,
    CompetitionV2Update,
    CompetitionV2Response,
    CompetitionV2WithRelations,
    CompetitionV2PaginatedResponse,
    # Phase
    CompetitionPhaseCreate,
    CompetitionPhaseUpdate,
    CompetitionPhaseResponse,
    # Opponent Team
    CompetitionOpponentTeamCreate,
    CompetitionOpponentTeamUpdate,
    CompetitionOpponentTeamResponse,
    # Match
    CompetitionMatchCreate,
    CompetitionMatchUpdate,
    CompetitionMatchResponse,
    CompetitionMatchResultUpdate,
    # Standing
    CompetitionStandingResponse,
    # AI
    AIParseRequest,
    AIParseResponse,
    AIValidateAndSaveRequest,
    AIExtractedCompetition,
)
from app.schemas.error import ErrorResponse
from app.services.gemini_competition_service import get_gemini_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["competitions-v2"])


# =============================================================================
# COMPETITION V2 ENDPOINTS
# =============================================================================

@router.post(
    "/competitions/v2",
    status_code=status.HTTP_201_CREATED,
    summary="Criar competição V2 (com novos campos)",
    operation_id="createCompetitionV2",
    response_model=CompetitionV2Response,
    responses={
        201: {"description": "Competição criada com sucesso"},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
async def create_competition_v2(
    data: CompetitionV2Create,
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> CompetitionV2Response:
    """
    Cria uma nova competição com todos os campos V2.
    """
    # Verifica permissão (dirigente ou coordenador)
    if context.role not in ["dirigente", "coordenador", "superadmin"]:
        raise ForbiddenError("Apenas dirigentes e coordenadores podem criar competições")

    competition = Competition(
        organization_id=str(context.organization_id),
        name=data.name,
        kind=data.kind,
        team_id=str(data.team_id) if data.team_id else None,
        season=data.season,
        modality=data.modality.value if data.modality else "masculino",
        competition_type=data.competition_type.value if data.competition_type else None,
        format_details=data.format_details,
        tiebreaker_criteria=data.tiebreaker_criteria,
        points_per_win=data.points_per_win,
        status="draft",
        regulation_file_url=data.regulation_file_url,
        regulation_notes=data.regulation_notes,
        created_by=str(context.user_id),
    )

    db.add(competition)
    await db.commit()
    await db.refresh(competition)

    logger.info(f"Competição V2 criada: {competition.id} por {context.user_id}")
    return CompetitionV2Response.model_validate(competition)


@router.post(
    "/competitions/v2/parse-pdf",
    status_code=status.HTTP_200_OK,
    summary="Extrair dados de PDF via IA (Gemini)",
    operation_id="parsePdfWithAI",
    response_model=AIParseResponse,
    responses={
        200: {"description": "Dados extraídos com sucesso"},
        400: {"description": "PDF inválido ou erro de parsing"},
        401: {"model": ErrorResponse},
        503: {"description": "Serviço Gemini indisponível"},
    },
)
async def parse_pdf_with_ai(
    data: AIParseRequest,
    context: ExecutionContext = Depends(get_current_context),
) -> AIParseResponse:
    """
    Envia um PDF para o Gemini e extrai dados estruturados da competição.
    
    O usuário deve validar os dados antes de salvar.
    """
    gemini = get_gemini_service()
    
    if not gemini.is_available():
        raise HTTPException(
            status_code=503,
            detail="Serviço de IA não está disponível. Verifique a configuração."
        )

    # Chamada SÍNCRONA (sem await) - compatível com Neon free
    result = gemini.parse_regulation_pdf(
        pdf_base64=data.pdf_base64,
        our_team_name=data.our_team_name,
        hints=data.hints,
    )

    if result.success and result.extracted_data:
        # Adiciona validação (também síncrona)
        validation = gemini.validate_extraction(result.extracted_data)
        logger.info(
            f"PDF processado com sucesso. Confidence: {result.extracted_data.overall_confidence_score}. "
            f"Warnings: {len(validation['warnings'])}"
        )

    return result


@router.post(
    "/competitions/v2/{competition_id}/import-from-ai",
    status_code=status.HTTP_200_OK,
    summary="Importar dados extraídos pela IA para uma competição",
    operation_id="importFromAI",
    response_model=CompetitionV2WithRelations,
    responses={
        200: {"description": "Dados importados com sucesso"},
        404: {"description": "Competição não encontrada"},
        422: {"model": ErrorResponse},
    },
)
async def import_from_ai(
    competition_id: UUID,
    data: AIValidateAndSaveRequest,
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> CompetitionV2WithRelations:
    """
    Importa os dados extraídos pela IA para uma competição existente.
    
    Este endpoint:
    1. Atualiza os campos da competição
    2. Cria as fases
    3. Cria as equipes adversárias
    4. Cria os jogos (com external_reference_id para upsert)
    """
    # Busca competição
    result = await db.execute(
        select(Competition).where(
            Competition.id == str(competition_id),
            Competition.organization_id == str(context.organization_id),
            Competition.deleted_at.is_(None),
        )
    )
    competition = result.scalar_one_or_none()
    
    if not competition:
        raise NotFoundError("Competição não encontrada")

    extracted = data.extracted_data

    # 1. Atualiza campos da competição
    if extracted.name:
        competition.name = extracted.name
    if extracted.season:
        competition.season = extracted.season
    if extracted.modality:
        competition.modality = extracted.modality
    if extracted.competition_type:
        competition.competition_type = extracted.competition_type
    if extracted.format_details:
        competition.format_details = extracted.format_details
    if extracted.tiebreaker_criteria:
        competition.tiebreaker_criteria = extracted.tiebreaker_criteria
    if extracted.points_per_win:
        competition.points_per_win = extracted.points_per_win
    if extracted.regulation_notes:
        competition.regulation_notes = extracted.regulation_notes
    
    if data.team_id:
        competition.team_id = str(data.team_id)

    # 2. Cria fases
    phase_map = {}  # name -> id (para vincular jogos)
    for idx, phase_data in enumerate(extracted.phases):
        phase = CompetitionPhase(
            competition_id=str(competition_id),
            name=phase_data.name,
            phase_type=phase_data.phase_type,
            order_index=phase_data.order_index or idx,
        )
        db.add(phase)
        await db.flush()
        phase_map[phase_data.name.lower()] = phase.id

    # 3. Cria equipes adversárias
    team_map = {}  # name -> id (para vincular jogos)
    for team_data in extracted.teams:
        opponent = CompetitionOpponentTeam(
            competition_id=str(competition_id),
            name=team_data.name,
            short_name=team_data.short_name,
            city=team_data.city,
            group_name=team_data.group_name,
        )
        
        # Tenta fazer fuzzy match se solicitado
        if data.auto_link_teams:
            linked = await _find_similar_team(db, team_data.name, context.organization_id)
            if linked:
                opponent.linked_team_id = linked
        
        db.add(opponent)
        await db.flush()
        team_map[team_data.name.lower()] = opponent.id

    # 4. Cria jogos
    for match_data in extracted.matches:
        home_id = team_map.get(match_data.home_team_name.lower())
        away_id = team_map.get(match_data.away_team_name.lower())
        
        match = CompetitionMatch(
            competition_id=str(competition_id),
            external_reference_id=match_data.external_reference_id,
            home_team_id=home_id,
            away_team_id=away_id,
            match_date=match_data.match_date,
            match_time=match_data.match_time,
            location=match_data.location,
            round_number=match_data.round_number,
            round_name=match_data.round_name,
            home_score=match_data.home_score,
            away_score=match_data.away_score,
            status="finished" if match_data.home_score is not None else "scheduled",
        )
        db.add(match)

    await db.commit()

    # Recarrega com relacionamentos
    result = await db.execute(
        select(Competition)
        .options(
            selectinload(Competition.phases),
            selectinload(Competition.opponent_teams),
            selectinload(Competition.matches),
        )
        .where(Competition.id == str(competition_id))
    )
    competition = result.scalar_one()

    return CompetitionV2WithRelations(
        **CompetitionV2Response.model_validate(competition).model_dump(),
        phases=[CompetitionPhaseResponse.model_validate(p) for p in competition.phases],
        opponent_teams=[CompetitionOpponentTeamResponse.model_validate(t) for t in competition.opponent_teams],
        matches_count=len(competition.matches),
        our_matches_count=sum(1 for m in competition.matches if m.is_our_match),
    )


@router.get(
    "/competitions/v2/{competition_id}/full",
    status_code=status.HTTP_200_OK,
    summary="Obter competição com todos os relacionamentos",
    operation_id="getCompetitionFull",
    response_model=CompetitionV2WithRelations,
)
async def get_competition_full(
    competition_id: UUID,
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> CompetitionV2WithRelations:
    """
    Retorna competição com fases, equipes e contagem de jogos.
    """
    result = await db.execute(
        select(Competition)
        .options(
            selectinload(Competition.phases),
            selectinload(Competition.opponent_teams),
            selectinload(Competition.matches),
        )
        .where(
            Competition.id == str(competition_id),
            Competition.organization_id == str(context.organization_id),
            Competition.deleted_at.is_(None),
        )
    )
    competition = result.scalar_one_or_none()
    
    if not competition:
        raise NotFoundError("Competição não encontrada")

    return CompetitionV2WithRelations(
        **CompetitionV2Response.model_validate(competition).model_dump(),
        phases=[CompetitionPhaseResponse.model_validate(p) for p in competition.phases],
        opponent_teams=[CompetitionOpponentTeamResponse.model_validate(t) for t in competition.opponent_teams],
        matches_count=len(competition.matches),
        our_matches_count=sum(1 for m in competition.matches if m.is_our_match),
    )


# =============================================================================
# PHASE ENDPOINTS
# =============================================================================

@router.get(
    "/competitions/{competition_id}/phases",
    status_code=status.HTTP_200_OK,
    summary="Listar fases da competição",
    operation_id="listCompetitionPhases",
    response_model=List[CompetitionPhaseResponse],
)
async def list_phases(
    competition_id: UUID,
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> List[CompetitionPhaseResponse]:
    """Lista todas as fases de uma competição ordenadas por order_index."""
    result = await db.execute(
        select(CompetitionPhase)
        .where(CompetitionPhase.competition_id == str(competition_id))
        .order_by(CompetitionPhase.order_index)
    )
    phases = result.scalars().all()
    return [CompetitionPhaseResponse.model_validate(p) for p in phases]


@router.post(
    "/competitions/{competition_id}/phases",
    status_code=status.HTTP_201_CREATED,
    summary="Criar fase na competição",
    operation_id="createCompetitionPhase",
    response_model=CompetitionPhaseResponse,
)
async def create_phase(
    competition_id: UUID,
    data: CompetitionPhaseCreate,
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> CompetitionPhaseResponse:
    """Cria uma nova fase na competição."""
    phase = CompetitionPhase(
        competition_id=str(competition_id),
        name=data.name,
        phase_type=data.phase_type.value,
        order_index=data.order_index,
        is_olympic_cross=data.is_olympic_cross,
        config=data.config,
    )
    db.add(phase)
    await db.commit()
    await db.refresh(phase)
    return CompetitionPhaseResponse.model_validate(phase)


@router.patch(
    "/competitions/{competition_id}/phases/{phase_id}",
    status_code=status.HTTP_200_OK,
    summary="Atualizar fase",
    operation_id="updateCompetitionPhase",
    response_model=CompetitionPhaseResponse,
)
async def update_phase(
    competition_id: UUID,
    phase_id: UUID,
    data: CompetitionPhaseUpdate,
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> CompetitionPhaseResponse:
    """Atualiza uma fase existente."""
    result = await db.execute(
        select(CompetitionPhase).where(
            CompetitionPhase.id == str(phase_id),
            CompetitionPhase.competition_id == str(competition_id),
        )
    )
    phase = result.scalar_one_or_none()
    if not phase:
        raise NotFoundError("Fase não encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(value, 'value'):  # Enum
            value = value.value
        setattr(phase, key, value)

    await db.commit()
    await db.refresh(phase)
    return CompetitionPhaseResponse.model_validate(phase)


@router.delete(
    "/competitions/{competition_id}/phases/{phase_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover fase",
    operation_id="deleteCompetitionPhase",
)
async def delete_phase(
    competition_id: UUID,
    phase_id: UUID,
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
):
    """Remove uma fase da competição."""
    result = await db.execute(
        select(CompetitionPhase).where(
            CompetitionPhase.id == str(phase_id),
            CompetitionPhase.competition_id == str(competition_id),
        )
    )
    phase = result.scalar_one_or_none()
    if not phase:
        raise NotFoundError("Fase não encontrada")

    await db.delete(phase)
    await db.commit()


# =============================================================================
# OPPONENT TEAMS ENDPOINTS
# =============================================================================

@router.get(
    "/competitions/{competition_id}/opponent-teams",
    status_code=status.HTTP_200_OK,
    summary="Listar equipes adversárias",
    operation_id="listOpponentTeams",
    response_model=List[CompetitionOpponentTeamResponse],
)
async def list_opponent_teams(
    competition_id: UUID,
    group_name: Optional[str] = Query(None, description="Filtrar por grupo"),
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> List[CompetitionOpponentTeamResponse]:
    """Lista todas as equipes adversárias de uma competição."""
    query = select(CompetitionOpponentTeam).where(
        CompetitionOpponentTeam.competition_id == str(competition_id)
    )
    if group_name:
        query = query.where(CompetitionOpponentTeam.group_name == group_name)
    
    result = await db.execute(query.order_by(CompetitionOpponentTeam.name))
    teams = result.scalars().all()
    return [CompetitionOpponentTeamResponse.model_validate(t) for t in teams]


@router.post(
    "/competitions/{competition_id}/opponent-teams",
    status_code=status.HTTP_201_CREATED,
    summary="Criar equipe adversária",
    operation_id="createOpponentTeam",
    response_model=CompetitionOpponentTeamResponse,
)
async def create_opponent_team(
    competition_id: UUID,
    data: CompetitionOpponentTeamCreate,
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> CompetitionOpponentTeamResponse:
    """Cria uma nova equipe adversária na competição."""
    team = CompetitionOpponentTeam(
        competition_id=str(competition_id),
        name=data.name,
        short_name=data.short_name,
        category=data.category,
        city=data.city,
        logo_url=data.logo_url,
        linked_team_id=str(data.linked_team_id) if data.linked_team_id else None,
        group_name=data.group_name,
    )
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return CompetitionOpponentTeamResponse.model_validate(team)


@router.post(
    "/competitions/{competition_id}/opponent-teams/bulk",
    status_code=status.HTTP_201_CREATED,
    summary="Criar várias equipes adversárias de uma vez",
    operation_id="bulkCreateOpponentTeams",
    response_model=List[CompetitionOpponentTeamResponse],
)
async def bulk_create_opponent_teams(
    competition_id: UUID,
    data: List[CompetitionOpponentTeamCreate],
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> List[CompetitionOpponentTeamResponse]:
    """Cria várias equipes adversárias de uma vez."""
    teams = []
    for item in data:
        team = CompetitionOpponentTeam(
            competition_id=str(competition_id),
            name=item.name,
            short_name=item.short_name,
            category=item.category,
            city=item.city,
            logo_url=item.logo_url,
            linked_team_id=str(item.linked_team_id) if item.linked_team_id else None,
            group_name=item.group_name,
        )
        db.add(team)
        teams.append(team)
    
    await db.commit()
    for team in teams:
        await db.refresh(team)
    
    return [CompetitionOpponentTeamResponse.model_validate(t) for t in teams]


@router.patch(
    "/competitions/{competition_id}/opponent-teams/{team_id}",
    status_code=status.HTTP_200_OK,
    summary="Atualizar equipe adversária",
    operation_id="updateOpponentTeam",
    response_model=CompetitionOpponentTeamResponse,
)
async def update_opponent_team(
    competition_id: UUID,
    team_id: UUID,
    data: CompetitionOpponentTeamUpdate,
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> CompetitionOpponentTeamResponse:
    """Atualiza uma equipe adversária."""
    result = await db.execute(
        select(CompetitionOpponentTeam).where(
            CompetitionOpponentTeam.id == str(team_id),
            CompetitionOpponentTeam.competition_id == str(competition_id),
        )
    )
    team = result.scalar_one_or_none()
    if not team:
        raise NotFoundError("Equipe não encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(value, 'value'):
            value = value.value
        setattr(team, key, value)

    await db.commit()
    await db.refresh(team)
    return CompetitionOpponentTeamResponse.model_validate(team)


# =============================================================================
# MATCHES ENDPOINTS
# =============================================================================

@router.get(
    "/competitions/{competition_id}/matches",
    status_code=status.HTTP_200_OK,
    summary="Listar jogos da competição",
    operation_id="listCompetitionMatches",
    response_model=List[CompetitionMatchResponse],
)
async def list_competition_matches(
    competition_id: UUID,
    phase_id: Optional[UUID] = Query(None, description="Filtrar por fase"),
    only_our_matches: bool = Query(False, description="Apenas nossos jogos"),
    status_filter: Optional[str] = Query(None, description="Filtrar por status"),
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> List[CompetitionMatchResponse]:
    """Lista todos os jogos de uma competição."""
    query = select(CompetitionMatch).where(
        CompetitionMatch.competition_id == str(competition_id)
    )
    
    if phase_id:
        query = query.where(CompetitionMatch.phase_id == str(phase_id))
    if only_our_matches:
        query = query.where(CompetitionMatch.is_our_match == True)
    if status_filter:
        query = query.where(CompetitionMatch.status == status_filter)
    
    result = await db.execute(
        query.order_by(CompetitionMatch.match_date, CompetitionMatch.match_time)
    )
    matches = result.scalars().all()
    return [CompetitionMatchResponse.model_validate(m) for m in matches]


@router.post(
    "/competitions/{competition_id}/matches",
    status_code=status.HTTP_201_CREATED,
    summary="Criar jogo na competição",
    operation_id="createCompetitionMatch",
    response_model=CompetitionMatchResponse,
)
async def create_competition_match(
    competition_id: UUID,
    data: CompetitionMatchCreate,
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> CompetitionMatchResponse:
    """Cria um novo jogo na competição."""
    match = CompetitionMatch(
        competition_id=str(competition_id),
        phase_id=str(data.phase_id) if data.phase_id else None,
        external_reference_id=data.external_reference_id,
        home_team_id=str(data.home_team_id) if data.home_team_id else None,
        away_team_id=str(data.away_team_id) if data.away_team_id else None,
        is_our_match=data.is_our_match,
        our_team_is_home=data.our_team_is_home,
        match_date=data.match_date,
        match_time=data.match_time,
        location=data.location,
        round_number=data.round_number,
        round_name=data.round_name,
    )
    db.add(match)
    await db.commit()
    await db.refresh(match)
    return CompetitionMatchResponse.model_validate(match)


@router.post(
    "/competitions/{competition_id}/matches/bulk",
    status_code=status.HTTP_201_CREATED,
    summary="Criar vários jogos de uma vez (com upsert)",
    operation_id="bulkCreateMatches",
    response_model=dict,
)
async def bulk_create_matches(
    competition_id: UUID,
    data: List[CompetitionMatchCreate],
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> dict:
    """
    Cria vários jogos de uma vez.
    Se external_reference_id já existir, atualiza o jogo existente (upsert).
    """
    created = 0
    updated = 0
    
    for item in data:
        # Verifica se já existe (upsert via external_reference_id)
        existing = None
        if item.external_reference_id:
            result = await db.execute(
                select(CompetitionMatch).where(
                    CompetitionMatch.competition_id == str(competition_id),
                    CompetitionMatch.external_reference_id == item.external_reference_id,
                )
            )
            existing = result.scalar_one_or_none()
        
        if existing:
            # Update
            for key, value in item.model_dump(exclude_unset=True).items():
                if value is not None:
                    setattr(existing, key, str(value) if isinstance(value, UUID) else value)
            updated += 1
        else:
            # Create
            match = CompetitionMatch(
                competition_id=str(competition_id),
                phase_id=str(item.phase_id) if item.phase_id else None,
                external_reference_id=item.external_reference_id,
                home_team_id=str(item.home_team_id) if item.home_team_id else None,
                away_team_id=str(item.away_team_id) if item.away_team_id else None,
                is_our_match=item.is_our_match,
                our_team_is_home=item.our_team_is_home,
                match_date=item.match_date,
                match_time=item.match_time,
                location=item.location,
                round_number=item.round_number,
                round_name=item.round_name,
            )
            db.add(match)
            created += 1
    
    await db.commit()
    return {"created": created, "updated": updated, "total": created + updated}


@router.patch(
    "/competitions/{competition_id}/matches/{match_id}/result",
    status_code=status.HTTP_200_OK,
    summary="Atualizar resultado do jogo",
    operation_id="updateMatchResult",
    response_model=CompetitionMatchResponse,
)
async def update_match_result(
    competition_id: UUID,
    match_id: UUID,
    data: CompetitionMatchResultUpdate,
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> CompetitionMatchResponse:
    """
    Atualiza apenas o resultado do jogo.
    O trigger do banco atualiza automaticamente as estatísticas das equipes.
    """
    result = await db.execute(
        select(CompetitionMatch).where(
            CompetitionMatch.id == str(match_id),
            CompetitionMatch.competition_id == str(competition_id),
        )
    )
    match = result.scalar_one_or_none()
    if not match:
        raise NotFoundError("Jogo não encontrado")

    match.home_score = data.home_score
    match.away_score = data.away_score
    match.home_score_extra = data.home_score_extra
    match.away_score_extra = data.away_score_extra
    match.home_score_penalties = data.home_score_penalties
    match.away_score_penalties = data.away_score_penalties
    match.status = data.status.value

    await db.commit()
    await db.refresh(match)
    
    logger.info(f"Resultado atualizado: {match_id} - {data.home_score}x{data.away_score}")
    return CompetitionMatchResponse.model_validate(match)


# =============================================================================
# STANDINGS ENDPOINTS
# =============================================================================

@router.get(
    "/competitions/{competition_id}/standings",
    status_code=status.HTTP_200_OK,
    summary="Obter classificação da competição",
    operation_id="getCompetitionStandings",
    response_model=List[CompetitionStandingResponse],
)
async def get_standings(
    competition_id: UUID,
    phase_id: Optional[UUID] = Query(None, description="Filtrar por fase"),
    group_name: Optional[str] = Query(None, description="Filtrar por grupo"),
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
) -> List[CompetitionStandingResponse]:
    """
    Retorna a classificação da competição.
    Se não houver dados em competition_standings, calcula a partir dos jogos.
    """
    # Primeiro tenta buscar do cache (competition_standings)
    query = select(CompetitionStanding).where(
        CompetitionStanding.competition_id == str(competition_id)
    )
    if phase_id:
        query = query.where(CompetitionStanding.phase_id == str(phase_id))
    if group_name:
        query = query.where(CompetitionStanding.group_name == group_name)
    
    result = await db.execute(query.order_by(CompetitionStanding.position))
    standings = result.scalars().all()
    
    if standings:
        return [CompetitionStandingResponse.model_validate(s) for s in standings]
    
    # Se não houver cache, calcula a partir das equipes (stats JSONB)
    query = select(CompetitionOpponentTeam).where(
        CompetitionOpponentTeam.competition_id == str(competition_id)
    )
    if group_name:
        query = query.where(CompetitionOpponentTeam.group_name == group_name)
    
    result = await db.execute(query)
    teams = result.scalars().all()
    
    # Ordena por pontos, saldo de gols, gols pro
    sorted_teams = sorted(
        teams,
        key=lambda t: (
            t.stats.get("points", 0) if t.stats else 0,
            t.stats.get("goal_difference", 0) if t.stats else 0,
            t.stats.get("goals_for", 0) if t.stats else 0,
        ),
        reverse=True
    )
    
    # Monta resposta
    standings_response = []
    for idx, team in enumerate(sorted_teams, 1):
        stats = team.stats or {}
        standings_response.append(CompetitionStandingResponse(
            id=UUID(team.id),
            competition_id=UUID(team.competition_id),
            phase_id=None,
            opponent_team_id=UUID(team.id),
            position=idx,
            group_name=team.group_name,
            points=stats.get("points", 0),
            played=stats.get("played", 0),
            wins=stats.get("wins", 0),
            draws=stats.get("draws", 0),
            losses=stats.get("losses", 0),
            goals_for=stats.get("goals_for", 0),
            goals_against=stats.get("goals_against", 0),
            goal_difference=stats.get("goal_difference", 0),
            recent_form=None,
            qualification_status=None,
            updated_at=team.updated_at,
        ))
    
    return standings_response


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def _find_similar_team(
    db: AsyncSession,
    team_name: str,
    organization_id: UUID,
) -> Optional[str]:
    """
    Tenta encontrar uma equipe similar pelo nome (fuzzy match simples).
    Retorna o ID se encontrar, None caso contrário.
    """
    # Busca equipes da organização
    result = await db.execute(
        select(Team).where(Team.organization_id == str(organization_id))
    )
    teams = result.scalars().all()
    
    # Fuzzy match simples: verifica se o nome contém ou está contido
    team_name_lower = team_name.lower()
    for team in teams:
        if team.name and (
            team_name_lower in team.name.lower() or
            team.name.lower() in team_name_lower
        ):
            return team.id
    
    return None
