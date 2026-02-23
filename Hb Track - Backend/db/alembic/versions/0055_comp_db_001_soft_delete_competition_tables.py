"""COMP-DB-001: soft delete em 5 tabelas domínio competições/scout

Revision ID: 0055
Revises: 0054
Create Date: 2026-02-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0055"
down_revision: Union[str, Sequence[str], None] = "0054"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # competition_matches
    op.add_column("competition_matches", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("competition_matches", sa.Column("deleted_reason", sa.Text(), nullable=True))
    op.create_check_constraint(
        "ck_competition_matches_deleted_reason",
        "competition_matches",
        "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
    )
    op.execute(
        "CREATE TRIGGER trg_competition_matches_block_delete "
        "BEFORE DELETE ON competition_matches "
        "FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete()"
    )

    # competition_opponent_teams
    op.add_column("competition_opponent_teams", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("competition_opponent_teams", sa.Column("deleted_reason", sa.Text(), nullable=True))
    op.create_check_constraint(
        "ck_competition_opponent_teams_deleted_reason",
        "competition_opponent_teams",
        "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
    )
    op.execute(
        "CREATE TRIGGER trg_competition_opponent_teams_block_delete "
        "BEFORE DELETE ON competition_opponent_teams "
        "FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete()"
    )

    # competition_phases
    op.add_column("competition_phases", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("competition_phases", sa.Column("deleted_reason", sa.Text(), nullable=True))
    op.create_check_constraint(
        "ck_competition_phases_deleted_reason",
        "competition_phases",
        "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
    )
    op.execute(
        "CREATE TRIGGER trg_competition_phases_block_delete "
        "BEFORE DELETE ON competition_phases "
        "FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete()"
    )

    # match_events
    op.add_column("match_events", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("match_events", sa.Column("deleted_reason", sa.Text(), nullable=True))
    op.create_check_constraint(
        "ck_match_events_deleted_reason",
        "match_events",
        "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
    )
    op.execute(
        "CREATE TRIGGER trg_match_events_block_delete "
        "BEFORE DELETE ON match_events "
        "FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete()"
    )

    # match_roster
    op.add_column("match_roster", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("match_roster", sa.Column("deleted_reason", sa.Text(), nullable=True))
    op.create_check_constraint(
        "ck_match_roster_deleted_reason",
        "match_roster",
        "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
    )
    op.execute(
        "CREATE TRIGGER trg_match_roster_block_delete "
        "BEFORE DELETE ON match_roster "
        "FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete()"
    )


def downgrade() -> None:
    tables = [
        "match_roster",
        "match_events",
        "competition_phases",
        "competition_opponent_teams",
        "competition_matches",
    ]

    for table in tables:
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_block_delete ON {table}")

    for table in tables:
        op.drop_constraint(f"ck_{table}_deleted_reason", table)

    for table in tables:
        op.drop_column(table, "deleted_reason")
        op.drop_column(table, "deleted_at")
