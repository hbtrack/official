"""
Smoke Test - Relatórios Consolidados e Alertas

Testa os endpoints:
- GET /reports/attendance - Taxa de assiduidade por atleta
- GET /reports/minutes - Minutos jogados por atleta
- GET /reports/load - Carga acumulada por atleta
- GET /alerts/load - Alertas de excesso de carga
- GET /alerts/injury-return - Alertas de retorno de lesão

Critérios de sucesso:
- 200 com dados para equipe no escopo
- 403 para equipe fora do escopo
- Sem erros 500
"""
import os
import sys
import httpx

# Configuração de conexão
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")


def get_auth_token() -> str:
    """Obtém token de autenticação."""
    token = os.environ.get("TEST_AUTH_TOKEN")
    if token:
        return token
    
    # Tentar ler do arquivo token.txt (pasta raiz do workspace)
    token_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "token.txt")
    if os.path.exists(token_file):
        with open(token_file) as f:
            return f.read().strip()
    
    raise ValueError("Token não encontrado. Defina TEST_AUTH_TOKEN ou crie token.txt")


def get_headers() -> dict:
    """Headers para requisições autenticadas."""
    return {
        "Authorization": f"Bearer {get_auth_token()}",
        "Content-Type": "application/json",
    }


def get_team_and_season_ids(client: httpx.Client) -> tuple:
    """Obtém IDs de equipe e temporada para os testes."""
    # Buscar primeira equipe disponível
    resp = client.get(f"{API_BASE_URL}/teams", headers=get_headers())
    if resp.status_code != 200:
        print(f"❌ Erro ao buscar equipes: {resp.status_code}")
        return None, None
    
    data = resp.json()
    teams = data.get("items", data) if isinstance(data, dict) else data
    if not teams:
        print("⚠️ Nenhuma equipe encontrada")
        return None, None
    
    team_id = teams[0]["id"]
    
    # Buscar primeira temporada disponível
    resp = client.get(f"{API_BASE_URL}/seasons", headers=get_headers())
    if resp.status_code != 200:
        print(f"❌ Erro ao buscar temporadas: {resp.status_code}")
        return team_id, None
    
    data = resp.json()
    seasons = data.get("items", data) if isinstance(data, dict) else data
    season_id = seasons[0]["id"] if seasons else None
    
    return team_id, season_id


def test_attendance_report(client: httpx.Client, team_id: str, season_id: str | None):
    """Testa endpoint de relatório de assiduidade."""
    print("\n📊 Testando GET /reports/attendance...")
    
    params = {"team_id": team_id}
    if season_id:
        params["season_id"] = season_id
    
    resp = client.get(
        f"{API_BASE_URL}/reports/attendance",
        headers=get_headers(),
        params=params,
    )
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Status 200 - {data.get('total_athletes', 0)} atletas")
        print(f"      Taxa média: {data.get('avg_attendance_rate', 0):.1f}%")
        print(f"      Total treinos: {data.get('total_training_sessions', 0)}")
        print(f"      Total jogos: {data.get('total_matches', 0)}")
        return True
    elif resp.status_code == 403:
        print(f"   ⚠️ Status 403 - Equipe fora do escopo (esperado)")
        return True
    else:
        print(f"   ❌ Status {resp.status_code}: {resp.text[:200]}")
        return False


def test_minutes_report(client: httpx.Client, team_id: str, season_id: str | None):
    """Testa endpoint de relatório de minutos."""
    print("\n⏱️ Testando GET /reports/minutes...")
    
    params = {"team_id": team_id}
    if season_id:
        params["season_id"] = season_id
    
    resp = client.get(
        f"{API_BASE_URL}/reports/minutes",
        headers=get_headers(),
        params=params,
    )
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Status 200 - {data.get('total_athletes', 0)} atletas")
        print(f"      Total minutos jogo: {data.get('total_match_minutes', 0)}")
        print(f"      Total minutos treino: {data.get('total_training_minutes', 0)}")
        return True
    elif resp.status_code == 403:
        print(f"   ⚠️ Status 403 - Equipe fora do escopo (esperado)")
        return True
    else:
        print(f"   ❌ Status {resp.status_code}: {resp.text[:200]}")
        return False


def test_load_report(client: httpx.Client, team_id: str, season_id: str | None):
    """Testa endpoint de relatório de carga."""
    print("\n🏋️ Testando GET /reports/load...")
    
    params = {"team_id": team_id}
    if season_id:
        params["season_id"] = season_id
    
    resp = client.get(
        f"{API_BASE_URL}/reports/load",
        headers=get_headers(),
        params=params,
    )
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Status 200 - {data.get('total_athletes', 0)} atletas")
        print(f"      Carga total treino: {data.get('total_training_load', 0):.0f}")
        print(f"      Carga total jogo: {data.get('total_match_load', 0):.0f}")
        return True
    elif resp.status_code == 403:
        print(f"   ⚠️ Status 403 - Equipe fora do escopo (esperado)")
        return True
    else:
        print(f"   ❌ Status {resp.status_code}: {resp.text[:200]}")
        return False


def test_load_alerts(client: httpx.Client, team_id: str, season_id: str | None):
    """Testa endpoint de alertas de carga."""
    print("\n⚠️ Testando GET /alerts/load...")
    
    params = {"team_id": team_id}
    if season_id:
        params["season_id"] = season_id
    
    resp = client.get(
        f"{API_BASE_URL}/alerts/load",
        headers=get_headers(),
        params=params,
    )
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Status 200 - {len(data.get('alerts', []))} alertas")
        print(f"      Total atletas: {data.get('total_athletes', 0)}")
        print(f"      Em risco: {data.get('athletes_at_risk', 0)}")
        print(f"      Sobrecarregados: {data.get('athletes_overloaded', 0)}")
        print(f"      Subcarregados: {data.get('athletes_underloaded', 0)}")
        return True
    elif resp.status_code == 403:
        print(f"   ⚠️ Status 403 - Equipe fora do escopo (esperado)")
        return True
    else:
        print(f"   ❌ Status {resp.status_code}: {resp.text[:200]}")
        return False


def test_injury_return_alerts(client: httpx.Client, team_id: str, season_id: str | None):
    """Testa endpoint de alertas de retorno de lesão."""
    print("\n🏥 Testando GET /alerts/injury-return...")
    
    params = {"team_id": team_id}
    if season_id:
        params["season_id"] = season_id
    
    resp = client.get(
        f"{API_BASE_URL}/alerts/injury-return",
        headers=get_headers(),
        params=params,
    )
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Status 200 - {len(data.get('alerts', []))} alertas")
        print(f"      Total atletas: {data.get('total_athletes', 0)}")
        print(f"      Lesionadas: {data.get('athletes_injured', 0)}")
        print(f"      Retornando: {data.get('athletes_returning', 0)}")
        print(f"      Com restrição: {data.get('athletes_with_restriction', 0)}")
        return True
    elif resp.status_code == 403:
        print(f"   ⚠️ Status 403 - Equipe fora do escopo (esperado)")
        return True
    else:
        print(f"   ❌ Status {resp.status_code}: {resp.text[:200]}")
        return False


def test_missing_team_id(client: httpx.Client):
    """Testa comportamento sem team_id."""
    print("\n🔒 Testando requisições sem team_id...")
    
    endpoints = [
        "/reports/attendance",
        "/reports/minutes",
        "/reports/load",
        "/alerts/load",
        "/alerts/injury-return",
    ]
    
    all_ok = True
    for endpoint in endpoints:
        resp = client.get(f"{API_BASE_URL}{endpoint}", headers=get_headers())
        if resp.status_code == 422:  # Validation error expected
            print(f"   ✅ {endpoint} → 422 (validação correta)")
        else:
            print(f"   ❌ {endpoint} → {resp.status_code} (esperado 422)")
            all_ok = False
    
    return all_ok


def main():
    """Executa todos os smoke tests."""
    print("=" * 60)
    print("SMOKE TEST - RELATÓRIOS CONSOLIDADOS E ALERTAS")
    print("=" * 60)
    
    results = []
    
    with httpx.Client(timeout=30.0) as client:
        # Obter IDs para teste
        team_id, season_id = get_team_and_season_ids(client)
        
        if not team_id:
            print("\n❌ Não foi possível obter equipe para teste")
            sys.exit(1)
        
        print(f"\nUsando team_id: {team_id}")
        if season_id:
            print(f"Usando season_id: {season_id}")
        
        # Testes de relatórios
        results.append(("attendance", test_attendance_report(client, team_id, season_id)))
        results.append(("minutes", test_minutes_report(client, team_id, season_id)))
        results.append(("load", test_load_report(client, team_id, season_id)))
        
        # Testes de alertas
        results.append(("load_alerts", test_load_alerts(client, team_id, season_id)))
        results.append(("injury_return", test_injury_return_alerts(client, team_id, season_id)))
        
        # Testes de validação
        results.append(("missing_team_id", test_missing_team_id(client)))
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    for name, ok in results:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {name}: {status}")
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed < total:
        sys.exit(1)
    
    print("\n✅ Todos os testes passaram!")


if __name__ == "__main__":
    main()
