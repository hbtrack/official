"""Create team_memberships table for staff-team relationships

Revision ID: 0025_create_team_memberships
Revises: 0024_update_training_status
Create Date: 2026-01-06

Cria tabela team_memberships para vincular staff (coordenadores/treinadores) 
a equipes específicas, análoga a team_registrations (que vincula atletas).

Motivação:
- Atualmente OrgMembership vincula staff à organização inteira
- Não há como vincular coordenadores/treinadores a equipes específicas
- Membros convidados aparecem como "pendentes" em todas as equipes

Nova estrutura:
- team_memberships: vínculo person ↔ team (para staff)
- team_registrations: vínculo athlete ↔ team (para atletas)

Status possíveis:
- 'pendente': Aguardando aceitação do convite
- 'ativo': Membro ativo da equipe
- 'inativo': Desativado/removido
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0025'
down_revision: Union[str, Sequence[str], None] = '0024'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Cria tabela team_memberships para vínculos staff-equipe.
    """
    
    # Criar tabela team_memberships
    op.create_table(
        'team_memberships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Pessoa (staff)'),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Equipe'),
        sa.Column('org_membership_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Referência ao cargo organizacional'),
        sa.Column('start_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Data de início do vínculo'),
        sa.Column('end_at', sa.TIMESTAMP(timezone=True), nullable=True, comment='Data de término; NULL = ativo'),
        sa.Column('status', sa.Text(), nullable=False, server_default='pendente', comment='Status: pendente, ativo, inativo'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['org_membership_id'], ['org_memberships.id'], ondelete='SET NULL'),
        sa.CheckConstraint("status IN ('pendente', 'ativo', 'inativo')", name='check_team_memberships_status'),
        comment='Vínculo de staff (coordenadores/treinadores) com equipes específicas'
    )
    
    # Índices para performance
    op.create_index('idx_team_memberships_person_id', 'team_memberships', ['person_id'])
    op.create_index('idx_team_memberships_team_id', 'team_memberships', ['team_id'])
    op.create_index('idx_team_memberships_org_membership_id', 'team_memberships', ['org_membership_id'])
    op.create_index('idx_team_memberships_status', 'team_memberships', ['status'])
    
    # Índice para buscar vínculos ativos de uma equipe
    op.create_index(
        'idx_team_memberships_team_active',
        'team_memberships',
        ['team_id', 'status'],
        postgresql_where=sa.text('deleted_at IS NULL AND end_at IS NULL')
    )
    
    # Índice único para evitar duplicatas (pessoa+equipe ativo/pendente)
    op.create_index(
        'idx_team_memberships_person_team_active',
        'team_memberships',
        ['person_id', 'team_id'],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL AND end_at IS NULL AND status IN ('pendente', 'ativo')")
    )


def downgrade() -> None:
    """
    Remove tabela team_memberships.
    """
    op.drop_index('idx_team_memberships_person_team_active', 'team_memberships')
    op.drop_index('idx_team_memberships_team_active', 'team_memberships')
    op.drop_index('idx_team_memberships_status', 'team_memberships')
    op.drop_index('idx_team_memberships_org_membership_id', 'team_memberships')
    op.drop_index('idx_team_memberships_team_id', 'team_memberships')
    op.drop_index('idx_team_memberships_person_id', 'team_memberships')
    op.drop_table('team_memberships')
