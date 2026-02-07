"""FASE 1.6 - Índices de Performance para Ficha Única

Revision ID: 018_ficha_unica_performance_indexes
Revises: 017_ficha_unica_audit_fields
Create Date: 2026-01-01

Referência: FICHA.MD - Seção 1.6
REGRAS.md: RDB8 (Índices obrigatórios), RDB9 (FKs sempre indexadas)

Cria índices otimizados para consultas da Ficha Única:
- Busca trigram em full_name para autocomplete
- Busca de contatos por valor (email, telefone)
- Busca de documentos por número (CPF, RG)
- Memberships ativos por usuário/organização
- Team registrations ativos por atleta
"""
from alembic import op
import sqlalchemy as sa


revision = '0019'
down_revision = '0018'
branch_labels = None
depends_on = None


def upgrade():
    # =========================================================
    # HABILITAR EXTENSÃO pg_trgm (se não existir)
    # =========================================================
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    
    # =========================================================
    # ÍNDICE TRIGRAM PARA BUSCA DE PESSOAS
    # =========================================================
    # Permite busca fuzzy em full_name para autocomplete
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_persons_full_name_trgm
        ON persons USING gin (full_name gin_trgm_ops)
        WHERE deleted_at IS NULL
    """)
    
    # Índice trigram em first_name + last_name
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_persons_first_name_trgm
        ON persons USING gin (first_name gin_trgm_ops)
        WHERE deleted_at IS NULL
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_persons_last_name_trgm
        ON persons USING gin (last_name gin_trgm_ops)
        WHERE deleted_at IS NULL
    """)
    
    # =========================================================
    # ÍNDICES PARA BUSCA DE CONTATOS
    # =========================================================
    # Busca de email/telefone para validação de duplicatas
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_person_contacts_value_active
        ON person_contacts (contact_value)
        WHERE deleted_at IS NULL
    """)
    
    # Índice composto para busca por tipo + valor (ex: email específico)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_person_contacts_type_value_active
        ON person_contacts (contact_type, contact_value)
        WHERE deleted_at IS NULL
    """)
    
    # =========================================================
    # ÍNDICES PARA BUSCA DE DOCUMENTOS
    # =========================================================
    # Busca de CPF para validação de duplicatas
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_person_documents_cpf_active
        ON person_documents (document_number)
        WHERE document_type = 'cpf' AND deleted_at IS NULL
    """)
    
    # Índice parcial para RG
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_person_documents_rg_active
        ON person_documents (document_number)
        WHERE document_type = 'rg' AND deleted_at IS NULL
    """)
    
    # =========================================================
    # ÍNDICES PARA MEMBERSHIPS (org_memberships)
    # =========================================================
    # Nota: org_memberships usa person_id, não user_id
    
    # Busca de memberships ativos por pessoa
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_org_memberships_person_active
        ON org_memberships (person_id)
        WHERE deleted_at IS NULL
    """)
    
    # Busca de memberships ativos por organização
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_org_memberships_org_active
        ON org_memberships (organization_id)
        WHERE deleted_at IS NULL
    """)
    
    # Índice composto para validação de escopo
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_org_memberships_person_org_active
        ON org_memberships (person_id, organization_id)
        WHERE deleted_at IS NULL AND end_at IS NULL
    """)
    
    # =========================================================
    # ÍNDICES PARA TEAM_REGISTRATIONS
    # =========================================================
    # Busca de vínculos ativos por atleta
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_team_registrations_athlete_active
        ON team_registrations (athlete_id)
        WHERE end_at IS NULL AND deleted_at IS NULL
    """)
    
    # Busca de vínculos ativos por equipe
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_team_registrations_team_active
        ON team_registrations (team_id)
        WHERE end_at IS NULL AND deleted_at IS NULL
    """)
    
    # =========================================================
    # ÍNDICES PARA ORGANIZAÇÕES
    # =========================================================
    # Busca trigram em nome da organização para autocomplete
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_organizations_name_trgm
        ON organizations USING gin (name gin_trgm_ops)
        WHERE deleted_at IS NULL
    """)
    
    # =========================================================
    # ÍNDICES PARA EQUIPES
    # =========================================================
    # Busca trigram em nome da equipe
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_teams_name_trgm
        ON teams USING gin (name gin_trgm_ops)
        WHERE deleted_at IS NULL
    """)
    
    # Busca por organização (para autocomplete de equipes)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_teams_organization_active
        ON teams (organization_id)
        WHERE deleted_at IS NULL
    """)
    
    # =========================================================
    # ÍNDICES PARA ATLETAS
    # =========================================================
    # Busca por person_id
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_athletes_person_id_active
        ON athletes (person_id)
        WHERE deleted_at IS NULL
    """)
    
    # NOTA: athletes não possui organization_id diretamente
    # O vínculo organizacional é feito via team_registrations -> teams -> organizations
    
    # Busca por estado (ativa, dispensada, arquivada)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_athletes_state_active
        ON athletes (state)
        WHERE deleted_at IS NULL
    """)
    
    # =========================================================
    # COMENTÁRIOS
    # =========================================================
    op.execute("""
        COMMENT ON INDEX ix_persons_full_name_trgm IS 
        'Índice trigram para busca fuzzy de pessoas (autocomplete). FICHA.MD 1.6'
    """)


def downgrade():
    # Remover índices na ordem inversa
    indexes = [
        'ix_athletes_state_active',
        'ix_athletes_person_id_active',
        'ix_teams_organization_active',
        'ix_teams_name_trgm',
        'ix_organizations_name_trgm',
        'ix_team_registrations_team_active',
        'ix_team_registrations_athlete_active',
        'ix_org_memberships_user_org_active',
        'ix_org_memberships_org_active',
        'ix_org_memberships_user_active',
        'ix_person_documents_rg_active',
        'ix_person_documents_cpf_active',
        'ix_person_contacts_type_value_active',
        'ix_person_contacts_value_active',
        'ix_persons_last_name_trgm',
        'ix_persons_first_name_trgm',
        'ix_persons_full_name_trgm',
    ]
    
    for idx in indexes:
        op.execute(f"DROP INDEX IF EXISTS {idx}")


    # Remover os índices renomeados
    op.execute("DROP INDEX IF EXISTS ix_org_memberships_person_active")
    op.execute("DROP INDEX IF EXISTS ix_org_memberships_person_org_active")
