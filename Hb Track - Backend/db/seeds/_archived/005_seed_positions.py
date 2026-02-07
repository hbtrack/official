"""
Seed 005: Posições Defensivas e Ofensivas

Insere as posições conforme nomenclatura correta do handebol brasileiro:

POSIÇÕES DEFENSIVAS:
- Defensora Base
- Defensora Avançada  
- 1ª Defensora
- 2ª Defensora
- Goleira (ID=5, especial conforme RD13)

POSIÇÕES OFENSIVAS:
- Armadora Central
- Lateral Esquerda
- Lateral Direita
- Ponta Esquerda
- Ponta Direita
- Pivô

Referências:
- REGRAS_GERENCIAMENTO_ATLETAS.md: RD13 (Goleira não tem posição ofensiva)
"""
import sys
from pathlib import Path

# Adicionar backend ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.core.db import db_context


def seed_positions():
    """Insere as posições defensivas e ofensivas."""
    
    with db_context() as session:
        # Verificar se já existem posições defensivas
        result = session.execute(text("SELECT COUNT(*) FROM defensive_positions"))
        defensive_count = result.scalar()
        
        result = session.execute(text("SELECT COUNT(*) FROM offensive_positions"))
        offensive_count = result.scalar()
        
        if defensive_count > 0 and offensive_count > 0:
            print(f"[SKIP] Posições já existem (def={defensive_count}, off={offensive_count}). Pulando seed.")
            return

        # Inserir posições defensivas se não existirem
        if defensive_count == 0:
            print("[OK] Inserindo posições defensivas...")
            session.execute(text("""
                INSERT INTO defensive_positions (id, code, name, abbreviation, is_active) VALUES
                (1, 'base_defender', 'Defensora Base', 'DB', true),
                (2, 'advanced_defender', 'Defensora Avançada', 'DA', true),
                (3, 'first_defender', '1ª Defensora', '1D', true),
                (4, 'second_defender', '2ª Defensora', '2D', true),
                (5, 'goalkeeper', 'Goleira', 'GOL', true)
            """))
            print(f"[OK] {5} posições defensivas inseridas!")
        else:
            print(f"[SKIP] Posições defensivas já existem ({defensive_count} registros).")

        # Inserir posições ofensivas se não existirem
        if offensive_count == 0:
            print("[OK] Inserindo posições ofensivas...")
            session.execute(text("""
                INSERT INTO offensive_positions (id, code, name, abbreviation, is_active) VALUES
                (1, 'center_back', 'Armadora Central', 'AC', true),
                (2, 'left_back', 'Lateral Esquerda', 'LE', true),
                (3, 'right_back', 'Lateral Direita', 'LD', true),
                (4, 'left_wing', 'Ponta Esquerda', 'PE', true),
                (5, 'right_wing', 'Ponta Direita', 'PD', true),
                (6, 'pivot', 'Pivô', 'PI', true)
            """))
            print(f"[OK] {6} posições ofensivas inseridas!")
        else:
            print(f"[SKIP] Posições ofensivas já existem ({offensive_count} registros).")
        
        print("[OK] Seed de posições concluído!")


if __name__ == "__main__":
    seed_positions()