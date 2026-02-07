"""create_session_templates_table_with_trigger

Revision ID: 0050
Revises: 0049
Create Date: 2026-01-18 01:42:07.650496

Step Training 30.1: Templates Customizados
- Tabela session_templates: coaches criam seus próprios templates de treino
- Trigger automático: seed de 4 templates padrão para novas orgs
- Limite 50 templates por org
- Hard delete (libera espaço no limite)
- Sistema de favoritos
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '0050'
down_revision = '0049'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create session_templates table and auto-seed trigger."""
    
    # Check if table already exists (idempotent migration)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'session_templates' not in inspector.get_table_names():
        # Create session_templates table
        op.create_table(
            'session_templates',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
            sa.Column('org_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('description', sa.Text, nullable=True),
            sa.Column('icon', sa.String(20), nullable=False, server_default='target'),
            
            # 7 focus percentages (0-100.00)
            sa.Column('focus_attack_positional_pct', sa.Numeric(5, 2), nullable=False, server_default='0'),
            sa.Column('focus_defense_positional_pct', sa.Numeric(5, 2), nullable=False, server_default='0'),
            sa.Column('focus_transition_offense_pct', sa.Numeric(5, 2), nullable=False, server_default='0'),
            sa.Column('focus_transition_defense_pct', sa.Numeric(5, 2), nullable=False, server_default='0'),
            sa.Column('focus_attack_technical_pct', sa.Numeric(5, 2), nullable=False, server_default='0'),
            sa.Column('focus_defense_technical_pct', sa.Numeric(5, 2), nullable=False, server_default='0'),
            sa.Column('focus_physical_pct', sa.Numeric(5, 2), nullable=False, server_default='0'),
            
            # Features
            sa.Column('is_favorite', sa.Boolean, nullable=False, server_default='false'),
            sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
            
            # Metadata
            sa.Column('created_by_membership_id', UUID(as_uuid=True), sa.ForeignKey('org_memberships.id', ondelete='SET NULL'), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
            
            # Constraints
            sa.CheckConstraint(
                "icon IN ('target', 'activity', 'bar-chart', 'shield', 'zap', 'flame')",
                name='chk_session_templates_icon'
            ),
            sa.CheckConstraint(
                """
                (focus_attack_positional_pct + focus_defense_positional_pct + 
                 focus_transition_offense_pct + focus_transition_defense_pct +
                 focus_attack_technical_pct + focus_defense_technical_pct + 
                 focus_physical_pct) <= 120
                """,
                name='chk_session_templates_total_focus'
            ),
            sa.UniqueConstraint('org_id', 'name', name='uq_session_templates_org_name')
        )
        
        # Create indexes
        op.create_index('idx_session_templates_org_favorite', 'session_templates', ['org_id', 'is_favorite', 'name'])
        op.create_index('idx_session_templates_active', 'session_templates', ['is_active'])
    
    # Create trigger function for auto-seed
    op.execute("""
        CREATE OR REPLACE FUNCTION trg_insert_default_session_templates()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Insert 4 default templates for new organization
            INSERT INTO session_templates (
                id, org_id, name, description, icon,
                focus_attack_positional_pct, focus_defense_positional_pct,
                focus_transition_offense_pct, focus_transition_defense_pct,
                focus_attack_technical_pct, focus_defense_technical_pct,
                focus_physical_pct, is_favorite
            ) VALUES
            (
                gen_random_uuid(), NEW.id,
                'Tático Ofensivo',
                'Foco em ataque posicional e transição ofensiva',
                'target',
                45.00, 10.00, 25.00, 5.00, 10.00, 0.00, 5.00, true
            ),
            (
                gen_random_uuid(), NEW.id,
                'Físico Intensivo',
                'Treino de alta intensidade física',
                'flame',
                10.00, 10.00, 5.00, 5.00, 0.00, 10.00, 60.00, true
            ),
            (
                gen_random_uuid(), NEW.id,
                'Balanceado',
                'Distribuição equilibrada entre todos os focos',
                'activity',
                15.00, 15.00, 15.00, 15.00, 10.00, 10.00, 20.00, false
            ),
            (
                gen_random_uuid(), NEW.id,
                'Defensivo',
                'Prioridade em defesa posicional e transição defensiva',
                'shield',
                5.00, 50.00, 0.00, 30.00, 5.00, 5.00, 5.00, false
            );
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Attach trigger to organizations table
    op.execute("""
        CREATE TRIGGER trg_after_insert_organization
        AFTER INSERT ON organizations
        FOR EACH ROW
        EXECUTE FUNCTION trg_insert_default_session_templates();
    """)


def downgrade() -> None:
    """Drop session_templates table and trigger."""
    
    # Drop trigger first
    op.execute("DROP TRIGGER IF EXISTS trg_after_insert_organization ON organizations")
    op.execute("DROP FUNCTION IF EXISTS trg_insert_default_session_templates()")
    
    # Drop indexes
    op.drop_index('idx_session_templates_active')
    op.drop_index('idx_session_templates_org_favorite')
    
    # Drop table
    op.drop_table('session_templates')
