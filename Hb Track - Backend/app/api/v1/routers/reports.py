"""
Routers para relatórios

Referências RAG:
- R26: Permissões por papel (coordenador, treinador)
- R42: Modo somente leitura sem vínculo
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Literal
from datetime import date
from uuid import UUID

from app.core.db import get_db
from app.core.context import ExecutionContext
from app.core.decorators import scoped_endpoint
from app.api.v1.deps.auth import require_role
from app.api.v1.deps.pagination import (
    pagination_params,
    PaginationParams,
    ATTENDANCE_ORDER_FIELDS,
    MINUTES_ORDER_FIELDS,
    LOAD_ORDER_FIELDS,
)

# Schemas
from app.schemas.reports.training import (
    TrainingPerformanceReport,
    TrainingPerformanceFilters,
    TrainingPerformanceTrend
)
from app.schemas.reports.athlete import (
    AthleteIndividualReport,
    AthleteIndividualFilters
)
from app.schemas.reports.wellness import (
    WellnessSummaryReport,
    WellnessSummaryFilters
)
from app.schemas.reports.medical import (
    MedicalCasesReport,
    MedicalCasesFilters
)
from app.schemas.reports.consolidated import (
    AttendanceReportResponse,
    MinutesReportResponse,
    LoadReportResponse,
)
from app.schemas.reports.team_correlation import (
    TeamTrainingGameCorrelationResponse,
    CorrelationContext,
    CorrelationSummary,
    TrainingFocusDistribution,
    ContentTranslationMacro,
    FocusBreakdown,
    LoadVsPerformance,
    LoadVsPerformancePoint,
    Consistency,
    Insights,
)

# Services
from app.services.reports.training_report_service import TrainingReportService
from app.services.reports.athlete_report_service import AthleteReportService
from app.services.reports.wellness_report_service import WellnessReportService
from app.services.reports.medical_report_service import MedicalReportService
from app.services.reports.consolidated_service import ConsolidatedReportService
from app.services.reports.team_analytics_service import TeamAnalyticsService


router = APIRouter(tags=["Reports"])


# ============================================================================
# R1: RELATÓRIOS DE PERFORMANCE EM TREINOS
# ============================================================================

@router.get(
    "/training-performance",
    response_model=list[TrainingPerformanceReport],
    summary="Relatório de Performance em Treinos",
    description="""
    Retorna métricas agregadas de performance de treinos.

    **Referências RAG:**
    - R18: Treinos como eventos operacionais
    - R22: Métricas de carga, PSE, assiduidade
    - RP5: Ausência gera carga = 0
    - RP6: Participação gera métricas obrigatórias

    **Permissões:**
    - Coordenador: acesso total
    - Treinador: acesso às suas equipes (R26)
    """
)
@scoped_endpoint("can_generate_reports")
async def get_training_performance_report(
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    team_id: Optional[UUID] = Query(None, description="Filtrar por equipe"),
    start_date: Optional[date] = Query(None, description="Data inicial"),
    end_date: Optional[date] = Query(None, description="Data final"),
    min_attendance_rate: Optional[float] = Query(None, ge=0, le=100, description="Taxa mínima de presença (%)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Lista relatórios de performance de treinos
    """
    filters = TrainingPerformanceFilters(
        organization_id=ctx.organization_id,
        season_id=season_id,
        team_id=team_id,
        start_date=start_date,
        end_date=end_date,
        min_attendance_rate=min_attendance_rate,
        skip=skip,
        limit=limit
    )

    return TrainingReportService.get_training_performance(db, filters)


@router.get(
    "/training-trends",
    response_model=list[TrainingPerformanceTrend],
    summary="Tendências de Performance em Treinos",
    description="""
    Retorna tendências agregadas por período (semana ou mês).

    **Referências RAG:**
    - R21: Estatísticas agregadas derivadas
    - R22: Métricas de treino
    """
)
@scoped_endpoint("can_generate_reports")
async def get_training_trends(
    season_id: Optional[UUID] = Query(None),
    team_id: Optional[UUID] = Query(None),
    period: str = Query("week", pattern="^(week|month)$"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Calcula tendências de performance ao longo do tempo
    """
    return TrainingReportService.get_training_trends(
        db=db,
        organization_id=ctx.organization_id,
        season_id=season_id,
        team_id=team_id,
        period=period
    )


@router.post(
    "/refresh-training-performance",
    status_code=status.HTTP_200_OK,
    summary="Atualizar Materialized View de Treinos",
    description="""
    Atualiza a materialized view de performance de treinos.

    **Referências RAG:**
    - R21: Estatísticas agregadas recalculáveis

    **Permissões:**
    - Apenas Coordenador
    """
)
async def refresh_training_performance(
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador"]))
):
    """
    Força atualização da materialized view
    """
    return TrainingReportService.refresh_materialized_view(db)


# ============================================================================
# R2: RELATÓRIOS INDIVIDUAIS DE ATLETA
# ============================================================================

@router.get(
    "/athletes/{athlete_id}",
    response_model=AthleteIndividualReport,
    summary="Relatório Individual de Atleta",
    description="""
    Retorna relatório completo de uma atleta (treinos, wellness, carga).

    **Referências RAG:**
    - R12: Atleta permanente no histórico
    - R13/R14: Estados e impactos
    - RP4: Escopo de participação
    - RP5: Ausência = carga 0
    - RP6: Participação = métricas obrigatórias

    **Permissões:**
    - Coordenador: acesso total
    - Treinador: acesso às suas atletas (R26)
    """
)
@scoped_endpoint("can_generate_reports")
async def get_athlete_individual_report(
    athlete_id: UUID,
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Retorna relatório individual de uma atleta
    """
    return AthleteReportService.get_athlete_report(db, athlete_id)


@router.get(
    "/athletes-list",
    response_model=list[AthleteIndividualReport],
    summary="Lista Relatorios de Atletas (alias legada)",
    description="""
    Alias legada para compatibilidade com chamadas /reports/athletes-list.
    Usa o mesmo payload e permissoes da rota oficial /reports/athletes.
    """,
    include_in_schema=False,
)
@router.get(
    "/athletes",
    response_model=list[AthleteIndividualReport],
    summary="Lista Relatórios de Atletas",
    description="""
    Lista relatórios individuais de atletas com filtros.

    **Referências RAG:**
    - R12: Atleta permanente
    - R13/R14: Estados e impactos
    - RP4: Escopo de participação

    **Permissões:**
    - Coordenador: acesso total
    - Treinador: acesso às suas atletas (R26)
    """
)
@scoped_endpoint("can_generate_reports")
async def list_athlete_reports(
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    team_id: Optional[UUID] = Query(None, description="Filtrar por equipe"),
    state: Optional[str] = Query(None, pattern="^(ativa|lesionada|dispensada)$", description="Estado da atleta"),
    min_attendance_rate: Optional[float] = Query(None, ge=0, le=100, description="Taxa mínima de assiduidade (%)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Lista relatórios individuais de atletas
    """
    filters = AthleteIndividualFilters(
        organization_id=ctx.organization_id,
        season_id=season_id,
        team_id=team_id,
        state=state,
        min_attendance_rate=min_attendance_rate,
        skip=skip,
        limit=limit
    )

    return AthleteReportService.list_athlete_reports(db, filters)


# ============================================================================
# R3: RELATÓRIOS DE PRONTIDÃO E BEM-ESTAR
# ============================================================================

@router.get(
    "/wellness-summary",
    response_model=WellnessSummaryReport,
    summary="Relatório de Prontidão e Bem-Estar",
    description="""
    Retorna resumo de bem-estar (wellness pré e pós-treino).

    **Referências RAG:**
    - RP6: Wellness obrigatório
    - RP7: Escalas padronizadas
    - RP8: Alertas de sobrecarga e fadiga

    **Permissões:**
    - Coordenador: acesso total
    - Treinador: acesso às suas equipes (R26)
    """
)
@scoped_endpoint("can_generate_reports")
async def get_wellness_summary_report(
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    team_id: Optional[UUID] = Query(None, description="Filtrar por equipe"),
    start_date: Optional[date] = Query(None, description="Data inicial"),
    end_date: Optional[date] = Query(None, description="Data final"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Retorna resumo de bem-estar
    """
    filters = WellnessSummaryFilters(
        organization_id=ctx.organization_id,
        season_id=season_id,
        team_id=team_id,
        start_date=start_date,
        end_date=end_date
    )

    return WellnessReportService.get_wellness_summary(db, filters)


@router.get(
    "/wellness-trends",
    response_model=list[dict],
    summary="Tendências de Bem-Estar",
    description="""
    Retorna tendências de wellness ao longo do tempo.

    **Referências RAG:**
    - RP8: Monitoramento de sobrecarga

    **Permissões:**
    - Coordenador: acesso total
    - Treinador: acesso às suas equipes (R26)
    """
)
@scoped_endpoint("can_generate_reports")
async def get_wellness_trends(
    season_id: Optional[UUID] = Query(None),
    team_id: Optional[UUID] = Query(None),
    period: str = Query("week", pattern="^(week|month)$"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Calcula tendências de wellness
    """
    return WellnessReportService.get_wellness_trends(
        db=db,
        organization_id=ctx.organization_id,
        season_id=season_id,
        team_id=team_id,
        period=period
    )


# ============================================================================
# R4: RELATÓRIOS DE GERENCIAMENTO DE LESÕES
# ============================================================================

@router.get(
    "/medical-summary",
    response_model=MedicalCasesReport,
    summary="Relatório de Gerenciamento de Lesões",
    description="""
    Retorna resumo de casos médicos e lesões.

    **Referências RAG:**
    - R13: Estados de atleta (lesionada)
    - R14: Impacto de estados em participação
    - RP7: Rastreamento de casos médicos

    **Permissões:**
    - Coordenador: acesso total
    - Treinador: acesso às suas equipes (R26)
    """
)
@scoped_endpoint("can_generate_reports")
async def get_medical_summary_report(
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    team_id: Optional[UUID] = Query(None, description="Filtrar por equipe"),
    start_date: Optional[date] = Query(None, description="Data inicial"),
    end_date: Optional[date] = Query(None, description="Data final"),
    status: Optional[str] = Query(None, pattern="^(ativo|resolvido)$", description="Status do caso"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Retorna resumo de casos médicos
    """
    filters = MedicalCasesFilters(
        organization_id=ctx.organization_id,
        season_id=season_id,
        team_id=team_id,
        start_date=start_date,
        end_date=end_date,
        status=status
    )

    return MedicalReportService.get_medical_summary(db, filters)


@router.get(
    "/athletes/{athlete_id}/medical-history",
    response_model=list[dict],
    summary="Histórico Médico de Atleta",
    description="""
    Retorna histórico completo de casos médicos de uma atleta.

    **Referências RAG:**
    - R13: Estados de atleta
    - RP7: Rastreamento médico

    **Permissões:**
    - Coordenador: acesso total
    - Treinador: acesso às suas atletas (R26)
    """
)
@scoped_endpoint("can_generate_reports")
async def get_athlete_medical_history(
    athlete_id: UUID,
    limit: int = Query(10, ge=1, le=100, description="Limite de registros"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Retorna histórico médico de uma atleta
    """
    return MedicalReportService.get_athlete_medical_history(db, athlete_id, limit)


# ============================================================================
# R5: RELATÓRIOS CONSOLIDADOS - ASSIDUIDADE, MINUTOS, CARGA
# ============================================================================

@router.get(
    "/attendance",
    response_model=AttendanceReportResponse,
    summary="Relatório de Assiduidade",
    description="""
    Retorna taxa de assiduidade por atleta em treinos e jogos.

    **Métricas incluídas:**
    - Total de treinos e jogos
    - Presenças em treinos e jogos
    - Taxa de presença (%) individual
    - Médias da equipe

    **Referências RAG:**
    - R17: Treinos como eventos operacionais
    - R19: Estatísticas vinculadas a jogo + equipe
    - R21: Métricas de treino (assiduidade)
    - RP5: Ausência = carga 0
    - RP6: Participação = métricas obrigatórias

    **Permissões:**
    - Coordenador: acesso total
    - Treinador: acesso às suas equipes (R26)
    """,
    responses={
        200: {"description": "Taxa de assiduidade por atleta"},
        403: {"description": "Equipe fora do escopo do usuário"},
        404: {"description": "Equipe não encontrada"},
    }
)
@scoped_endpoint("can_generate_reports")
async def get_attendance_report(
    team_id: UUID = Query(..., description="ID da equipe (obrigatório)"),
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    start_date: Optional[date] = Query(None, description="Data inicial"),
    end_date: Optional[date] = Query(None, description="Data final"),
    page: int = Query(1, ge=1, description="Página (1-indexed)"),
    page_size: int = Query(25, ge=1, le=100, description="Itens por página"),
    order_by: Optional[str] = Query(
        None,
        description="Campo de ordenação: athlete_name, training_attendance_rate, match_participation_rate, combined_attendance_rate"
    ),
    order_dir: str = Query("desc", pattern="^(asc|desc)$", description="Direção: asc ou desc"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Lista assiduidade de todos os atletas de uma equipe.
    
    **Paginação:**
    - page: número da página (default: 1)
    - page_size: itens por página (default: 25, máx: 100)
    
    **Ordenação:**
    - order_by: athlete_name, combined_attendance_rate, training_attendance_rate, match_participation_rate
    - order_dir: asc ou desc (default: desc)
    """
    # Validar order_by contra whitelist
    if order_by and order_by not in ATTENDANCE_ORDER_FIELDS:
        order_by = None  # Fallback para default
    
    try:
        return ConsolidatedReportService.get_attendance_report(
            db=db,
            team_id=team_id,
            organization_id=ctx.organization_id,
            season_id=season_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_dir=order_dir,
        )
    except ValueError as e:
        if "not_found_or_out_of_scope" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Team not found or out of scope"
            )
        raise


@router.get(
    "/minutes",
    response_model=MinutesReportResponse,
    summary="Relatório de Minutos Jogados",
    description="""
    Retorna minutos jogados por atleta em partidas e treinos.

    **Métricas incluídas:**
    - Minutos em jogos (minutes_played)
    - Minutos em treinos (minutes_effective)
    - Jogos com participação (played=true)
    - Titularidades (started=true)

    **Referências RAG:**
    - R19: minutes_played como estatística primária
    - R20: Estatísticas agregadas derivadas
    - R21: minutes_effective em treinos

    **Permissões:**
    - Coordenador: acesso total
    - Treinador: acesso às suas equipes (R26)
    """,
    responses={
        200: {"description": "Minutos por atleta"},
        403: {"description": "Equipe fora do escopo do usuário"},
        404: {"description": "Equipe não encontrada"},
    }
)
@scoped_endpoint("can_generate_reports")
async def get_minutes_report(
    team_id: UUID = Query(..., description="ID da equipe (obrigatório)"),
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    start_date: Optional[date] = Query(None, description="Data inicial"),
    end_date: Optional[date] = Query(None, description="Data final"),
    page: int = Query(1, ge=1, description="Página (1-indexed)"),
    page_size: int = Query(25, ge=1, le=100, description="Itens por página"),
    order_by: Optional[str] = Query(
        None,
        description="Campo de ordenação: athlete_name, total_minutes_played, total_training_minutes, total_activity_minutes"
    ),
    order_dir: str = Query("desc", pattern="^(asc|desc)$", description="Direção: asc ou desc"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Lista minutos jogados de todos os atletas de uma equipe.
    
    **Paginação:**
    - page: número da página (default: 1)
    - page_size: itens por página (default: 25, máx: 100)
    
    **Ordenação:**
    - order_by: athlete_name, total_minutes_played, total_training_minutes, total_activity_minutes
    - order_dir: asc ou desc (default: desc)
    """
    # Validar order_by contra whitelist
    if order_by and order_by not in MINUTES_ORDER_FIELDS:
        order_by = None
    
    try:
        return ConsolidatedReportService.get_minutes_report(
            db=db,
            team_id=team_id,
            organization_id=ctx.organization_id,
            season_id=season_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_dir=order_dir,
        )
    except ValueError as e:
        if "not_found_or_out_of_scope" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Team not found or out of scope"
            )
        raise


@router.get(
    "/load",
    response_model=LoadReportResponse,
    summary="Relatório de Carga",
    description="""
    Retorna carga acumulada por atleta (treinos + jogos).

    **Cálculo de carga:**
    - Treino: RPE × minutes_effective (wellness_post.session_rpe)
    - Jogo: minutes_played (carga estimada)
    - RPE padrão: 5 quando não informado

    **Métricas incluídas:**
    - Carga total de treinos
    - Carga total de jogos
    - Número de sessões/jogos
    - Média por sessão/jogo

    **Referências RAG:**
    - R21: Métricas de treino (carga)
    - RP5: Ausência = carga 0
    - RP8: Monitoramento de sobrecarga

    **Permissões:**
    - Coordenador: acesso total
    - Treinador: acesso às suas equipes (R26)
    """,
    responses={
        200: {"description": "Carga acumulada por atleta"},
        403: {"description": "Equipe fora do escopo do usuário"},
        404: {"description": "Equipe não encontrada"},
    }
)
@scoped_endpoint("can_generate_reports")
async def get_load_report(
    team_id: UUID = Query(..., description="ID da equipe (obrigatório)"),
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    start_date: Optional[date] = Query(None, description="Data inicial"),
    end_date: Optional[date] = Query(None, description="Data final"),
    page: int = Query(1, ge=1, description="Página (1-indexed)"),
    page_size: int = Query(25, ge=1, le=100, description="Itens por página"),
    order_by: Optional[str] = Query(
        None,
        description="Campo de ordenação: athlete_name, training_load_total, match_load_total, total_load, avg_daily_load"
    ),
    order_dir: str = Query("desc", pattern="^(asc|desc)$", description="Direção: asc ou desc"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Lista carga acumulada de todos os atletas de uma equipe.
    
    **Paginação:**
    - page: número da página (default: 1)
    - page_size: itens por página (default: 25, máx: 100)
    
    **Ordenação:**
    - order_by: athlete_name, training_load_total, match_load_total, total_load, avg_daily_load
    - order_dir: asc ou desc (default: desc)
    """
    # Validar order_by contra whitelist
    if order_by and order_by not in LOAD_ORDER_FIELDS:
        order_by = None
    
    try:
        return ConsolidatedReportService.get_load_report(
            db=db,
            team_id=team_id,
            organization_id=ctx.organization_id,
            season_id=season_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_dir=order_dir,
        )
    except ValueError as e:
        if "not_found_or_out_of_scope" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Team not found or out of scope"
            )
        raise


# ============================================================================
# REFRESH ENDPOINTS - Atualização de Materialized Views
# ============================================================================

@router.post(
    "/refresh/{view_name}",
    summary="Refresh Materialized View Específica",
    description="""
    Atualiza uma materialized view específica.

    **Views disponíveis:**
    - training_performance (R1)
    - athlete_training_summary (R2)
    - wellness_summary (R3)
    - medical_cases_summary (R4)

    **Referências RAG:**
    - RF29: Performance de queries
    - RD85: Índices e otimizações
    - R21: Atualização de relatórios

    **Permissões:**
    - Coordenador: acesso total
    """,
    tags=["Reports - Maintenance"]
)
async def refresh_specific_view(
    view_name: Literal["training_performance", "athlete_training_summary", "wellness_summary", "medical_cases_summary"],
    concurrent: bool = Query(True, description="Usar CONCURRENTLY (recomendado)"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador"]))
):
    """
    Refresh de uma materialized view específica (RF29, RD85)
    """

    from app.services.reports.refresh_service import RefreshService
    return RefreshService.refresh_view(db, view_name, concurrent)


@router.post(
    "/refresh-all",
    summary="Refresh de Todas as Materialized Views",
    description="""
    Atualiza todas as 4 materialized views do sistema de relatórios.

    **Operação:**
    - Refresha todas as views com CONCURRENTLY (não bloqueia leituras)
    - Retorna estatísticas de cada view após refresh

    **Referências RAG:**
    - RF29: Performance de queries
    - RD85: Índices e otimizações
    - R21: Atualização de relatórios

    **Permissões:**
    - Coordenador: acesso total
    """,
    tags=["Reports - Maintenance"]
)
async def refresh_all_views(
    concurrent: bool = Query(True, description="Usar CONCURRENTLY"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador"]))
):
    """
    Refresh de todas as materialized views (RF29, RD85)
    """
    from app.services.reports.refresh_service import RefreshService
    return RefreshService.refresh_all(db, concurrent)


@router.get(
    "/stats",
    summary="Estatísticas das Materialized Views",
    description="""
    Retorna estatísticas sobre todas as materialized views.

    **Informações retornadas:**
    - Número de registros em cada view
    - Schema e metadados
    - Último vacuum/refresh

    **Referências RAG:**
    - RF29: Monitoramento de performance
    - RD85: Otimizações

    **Permissões:**
    - Coordenador: acesso total
    """,
    tags=["Reports - Maintenance"]
)
async def get_views_stats(
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador"]))
):
    """
    Estatísticas das materialized views (RF29)
    """
    from app.services.reports.refresh_service import RefreshService
    return RefreshService.get_view_stats(db)


# ============================================================================
# R_STATISTICS_TEAMS: CORRELAÇÃO TREINO → JOGO
# ============================================================================

@router.get(
    "/team-training-game-correlation",
    response_model=TeamTrainingGameCorrelationResponse,
    summary="Correlação Treino → Jogo por Equipe",
    description="""
    Análise estratégica de correlação entre focos de treino e performance em jogos.
    
    **Pergunta estratégica respondida:**
    "O que do treino está (ou não) se traduzindo em performance de jogo?"
    
    **Estrutura da resposta:**
    - `context`: Contexto da análise (equipe, temporada, competição, período)
    - `summary`: Resumo executivo (total de jogos/treinos, médias, força de correlação)
    - `training_focus_distribution`: Distribuição dos 7 focos de treino (%)
    - `content_translation`: Mapeamento treino → jogo por macroblock (attack/defense/physical)
    - `load_vs_performance`: Scatter plot carga × eficiência
    - `consistency`: Métricas de variabilidade treino/jogo
    - `insights`: Arrays interpretativos (works/adjust/avoid)
    
    **Referências RAG:**
    - Especificação: eststisticas_equipes (2,199 linhas)
    - RAG/IMPLEMENTACAO_FOCOS_TREINO.md
    - R26: Permissões por papel (coordenador, treinador)
    - Domínio: /statistics/teams (análise estratégica, não operacional)
    
    **Permissões:**
    - Coordenador: acesso total
    - Treinador: acesso às suas equipes
    - Dirigente: acesso às equipes da organização
    """,
    tags=["Reports - Team Analytics"]
)
@scoped_endpoint("can_generate_reports")
async def get_team_training_game_correlation(
    team_id: UUID = Query(..., description="ID da equipe"),
    season_id: UUID = Query(..., description="ID da temporada"),
    competition_id: Optional[UUID] = Query(None, description="ID da competição (opcional)"),
    period_games: int = Query(5, ge=1, le=20, description="Número de jogos recentes a analisar"),
    training_window_days: int = Query(7, ge=3, le=21, description="Janela de treino pré-jogo (dias)"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador", "dirigente"]))
):
    """
    Retorna correlação entre focos de treino e performance de jogo.
    
    **Fluxo:**
    1. Busca últimos N jogos da equipe (period_games)
    2. Para cada jogo, busca treinos na janela pré-jogo (training_window_days)
    3. Agrega focos de treino (7 individuais → 3 macroblocks)
    4. Calcula correlações carga × eficiência
    5. Gera insights interpretativos (works/adjust/avoid)
    
    **Caso sem dados:**
    Retorna snapshot vazio com total_games=0 e arrays vazios.
    """
    from datetime import datetime, timedelta
    from sqlalchemy import and_, desc
    from app.models.match import Match
    from app.models.team import Team
    from app.models.season import Season
    from app.models.competition import Competition
    
    # Inicializar service
    analytics_service = TeamAnalyticsService(db)
    
    # 1. Validar acesso à equipe (scoped)
    team_stmt = select(Team).where(
        and_(
            Team.id == team_id,
            Team.organization_id == ctx.organization_id,
            Team.deleted_at.is_(None)
        )
    )
    team = db.execute(team_stmt).scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipe não encontrada ou sem acesso"
        )
    
    # 2. Buscar temporada
    season_stmt = select(Season).where(
        and_(
            Season.id == season_id,
            Season.organization_id == ctx.organization_id,
            Season.deleted_at.is_(None)
        )
    )
    season = db.execute(season_stmt).scalar_one_or_none()
    
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Temporada não encontrada"
        )
    
    # 3. Buscar competição (opcional)
    competition = None
    if competition_id:
        comp_stmt = select(Competition).where(
            and_(
                Competition.id == competition_id,
                Competition.organization_id == ctx.organization_id,
                Competition.deleted_at.is_(None)
            )
        )
        competition = db.execute(comp_stmt).scalar_one_or_none()
    
    # 4. Buscar jogos recentes da equipe
    games_stmt = (
        select(Match)
        .where(
            and_(
                Match.team_id == team_id,
                Match.season_id == season_id,
                Match.deleted_at.is_(None)
            )
        )
        .order_by(desc(Match.match_date))
        .limit(period_games)
    )
    
    if competition_id:
        games_stmt = games_stmt.where(Match.competition_id == competition_id)
    
    games = list(db.execute(games_stmt).scalars().all())
    
    # 5. Caso sem jogos: retornar snapshot vazio
    if not games:
        return TeamTrainingGameCorrelationResponse(
            context=CorrelationContext(
                team_id=team_id,
                team_name=team.name,
                season_id=season_id,
                season_name=season.name,
                competition_id=competition_id,
                competition_name=competition.name if competition else None,
                period=f"últimos {period_games} jogos",
                training_window_days=training_window_days,
                analysis_date=date.today()
            ),
            summary=CorrelationSummary(
                total_games=0,
                total_training_sessions=0,
                avg_training_load=0.0,
                avg_game_efficiency=0.0,
                correlation_strength="insuficiente"
            ),
            training_focus_distribution=TrainingFocusDistribution(
                attack_positional=0.0,
                defense_positional=0.0,
                transition_offense=0.0,
                transition_defense=0.0,
                attack_technical=0.0,
                defense_technical=0.0,
                physical=0.0
            ),
            content_translation={},
            load_vs_performance=LoadVsPerformance(points=[], trend=None),
            consistency=Consistency(
                training_load_variability=0.0,
                game_performance_variability=0.0,
                consistency_score="insuficiente"
            ),
            insights=Insights(works=[], adjust=[], avoid=[])
        )
    
    # 6. Processar cada jogo: buscar treinos na janela e calcular métricas
    all_training_sessions = []
    load_performance_points = []
    game_efficiencies = {"attack": [], "defense": []}
    
    for game in games:
        game_date = game.match_date
        window_start = game_date - timedelta(days=training_window_days)
        
        # Buscar treinos na janela pré-jogo
        sessions = analytics_service.fetch_training_sessions_in_window(
            team_id=team_id,
            season_id=season_id,
            start_date=window_start,
            end_date=game_date,
            organization_id=ctx.organization_id
        )
        
        all_training_sessions.extend(sessions)
        
        # Calcular carga média de treino
        avg_load = analytics_service.compute_avg_training_load_from_sessions(sessions)
        
        # Calcular eficiência de jogo (placeholder - necessita lógica específica)
        # TODO: Implementar compute_game_efficiency usando match_events
        game_efficiency = 65.0  # Placeholder
        
        load_performance_points.append(
            LoadVsPerformancePoint(
                game_id=game.id,
                game_date=game_date,
                avg_training_load=avg_load,
                game_efficiency=game_efficiency
            )
        )
        
        game_efficiencies["attack"].append(72.5)  # Placeholder
        game_efficiencies["defense"].append(65.2)  # Placeholder
    
    # 7. Agregar focos de treino
    focus_distribution = analytics_service.aggregate_training_focus(all_training_sessions)
    
    # 8. Computar macroblocks
    macroblock_data = analytics_service.compute_macroblock_aggregation(focus_distribution)
    
    # 9. Montar content_translation
    avg_attack_eff = sum(game_efficiencies["attack"]) / len(game_efficiencies["attack"]) if game_efficiencies["attack"] else 0.0
    avg_defense_eff = sum(game_efficiencies["defense"]) / len(game_efficiencies["defense"]) if game_efficiencies["defense"] else 0.0
    
    content_translation = {
        "attack": ContentTranslationMacro(
            training_focus_pct=macroblock_data["attack"]["total_pct"],
            game_efficiency=avg_attack_eff,
            focus_breakdown=FocusBreakdown(
                attack_positional=macroblock_data["attack"]["breakdown"]["attack_positional"],
                attack_technical=macroblock_data["attack"]["breakdown"]["attack_technical"],
                transition_offense=macroblock_data["attack"]["breakdown"]["transition_offense"]
            )
        ),
        "defense": ContentTranslationMacro(
            training_focus_pct=macroblock_data["defense"]["total_pct"],
            game_efficiency=avg_defense_eff,
            focus_breakdown=FocusBreakdown(
                defense_positional=macroblock_data["defense"]["breakdown"]["defense_positional"],
                defense_technical=macroblock_data["defense"]["breakdown"]["defense_technical"],
                transition_defense=macroblock_data["defense"]["breakdown"]["transition_defense"]
            )
        ),
        "physical": ContentTranslationMacro(
            training_focus_pct=macroblock_data["physical"]["total_pct"],
            game_efficiency=None,
            focus_breakdown=FocusBreakdown(
                physical=macroblock_data["physical"]["breakdown"]["physical"]
            )
        )
    }
    
    # 10. Calcular consistência
    training_load_var = analytics_service.compute_training_load_variability(all_training_sessions)
    
    # Placeholder para variabilidade de performance de jogo
    game_performance_var = 8.5  # TODO: Calcular a partir de game_efficiencies
    
    consistency_score = "alta" if training_load_var < 1.5 else "média" if training_load_var < 2.5 else "baixa"
    
    # 11. Gerar insights
    insights = analytics_service.generate_insights_from_correlation(
        macroblock_data=macroblock_data,
        game_efficiency={"attack": avg_attack_eff, "defense": avg_defense_eff},
        consistency={"training_load_variability": training_load_var}
    )
    
    # 12. Calcular médias para summary
    avg_training_load = analytics_service.compute_avg_training_load_from_sessions(all_training_sessions)
    avg_game_efficiency = (avg_attack_eff + avg_defense_eff) / 2 if (avg_attack_eff or avg_defense_eff) else 0.0
    
    # Determinar força de correlação (placeholder - necessita análise estatística)
    correlation_strength = "moderada"  # TODO: Calcular correlação de Pearson
    
    # 13. Determinar tendência do scatter plot
    if len(load_performance_points) >= 2:
        # Análise simples: se cargas maiores correspondem a eficiências maiores
        sorted_by_load = sorted(load_performance_points, key=lambda p: p.avg_training_load)
        first_half_eff = sum(p.game_efficiency for p in sorted_by_load[:len(sorted_by_load)//2]) / max(1, len(sorted_by_load)//2)
        second_half_eff = sum(p.game_efficiency for p in sorted_by_load[len(sorted_by_load)//2:]) / max(1, len(sorted_by_load) - len(sorted_by_load)//2)
        
        if second_half_eff > first_half_eff + 5:
            trend = "positiva"
        elif second_half_eff < first_half_eff - 5:
            trend = "negativa"
        else:
            trend = "neutra"
    else:
        trend = None
    
    # 14. Montar resposta completa
    return TeamTrainingGameCorrelationResponse(
        context=CorrelationContext(
            team_id=team_id,
            team_name=team.name,
            season_id=season_id,
            season_name=season.name,
            competition_id=competition_id,
            competition_name=competition.name if competition else None,
            period=f"últimos {len(games)} jogos",
            training_window_days=training_window_days,
            analysis_date=date.today()
        ),
        summary=CorrelationSummary(
            total_games=len(games),
            total_training_sessions=len(all_training_sessions),
            avg_training_load=avg_training_load,
            avg_game_efficiency=avg_game_efficiency,
            correlation_strength=correlation_strength
        ),
        training_focus_distribution=TrainingFocusDistribution(**focus_distribution),
        content_translation=content_translation,
        load_vs_performance=LoadVsPerformance(
            points=load_performance_points,
            trend=trend
        ),
        consistency=Consistency(
            training_load_variability=training_load_var,
            game_performance_variability=game_performance_var,
            consistency_score=consistency_score
        ),
        insights=Insights(**insights)
    )

