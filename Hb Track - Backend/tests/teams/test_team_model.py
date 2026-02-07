"""
Testes do Model Team.
"""
import pytest
from uuid import uuid4
from app.models.team import Team


class TestTeamModel:
    """Testes do modelo Team."""

    def test_create_team(self, db, organization, season_ativa):
        """Cria team com campos obrigatórios."""
        team = Team(
            name="Sub-17 Feminino",
            organization_id=organization.id,
            season_id=season_ativa.id,
            category_id=1,
            created_by_membership_id=uuid4(),
        )
        db.add(team)
        db.flush()

        assert team.id is not None
        assert team.name == "Sub-17 Feminino"
        assert team.created_at is not None

    def test_team_relationships(self, db, team):
        """Verifica relationships do team."""
        assert team.organization is not None
        assert team.season is not None

    def test_team_repr(self, team):
        """Verifica __repr__ do model."""
        repr_str = repr(team)
        assert "Team" in repr_str
        assert team.name in repr_str
