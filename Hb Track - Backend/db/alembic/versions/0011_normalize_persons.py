"""
v1.2 - Normalize persons table with specialized tables

Revision ID: 010_v1_2_persons_normalized
Revises: 009_v1_2_password_reset
Create Date: 2025-12-30

Referências RAG:
- R1: Pessoa é entidade raiz, independente de função esportiva
- R10: Histórico imutável em todas as tabelas
- R32: Nada relevante é apagado

Estrutura normalizada:
- persons: identidade básica (nome, gênero, nascimento)
- person_contacts: telefone, email, whatsapp (1:N)
- person_addresses: endereços residenciais (1:N)
- person_documents: CPF, RG, CNH, passaporte (1:N)
- person_media: fotos de perfil e documentos (1:N)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0011'
down_revision = '0010'
branch_labels = None
depends_on = None


def upgrade():
    # =========================================================
    # PARTE 1: ADICIONAR CAMPOS ESTRUTURADOS EM PERSONS
    # =========================================================
    
    # Adicionar campos estruturados
    op.add_column('persons', sa.Column('first_name', sa.String(100), nullable=True))
    op.add_column('persons', sa.Column('last_name', sa.String(100), nullable=True))
    op.add_column('persons', sa.Column('gender', sa.String(20), nullable=True))
    op.add_column('persons', sa.Column('nationality', sa.String(100), server_default='brasileira', nullable=True))
    op.add_column('persons', sa.Column('notes', sa.Text(), nullable=True))
    
    # Migrar full_name para first_name/last_name
    op.execute("""
        UPDATE persons 
        SET 
            first_name = split_part(full_name, ' ', 1),
            last_name = CASE 
                WHEN position(' ' IN full_name) > 0 
                THEN substring(full_name FROM position(' ' IN full_name) + 1)
                ELSE ''
            END
        WHERE first_name IS NULL
    """)
    
    # Tornar NOT NULL após migração
    op.alter_column('persons', 'first_name', nullable=False)
    op.alter_column('persons', 'last_name', nullable=False)
    
    # Adicionar constraint de gênero
    op.execute("""
        ALTER TABLE persons ADD CONSTRAINT ck_persons_gender 
        CHECK (gender IS NULL OR gender IN ('masculino', 'feminino', 'outro', 'prefiro_nao_dizer'))
    """)
    
    # Índices para busca
    op.create_index('ix_persons_first_name', 'persons', ['first_name'])
    op.create_index('ix_persons_last_name', 'persons', ['last_name'])
    op.create_index('ix_persons_birth_date', 'persons', ['birth_date'])
    
    # Atualizar comentário
    op.execute("""
        COMMENT ON TABLE persons IS 'R1: Pessoas físicas do sistema. Identidade básica (nome, gênero, nascimento). V1.2: normalizada.'
    """)
    
    op.execute("""
        COMMENT ON COLUMN persons.first_name IS 'Primeiro nome da pessoa';
        COMMENT ON COLUMN persons.last_name IS 'Sobrenome da pessoa';
        COMMENT ON COLUMN persons.gender IS 'Gênero: masculino, feminino, outro, prefiro_nao_dizer';
        COMMENT ON COLUMN persons.nationality IS 'Nacionalidade (default: brasileira)';
        COMMENT ON COLUMN persons.notes IS 'Observações gerais sobre a pessoa';
    """)
    
    
    # =========================================================
    # PARTE 2: TABELA person_contacts
    # =========================================================
    op.create_table(
        'person_contacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('persons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('contact_type', sa.String(50), nullable=False),
        sa.Column('contact_value', sa.String(200), nullable=False),
        sa.Column('is_primary', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('deleted_reason', sa.Text()),
        sa.CheckConstraint(
            "contact_type IN ('telefone', 'email', 'whatsapp', 'outro')",
            name='ck_person_contacts_type'
        ),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_person_contacts_deleted_reason'
        )
    )
    
    op.create_index('ix_person_contacts_person_id', 'person_contacts', ['person_id'])
    op.create_index('ix_person_contacts_type_value', 'person_contacts', ['contact_type', 'contact_value'])
    op.create_index('ix_person_contacts_deleted_at', 'person_contacts', ['deleted_at'])
    
    # Partial unique index para contato primário por tipo
    op.execute("""
        CREATE UNIQUE INDEX uq_person_contacts_primary_per_type 
        ON person_contacts (person_id, contact_type) 
        WHERE is_primary = true AND deleted_at IS NULL
    """)
    
    # Triggers
    op.execute("""
        CREATE TRIGGER trg_person_contacts_updated_at 
        BEFORE UPDATE ON person_contacts 
        FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_person_contacts_block_delete 
        BEFORE DELETE ON person_contacts 
        FOR EACH ROW EXECUTE FUNCTION trg_block_physical_delete()
    """)
    
    op.execute("COMMENT ON TABLE person_contacts IS 'Contatos da pessoa (telefone, email, whatsapp). Suporta múltiplos contatos por pessoa.'")
    
    
    # =========================================================
    # PARTE 3: TABELA person_addresses
    # =========================================================
    op.create_table(
        'person_addresses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('persons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('address_type', sa.String(50), nullable=False),
        sa.Column('street', sa.String(200), nullable=False),
        sa.Column('number', sa.String(20)),
        sa.Column('complement', sa.String(100)),
        sa.Column('neighborhood', sa.String(100)),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('state', sa.String(2), nullable=False),
        sa.Column('postal_code', sa.String(10)),
        sa.Column('country', sa.String(100), server_default='Brasil', nullable=False),
        sa.Column('is_primary', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('deleted_reason', sa.Text()),
        sa.CheckConstraint(
            "address_type IN ('residencial_1', 'residencial_2', 'comercial', 'outro')",
            name='ck_person_addresses_type'
        ),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_person_addresses_deleted_reason'
        )
    )
    
    op.create_index('ix_person_addresses_person_id', 'person_addresses', ['person_id'])
    op.create_index('ix_person_addresses_city_state', 'person_addresses', ['city', 'state'])
    op.create_index('ix_person_addresses_deleted_at', 'person_addresses', ['deleted_at'])
    
    op.execute("""
        CREATE UNIQUE INDEX uq_person_addresses_primary 
        ON person_addresses (person_id) 
        WHERE is_primary = true AND deleted_at IS NULL
    """)
    
    op.execute("""
        CREATE TRIGGER trg_person_addresses_updated_at 
        BEFORE UPDATE ON person_addresses 
        FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_person_addresses_block_delete 
        BEFORE DELETE ON person_addresses 
        FOR EACH ROW EXECUTE FUNCTION trg_block_physical_delete()
    """)
    
    op.execute("COMMENT ON TABLE person_addresses IS 'Endereços da pessoa. Suporta múltiplos endereços (residencial_1, residencial_2).'")
    
    
    # =========================================================
    # PARTE 4: TABELA person_documents
    # =========================================================
    op.create_table(
        'person_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('persons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('document_number', sa.String(100), nullable=False),
        sa.Column('issuing_authority', sa.String(100)),
        sa.Column('issue_date', sa.Date()),
        sa.Column('expiry_date', sa.Date()),
        sa.Column('document_file_url', sa.Text()),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('deleted_reason', sa.Text()),
        sa.CheckConstraint(
            "document_type IN ('cpf', 'rg', 'cnh', 'passaporte', 'certidao_nascimento', 'titulo_eleitor', 'outro')",
            name='ck_person_documents_type'
        ),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_person_documents_deleted_reason'
        )
    )
    
    op.create_index('ix_person_documents_person_id', 'person_documents', ['person_id'])
    op.create_index('ix_person_documents_type', 'person_documents', ['document_type'])
    op.create_index('ix_person_documents_number', 'person_documents', ['document_number'])
    op.create_index('ix_person_documents_deleted_at', 'person_documents', ['deleted_at'])
    
    op.execute("""
        CREATE UNIQUE INDEX uq_person_documents_per_type 
        ON person_documents (person_id, document_type, document_number) 
        WHERE deleted_at IS NULL
    """)
    
    op.execute("""
        CREATE TRIGGER trg_person_documents_updated_at 
        BEFORE UPDATE ON person_documents 
        FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_person_documents_block_delete 
        BEFORE DELETE ON person_documents 
        FOR EACH ROW EXECUTE FUNCTION trg_block_physical_delete()
    """)
    
    op.execute("COMMENT ON TABLE person_documents IS 'Documentos oficiais da pessoa (CPF, RG, CNH, passaporte).'")
    
    
    # =========================================================
    # PARTE 5: TABELA person_media
    # =========================================================
    op.create_table(
        'person_media',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('persons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('media_type', sa.String(50), nullable=False),
        sa.Column('file_url', sa.Text(), nullable=False),
        sa.Column('file_name', sa.String(255)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('is_primary', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('deleted_reason', sa.Text()),
        sa.CheckConstraint(
            "media_type IN ('foto_perfil', 'foto_documento', 'video', 'outro')",
            name='ck_person_media_type'
        ),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_person_media_deleted_reason'
        )
    )
    
    op.create_index('ix_person_media_person_id', 'person_media', ['person_id'])
    op.create_index('ix_person_media_type', 'person_media', ['media_type'])
    op.create_index('ix_person_media_deleted_at', 'person_media', ['deleted_at'])
    
    op.execute("""
        CREATE UNIQUE INDEX uq_person_media_primary_per_type 
        ON person_media (person_id, media_type) 
        WHERE is_primary = true AND deleted_at IS NULL
    """)
    
    op.execute("""
        CREATE TRIGGER trg_person_media_updated_at 
        BEFORE UPDATE ON person_media 
        FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_person_media_block_delete 
        BEFORE DELETE ON person_media 
        FOR EACH ROW EXECUTE FUNCTION trg_block_physical_delete()
    """)
    
    op.execute("COMMENT ON TABLE person_media IS 'Mídias da pessoa (fotos de perfil, documentos digitalizados).'")


def downgrade():
    # Dropar tabelas especializadas
    op.execute("DROP TRIGGER IF EXISTS trg_person_media_block_delete ON person_media")
    op.execute("DROP TRIGGER IF EXISTS trg_person_media_updated_at ON person_media")
    op.drop_table('person_media')
    
    op.execute("DROP TRIGGER IF EXISTS trg_person_documents_block_delete ON person_documents")
    op.execute("DROP TRIGGER IF EXISTS trg_person_documents_updated_at ON person_documents")
    op.drop_table('person_documents')
    
    op.execute("DROP TRIGGER IF EXISTS trg_person_addresses_block_delete ON person_addresses")
    op.execute("DROP TRIGGER IF EXISTS trg_person_addresses_updated_at ON person_addresses")
    op.drop_table('person_addresses')
    
    op.execute("DROP TRIGGER IF EXISTS trg_person_contacts_block_delete ON person_contacts")
    op.execute("DROP TRIGGER IF EXISTS trg_person_contacts_updated_at ON person_contacts")
    op.drop_table('person_contacts')
    
    # Remover campos de persons
    op.drop_index('ix_persons_birth_date', 'persons')
    op.drop_index('ix_persons_last_name', 'persons')
    op.drop_index('ix_persons_first_name', 'persons')
    op.execute("ALTER TABLE persons DROP CONSTRAINT IF EXISTS ck_persons_gender")
    op.drop_column('persons', 'notes')
    op.drop_column('persons', 'nationality')
    op.drop_column('persons', 'gender')
    op.drop_column('persons', 'last_name')
    op.drop_column('persons', 'first_name')
