"""
INV-COMP-018: Times diferentes em competition_matches

Evidence:
  db/alembic/versions/0062_comp_db_check_constraints_competition_matches.py
  Constraint: ck_competition_matches_different_teams
              (home_team_id != away_team_id OR home_team_id IS NULL OR away_team_id IS NULL)
  Table: competition_matches
  SSOT: Hb Track - Backend/docs/ssot/schema.sql :: competition_matches

Classe: A (DB Constraint — Runtime Integration)
Anti-falso-positivo: testa explicitamente SQLSTATE 23514 ou nome da constraint.
Nota: home=X, away=NULL é permitido pela constraint (um dos lados NULL → TRUE).
"""

import pytest
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

pytestmark = pytest.mark.asyncio

# ---------------------------------------------------------------------------
# SQL mínimo
# ---------------------------------------------------------------------------

_ORG_INSERT = "INSERT INTO organizations (id, name) VALUES (:id, :name)"

_COMP_INSERT = (
    "INSERT INTO competitions (id, organization_id, name)"
    " VALUES (:id, :org_id, :name)"
)

_TEAM_INSERT = (
    "INSERT INTO competition_opponent_teams (id, competition_id, name)"
    " VALUES (:id, :comp_id, :name)"
)

_MATCH_INSERT = (
    "INSERT INTO competition_matches (id, competition_id, home_team_id, away_team_id)"
    " VALUES (:id, :comp_id, :home_team_id, :away_team_id)"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _create_teams(session) -> dict:
    """Cria org → competition → 2 teams e retorna os IDs."""
    org_id = str(uuid4())
    comp_id = str(uuid4())
    team1_id = str(uuid4())
    team2_id = str(uuid4())

    await session.execute(text(_ORG_INSERT), {"id": org_id, "name": "Test Org INV-018"})
    await session.execute(text(_COMP_INSERT), {"id": comp_id, "org_id": org_id, "name": "Test Comp INV-018"})
    await session.execute(text(_TEAM_INSERT), {"id": team1_id, "comp_id": comp_id, "name": "Team A"})
    await session.execute(text(_TEAM_INSERT), {"id": team2_id, "comp_id": comp_id, "name": "Team B"})
    await session.flush()

    return {"comp_id": comp_id, "team1_id": team1_id, "team2_id": team2_id}


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------

class TestInvComp018DifferentTeams:
    """
    INV-COMP-018: ck_competition_matches_different_teams em competition_matches.
    Time não pode jogar contra si mesmo.

    Evidence: db/alembic/versions/0062_comp_db_check_constraints_competition_matches.py
    Constraint: ck_competition_matches_different_teams
    """

    async def test_different_teams_pass(self, async_db):
        """Caso válido: home_team_id != away_team_id deve ser aceito."""
        data = await _create_teams(async_db)
        await async_db.execute(
            text(_MATCH_INSERT),
            {
                "id": str(uuid4()),
                "comp_id": data["comp_id"],
                "home_team_id": data["team1_id"],
                "away_team_id": data["team2_id"],
            },
        )
        await async_db.flush()  # deve passar sem exceção

    async def test_both_null_pass(self, async_db):
        """Ambos NULL — partida em draft sem equipes definidas — deve passar."""
        data = await _create_teams(async_db)
        await async_db.execute(
            text(_MATCH_INSERT),
            {
                "id": str(uuid4()),
                "comp_id": data["comp_id"],
                "home_team_id": None,
                "away_team_id": None,
            },
        )
        await async_db.flush()  # deve passar sem exceção

    async def test_home_set_away_null_pass(self, async_db):
        """home preenchido + away=NULL — partida parcialmente definida — deve passar (critério 5 da AR)."""
        data = await _create_teams(async_db)
        await async_db.execute(
            text(_MATCH_INSERT),
            {
                "id": str(uuid4()),
                "comp_id": data["comp_id"],
                "home_team_id": data["team1_id"],
                "away_team_id": None,
            },
        )
        await async_db.flush()  # deve passar sem exceção

    async def test_same_team_fails(self, async_db):
        """
        home_team_id == away_team_id deve violar ck_competition_matches_different_teams.
        SQLSTATE esperado: 23514 (check_violation).
        """
        data = await _create_teams(async_db)
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(
                text(_MATCH_INSERT),
                {
                    "id": str(uuid4()),
                    "comp_id": data["comp_id"],
                    "home_team_id": data["team1_id"],  # mesmo UUID
                    "away_team_id": data["team1_id"],  # mesmo UUID → violação
                },
            )
            await async_db.flush()

        err = str(exc_info.value)
        assert "23514" in err or "ck_competition_matches_different_teams" in err.lower(), (
            f"Esperado SQLSTATE 23514 ou nome da constraint; obtido: {err[:300]}"
        )
