"""V1.2 - Create athletes and org_memberships

Revision ID: 004_v1_2_athletes_memberships
Revises: 003_v1_2_teams_seasons
Create Date: 2025-12-28 05:10:00

REGRAS_SISTEMAS_V1.2.md: R6, R7, R9, R12, R13, RDB9, RDB17
V1.2: org_memberships (staff apenas), athletes com estado + flags
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '004_v1_2_athletes_memberships'
down_revision = '003_v1_2_teams_seasons'
branch_labels = None
depends_on = None


def upgrade():
    # ORG_MEMBERSHIPS (staff apenas: Dirigente, Coordenador, Treinador)
    # V1.2: substitui membership sazonal
    # RDB9: vínculo com organização, não com temporada
    op.create_table(
        'org_memberships',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('end_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], name='fk_org_memberships_person_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name='fk_org_memberships_role_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_org_memberships_organization_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_org_memberships'),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_org_memberships_deleted_reason'
        ),
        comment='Vínculos organizacionais (staff). V1.2: sem season_id; apenas org+person+role.'
    )

    # Índice parcial: 1 vínculo ativo por pessoa+organização+papel
    op.create_index(
        'ux_org_memberships_active',
        'org_memberships',
        ['person_id', 'organization_id', 'role_id'],
        unique=True,
        postgresql_where=sa.text('end_at IS NULL AND deleted_at IS NULL')
    )
    op.create_index('ix_org_memberships_organization_id', 'org_memberships', ['organization_id'])
    op.create_index('ix_org_memberships_person_id', 'org_memberships', ['person_id'])
    op.create_index('ix_org_memberships_role_id', 'org_memberships', ['role_id'])

    # ATHLETES (com estado base + flags)
    # RDB17: estado base (ativa/dispensada/arquivada) + flags de restrição
    # R12, R13: injured, medical_restriction, suspended_until, load_restricted
    op.create_table(
        'athletes',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Estado base
        sa.Column('state', sa.String(20), server_default=sa.text("'ativa'"), nullable=False),

        # Flags de restrição (camadas adicionais)
        sa.Column('injured', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('medical_restriction', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('suspended_until', sa.Date(), nullable=True),
        sa.Column('load_restricted', sa.Boolean(), server_default=sa.text('false'), nullable=False),

        # Dados cadastrais
        sa.Column('athlete_name', sa.String(100), nullable=False),
        sa.Column('birth_date', sa.Date(), nullable=False),
        sa.Column('athlete_rg', sa.String(20), nullable=True),
        sa.Column('athlete_cpf', sa.String(11), nullable=True),
        sa.Column('athlete_phone', sa.String(20), nullable=True),
        sa.Column('athlete_email', sa.String(100), nullable=True),
        sa.Column('athlete_nickname', sa.String(50), nullable=True),
        sa.Column('shirt_number', sa.Integer(), nullable=True),
        sa.Column('main_defensive_position_id', sa.Integer(), nullable=True),
        sa.Column('secondary_defensive_position_id', sa.Integer(), nullable=True),
        sa.Column('main_offensive_position_id', sa.Integer(), nullable=True),
        sa.Column('secondary_offensive_position_id', sa.Integer(), nullable=True),
        sa.Column('schooling_id', sa.Integer(), nullable=True),
        sa.Column('guardian_name', sa.String(100), nullable=True),
        sa.Column('guardian_phone', sa.String(20), nullable=True),
        sa.Column('zip_code', sa.String(10), nullable=True),
        sa.Column('street', sa.String(200), nullable=True),
        sa.Column('neighborhood', sa.String(100), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state_address', sa.String(2), nullable=True),
        sa.Column('address_number', sa.String(20), nullable=True),
        sa.Column('address_complement', sa.String(100), nullable=True),
        sa.Column('athlete_photo_path', sa.String(500), nullable=True),
        sa.Column('registered_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('athlete_age_at_registration', sa.Integer(), nullable=True),

        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),

        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], name='fk_athletes_person_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['main_defensive_position_id'], ['defensive_positions.id'], name='fk_athletes_main_defensive_position_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['secondary_defensive_position_id'], ['defensive_positions.id'], name='fk_athletes_secondary_defensive_position_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['main_offensive_position_id'], ['offensive_positions.id'], name='fk_athletes_main_offensive_position_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['secondary_offensive_position_id'], ['offensive_positions.id'], name='fk_athletes_secondary_offensive_position_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['schooling_id'], ['schooling_levels.id'], name='fk_athletes_schooling_id', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name='pk_athletes'),
        sa.CheckConstraint(
            "state IN ('ativa', 'dispensada', 'arquivada')",
            name='ck_athletes_state'
        ),
        sa.CheckConstraint(
            "shirt_number IS NULL OR (shirt_number BETWEEN 1 AND 99)",
            name='ck_athletes_shirt_number'
        ),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_athletes_deleted_reason'
        ),
        comment='Atletas. V1.2: estado base + flags (injured, medical_restriction, suspended_until, load_restricted).'
    )

    # Índices únicos parciais
    op.create_index(
        'ux_athletes_rg',
        'athletes',
        ['athlete_rg'],
        unique=True,
        postgresql_where=sa.text('athlete_rg IS NOT NULL AND deleted_at IS NULL')
    )
    op.create_index(
        'ux_athletes_cpf',
        'athletes',
        ['athlete_cpf'],
        unique=True,
        postgresql_where=sa.text('athlete_cpf IS NOT NULL AND deleted_at IS NULL')
    )
    op.create_index(
        'ux_athletes_email',
        'athletes',
        [sa.text('LOWER(athlete_email)')],
        unique=True,
        postgresql_where=sa.text('athlete_email IS NOT NULL AND deleted_at IS NULL')
    )
    op.create_index('ix_athletes_person_id', 'athletes', ['person_id'])
    op.create_index('ix_athletes_state', 'athletes', ['state'])
    op.create_index('ix_athletes_birth_date', 'athletes', ['birth_date'])

    # TEAM_REGISTRATIONS (vínculos de atletas com equipes)
    # RDB10: permite múltiplos vínculos ativos simultâneos em equipes diferentes
    op.create_table(
        'team_registrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('athlete_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('end_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['athlete_id'], ['athletes.id'], name='fk_team_registrations_athlete_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name='fk_team_registrations_team_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_team_registrations'),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_team_registrations_deleted_reason'
        ),
        comment='Vínculos de atletas com equipes. V1.2: múltiplos vínculos ativos simultâneos permitidos.'
    )

    # Índice parcial: 1 vínculo ativo por atleta+equipe
    op.create_index(
        'ux_team_registrations_active',
        'team_registrations',
        ['athlete_id', 'team_id'],
        unique=True,
        postgresql_where=sa.text('end_at IS NULL AND deleted_at IS NULL')
    )
    op.create_index('ix_team_registrations_athlete_id', 'team_registrations', ['athlete_id'])
    op.create_index('ix_team_registrations_team_id', 'team_registrations', ['team_id'])


def downgrade():
    op.drop_table('team_registrations')
    op.drop_table('athletes')
    op.drop_table('org_memberships')
