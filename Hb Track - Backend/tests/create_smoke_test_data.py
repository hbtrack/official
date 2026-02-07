"""
Script para criar dados de teste para smoke tests
Cria: season, team, athlete, match, training
"""
import requests
from datetime import datetime, timedelta
from uuid import uuid4

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


def get_token():
    """Obtém token de autenticação"""
    resp = requests.post(
        f"{API_V1}/auth/login",
        data={"username": "admin@hbtracking.com", "password": "Admin@123"},
        timeout=10
    )
    if resp.status_code == 200:
        return resp.json().get("access_token")
    raise Exception(f"Login failed: {resp.status_code} - {resp.text}")


def get_headers(token):
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }


def create_test_data():
    print("🔧 Criando dados de teste...")
    
    # 1. Obter token
    print("\n1️⃣ Obtendo token...")
    token = get_token()
    headers = get_headers(token)
    print("   ✅ Token obtido")
    
    # 2. Obter org_id do contexto
    print("\n2️⃣ Obtendo contexto...")
    resp = requests.get(f"{API_V1}/auth/context", headers=headers, timeout=10)
    if resp.status_code != 200:
        raise Exception(f"Falha ao obter contexto: {resp.text}")
    ctx = resp.json()
    org_id = ctx.get("organization_id")
    print(f"   ✅ org_id: {org_id}")
    
    # 3. Obter categoria existente
    print("\n3️⃣ Obtendo categorias...")
    resp = requests.get(f"{API_V1}/categories", headers=headers, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        category_id = items[0]["id"] if items else None
        print(f"   ✅ category_id: {category_id}")
    else:
        category_id = None
        print(f"   ⚠️ Sem categorias: {resp.status_code}")
    
    # 4. Criar equipe primeiro (não depende de temporada no schema real)
    print("\n4️⃣ Criando equipe...")
    team_data = {
        "name": f"Equipe Teste {datetime.now().strftime('%H%M%S')}",
        "category_id": category_id,
        "gender": "feminino"
    }
    resp = requests.post(f"{API_V1}/teams", json=team_data, headers=headers, timeout=10)
    if resp.status_code in [200, 201]:
        team = resp.json()
        team_id = team.get("id")
        print(f"   ✅ team_id: {team_id}")
    else:
        print(f"   ❌ Falha ao criar equipe: {resp.status_code} - {resp.text}")
        team_id = None
    
    # 5. Criar temporada (agora que temos team_id)
    print("\n5️⃣ Criando temporada...")
    if team_id:
        today = datetime.now().date()
        season_data = {
            "team_id": team_id,
            "year": today.year,
            "name": f"Temporada Teste {datetime.now().strftime('%H%M%S')}",
            "start_date": str(today),
            "end_date": str(today + timedelta(days=180))
        }
        resp = requests.post(f"{API_V1}/seasons", json=season_data, headers=headers, timeout=10)
        if resp.status_code in [200, 201]:
            season = resp.json()
            season_id = season.get("id")
            print(f"   ✅ season_id: {season_id}")
        else:
            print(f"   ❌ Falha ao criar temporada: {resp.status_code} - {resp.text}")
            season_id = None
    else:
        season_id = None
        print("   ⏭️ Pulando (sem team_id)")
    
    # 6. Criar treino
    print("\n6️⃣ Criando treino...")
    if team_id:
        training_data = {
            "team_id": team_id,
            "session_date": str(today),
            "start_time": "14:00:00",
            "end_time": "16:00:00",
            "session_type": "technical",
            "description": "Treino de teste smoke"
        }
        resp = requests.post(f"{API_V1}/teams/{team_id}/trainings", json=training_data, headers=headers, timeout=10)
        if resp.status_code in [200, 201]:
            training = resp.json()
            training_id = training.get("id")
            print(f"   ✅ training_id: {training_id}")
        else:
            print(f"   ❌ Falha ao criar treino: {resp.status_code} - {resp.text}")
            training_id = None
    else:
        training_id = None
        print("   ⏭️ Pulando (sem team_id)")
    
    # 7. Criar partida
    print("\n7️⃣ Criando partida...")
    if team_id:
        match_data = {
            "team_id": team_id,
            "opponent_name": "Time Adversário Teste",
            "match_date": str(today),
            "match_time": "18:00:00",
            "location": "Ginásio de Testes",
            "is_home": True,
            "status": "scheduled"
        }
        resp = requests.post(f"{API_V1}/teams/{team_id}/matches", json=match_data, headers=headers, timeout=10)
        if resp.status_code in [200, 201]:
            match = resp.json()
            match_id = match.get("id")
            print(f"   ✅ match_id: {match_id}")
        else:
            print(f"   ❌ Falha ao criar partida: {resp.status_code} - {resp.text}")
            match_id = None
    else:
        match_id = None
        print("   ⏭️ Pulando (sem team_id)")
    
    # Resumo
    print("\n" + "="*50)
    print("  RESUMO DOS DADOS CRIADOS")
    print("="*50)
    print(f"  org_id:      {org_id}")
    print(f"  season_id:   {season_id or 'FALHOU'}")
    print(f"  team_id:     {team_id or 'FALHOU'}")
    print(f"  training_id: {training_id or 'FALHOU'}")
    print(f"  match_id:    {match_id or 'FALHOU'}")
    print("="*50)
    
    return {
        "org_id": org_id,
        "season_id": season_id,
        "team_id": team_id,
        "training_id": training_id,
        "match_id": match_id
    }


if __name__ == "__main__":
    create_test_data()
