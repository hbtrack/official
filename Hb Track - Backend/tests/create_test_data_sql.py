"""
Script para criar dados de teste via SQL direto
Cria: team, season (no DB, não via API)
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import date, datetime, timedelta
from uuid import uuid4

from sqlalchemy import text
from app.core.db import SessionLocal


def create_test_data_sql():
    """Cria dados de teste diretamente no banco"""
    db = SessionLocal()
    
    try:
        print("🔧 Criando dados de teste via SQL...")
        
        # 1. Buscar org_id existente
        org = db.execute(text("SELECT id FROM organizations WHERE deleted_at IS NULL LIMIT 1")).fetchone()
        if not org:
            print("❌ Nenhuma organização encontrada")
            return
        org_id = str(org[0])
        print(f"   ✅ org_id: {org_id}")
        
        # 2. Buscar categoria existente
        cat = db.execute(text("SELECT id FROM categories LIMIT 1")).fetchone()
        if not cat:
            print("❌ Nenhuma categoria encontrada")
            return
        category_id = cat[0]
        print(f"   ✅ category_id: {category_id}")
        
        # 3. Criar equipe
        team_id = str(uuid4())
        team_name = f"Equipe Smoke Test {datetime.now().strftime('%H%M%S')}"
        db.execute(text("""
            INSERT INTO teams (id, organization_id, name, category_id, gender, is_our_team)
            VALUES (:id, :org_id, :name, :cat_id, 'feminino', true)
        """), {"id": team_id, "org_id": org_id, "name": team_name, "cat_id": category_id})
        print(f"   ✅ team_id: {team_id}")
        
        # 4. Criar temporada
        season_id = str(uuid4())
        today = date.today()
        end_date = today + timedelta(days=180)
        db.execute(text("""
            INSERT INTO seasons (id, team_id, name, year, start_date, end_date)
            VALUES (:id, :team_id, :name, :year, :start, :end)
        """), {
            "id": season_id, 
            "team_id": team_id, 
            "name": f"Season Smoke {datetime.now().strftime('%H%M%S')}",
            "year": today.year,
            "start": today,
            "end": end_date
        })
        print(f"   ✅ season_id: {season_id}")
        
        # 4.5. Buscar um user_id existente
        user = db.execute(text("SELECT id FROM users WHERE deleted_at IS NULL LIMIT 1")).fetchone()
        user_id = str(user[0]) if user else None
        print(f"   ✅ user_id: {user_id}")
        
        # 5. Criar treino
        training_id = str(uuid4())
        session_at = datetime.now()
        db.execute(text("""
            INSERT INTO training_sessions 
            (id, organization_id, team_id, season_id, session_at, session_type, main_objective, created_by_user_id)
            VALUES (:id, :org_id, :team_id, :season_id, :session_at, 'quadra', 'Teste Smoke', :user_id)
        """), {
            "id": training_id,
            "org_id": org_id,
            "team_id": team_id,
            "season_id": season_id,
            "session_at": session_at,
            "user_id": user_id
        })
        print(f"   ✅ training_id: {training_id}")
        
        # 6. Criar partida (precisa de home_team_id e away_team_id diferentes)
        # Primeiro criar um time adversário
        away_team_id = str(uuid4())
        db.execute(text("""
            INSERT INTO teams (id, organization_id, name, category_id, gender, is_our_team)
            VALUES (:id, :org_id, 'Time Adversário Smoke', :cat_id, 'feminino', false)
        """), {"id": away_team_id, "org_id": org_id, "cat_id": category_id})
        print(f"   ✅ away_team_id: {away_team_id}")
        
        match_id = str(uuid4())
        match_date = date.today()
        db.execute(text("""
            INSERT INTO matches 
            (id, season_id, match_date, home_team_id, away_team_id, our_team_id, phase, status, created_by_user_id)
            VALUES (:id, :season_id, :match_date, :home_team_id, :away_team_id, :our_team_id, 'friendly', 'scheduled', :user_id)
        """), {
            "id": match_id,
            "season_id": season_id,
            "match_date": match_date,
            "home_team_id": team_id,
            "away_team_id": away_team_id,
            "our_team_id": team_id,
            "user_id": user_id
        })
        print(f"   ✅ match_id: {match_id}")
        
        db.commit()
        
        # Resumo
        print("\n" + "="*50)
        print("  DADOS CRIADOS COM SUCESSO")
        print("="*50)
        print(f"  org_id:      {org_id}")
        print(f"  team_id:     {team_id}")
        print(f"  season_id:   {season_id}")
        print(f"  training_id: {training_id}")
        print(f"  match_id:    {match_id}")
        print("="*50)
        
        return {
            "org_id": org_id,
            "team_id": team_id,
            "season_id": season_id,
            "training_id": training_id,
            "match_id": match_id
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data_sql()
