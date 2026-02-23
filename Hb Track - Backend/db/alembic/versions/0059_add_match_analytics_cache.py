"""Add match_analytics_cache table for match reports v1.1

Revision ID: 0059
Revises: 0058
Create Date: 2026-02-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "0059"
down_revision: Union[str, Sequence[str], None] = "0058"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "match_analytics_cache",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("match_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("athlete_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cache_type", sa.String(length=32), nullable=False),
        sa.Column("total_shots", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("total_goals", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("goals_7m", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("shot_conversion_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("total_saves", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("goals_conceded", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("goalkeeper_efficiency_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("yellow_cards", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("red_cards", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("exclusions_2min", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("total_turnovers", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("total_assists", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("computed_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_final", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.ForeignKeyConstraint(
            ["match_id"],
            ["matches.id"],
            name="fk_match_analytics_cache_match_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.id"],
            name="fk_match_analytics_cache_team_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["athlete_id"],
            ["athletes.id"],
            name="fk_match_analytics_cache_athlete_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_match_analytics_cache"),
        sa.CheckConstraint(
            "cache_type IN ('team', 'athlete', 'goalkeeper')",
            name="ck_match_analytics_cache_type",
        ),
    )

    op.create_index(
        "ix_match_analytics_cache_match_id",
        "match_analytics_cache",
        ["match_id"],
        unique=False,
    )

    op.execute(
        """
        CREATE UNIQUE INDEX ux_match_analytics_cache_match_team_athlete
            ON match_analytics_cache (
                match_id,
                team_id,
                COALESCE(athlete_id, '00000000-0000-0000-0000-000000000000'::uuid),
                cache_type
            )
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ux_match_analytics_cache_match_team_athlete")
    op.drop_index("ix_match_analytics_cache_match_id", table_name="match_analytics_cache")
    op.drop_table("match_analytics_cache")
