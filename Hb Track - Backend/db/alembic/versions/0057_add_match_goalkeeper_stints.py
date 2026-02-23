"""Add match_goalkeeper_stints table for goalkeeper efficiency analytics

Revision ID: 0057
Revises: 0056
Create Date: 2026-02-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "0057"
down_revision: Union[str, Sequence[str], None] = "0056"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "match_goalkeeper_stints",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("athlete_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_period_number", sa.SmallInteger(), nullable=False),
        sa.Column("start_time_seconds", sa.Integer(), nullable=False),
        sa.Column("end_period_number", sa.SmallInteger(), nullable=True),
        sa.Column("end_time_seconds", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["match_id"],
            ["matches.id"],
            name="fk_match_goalkeeper_stints_match_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["athlete_id"],
            ["athletes.id"],
            name="fk_match_goalkeeper_stints_athlete_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_match_goalkeeper_stints"),
        sa.CheckConstraint("start_time_seconds >= 0", name="ck_gk_stints_start"),
        sa.CheckConstraint("end_time_seconds IS NULL OR end_time_seconds >= 0", name="ck_gk_stints_end"),
        sa.CheckConstraint("start_period_number >= 1", name="ck_gk_stints_period"),
        comment="Stints de goleiras por partida para cálculo de eficiência e gols sofridos por intervalo.",
    )

    op.create_index(
        "ix_match_goalkeeper_stints_match_id",
        "match_goalkeeper_stints",
        ["match_id"],
    )
    op.create_index(
        "ix_match_goalkeeper_stints_athlete_id",
        "match_goalkeeper_stints",
        ["athlete_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_match_goalkeeper_stints_athlete_id", table_name="match_goalkeeper_stints")
    op.drop_index("ix_match_goalkeeper_stints_match_id", table_name="match_goalkeeper_stints")
    op.drop_table("match_goalkeeper_stints")
