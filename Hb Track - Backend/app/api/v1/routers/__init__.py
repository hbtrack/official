"""API v1 routers package (FASE 5 - recursos conforme RAG V1.1)"""

from app.api.v1.routers import (
    health,
    persons,
    categories,
    roles,
    organizations,
    seasons,
    users,
    memberships,
    teams,
    # NOTA: Athletes desabilitado temporariamente - usa tabelas que não existem no DB
    # athletes,
    # athlete_states,
    team_registrations,
    training_sessions,
    matches,
    match_events,
    match_roster,
    match_teams,
    reports,
    alerts,
    admin_neon,
    lookup,
    unified_registration,
    intake,
    media,
)

__all__ = [
    "health",
    "persons",
    "categories",
    "roles",
    "organizations",
    "seasons",
    "users",
    "memberships",
    "teams",
    # "athletes",  # Desabilitado
    # "athlete_states",  # Desabilitado
    "team_registrations",
    "training_sessions",
    "matches",
    "match_events",
    "match_roster",
    "match_teams",
    "reports",
    "alerts",
    "admin_neon",
    "lookup",
    "unified_registration",
    "intake",
    "media",
]

# Routers disponíveis mas não registrados ainda na API v1 (FASE 6+):
# - attendance
# - audit_logs
# - competitions
# - competition_seasons
# - match_roster
# - match_teams
# - permissions
# - wellness_post
# - wellness_pre
