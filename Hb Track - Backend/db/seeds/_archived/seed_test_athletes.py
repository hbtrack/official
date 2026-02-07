"""
Seed: Atletas de teste

Cria atletas de teste para desenvolvimento.
Usa a organização e super admin criados anteriormente.
"""
import sys
from pathlib import Path
import uuid
from datetime import datetime, date

# Adicionar backend ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.core.db import db_context


def seed_test_athletes():
    """Cria atletas de teste para desenvolvimento."""
    with db_context() as session:
        # Verificar se já existem atletas de teste
        result = session.execute(
            text("SELECT COUNT(*) FROM athletes WHERE state = 'ativa'")
        )
        count = result.scalar()

        if count > 0:
            print(f"[SKIP] Já existem {count} atletas. Pulando seed.")
            return

        # Buscar organização de teste
        result = session.execute(
            text("SELECT id FROM organizations WHERE name = 'Clube de Teste HB Track' LIMIT 1")
        )
        org_row = result.fetchone()
        
        if not org_row:
            print("[ERRO] Organização de teste não encontrada. Execute primeiro o seed da organização.")
            return
            
        org_id = org_row[0]

        # Buscar categoria Juvenil
        result = session.execute(
            text("SELECT id FROM categories WHERE name = 'Juvenil' LIMIT 1")
        )
        category_row = result.fetchone()
        
        if not category_row:
            print("[ERRO] Categoria Juvenil não encontrada.")
            return
            
        category_id = category_row[0]

        # Buscar nível de escolaridade
        result = session.execute(
            text("SELECT id FROM schooling_levels WHERE code = 'high_school_incomplete' LIMIT 1")
        )
        schooling_row = result.fetchone()
        
        if not schooling_row:
            print("[ERRO] Nível de escolaridade não encontrado.")
            return
            
        schooling_id = schooling_row[0]

        # Buscar posições defensivas e ofensivas
        result = session.execute(
            text("SELECT id FROM defensive_positions WHERE code = 'base_defender' LIMIT 1")
        )
        def_pos_row = result.fetchone()
        
        result = session.execute(
            text("SELECT id FROM offensive_positions WHERE code = 'center_back' LIMIT 1")
        )
        off_pos_row = result.fetchone()

        def_position_id = def_pos_row[0] if def_pos_row else None
        off_position_id = off_pos_row[0] if off_pos_row else None

        # Criar atletas de teste
        athletes_data = [
            {
                "first_name": "Maria",
                "last_name": "Silva Santos",
                "full_name": "Maria Silva Santos",
                "birth_date": date(2007, 5, 15),
                "athlete_name": "Maria",
                "nickname": "Mary",
                "guardian_name": "Ana Silva",
                "guardian_phone": "(11) 91111-1111"
            },
            {
                "first_name": "Ana",
                "last_name": "Paula Costa",
                "full_name": "Ana Paula Costa",
                "birth_date": date(2008, 8, 22),
                "athlete_name": "Ana Paula",
                "nickname": "Ana",
                "guardian_name": "João Costa",
                "guardian_phone": "(11) 92222-2222"
            },
            {
                "first_name": "Carla",
                "last_name": "Oliveira",
                "full_name": "Carla Oliveira",
                "birth_date": date(2007, 12, 3),
                "athlete_name": "Carla",
                "nickname": "Carlinha",
                "guardian_name": "Rita Oliveira",
                "guardian_phone": "(11) 93333-3333"
            }
        ]

        for i, athlete_data in enumerate(athletes_data, 1):
            # Criar pessoa
            person_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO persons (id, first_name, last_name, full_name, birth_date, gender, created_at, updated_at)
                VALUES (
                    :person_id, :first_name, :last_name, :full_name, :birth_date, 'feminino', NOW(), NOW()
                )
            """), {
                "person_id": person_id,
                "first_name": athlete_data["first_name"],
                "last_name": athlete_data["last_name"],
                "full_name": athlete_data["full_name"],
                "birth_date": athlete_data["birth_date"]
            })

            # Criar atleta
            athlete_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO athletes (
                    id, person_id, organization_id, athlete_name, birth_date, athlete_nickname,
                    main_defensive_position_id, main_offensive_position_id, schooling_id,
                    guardian_name, guardian_phone, state, shirt_number, registered_at,
                    created_at, updated_at
                )
                VALUES (
                    :athlete_id, :person_id, :org_id, :athlete_name, :birth_date, :nickname,
                    :def_position_id, :off_position_id, :schooling_id,
                    :guardian_name, :guardian_phone, 'ativa', :shirt_number, NOW(),
                    NOW(), NOW()
                )
            """), {
                "athlete_id": athlete_id,
                "person_id": person_id,
                "org_id": org_id,
                "athlete_name": athlete_data["athlete_name"],
                "birth_date": athlete_data["birth_date"],
                "nickname": athlete_data["nickname"],
                "def_position_id": def_position_id,
                "off_position_id": off_position_id,
                "schooling_id": schooling_id,
                "guardian_name": athlete_data["guardian_name"],
                "guardian_phone": athlete_data["guardian_phone"],
                "shirt_number": i
            })

            print(f"[OK] Atleta criada: {athlete_data['full_name']} (ID: {athlete_id})")


if __name__ == "__main__":
    seed_test_athletes()