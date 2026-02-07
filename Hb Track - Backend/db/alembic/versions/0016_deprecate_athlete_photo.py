"""
015 - Deprecate athlete_photo_path

CANÔNICO (31/12/2025): Fotos de atletas devem usar person_media, não athletes.athlete_photo_path.

Esta migration:
1. Adiciona comentário de deprecação ao campo athlete_photo_path
2. NÃO remove o campo (mantém compatibilidade com código legado)
3. Campo será removido em migration futura após migração completa para person_media

Revision ID: 015_deprecate_athlete_photo_path
Revises: 014_remove_misto_from_teams_gender
Create Date: 2025-01-01
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '0016'
down_revision = '0015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Marca athlete_photo_path como DEPRECATED.
    
    O campo será mantido para compatibilidade, mas novos uploads
    devem usar a tabela person_media.
    """
    # Adicionar comentário de deprecação ao campo
    op.execute("""
        COMMENT ON COLUMN athletes.athlete_photo_path IS 
        'DEPRECATED (31/12/2025): Use person_media para fotos de atletas. '
        'Este campo será removido em versão futura. '
        'Novo fluxo: POST /api/v1/persons/{person_id}/media com media_type=profile_photo';
    """)
    
    # Criar índice na tabela person_media para facilitar buscas por tipo
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_person_media_person_type 
        ON person_media (person_id, media_type) 
        WHERE deleted_at IS NULL;
    """)


def downgrade() -> None:
    """
    Remove comentário de deprecação e índice.
    """
    op.execute("""
        COMMENT ON COLUMN athletes.athlete_photo_path IS NULL;
    """)
    
    op.execute("""
        DROP INDEX IF EXISTS ix_person_media_person_type;
    """)
