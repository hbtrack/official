"""fase1_ficha_performance_indexes

Revision ID: 41e6ff9bc859
Revises: 314e57818480
Create Date: 2026-01-01 16:31:36.239532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0028'
down_revision: Union[str, Sequence[str], None] = '0027'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    FASE 1 - Índices de Performance para Ficha Única
    
    Cria índices otimizados para:
    - Busca de pessoas por nome (fuzzy search)
    - Validação de duplicatas (contatos e documentos)
    - Filtros de escopo organizacional
    - Performance de consultas de atletas
    """
    
    # ========= PERSONS =========
    # Busca por nome (trigram GIN para busca fuzzy)
    # Nota: Requer extensão pg_trgm
    op.execute("""
        CREATE EXTENSION IF NOT EXISTS pg_trgm
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_persons_full_name_trgm 
        ON persons USING gin(full_name gin_trgm_ops)
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_persons_deleted_at 
        ON persons(deleted_at)
    """)
    
    # ========= PERSON_CONTACTS =========
    # Busca por contato + tipo (validação de duplicatas)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_person_contacts_value 
        ON person_contacts(contact_value) 
        WHERE deleted_at IS NULL
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_person_contacts_type_value 
        ON person_contacts(contact_type, contact_value) 
        WHERE deleted_at IS NULL
    """)
    
    # Email normalizado (lowercase)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_person_contacts_email_lower 
        ON person_contacts(LOWER(contact_value)) 
        WHERE contact_type = 'email' AND deleted_at IS NULL
    """)
    
    # ========= PERSON_DOCUMENTS =========
    # Busca por documento + tipo (validação de duplicatas)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_person_documents_number 
        ON person_documents(document_number) 
        WHERE deleted_at IS NULL
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_person_documents_type_number 
        ON person_documents(document_type, document_number) 
        WHERE deleted_at IS NULL
    """)
    
    # ========= ORG_MEMBERSHIPS =========
    # Busca por person + org + end_at (validação de escopo)
    # Nota: Índice ix_org_memberships_person_org_active já existe, não criar duplicata
    
    # ========= ATHLETES =========
    # NOTA: athletes não possui organization_id diretamente
    # O vínculo organizacional é feito via team_registrations -> teams -> organizations
    
    # Busca por estado
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_athletes_state 
        ON athletes(state) 
        WHERE deleted_at IS NULL
    """)
    
    # Busca por person_id (join com persons)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_athletes_person_id 
        ON athletes(person_id) 
        WHERE deleted_at IS NULL
    """)
    
    # ========= TEAM_REGISTRATIONS =========
    # Busca por atleta + ativo
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_team_registrations_athlete_active 
        ON team_registrations(athlete_id, end_at) 
        WHERE deleted_at IS NULL
    """)
    
    # Busca por equipe + ativo
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_team_registrations_team_active 
        ON team_registrations(team_id, end_at) 
        WHERE deleted_at IS NULL
    """)
    
    # Busca por período (start_at, end_at)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_team_registrations_period 
        ON team_registrations(start_at, end_at) 
        WHERE deleted_at IS NULL
    """)


def downgrade() -> None:
    """Downgrade schema - Remove índices de performance."""
    
    # TEAM_REGISTRATIONS
    op.execute("DROP INDEX IF EXISTS ix_team_registrations_period")
    op.execute("DROP INDEX IF EXISTS ix_team_registrations_team_active")
    op.execute("DROP INDEX IF EXISTS ix_team_registrations_athlete_active")
    
    # ATHLETES
    op.execute("DROP INDEX IF EXISTS ix_athletes_person_id")
    op.execute("DROP INDEX IF EXISTS ix_athletes_state")
    
    # PERSON_DOCUMENTS
    op.execute("DROP INDEX IF EXISTS ix_person_documents_type_number")
    op.execute("DROP INDEX IF EXISTS ix_person_documents_number")
    
    # PERSON_CONTACTS
    op.execute("DROP INDEX IF EXISTS ix_person_contacts_email_lower")
    op.execute("DROP INDEX IF EXISTS ix_person_contacts_type_value")
    op.execute("DROP INDEX IF EXISTS ix_person_contacts_value")
    
    # PERSONS
    op.execute("DROP INDEX IF EXISTS ix_persons_deleted_at")
    op.execute("DROP INDEX IF EXISTS ix_persons_full_name_trgm")

