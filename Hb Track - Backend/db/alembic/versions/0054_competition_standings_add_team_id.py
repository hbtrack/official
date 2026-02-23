"""add team_id to competition_standings

Revision ID: 0054
Revises: 0053
Create Date: 2026-02-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "0054"
down_revision: Union[str, Sequence[str], None] = "0053"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "competition_standings",
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_competition_standings_team_id",
        "competition_standings",
        "teams",
        ["team_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_competition_standings_team_id",
        "competition_standings",
        ["team_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_competition_standings_team_id", table_name="competition_standings")
    op.drop_constraint(
        "fk_competition_standings_team_id",
        "competition_standings",
        type_="foreignkey",
    )
    op.drop_column("competition_standings", "team_id")
