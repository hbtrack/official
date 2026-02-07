"""
Schemas package for HandLab API.

Exports all Pydantic schemas for API request/response handling.
"""

from app.schemas.athletes import (
    Athlete,
    AthleteCreate,
    AthletePaginatedResponse,
    AthleteState,
    AthleteStateCreate,
    AthleteStateEnum,
    AthleteUpdate,
    TeamRegistration,
    TeamRegistrationCreate,
    TeamRegistrationUpdate,
)
from app.schemas.error import (
    ERROR_AGE_CATEGORY_VIOLATION,
    ERROR_CONFLICT_MEMBERSHIP_ACTIVE,
    ERROR_EDIT_FINALIZED_GAME,
    ERROR_INVALID_GOALKEEPER_STAT,
    ERROR_INVALID_STATE_TRANSITION,
    ERROR_NOT_FOUND,
    ERROR_PERIOD_OVERLAP,
    ERROR_PERMISSION_DENIED,
    ERROR_SEASON_LOCKED,
    ERROR_UNAUTHORIZED,
    ERROR_VALIDATION,
    ErrorResponse,
    error_age_category_violation,
    error_conflict_membership_active,
    error_edit_finalized_game,
    error_invalid_goalkeeper_stat,
    error_invalid_state_transition,
    error_not_found,
    error_period_overlap,
    error_permission_denied,
    error_season_locked,
    error_unauthorized,
    error_validation,
)
from app.schemas.categories import (
    CategoryBase,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryList,
)
from app.schemas.matches import (
    MatchBase,
    MatchCreate,
    MatchUpdate,
    MatchStatusUpdate,
    MatchResponse,
    MatchSummary,
    MatchList,
    MatchWithEvents,
)
from app.schemas.match_events import (
    MatchEventBase,
    MatchEventCreate,
    MatchEventUpdate,
    MatchEventCorrection,
    MatchEventResponse,
    MatchEventSummary,
    MatchEventList,
    AthleteMatchStats,
    TeamMatchStats,
)

__all__ = [
    # Athletes
    "Athlete",
    "AthleteCreate",
    "AthleteUpdate",
    "AthletePaginatedResponse",
    "AthleteStateEnum",
    # Athlete States
    "AthleteState",
    "AthleteStateCreate",
    # Team Registrations
    "TeamRegistration",
    "TeamRegistrationCreate",
    "TeamRegistrationUpdate",
    # Categories
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryList",
    # Matches
    "MatchBase",
    "MatchCreate",
    "MatchUpdate",
    "MatchStatusUpdate",
    "MatchResponse",
    "MatchSummary",
    "MatchList",
    "MatchWithEvents",
    # Match Events
    "MatchEventBase",
    "MatchEventCreate",
    "MatchEventUpdate",
    "MatchEventCorrection",
    "MatchEventResponse",
    "MatchEventSummary",
    "MatchEventList",
    "AthleteMatchStats",
    "TeamMatchStats",
    # Errors
    "ErrorResponse",
    "ERROR_UNAUTHORIZED",
    "ERROR_PERMISSION_DENIED",
    "ERROR_NOT_FOUND",
    "ERROR_CONFLICT_MEMBERSHIP_ACTIVE",
    "ERROR_PERIOD_OVERLAP",
    "ERROR_SEASON_LOCKED",
    "ERROR_EDIT_FINALIZED_GAME",
    "ERROR_VALIDATION",
    "ERROR_AGE_CATEGORY_VIOLATION",
    "ERROR_INVALID_STATE_TRANSITION",
    "ERROR_INVALID_GOALKEEPER_STAT",
    # Error factories
    "error_unauthorized",
    "error_permission_denied",
    "error_not_found",
    "error_conflict_membership_active",
    "error_period_overlap",
    "error_season_locked",
    "error_edit_finalized_game",
    "error_age_category_violation",
    "error_invalid_state_transition",
    "error_invalid_goalkeeper_stat",
    "error_validation",
]
