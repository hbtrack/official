"""V1.2 - Fix medical_cases table to comply with REGRAS.md

Revision ID: 011_v1_2_fix_medical_cases
Revises: 010_v1_2_persons_normalized
Create Date: 2025-12-30 20:00:00

REGRAS.md compliance fixes:
- RDB4: Add deleted_reason column with constraint
- RDB18.1: Add updated_at trigger
- RDB18.4: Add soft delete block trigger
- Add proper CHECK constraints
"""
from alembic import op
import sqlalchemy as sa

revision = '0012'
down_revision = '0011'
branch_labels = None
depends_on = None


def upgrade():
    # ========== medical_cases table já foi criada na migration 0005 ==========
    # Esta migration apenas adiciona triggers e ajustes específicos
    
    # ========== 1. Add updated_at trigger (RDB18.1) ==========
    op.execute("""
        CREATE TRIGGER trg_medical_cases_updated_at
        BEFORE UPDATE ON medical_cases
        FOR EACH ROW
        EXECUTE FUNCTION trg_set_updated_at();
    """)
    
    # ========== 3. Add soft delete block trigger (RDB18.4) ==========
    op.execute("""
        CREATE TRIGGER trg_medical_cases_block_delete
        BEFORE DELETE ON medical_cases
        FOR EACH ROW
        EXECUTE FUNCTION trg_block_physical_delete();
    """)
    
    # ========== 4. Add comment ==========
    op.execute("""
        COMMENT ON TABLE medical_cases IS 
        'Casos médicos de atletas. V1.2: RDB4 compliant (soft delete + deleted_reason).';
    """)
    
    # ========== 5. Add foreign key to organizations (organization context) ==========
    # Check if organization_id column exists
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'medical_cases' 
                AND column_name = 'organization_id'
            ) THEN
                ALTER TABLE medical_cases 
                ADD COLUMN organization_id UUID;
                
                -- Update existing records to get organization from athlete's team
                UPDATE medical_cases mc
                SET organization_id = (
                    SELECT t.organization_id 
                    FROM team_registrations tr
                    JOIN teams t ON t.id = tr.team_id
                    WHERE tr.athlete_id = mc.athlete_id
                    AND tr.deleted_at IS NULL
                    ORDER BY tr.start_at DESC
                    LIMIT 1
                );
                
                -- Add foreign key
                ALTER TABLE medical_cases
                ADD CONSTRAINT fk_medical_cases_organization
                FOREIGN KEY (organization_id) REFERENCES organizations(id);
                
                -- Add index
                CREATE INDEX idx_medical_cases_organization_id 
                ON medical_cases(organization_id);
            END IF;
        END $$;
    """)
    
    # ========== 6. Add created_by_user_id for audit trail ==========
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'medical_cases' 
                AND column_name = 'created_by_user_id'
            ) THEN
                ALTER TABLE medical_cases 
                ADD COLUMN created_by_user_id UUID REFERENCES users(id);
            END IF;
        END $$;
    """)


def downgrade():
    # Remove triggers
    op.execute("DROP TRIGGER IF EXISTS trg_medical_cases_updated_at ON medical_cases;")
    op.execute("DROP TRIGGER IF EXISTS trg_medical_cases_block_delete ON medical_cases;")
    
    # Remove constraint
    op.execute("ALTER TABLE medical_cases DROP CONSTRAINT IF EXISTS ck_medical_cases_deleted_reason;")
    
    # Remove columns
    op.execute("ALTER TABLE medical_cases DROP COLUMN IF EXISTS deleted_reason;")
    op.execute("ALTER TABLE medical_cases DROP COLUMN IF EXISTS organization_id;")
    op.execute("ALTER TABLE medical_cases DROP COLUMN IF EXISTS created_by_user_id;")
