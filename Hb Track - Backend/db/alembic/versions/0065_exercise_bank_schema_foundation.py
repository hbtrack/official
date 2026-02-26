"""exercise_bank_schema_foundation - Add scope, visibility_mode, soft delete to exercises + create exercise_media, exercise_acl

Revision ID: 0065
Revises: 0064
Create Date: 2026-02-26 00:00:00.000000

Evidencia:
  - AR: AR_144_db_exercise_bank_-_schema_foundation.md
  - INV-TRAIN-047: exercises.scope IN ('SYSTEM', 'ORG')
  - INV-TRAIN-048: ORG exercises require organization_id; SYSTEM have NULL
  - INV-TRAIN-049: exercises soft delete (deleted_at + deleted_reason)
  - INV-TRAIN-050: exercise_favorites unique (user_id, exercise_id) - PK already satisfies
  - INV-TRAIN-051: exercises.visibility_mode IN ('org_wide', 'restricted')
  - INV-TRAIN-052: exercise_media belongs to exercise
  - INV-TRAIN-EXB-ACL-001..007: exercise_acl for restricted visibility
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '0065'
down_revision = '0064'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =========================================================================
    # 1. ALTER TABLE exercises: add scope, visibility_mode, deleted_at, deleted_reason
    # =========================================================================
    
    # 1a. Add scope column with CHECK constraint
    op.add_column('exercises', sa.Column('scope', sa.String(10), nullable=False, server_default='ORG'))
    op.create_check_constraint(
        'ck_exercises_scope',
        'exercises',
        "scope IN ('SYSTEM', 'ORG')"
    )
    
    # 1b. Add visibility_mode column with CHECK constraint
    op.add_column('exercises', sa.Column('visibility_mode', sa.String(20), nullable=False, server_default='restricted'))
    op.create_check_constraint(
        'ck_exercises_visibility_mode',
        'exercises',
        "visibility_mode IN ('org_wide', 'restricted')"
    )
    
    # 1c. Add soft delete columns
    op.add_column('exercises', sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('exercises', sa.Column('deleted_reason', sa.Text(), nullable=True))
    op.create_check_constraint(
        'ck_exercises_deleted_reason',
        'exercises',
        "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)"
    )
    
    # 1d. Drop NOT NULL from organization_id (needed for SYSTEM exercises)
    op.alter_column('exercises', 'organization_id', nullable=True)
    
    # 1e. Add scope/org_id consistency constraint
    op.create_check_constraint(
        'ck_exercises_org_scope',
        'exercises',
        "(scope = 'SYSTEM' AND organization_id IS NULL) OR (scope = 'ORG' AND organization_id IS NOT NULL)"
    )
    
    # =========================================================================
    # 2. exercise_favorites: PK (user_id, exercise_id) already satisfies INV-050
    #    No additional unique constraint needed (would be redundant)
    # =========================================================================
    # NOTA: exercise_favorites_pkey PRIMARY KEY (user_id, exercise_id) já garante unicidade
    
    # =========================================================================
    # 3. CREATE TABLE exercise_media
    # =========================================================================
    op.create_table(
        'exercise_media',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('exercise_id', UUID(), nullable=False),
        sa.Column('media_type', sa.String(20), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('order_index', sa.SmallInteger(), nullable=False, server_default='1'),
        sa.Column('created_by_user_id', UUID(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("media_type IN ('video', 'image', 'gif', 'document')", name='ck_exercise_media_type'),
        sa.UniqueConstraint('exercise_id', 'order_index', name='uq_exercise_media_exercise_order')
    )
    
    # Index for exercise_id lookup
    op.create_index('idx_exercise_media_exercise', 'exercise_media', ['exercise_id'])
    
    # =========================================================================
    # 4. CREATE TABLE exercise_acl
    # =========================================================================
    op.create_table(
        'exercise_acl',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('exercise_id', UUID(), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('granted_by_user_id', UUID(), nullable=False),
        sa.Column('granted_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['granted_by_user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.UniqueConstraint('exercise_id', 'user_id', name='uq_exercise_acl_exercise_user')
    )
    
    # Indexes for common lookups
    op.create_index('idx_exercise_acl_exercise', 'exercise_acl', ['exercise_id'])
    op.create_index('idx_exercise_acl_user', 'exercise_acl', ['user_id'])


def downgrade() -> None:
    # Drop exercise_acl
    op.drop_index('idx_exercise_acl_user', table_name='exercise_acl')
    op.drop_index('idx_exercise_acl_exercise', table_name='exercise_acl')
    op.drop_table('exercise_acl')
    
    # Drop exercise_media
    op.drop_index('idx_exercise_media_exercise', table_name='exercise_media')
    op.drop_table('exercise_media')
    
    # Revert exercises changes
    op.drop_constraint('ck_exercises_org_scope', 'exercises', type_='check')
    op.alter_column('exercises', 'organization_id', nullable=False)
    op.drop_constraint('ck_exercises_deleted_reason', 'exercises', type_='check')
    op.drop_column('exercises', 'deleted_reason')
    op.drop_column('exercises', 'deleted_at')
    op.drop_constraint('ck_exercises_visibility_mode', 'exercises', type_='check')
    op.drop_column('exercises', 'visibility_mode')
    op.drop_constraint('ck_exercises_scope', 'exercises', type_='check')
    op.drop_column('exercises', 'scope')
