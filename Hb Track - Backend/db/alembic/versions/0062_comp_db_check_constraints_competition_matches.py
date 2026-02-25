"""
COMP-DB-016+018: CHECK constraints em competition_matches (score >= 0, times diferentes)

Revision ID: 0062
Revises: 0061
Create Date: 2026-02-25 04:30:00.000000

Materializa:
- INV-COMP-016 (ck_match_score_valid_for_standings): Placar não pode ser negativo
- INV-COMP-018 (ck_match_different_teams): Time não pode jogar contra si mesmo

NULL handling: constraints permitem NULL para partidas em draft/não finalizadas.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0062'
down_revision = '0061'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # INV-COMP-016: Placar não pode ser negativo (NULL permitido para partidas não finalizadas)
    op.create_check_constraint(
        'ck_competition_matches_score_home_gte_0',
        'competition_matches',
        'home_score >= 0 OR home_score IS NULL'
    )
    op.create_check_constraint(
        'ck_competition_matches_score_away_gte_0',
        'competition_matches',
        'away_score >= 0 OR away_score IS NULL'
    )

    # INV-COMP-018: Time não pode jogar contra si mesmo (NULL permitido para partidas em draft)
    op.create_check_constraint(
        'ck_competition_matches_different_teams',
        'competition_matches',
        'home_team_id != away_team_id OR home_team_id IS NULL OR away_team_id IS NULL'
    )


def downgrade() -> None:
    # Remove constraints in reverse order
    op.drop_constraint('ck_competition_matches_different_teams', 'competition_matches', type_='check')
    op.drop_constraint('ck_competition_matches_score_away_gte_0', 'competition_matches', type_='check')
    op.drop_constraint('ck_competition_matches_score_home_gte_0', 'competition_matches', type_='check')
