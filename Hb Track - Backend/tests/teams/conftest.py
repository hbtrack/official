"""
Fixtures para testes de Teams.
"""
import pytest
from uuid import uuid4
from app.models.team import Team


@pytest.fixture
def team_data(organization, season_ativa):
    """Dados para criar team."""
    return {
        "name": "Sub-15 Feminino",
        "organization_id": organization.id,
        "season_id": season_ativa.id,
        "category_id": 1,
        "created_by_membership_id": uuid4(),
    }


@pytest.fixture
def team(db, team_data):
    """Team para testes."""
    t = Team(**team_data)
    db.add(t)
    db.flush()
    return t
