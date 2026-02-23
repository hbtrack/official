"""Add justified status to attendance presence_status

Revision ID: 0058
Revises: 0057
Create Date: 2026-02-21
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0058"
down_revision: Union[str, Sequence[str], None] = "0057"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_attendance_status", "attendance", type_="check")
    op.create_check_constraint(
        "ck_attendance_status",
        "attendance",
        "presence_status IN ('present', 'absent', 'justified')",
    )

    op.execute(
        """
        UPDATE attendance
           SET presence_status = 'justified'
         WHERE presence_status = 'absent'
           AND reason_absence IS NOT NULL
           AND deleted_at IS NULL
        """
    )

    op.create_check_constraint(
        "ck_attendance_absent_reason_null",
        "attendance",
        "(deleted_at IS NOT NULL) OR (presence_status <> 'absent') OR (reason_absence IS NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_attendance_absent_reason_null", "attendance", type_="check")

    op.execute(
        """
        UPDATE attendance
           SET presence_status = 'absent'
         WHERE presence_status = 'justified'
        """
    )

    op.drop_constraint("ck_attendance_status", "attendance", type_="check")
    op.create_check_constraint(
        "ck_attendance_status",
        "attendance",
        "presence_status IN ('present', 'absent')",
    )
