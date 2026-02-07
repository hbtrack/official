"""V1.2 - Create core tables (organizations, persons, users, roles, permissions)

Revision ID: 001_v1_2_core
Revises:
Create Date: 2025-12-28 04:45:00

REGRAS_SISTEMAS_V1.2.md: R1, R2, R3, R4, R24, R33, RDB1, RDB2, RDB3, RDB4, RDB6, RDB14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_v1_2_core'
down_revision = '000_v1_2_prepare_database'
branch_labels = None
depends_on = None


def upgrade():
    # ========================================
    # 1. ORGANIZATIONS
    # ========================================
    # R33: Múltiplos clubes na V1
    # RDB15: organizations sem owner_user_id, sem status
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_organizations'),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_organizations_deleted_reason'
        ),
        comment='Clubes/organizações esportivas. V1.2: suporta múltiplos clubes desde V1.'
    )
    op.create_index('ix_organizations_name', 'organizations', ['name'])

    # ========================================
    # 2. PERSONS
    # ========================================
    # R1: Pessoa representa indivíduo real, independente de função
    op.create_table(
        'persons',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('full_name', sa.Text(), nullable=False),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_persons'),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_persons_deleted_reason'
        ),
        comment='Pessoas físicas do sistema. R1: independente de função esportiva.'
    )

    # ========================================
    # 3. ROLES
    # ========================================
    # R4: Papéis organizacionais válidos: Dirigente, Coordenador, Treinador, Atleta
    # RDB2.1: Lookup pode usar INTEGER PK
    op.create_table(
        'roles',
        sa.Column('id', sa.SmallInteger(), nullable=False),
        sa.Column('code', sa.String(32), nullable=False),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_roles'),
        sa.UniqueConstraint('code', name='ux_roles_code'),
        sa.UniqueConstraint('name', name='ux_roles_name'),
        comment='Papéis do sistema. R4: Dirigente, Coordenador, Treinador, Atleta.'
    )

    # ========================================
    # 4. PERMISSIONS
    # ========================================
    # R24: Permissões definidas por papel
    # RDB2.1: Lookup pode usar SMALLINT PK
    op.create_table(
        'permissions',
        sa.Column('id', sa.SmallInteger(), nullable=False),
        sa.Column('code', sa.String(64), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_permissions'),
        sa.UniqueConstraint('code', name='ux_permissions_code'),
        comment='Permissões do sistema. R24: aplicadas via papel.'
    )

    # ========================================
    # 5. ROLE_PERMISSIONS
    # ========================================
    # RDB2.1: Junction table sem soft delete
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.SmallInteger(), nullable=False),
        sa.Column('permission_id', sa.SmallInteger(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name='fk_role_permissions_role_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], name='fk_role_permissions_permission_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id', name='pk_role_permissions'),
        comment='Junction table: papéis ↔ permissões.'
    )

    # ========================================
    # 6. USERS
    # ========================================
    # R2: Usuário representa acesso ao sistema
    # R3: Super Administrador único, vitalício, imutável
    # RDB6: Índice parcial único para is_superadmin=true
    # RF1.1: person_id pode não ter user (atleta sem login)
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=True),
        sa.Column('is_superadmin', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('is_locked', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('status', sa.String(20), server_default=sa.text("'ativo'"), nullable=False),
        sa.Column('expired_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], name='fk_users_person_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_users'),
        sa.CheckConstraint(
            "status IN ('ativo', 'inativo', 'arquivado')",
            name='ck_users_status'
        ),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_users_deleted_reason'
        ),
        comment='Usuários com acesso ao sistema. R2, R3: Super Admin único e vitalício (RDB6).'
    )

    # R2: Email único case-insensitive
    op.create_index('ux_users_email', 'users', [sa.text('LOWER(email)')], unique=True)

    # RDB6: Super Administrador único (índice parcial)
    op.execute("""
        CREATE UNIQUE INDEX ux_users_superadmin
        ON users (is_superadmin)
        WHERE is_superadmin = true AND deleted_at IS NULL;
    """)
    op.create_index('ix_users_person_id', 'users', ['person_id'])

    # ========================================
    # 7. AUDIT_LOGS
    # ========================================
    # R30, R31, R32: Ações críticas auditáveis
    # RDB5: Append-only, imutável
    # RDB4.1: Sem soft delete (append-only, nunca deletada)
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('entity', sa.String(64), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(64), nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('context', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('old_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('justification', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], name='fk_audit_logs_actor_id', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name='pk_audit_logs'),
        comment='Logs de auditoria. R35: absolutamente imutável (RDB5: append-only).'
    )
    op.create_index('ix_audit_logs_entity', 'audit_logs', ['entity'])
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])
    op.create_index('ix_audit_logs_actor_id', 'audit_logs', ['actor_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('users')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('persons')
    op.drop_table('organizations')
