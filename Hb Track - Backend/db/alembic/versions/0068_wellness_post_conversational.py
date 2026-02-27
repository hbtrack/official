"""wellness_post conversational feedback

Revision ID: 0068
Revises: 0067
Create Date: 2026-02-26 00:00:00.000000

Evidencia:
  - AR: AR_157_service_wellness_post_-_campo_conversacional_inv-0.md
  - INV-070: wellness_post aceita input conversacional (texto/voz)

Changes:
  1. ALTER TABLE wellness_post: ADD conversational_feedback TEXT (nullable)
  2. ALTER TABLE wellness_post: ADD conversation_completed BOOLEAN DEFAULT FALSE

Rationale:
  - conversational_feedback: armazena input conversacional (texto/voz transcrito)
  - conversation_completed: controle de fluxo (permite submissões parciais)
  - Preserva campo `notes` existente (semântica tradicional)
  - Permite coexistência: formulário tradicional + conversacional
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0068'
down_revision = '0067'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Adiciona campos conversacionais à wellness_post"""
    # Add conversational_feedback column (nullable, sem default)
    op.add_column(
        'wellness_post',
        sa.Column('conversational_feedback', sa.Text(), nullable=True)
    )
    
    # Add conversation_completed column (NOT NULL com default FALSE)
    op.add_column(
        'wellness_post',
        sa.Column(
            'conversation_completed',
            sa.Boolean(),
            nullable=False,
            server_default='false'
        )
    )


def downgrade() -> None:
    """Remove campos conversacionais da wellness_post"""
    op.drop_column('wellness_post', 'conversation_completed')
    op.drop_column('wellness_post', 'conversational_feedback')
