"""
INV-COMP-016: Placar de competição não pode ser negativo

Evidence:
  db/alembic/versions/0062_comp_db_check_constraints_competition_matches.py
  Constraint: ck_competition_matches_score_home_gte_0 (home_score >= 0 OR NULL)
  Constraint: ck_competition_matches_score_away_gte_0 (away_score >= 0 OR NULL)
  Table: competition_matches
  SSOT: Hb Track - Backend/docs/ssot/schema.sql :: competition_matches

Classe: A (DB Constraint — Runtime Integration)
Anti-falso-positivo: testa explicitamente SQLSTATE 23514 ou nome da constraint.
"""

import pytest
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

pytestmark = pytest.mark.asyncio

# ---------------------------------------------------------------------------
# SQL mínimo (sem depender de message humana)
# ---------------------------------------------------------------------------

_ORG_INSERT = "INSERT INTO organizations (id, name) VALUES (:id, :name)"

_COMP_INSERT = (
    "INSERT INTO competitions (id, organization_id, name)"
    " VALUES (:id, :org_id, :name)"
)

_MATCH_INSERT = (
    "INSERT INTO competition_matches (id, competition_id, home_score, away_score)"
    " VALUES (:id, :comp_id, :home_score, :away_score)"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _create_competition(session) -> str:
    """Cria org + competition e retorna comp_id como str."""
    org_id = str(uuid4())
    comp_id = str(uuid4())
    await session.execute(text(_ORG_INSERT), {"id": org_id, "name": "Test Org INV-016"})
    await session.execute(text(_COMP_INSERT), {"id": comp_id, "org_id": org_id, "name": "Test Comp INV-016"})
    await session.flush()
    return comp_id


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------

class TestInvComp016ScoreValid:
    """
    INV-COMP-016: ck_competition_matches_score_home_gte_0 e
    ck_competition_matches_score_away_gte_0 em competition_matches.

    Evidence: db/alembic/versions/0062_comp_db_check_constraints_competition_matches.py
    Constraint: ck_competition_matches_score_home_gte_0 /
                ck_competition_matches_score_away_gte_0
    """

    async def test_valid_scores_pass(self, async_db):
        """Caso válido: home=30, away=25 deve ser aceito."""
        comp_id = await _create_competition(async_db)
        await async_db.execute(
            text(_MATCH_INSERT),
            {"id": str(uuid4()), "comp_id": comp_id, "home_score": 30, "away_score": 25},
        )
        await async_db.flush()  # deve passar sem exceção

    async def test_null_scores_pass(self, async_db):
        """NULL scores são permitidos (partida não finalizada / em draft)."""
        comp_id = await _create_competition(async_db)
        await async_db.execute(
            text(_MATCH_INSERT),
            {"id": str(uuid4()), "comp_id": comp_id, "home_score": None, "away_score": None},
        )
        await async_db.flush()  # deve passar sem exceção

    async def test_negative_home_score_fails(self, async_db):
        """
        home_score=-1 deve violar ck_competition_matches_score_home_gte_0.
        SQLSTATE esperado: 23514 (check_violation).
        """
        comp_id = await _create_competition(async_db)
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(
                text(_MATCH_INSERT),
                {"id": str(uuid4()), "comp_id": comp_id, "home_score": -1, "away_score": 20},
            )
            await async_db.flush()

        err = str(exc_info.value)
        assert "23514" in err or "ck_competition_matches_score" in err.lower(), (
            f"Esperado SQLSTATE 23514 ou nome da constraint; obtido: {err[:300]}"
        )

    async def test_negative_away_score_fails(self, async_db):
        """
        away_score=-5 deve violar ck_competition_matches_score_away_gte_0.
        SQLSTATE esperado: 23514 (check_violation).
        """
        comp_id = await _create_competition(async_db)
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(
                text(_MATCH_INSERT),
                {"id": str(uuid4()), "comp_id": comp_id, "home_score": 20, "away_score": -5},
            )
            await async_db.flush()

        err = str(exc_info.value)
        assert "23514" in err or "ck_competition_matches_score" in err.lower(), (
            f"Esperado SQLSTATE 23514 ou nome da constraint; obtido: {err[:300]}"
        )
