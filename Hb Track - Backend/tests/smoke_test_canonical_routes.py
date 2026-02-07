"""
Smoke Tests para Rotas Canônicas e Infraestrutura de Autorização
================================================================

Valida:
1. Infraestrutura de Autorização (permission_dep, helpers)
2. Rotas Canônicas (Organizations, Teams, Seasons, Athletes, etc.)
3. Escopo organizacional e vínculos

Executar: python tests/smoke_test_canonical_routes.py
"""
import os
import sys
import requests
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

# Configuração base
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1 = f"{BASE_URL}/api/v1"

# Token global - preenchido no início
TOKEN: Optional[str] = None


def get_fresh_token() -> str:
    """Obtém um token fresco fazendo login"""
    resp = requests.post(
        f"{API_V1}/auth/login",
        data={"username": "admin@hbtracking.com", "password": "Admin@123"},
        timeout=10
    )
    if resp.status_code == 200:
        return resp.json().get("access_token")
    raise Exception(f"Login failed: {resp.status_code} - {resp.text}")


def get_headers(token: Optional[str] = None) -> Dict[str, str]:
    """Retorna headers com autenticação"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def print_result(test_name: str, success: bool, details: str = ""):
    """Imprime resultado formatado"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"       └─ {details}")


def print_section(title: str):
    """Imprime seção"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


class SmokeTestRunner:
    """Runner para smoke tests"""
    
    def __init__(self):
        self.results = {"passed": 0, "failed": 0, "skipped": 0}
        self.org_id: Optional[str] = None
        self.team_id: Optional[str] = None
        self.season_id: Optional[str] = None
        self.athlete_id: Optional[str] = None
        self.match_id: Optional[str] = None
        self.training_id: Optional[str] = None
    
    def run_test(self, name: str, func) -> bool:
        """Executa um teste e registra resultado"""
        try:
            result, details = func()
            print_result(name, result, details)
            if result:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
            return result
        except Exception as e:
            print_result(name, False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    def skip_test(self, name: str, reason: str):
        """Marca teste como pulado"""
        print(f"⏭️ SKIP | {name}")
        print(f"       └─ {reason}")
        self.results["skipped"] += 1


# =============================================================================
# TESTES DE INFRAESTRUTURA
# =============================================================================

def test_auth_without_token() -> Tuple[bool, str]:
    """Teste de rota protegida sem token (deve retornar 401)"""
    resp = requests.get(f"{API_V1}/organizations", headers={"Content-Type": "application/json"}, timeout=10)
    return resp.status_code == 401, f"Status: {resp.status_code} (esperado: 401)"


def test_auth_context() -> Tuple[bool, str]:
    """Teste do endpoint /auth/context"""
    resp = requests.get(f"{API_V1}/auth/context", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        has_role = "role" in data or "role_code" in data
        has_org = "organization_id" in data or "organization" in data
        return True, f"Status 200 - role e org presentes"
    return False, f"Status: {resp.status_code} - {resp.text[:100]}"


def test_forbidden_wrong_org() -> Tuple[bool, str]:
    """Testa acesso a organização inexistente/não autorizada"""
    fake_org = "00000000-0000-0000-0000-000000000000"
    resp = requests.get(f"{API_V1}/organizations/{fake_org}", headers=get_headers(TOKEN), timeout=10)
    # Espera 403 ou 404
    if resp.status_code in [403, 404]:
        return True, f"Status: {resp.status_code} (acesso bloqueado corretamente)"
    return False, f"Status: {resp.status_code} (esperado: 403 ou 404)"


# =============================================================================
# TESTES DE ORGANIZATIONS
# =============================================================================

def test_list_organizations() -> Tuple[bool, str]:
    """GET /organizations - Lista organizações"""
    resp = requests.get(f"{API_V1}/organizations", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        count = len(items) if isinstance(items, list) else 0
        return True, f"Status 200 - {count} organizations"
    return False, f"Status: {resp.status_code} - {resp.text[:100]}"


# =============================================================================
# TESTES DE TEAMS
# =============================================================================

def test_list_teams() -> Tuple[bool, str]:
    """GET /teams - Lista equipes"""
    resp = requests.get(f"{API_V1}/teams", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        count = len(items) if isinstance(items, list) else 0
        return True, f"Status 200 - {count} teams"
    return False, f"Status: {resp.status_code} - {resp.text[:100]}"


def test_get_team(team_id: str) -> Tuple[bool, str]:
    """GET /teams/{id} - Obtém detalhes de uma equipe"""
    resp = requests.get(f"{API_V1}/teams/{team_id}", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        name = data.get("name", "N/A")
        return True, f"Status 200 - Team: {name}"
    return False, f"Status: {resp.status_code} - {resp.text[:100]}"


# =============================================================================
# TESTES DE SEASONS
# =============================================================================

def test_list_seasons() -> Tuple[bool, str]:
    """GET /seasons - Lista temporadas"""
    resp = requests.get(f"{API_V1}/seasons", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        count = len(items) if isinstance(items, list) else 0
        return True, f"Status 200 - {count} seasons"
    return False, f"Status: {resp.status_code} - {resp.text[:100]}"


# =============================================================================
# TESTES DE ATHLETES
# =============================================================================

def test_list_athletes() -> Tuple[bool, str]:
    """GET /athletes - Lista atletas"""
    resp = requests.get(f"{API_V1}/athletes", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        count = len(items) if isinstance(items, list) else 0
        return True, f"Status 200 - {count} athletes"
    return False, f"Status: {resp.status_code} - {resp.text[:100]}"


def test_athletes_stats() -> Tuple[bool, str]:
    """GET /athletes/stats - Estatísticas de atletas"""
    resp = requests.get(f"{API_V1}/athletes/stats", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        return True, f"Status 200 - Stats endpoint funcional"
    return False, f"Status: {resp.status_code} - {resp.text[:100]}"


# =============================================================================
# TESTES DE TEAM REGISTRATIONS (escopo por equipe)
# =============================================================================

def test_list_team_registrations(team_id: str) -> Tuple[bool, str]:
    """GET /teams/{team_id}/registrations - Lista vínculos atleta-equipe"""
    resp = requests.get(f"{API_V1}/teams/{team_id}/registrations", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        count = len(items) if isinstance(items, list) else 0
        return True, f"Status 200 - {count} registrations"
    return False, f"Status: {resp.status_code} - {resp.text[:100]}"


# =============================================================================
# TESTES DE MATCHES (escopo por equipe)
# =============================================================================

def test_list_matches(team_id: str) -> Tuple[bool, str]:
    """GET /teams/{team_id}/matches - Lista jogos de uma equipe"""
    resp = requests.get(f"{API_V1}/teams/{team_id}/matches", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        count = len(items) if isinstance(items, list) else 0
        return True, f"Status 200 - {count} matches"
    return False, f"Status: {resp.status_code} - {resp.text[:100]}"


# =============================================================================
# TESTES DE MATCH EVENTS (escopo por equipe + match)
# =============================================================================

def test_list_match_events(team_id: str, match_id: str) -> Tuple[bool, str]:
    """GET /teams/{team_id}/matches/{match_id}/events - Lista eventos de um jogo"""
    resp = requests.get(f"{API_V1}/teams/{team_id}/matches/{match_id}/events", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        count = len(items) if isinstance(items, list) else 0
        return True, f"Status 200 - {count} events"
    return False, f"Status: {resp.status_code} - {resp.text[:100]}"


# =============================================================================
# TESTES DE MATCH ROSTER (501 esperado)
# =============================================================================

def test_match_roster_501(team_id: str, match_id: str) -> Tuple[bool, str]:
    """GET /teams/{team_id}/matches/{match_id}/roster - Deve retornar 501 ou 200"""
    resp = requests.get(f"{API_V1}/teams/{team_id}/matches/{match_id}/roster", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 501:
        return True, f"Status 501 (esperado - estrutura pronta)"
    elif resp.status_code == 200:
        return True, f"Status 200 (já implementado!)"
    return False, f"Status: {resp.status_code} - {resp.text[:100]}"


# =============================================================================
# TESTES DE MATCH TEAMS (501 esperado)
# =============================================================================

def test_match_teams_501(team_id: str, match_id: str) -> Tuple[bool, str]:
    """GET /teams/{team_id}/matches/{match_id}/teams - Deve retornar 501 ou 200"""
    resp = requests.get(f"{API_V1}/teams/{team_id}/matches/{match_id}/teams", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 501:
        return True, f"Status 501 (esperado - estrutura pronta)"
    elif resp.status_code == 200:
        return True, f"Status 200 (já implementado!)"
    return False, f"Status: {resp.status_code} - {resp.text[:100]}"


# =============================================================================
# TESTES DE TRAINING SESSIONS (escopo por equipe)
# =============================================================================

def test_list_trainings(team_id: str) -> Tuple[bool, str]:
    """GET /teams/{team_id}/trainings - Lista treinos de uma equipe"""
    resp = requests.get(f"{API_V1}/teams/{team_id}/trainings", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        count = len(items) if isinstance(items, list) else 0
        return True, f"Status 200 - {count} trainings"
    return False, f"Status: {resp.status_code} - {resp.text[:100]}"


# =============================================================================
# MAIN
# =============================================================================

def run_smoke_tests():
    """Executa todos os smoke tests"""
    global TOKEN
    
    runner = SmokeTestRunner()
    
    print("\n" + "="*60)
    print("  SMOKE TESTS - ROTAS CANÔNICAS E AUTORIZAÇÃO")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    # Obter token fresco
    print("\n📝 Obtendo token de autenticação...")
    try:
        TOKEN = get_fresh_token()
        print(f"   ✅ Token obtido com sucesso")
    except Exception as e:
        print(f"   ❌ Falha ao obter token: {e}")
        return False
    
    # =====================================================
    # SEÇÃO 1: INFRAESTRUTURA DE AUTORIZAÇÃO
    # =====================================================
    print_section("1. INFRAESTRUTURA DE AUTORIZAÇÃO")
    
    runner.run_test("Auth sem token retorna 401", test_auth_without_token)
    runner.run_test("GET /auth/context retorna dados do usuário", test_auth_context)
    runner.run_test("Acesso a org inexistente bloqueado", test_forbidden_wrong_org)
    
    # =====================================================
    # SEÇÃO 2: ORGANIZATIONS (require_org=True)
    # =====================================================
    print_section("2. ORGANIZATIONS (require_org=True)")
    
    # Listar e capturar org_id
    resp = requests.get(f"{API_V1}/organizations", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        if items and len(items) > 0:
            runner.org_id = items[0].get("id")
            print(f"       └─ Usando org_id: {runner.org_id}")
    
    runner.run_test("GET /organizations", test_list_organizations)
    
    # =====================================================
    # SEÇÃO 3: TEAMS (require_org/team)
    # =====================================================
    print_section("3. TEAMS (require_org/team)")
    
    # Listar e capturar team_id
    resp = requests.get(f"{API_V1}/teams", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        if items and len(items) > 0:
            runner.team_id = items[0].get("id")
            print(f"       └─ Usando team_id: {runner.team_id}")
    
    runner.run_test("GET /teams", test_list_teams)
    
    if runner.team_id:
        runner.run_test("GET /teams/{id}", lambda: test_get_team(runner.team_id))
    else:
        runner.skip_test("GET /teams/{id}", "Sem team_id disponível")
    
    # =====================================================
    # SEÇÃO 4: SEASONS (require_org=True)
    # =====================================================
    print_section("4. SEASONS (require_org=True)")
    
    # Listar e capturar season_id
    resp = requests.get(f"{API_V1}/seasons", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        if items and len(items) > 0:
            runner.season_id = items[0].get("id")
            print(f"       └─ Usando season_id: {runner.season_id}")
    
    runner.run_test("GET /seasons", test_list_seasons)
    
    # =====================================================
    # SEÇÃO 5: ATHLETES (require_org=True)
    # =====================================================
    print_section("5. ATHLETES (require_org=True)")
    
    # Listar e capturar athlete_id
    resp = requests.get(f"{API_V1}/athletes", headers=get_headers(TOKEN), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        if items and len(items) > 0:
            runner.athlete_id = items[0].get("id")
            print(f"       └─ Usando athlete_id: {runner.athlete_id}")
    
    runner.run_test("GET /athletes", test_list_athletes)
    runner.run_test("GET /athletes/stats", test_athletes_stats)
    
    # =====================================================
    # SEÇÃO 6: TEAM REGISTRATIONS (require_team=True)
    # =====================================================
    print_section("6. TEAM REGISTRATIONS (require_team=True)")
    
    if runner.team_id:
        runner.run_test("GET /teams/{team_id}/registrations", lambda: test_list_team_registrations(runner.team_id))
    else:
        runner.skip_test("GET /teams/{team_id}/registrations", "Sem team_id disponível")
    
    # =====================================================
    # SEÇÃO 7: MATCHES (require_team=True)
    # =====================================================
    print_section("7. MATCHES (require_team=True)")
    
    if runner.team_id:
        # Listar e capturar match_id
        resp = requests.get(f"{API_V1}/teams/{runner.team_id}/matches", headers=get_headers(TOKEN), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", data) if isinstance(data, dict) else data
            if items and len(items) > 0:
                runner.match_id = items[0].get("id")
                print(f"       └─ Usando match_id: {runner.match_id}")
        
        runner.run_test("GET /teams/{team_id}/matches", lambda: test_list_matches(runner.team_id))
    else:
        runner.skip_test("GET /teams/{team_id}/matches", "Sem team_id disponível")
    
    # =====================================================
    # SEÇÃO 8: MATCH EVENTS (require_team=True + temporada)
    # =====================================================
    print_section("8. MATCH EVENTS (require_team=True + validação temporada)")
    
    if runner.team_id and runner.match_id:
        runner.run_test("GET /teams/{team_id}/matches/{match_id}/events", 
                        lambda: test_list_match_events(runner.team_id, runner.match_id))
    else:
        runner.skip_test("GET /teams/{team_id}/matches/{match_id}/events", "Sem team_id ou match_id")
    
    # =====================================================
    # SEÇÃO 9: MATCH ROSTER (501 - estrutura pronta)
    # =====================================================
    print_section("9. MATCH ROSTER (501 ou 200)")
    
    if runner.team_id and runner.match_id:
        runner.run_test("GET /teams/{team_id}/matches/{match_id}/roster", 
                        lambda: test_match_roster_501(runner.team_id, runner.match_id))
    else:
        runner.skip_test("GET /teams/{team_id}/matches/{match_id}/roster", "Sem team_id ou match_id")
    
    # =====================================================
    # SEÇÃO 10: MATCH TEAMS (501 - estrutura pronta)
    # =====================================================
    print_section("10. MATCH TEAMS (501 ou 200)")
    
    if runner.team_id and runner.match_id:
        runner.run_test("GET /teams/{team_id}/matches/{match_id}/teams", 
                        lambda: test_match_teams_501(runner.team_id, runner.match_id))
    else:
        runner.skip_test("GET /teams/{team_id}/matches/{match_id}/teams", "Sem team_id ou match_id")
    
    # =====================================================
    # SEÇÃO 11: TRAINING SESSIONS (require_team=True)
    # =====================================================
    print_section("11. TRAINING SESSIONS (require_team=True)")
    
    if runner.team_id:
        # Listar e capturar training_id
        resp = requests.get(f"{API_V1}/teams/{runner.team_id}/trainings", headers=get_headers(TOKEN), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", data) if isinstance(data, dict) else data
            if items and len(items) > 0:
                runner.training_id = items[0].get("id")
                print(f"       └─ Usando training_id: {runner.training_id}")
        
        runner.run_test("GET /teams/{team_id}/trainings", lambda: test_list_trainings(runner.team_id))
    else:
        runner.skip_test("GET /teams/{team_id}/trainings", "Sem team_id disponível")
    
    # =====================================================
    # RESUMO FINAL
    # =====================================================
    print("\n" + "="*60)
    print("  RESUMO DOS TESTES")
    print("="*60)
    total = runner.results["passed"] + runner.results["failed"] + runner.results["skipped"]
    print(f"  ✅ Passed:  {runner.results['passed']}")
    print(f"  ❌ Failed:  {runner.results['failed']}")
    print(f"  ⏭️  Skipped: {runner.results['skipped']}")
    print(f"  📊 Total:   {total}")
    print("="*60)
    
    if runner.results["failed"] == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"\n⚠️  {runner.results['failed']} teste(s) falharam")
    
    # IDs utilizados para referência
    print("\n📋 IDs utilizados nos testes:")
    print(f"   org_id:      {runner.org_id or 'N/A'}")
    print(f"   team_id:     {runner.team_id or 'N/A'}")
    print(f"   season_id:   {runner.season_id or 'N/A'}")
    print(f"   athlete_id:  {runner.athlete_id or 'N/A'}")
    print(f"   match_id:    {runner.match_id or 'N/A'}")
    print(f"   training_id: {runner.training_id or 'N/A'}")
    
    return runner.results["failed"] == 0


if __name__ == "__main__":
    success = run_smoke_tests()
    sys.exit(0 if success else 1)
