# Services package
"""
Exporta todos os services de domínio.

FASE 5 - Todos os services implementados conforme RAG V1.1
"""

from app.services.organization_service import OrganizationService
from app.services.season_service import SeasonService
from app.services.team_service import TeamService
from app.services.user_service import UserService
# NOTA: athlete_service usa estruturas que não existem no DB atual (organization_id em Athlete, AthleteStateHistory)
# from app.services.athlete_service import AthleteService
from app.services.membership_service import MembershipService
from app.services.team_registration_service import TeamRegistrationService
from app.services.category_service import CategoryService
from app.services.match_service import MatchService
from app.services.match_event_service import MatchEventService
from app.services.training_session_service import TrainingSessionService
from app.services.role_service import RoleService

__all__ = [
    "OrganizationService",
    "SeasonService",
    "TeamService",
    "UserService",
    # "AthleteService",  # Desabilitado temporariamente
    "MembershipService",
    "TeamRegistrationService",
    "CategoryService",
    "MatchService",
    "MatchEventService",
    "TrainingSessionService",
    "RoleService",
]
