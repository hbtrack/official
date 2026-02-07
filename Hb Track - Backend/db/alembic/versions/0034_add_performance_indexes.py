"""Add performance indexes for team_memberships and notifications

Revision ID: 0034_add_performance_indexes
Revises: 0033_create_notifications
Create Date: 2026-01-14

Step 24: Criar índices de performance para otimizar queries de staff, histórico e limpeza de notificações
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0034'
down_revision: Union[str, None] = '0033'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Cria índice composto para otimizar queries críticas:
    
    1. idx_team_memberships_active: Otimiza queries de staff ativo por equipe
       - Usado em: get_team_staff(), histórico de coaches, validação de permissões
       - Query otimizada: SELECT ... WHERE team_id = X AND status = 'ativo' AND end_at IS NULL
    
    Nota: idx_notifications_cleanup já foi criado na migration 0033_create_notifications_table
    """
    # Índice composto para queries de team_memberships ativos
    op.create_index(
        'idx_team_memberships_active',
        'team_memberships',
        ['team_id', 'status', 'end_at'],
        unique=False
    )


def downgrade() -> None:
    """Remove o índice de performance."""
    op.drop_index('idx_team_memberships_active', table_name='team_memberships')
