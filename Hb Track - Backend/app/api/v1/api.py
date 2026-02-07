"""
API v1 router aggregator.

Este módulo centraliza todos os routers da API v1, definindo prefixos
e organizando os endpoints por domínio.

FASE 4 — FastAPI mínimo
"""

from fastapi import APIRouter

# Health
from app.api.v1.routers import health

# Exercises (Banco de Exercícios)
from app.api.v1.routers import exercises
from app.api.v1.routers import session_exercises  # Step 21: Drag-and-drop exercícios
from app.api.v1.routers import session_templates  # Step 30: Templates customizados

# Domain routers
from app.api.v1.routers import (
    analytics,
    auth,
    categories,
    seasons,
    teams,
    athletes,
    # athlete_states,  # DESABILITADO: depende de AthleteStateHistory que não existe
    attendance,
    audit_logs,
    competitions,
    competitions_v2,  # V2: Módulo com IA
    competition_seasons,
    match_events,
    match_roster,
    match_teams,
    matches,
    organizations,
    permissions,
    roles,
    team_registrations,
    training_sessions,
    training_cycles,
    training_microcycles,
    training_alerts_step18,  # Step 18: Alertas e Sugestões
    training_analytics,  # Step 16/22: Training Analytics
    users,
    wellness_post,
    wellness_pre,
    persons,
    admin_neon,
)

# Memberships tem 2 routers - importar ambos
from app.api.v1.routers.memberships import router as memberships_router
from app.api.v1.routers.memberships import org_memberships_router

# Unified Registration (Ficha Única)
from app.api.v1.routers import unified_registration

# Intake (Ficha Única - Endpoints complementares)
from app.api.v1.routers import intake

# Media (Upload de arquivos)
from app.api.v1.routers import media

# Lookup (tabelas de referência)
from app.api.v1.routers import lookup

# Reports (Relatórios)
from app.api.v1.routers import reports
from app.api.v1.routers import reports_operational

# Dashboard (Endpoint agregado otimizado)
from app.api.v1.routers import dashboard

# Exports (Step 23: Export PDF Assíncrono) - TEMPORARIAMENTE DESABILITADO
# from app.api.v1.routers import exports

# Athlete Export (Step 24: LGPD Data Export) - TEMPORARIAMENTE DESABILITADO
# from app.api.v1.routers import athlete_export
# from app.api.v1.routers import data_retention

# Import Legacy (Step 28: CSV Import) - TEMPORARIAMENTE DESABILITADO
# from app.api.v1.routers import import_legacy

api_router = APIRouter()

# =============================================================================
# HEALTH
# =============================================================================
# health.router já tem /health nas rotas internas
api_router.include_router(health.router, tags=["health"])
api_router.include_router(admin_neon.router, tags=["admin"])

# =============================================================================
# AUTHENTICATION
# =============================================================================
# auth.router já tem prefix="/auth" interno
api_router.include_router(auth.router)

# =============================================================================
# RECURSOS PRINCIPAIS
# =============================================================================

# Categories
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])

# Seasons (prefix removido do router em PC-01)
api_router.include_router(seasons.router, prefix="/seasons", tags=["seasons"])

# Teams (prefix removido do router em PC-02)
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])

# Athletes (já tem prefix="/athletes" interno)
api_router.include_router(athletes.router, tags=["athletes"])

# Memberships - DOIS routers (verificado em PC-03)
# memberships_router já tem prefix="/memberships" interno
api_router.include_router(memberships_router, tags=["memberships"])
# org_memberships_router já tem prefix="/organizations" e rotas /{id}/memberships
api_router.include_router(org_memberships_router, tags=["memberships"])

# Competitions (rotas internas já definem paths completos com /competitions)
api_router.include_router(competitions.router, tags=["competitions"])

# Competitions V2 - Módulo com IA Gemini
api_router.include_router(competitions_v2.router, tags=["competitions-v2"])

# Training Sessions
api_router.include_router(training_sessions.router, prefix="/training-sessions", tags=["training-sessions"])
api_router.include_router(training_sessions.scoped_router, tags=["training-sessions"])

# Training Cycles (TRAINNIG.MD)
api_router.include_router(training_cycles.router, tags=["training-cycles"])

# Training Microcycles (TRAINNIG.MD)
api_router.include_router(training_microcycles.router, tags=["training-microcycles"])

# Training Alerts & Suggestions (Step 18)
api_router.include_router(training_alerts_step18.router, tags=["training-alerts-suggestions"])

# Exercises (Banco de Exercícios) - Routers: exercise-tags, exercises, exercise-favorites
import logging
logger = logging.getLogger(__name__)
logger.info(f"[DEBUG] Including exercises.router with {len(exercises.router.routes)} routes")
try:
    api_router.include_router(exercises.router)
    logger.info("[DEBUG] exercises.router included successfully")
except Exception as e:
    logger.error(f"[DEBUG] ERROR including exercises.router: {e}", exc_info=True)

# Session Exercises (Step 21)
api_router.include_router(session_exercises.router, tags=["session-exercises"])

# Session Templates (Step 30: Templates customizados de treino)
api_router.include_router(session_templates.router, tags=["session-templates"])

# Audit Logs
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])

# =============================================================================
# SUBRECURSOS
# =============================================================================

# Subrecursos de Athletes (já tem prefix="/athletes" interno)
# api_router.include_router(athlete_states.router, tags=["athlete-states"])  # DESABILITADO

# Team Registrations (rotas internas já definem paths completos)
api_router.include_router(team_registrations.router, tags=["team-registrations"])

# Subrecursos de Competitions (rotas internas já definem paths completos)
api_router.include_router(competition_seasons.router, tags=["competition-seasons"])

# Matches e subrecursos (rotas internas já definem paths completos)
api_router.include_router(matches.scoped_router, tags=["Matches"])
api_router.include_router(match_teams.router, prefix="/matches", tags=["match-teams"])
api_router.include_router(match_teams.scoped_router, tags=["match-teams"])
api_router.include_router(match_roster.router, prefix="/matches", tags=["match-roster"])
api_router.include_router(match_roster.scoped_router, tags=["match-roster"])
api_router.include_router(match_events.router, prefix="/matches", tags=["match-events"])
api_router.include_router(match_events.scoped_events_router, tags=["match-events"])

# Subrecursos de Training (attendance já inclui /training_sessions nos paths)
api_router.include_router(attendance.router, tags=["attendance"])

# Wellness
api_router.include_router(wellness_pre.router, prefix="/wellness-pre", tags=["wellness"])
api_router.include_router(wellness_post.router, prefix="/wellness-post", tags=["wellness"])

# Analytics
api_router.include_router(analytics.router, tags=["analytics"])
api_router.include_router(training_analytics.router, tags=["training-analytics"])

# =============================================================================
# RBAC
# =============================================================================

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
api_router.include_router(persons.router, prefix="/persons", tags=["persons"])

# =============================================================================
# UNIFIED REGISTRATION (Ficha Única)
# =============================================================================
api_router.include_router(unified_registration.router, tags=["unified-registration"])

# =============================================================================
# INTAKE (Ficha Única - Endpoints complementares)
# =============================================================================
api_router.include_router(intake.router, tags=["intake"])

# =============================================================================
# MEDIA (Upload de arquivos)
# =============================================================================
api_router.include_router(media.router, tags=["media"])

# =============================================================================
# LOOKUP (Tabelas de referência)
# =============================================================================
api_router.include_router(lookup.router, tags=["lookup"])

# =============================================================================
# REPORTS (Relatórios)
# =============================================================================
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(reports_operational.router, prefix="/reports", tags=["reports"])

# =============================================================================
# DASHBOARD (Endpoint agregado otimizado)
# =============================================================================
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# =============================================================================
# EXPORTS (Step 23: Export PDF Assíncrono) - TEMPORARIAMENTE DESABILITADO
# =============================================================================
# api_router.include_router(exports.router, tags=["exports"])

# =============================================================================
# ATHLETE DATA EXPORT (Step 24: LGPD Compliance) - TEMPORARIAMENTE DESABILITADO
# =============================================================================
# api_router.include_router(athlete_export.router, tags=["lgpd"])

# =============================================================================
# DATA RETENTION & ANONYMIZATION (Step 25: LGPD Compliance) - TEMPORARIAMENTE DESABILITADO
# =============================================================================
# api_router.include_router(data_retention.router, prefix="/data-retention", tags=["lgpd"])

# Import Legacy - TEMPORARIAMENTE DESABILITADO
# api_router.include_router(import_legacy.router, tags=["admin-import"])
