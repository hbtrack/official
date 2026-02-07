"""canonical athletes - migrate data and remove duplicated fields

Revision ID: 012_canonical
Revises: 011_v1_2_fix_medical_cases
Create Date: 2025-12-31 00:00:00.000000

DECISÕES CANÔNICAS:
- Q1: Remover duplicações de athletes e usar exclusivamente person_documents, 
      person_contacts, person_addresses
- Q5: Remover campo state_address (usar person_addresses.state)

Esta migration:
1. MIGRA dados existentes para tabelas normalizadas (person_documents, person_contacts, person_addresses)
2. REMOVE campos duplicados da tabela athletes

CAMPOS REMOVIDOS:
- athlete_rg, athlete_cpf → person_documents
- athlete_phone, athlete_email → person_contacts
- zip_code, street, neighborhood, city, state_address, address_number, 
  address_complement → person_addresses
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '012_canonical'
down_revision = '011_v1_2_fix_medical_cases'
branch_labels = None
depends_on = None


def upgrade():
    """
    Migra dados e remove campos duplicados da tabela athletes.
    
    PASSO 1: Migrar dados existentes para tabelas normalizadas
    PASSO 2: Remover colunas duplicadas
    """
    
    conn = op.get_bind()
    
    # =========================================================================
    # PASSO 1: MIGRAR DADOS EXISTENTES
    # =========================================================================
    
    # 1.1 Migrar CPF para person_documents
    conn.execute(text("""
        INSERT INTO person_documents (person_id, document_type, document_number, created_at, updated_at)
        SELECT 
            a.person_id,
            'cpf',
            a.athlete_cpf,
            NOW(),
            NOW()
        FROM athletes a
        WHERE a.athlete_cpf IS NOT NULL 
          AND a.athlete_cpf != ''
          AND a.deleted_at IS NULL
          AND NOT EXISTS (
              SELECT 1 FROM person_documents pd 
              WHERE pd.person_id = a.person_id 
                AND pd.document_type = 'cpf'
                AND pd.deleted_at IS NULL
          )
    """))
    
    # 1.2 Migrar RG para person_documents
    conn.execute(text("""
        INSERT INTO person_documents (person_id, document_type, document_number, created_at, updated_at)
        SELECT 
            a.person_id,
            'rg',
            a.athlete_rg,
            NOW(),
            NOW()
        FROM athletes a
        WHERE a.athlete_rg IS NOT NULL 
          AND a.athlete_rg != ''
          AND a.deleted_at IS NULL
          AND NOT EXISTS (
              SELECT 1 FROM person_documents pd 
              WHERE pd.person_id = a.person_id 
                AND pd.document_type = 'rg'
                AND pd.deleted_at IS NULL
          )
    """))
    
    # 1.3 Migrar telefone para person_contacts
    conn.execute(text("""
        INSERT INTO person_contacts (person_id, contact_type, contact_value, is_primary, created_at, updated_at)
        SELECT 
            a.person_id,
            'telefone',
            a.athlete_phone,
            true,
            NOW(),
            NOW()
        FROM athletes a
        WHERE a.athlete_phone IS NOT NULL 
          AND a.athlete_phone != ''
          AND a.deleted_at IS NULL
          AND NOT EXISTS (
              SELECT 1 FROM person_contacts pc 
              WHERE pc.person_id = a.person_id 
                AND pc.contact_type = 'telefone'
                AND pc.deleted_at IS NULL
          )
    """))
    
    # 1.4 Migrar email para person_contacts
    conn.execute(text("""
        INSERT INTO person_contacts (person_id, contact_type, contact_value, is_primary, created_at, updated_at)
        SELECT 
            a.person_id,
            'email',
            a.athlete_email,
            true,
            NOW(),
            NOW()
        FROM athletes a
        WHERE a.athlete_email IS NOT NULL 
          AND a.athlete_email != ''
          AND a.deleted_at IS NULL
          AND NOT EXISTS (
              SELECT 1 FROM person_contacts pc 
              WHERE pc.person_id = a.person_id 
                AND pc.contact_type = 'email'
                AND pc.deleted_at IS NULL
          )
    """))
    
    # 1.5 Migrar endereço para person_addresses
    conn.execute(text("""
        INSERT INTO person_addresses (
            person_id, address_type, postal_code, street, number, complement,
            neighborhood, city, state, country, is_primary, created_at, updated_at
        )
        SELECT 
            a.person_id,
            'residencial_1',
            a.zip_code,
            a.street,
            a.address_number,
            a.address_complement,
            a.neighborhood,
            a.city,
            a.state_address,
            'Brasil',
            true,
            NOW(),
            NOW()
        FROM athletes a
        WHERE a.deleted_at IS NULL
          AND (a.zip_code IS NOT NULL OR a.street IS NOT NULL OR a.city IS NOT NULL)
          AND NOT EXISTS (
              SELECT 1 FROM person_addresses pa 
              WHERE pa.person_id = a.person_id 
                AND pa.deleted_at IS NULL
          )
    """))
    
    # =========================================================================
    # PASSO 2: REMOVER COLUNAS DUPLICADAS
    # =========================================================================
    
    # Remover índice único de athlete_rg se existir
    conn.execute(text("""
        DROP INDEX IF EXISTS ux_athletes_rg
    """))
    
    # Remover campos de documentos (movidos para person_documents)
    op.drop_column('athletes', 'athlete_rg')
    op.drop_column('athletes', 'athlete_cpf')
    
    # Remover campos de contatos (movidos para person_contacts)
    op.drop_column('athletes', 'athlete_phone')
    op.drop_column('athletes', 'athlete_email')
    
    # Remover campos de endereço (movidos para person_addresses)
    op.drop_column('athletes', 'zip_code')
    op.drop_column('athletes', 'street')
    op.drop_column('athletes', 'neighborhood')
    op.drop_column('athletes', 'city')
    op.drop_column('athletes', 'state_address')
    op.drop_column('athletes', 'address_number')
    op.drop_column('athletes', 'address_complement')


def downgrade():
    """
    Recria campos removidos (apenas estrutura, dados não podem ser restaurados).
    
    ATENÇÃO: Downgrade apenas recria colunas vazias. Dados não são restaurados.
    """
    
    # Recriar campos de endereço
    op.add_column('athletes', sa.Column('address_complement', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('athletes', sa.Column('address_number', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.add_column('athletes', sa.Column('state_address', sa.VARCHAR(length=2), autoincrement=False, nullable=True))
    op.add_column('athletes', sa.Column('city', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('athletes', sa.Column('neighborhood', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('athletes', sa.Column('street', sa.VARCHAR(length=200), autoincrement=False, nullable=True))
    op.add_column('athletes', sa.Column('zip_code', sa.VARCHAR(length=9), autoincrement=False, nullable=True))
    
    # Recriar campos de contatos
    op.add_column('athletes', sa.Column('athlete_email', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('athletes', sa.Column('athlete_phone', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    
    # Recriar campos de documentos
    op.add_column('athletes', sa.Column('athlete_cpf', sa.VARCHAR(length=14), autoincrement=False, nullable=True))
    op.add_column('athletes', sa.Column('athlete_rg', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
