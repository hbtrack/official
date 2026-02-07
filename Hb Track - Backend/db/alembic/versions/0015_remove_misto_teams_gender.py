"""014 - Remove 'misto' from teams.gender

Conforme RAG (REGRAS_GERENCIAMENTO_ATLETAS.md):
- No handebol, **não existe categoria mista**
- Apenas gêneros masculino e feminino são permitidos para atletas e equipes
- teams.gender: **'masculino'** ou **'feminino'** (OBRIGATÓRIO)

Revision ID: 014_remove_misto
Revises: 013_fix_defensive_positions
Create Date: 2025-12-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0015'
down_revision: Union[str, Sequence[str], None] = '0014'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Remove 'misto' da constraint ck_teams_gender.
    Conforme RAG: handebol não possui categoria mista.
    """
    # 1. Remover a constraint atual
    op.drop_constraint('ck_teams_gender', 'teams', type_='check')
    
    # 2. Criar nova constraint sem 'misto'
    op.create_check_constraint(
        'ck_teams_gender',
        'teams',
        "gender IN ('masculino', 'feminino')"
    )


def downgrade() -> None:
    """Reverter para incluir 'misto' novamente."""
    # 1. Remover a constraint nova
    op.drop_constraint('ck_teams_gender', 'teams', type_='check')
    
    # 2. Recriar constraint original com 'misto'
    op.create_check_constraint(
        'ck_teams_gender',
        'teams',
        "gender IN ('masculino', 'feminino', 'misto')"
    )
