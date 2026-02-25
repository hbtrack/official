"""
COMP-DB-009+014: UNIQUE partial indexes em match_roster e competition_matches

Revision ID: 0063
Revises: 0062
Create Date: 2026-02-25 09:00:00.000000

Materializa:
- INV-COMP-009 (uq_match_roster_athlete_per_match): Um atleta no máximo uma vez
  na escalação de cada partida (proteção contra IA/OCR duplicado)
- INV-COMP-014 (uq_competition_matches_external_ref): Cada súmula importada apenas
  uma vez por competição (proteção contra re-importação acidental)

Partial index strategy:
- WHERE deleted_at IS NULL (ignora soft-deleted rows — não conflitam)
- external_reference condicional: WHERE IS NOT NULL (partidas sem id não conflitam)
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0063'
down_revision = '0062'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # INV-COMP-009: Um atleta no máximo uma vez por partida (ativo)
    # Partial index: ignora rows com soft-delete (deleted_at IS NOT NULL)
    op.create_index(
        'uq_match_roster_athlete_per_match',
        'match_roster',
        ['match_id', 'athlete_id'],
        unique=True,
        postgresql_where=sa.text('deleted_at IS NULL'),
    )

    # INV-COMP-014: Cada external_reference_id único por competição (ativo, com ID)
    # Partial index: ignora rows sem external_reference_id e rows soft-deleted
    op.create_index(
        'uq_competition_matches_external_ref',
        'competition_matches',
        ['competition_id', 'external_reference_id'],
        unique=True,
        postgresql_where=sa.text('external_reference_id IS NOT NULL AND deleted_at IS NULL'),
    )


def downgrade() -> None:
    # Remove indexes in reverse order
    op.drop_index('uq_competition_matches_external_ref', table_name='competition_matches')
    op.drop_index('uq_match_roster_athlete_per_match', table_name='match_roster')
