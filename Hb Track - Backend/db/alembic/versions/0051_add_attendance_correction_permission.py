"""add_attendance_correction_permission

Revision ID: 0051
Revises: 0050
Create Date: 2026-01-21 22:19:15.163030

Step 11 - Plano de Refatoração Training:
Adiciona permissão can_correct_attendance para roles:
- superadmin: TRUE
- dirigente: TRUE
- coordenador: TRUE
- treinador: FALSE
- atleta: FALSE
- membro: FALSE

Permite correção administrativa de presenças após fechamento da sessão (R37).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0051'
down_revision: Union[str, Sequence[str], None] = '0050'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona permissão can_correct_attendance."""
    
    # 1. Inserir nova permissão (idempotente)
    op.execute("""
        INSERT INTO permissions (code, description)
        VALUES ('can_correct_attendance', 'Permite correção de presenças após fechamento da sessão (R37: ação administrativa auditada)')
        ON CONFLICT (code) DO NOTHING;
    """)
    
    # 2. Associar permissão às roles (apenas superadmin, dirigente, coordenador)
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r
        CROSS JOIN permissions p
        WHERE p.code = 'can_correct_attendance'
        AND r.code IN ('superadmin', 'dirigente', 'coordenador')
        AND NOT EXISTS (
            SELECT 1 
            FROM role_permissions rp 
            WHERE rp.role_id = r.id 
            AND rp.permission_id = p.id
        );
    """)


def downgrade() -> None:
    """Remove permissão can_correct_attendance."""
    
    # 1. Remover associações
    op.execute("""
        DELETE FROM role_permissions
        WHERE permission_id IN (
            SELECT id FROM permissions WHERE code = 'can_correct_attendance'
        );
    """)
    
    # 2. Remover permissão
    op.execute("""
        DELETE FROM permissions WHERE code = 'can_correct_attendance';
    """)
