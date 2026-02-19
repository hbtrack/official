"""
Smoke Test: Match Roster e Match Teams
======================================

Valida escopo, temporada e CRUD conforme RAG.

Pré-condições:
- Backend rodando
- team_id válido
- season_id ativa
- match_id com season_id
- athlete_id com inscrição ativa na temporada
- Token de usuário com membership ativo

Execução: python tests/smoke_match_roster_teams.py
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
from datetime import datetime, date, timedelta
from uuid import uuid4
from typing import Optional

from sqlalchemy import text
from app.core.db import SessionLocal

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1 = f"{BASE_URL}/api/v1"


def print_result(test_name: str, success: bool, details: str = ""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"       └─ {details}")


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


class SmokeTestSetup:
    """Cria dados necessários para o smoke test"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.org_id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.person_id: Optional[str] = None
        self.membership_id: Optional[str] = None
        self.team_id: Optional[str] = None
        self.opponent_team_id: Optional[str] = None
        self.season_id: Optional[str] = None
        self.match_id: Optional[str] = None
        self.athlete_id: Optional[str] = None
        self.athlete_person_id: Optional[str] = None
        self.token: Optional[str] = None
        self.test_email = f"smoke_coord_{datetime.now().strftime('%H%M%S')}@hbtest.com"
        self.test_password = "SmokeTest@123"
    
    def setup(self) -> bool:
        """Cria todos os dados necessários"""
        try:
            print_section("SETUP - Criando Dados de Teste")
            
            # 1. Obter organização existente
            org = self.db.execute(text(
                "SELECT id FROM organizations WHERE deleted_at IS NULL LIMIT 1"
            )).fetchone()
            if not org:
                print("❌ Nenhuma organização encontrada")
                return False
            self.org_id = str(org[0])
            print(f"   ✅ org_id: {self.org_id}")
            
            # 2. Obter categoria existente
            cat = self.db.execute(text("SELECT id FROM categories LIMIT 1")).fetchone()
            if not cat:
                print("❌ Nenhuma categoria encontrada")
                return False
            category_id = cat[0]
            print(f"   ✅ category_id: {category_id}")
            
            # 3. Criar person para coordenador
            self.person_id = str(uuid4())
            self.db.execute(text("""
                INSERT INTO persons (id, first_name, last_name, full_name, gender)
                VALUES (:id, 'Coordenador', 'Smoke', 'Coordenador Smoke', 'masculino')
            """), {"id": self.person_id})
            print(f"   ✅ person_id: {self.person_id}")
            
            # 4. Criar user
            self.user_id = str(uuid4())
            # Hash bcrypt para senha "SmokeTest@123"
            password_hash = "$2b$12$zcCfrTH3/yOrMRLSWqN5BOttH1uTf7NLOLXiBHGSlIGdTHxIiQ7r2"
            self.db.execute(text("""
                INSERT INTO users (id, person_id, email, password_hash, status)
                VALUES (:id, :person_id, :email, :hash, 'ativo')
            """), {
                "id": self.user_id,
                "person_id": self.person_id,
                "email": self.test_email,
                "hash": password_hash
            })
            print(f"   ✅ user_id: {self.user_id}")
            
            # 5. Obter role_id para coordenador
            role = self.db.execute(text(
                "SELECT id FROM roles WHERE code = 'coordenador' LIMIT 1"
            )).fetchone()
            role_id = role[0] if role else 2
            print(f"   ✅ role_id (coordenador): {role_id}")
            
            # 6. Criar membership
            self.membership_id = str(uuid4())
            self.db.execute(text("""
                INSERT INTO org_memberships (id, person_id, organization_id, role_id, start_at)
                VALUES (:id, :person_id, :org_id, :role_id, NOW())
            """), {
                "id": self.membership_id,
                "person_id": self.person_id,
                "org_id": self.org_id,
                "role_id": role_id
            })
            print(f"   ✅ membership_id: {self.membership_id}")
            
            # 7. Criar equipe (nossa)
            self.team_id = str(uuid4())
            self.db.execute(text("""
                INSERT INTO teams (id, organization_id, name, category_id, gender, is_our_team)
                VALUES (:id, :org_id, 'Equipe Smoke Test', :cat_id, 'feminino', true)
            """), {"id": self.team_id, "org_id": self.org_id, "cat_id": category_id})
            print(f"   ✅ team_id: {self.team_id}")
            
            # 7b. Criar equipe oponente
            self.opponent_team_id = str(uuid4())
            self.db.execute(text("""
                INSERT INTO teams (id, organization_id, name, category_id, gender, is_our_team)
                VALUES (:id, :org_id, 'Oponente Smoke Test', :cat_id, 'feminino', false)
            """), {"id": self.opponent_team_id, "org_id": self.org_id, "cat_id": category_id})
            print(f"   ✅ opponent_team_id: {self.opponent_team_id}")
            
            # 8. Criar temporada
            self.season_id = str(uuid4())
            today = date.today()
            self.db.execute(text("""
                INSERT INTO seasons (id, team_id, name, year, start_date, end_date)
                VALUES (:id, :team_id, 'Season Smoke Test', :year, :start, :end)
            """), {
                "id": self.season_id,
                "team_id": self.team_id,
                "year": today.year,
                "start": today - timedelta(days=30),
                "end": today + timedelta(days=180)
            })
            print(f"   ✅ season_id: {self.season_id}")
            
            # 9. Criar match (home_team != away_team)
            self.match_id = str(uuid4())
            self.db.execute(text("""
                INSERT INTO matches (
                    id, season_id, match_date, phase, status,
                    home_team_id, away_team_id, our_team_id, created_by_user_id
                ) VALUES (
                    :id, :season_id, :match_date, 'friendly', 'scheduled',
                    :home_team_id, :away_team_id, :our_team_id, :user_id
                )
            """), {
                "id": self.match_id,
                "season_id": self.season_id,
                "match_date": today + timedelta(days=7),
                "home_team_id": self.team_id,
                "away_team_id": self.opponent_team_id,
                "our_team_id": self.team_id,
                "user_id": self.user_id
            })
            print(f"   ✅ match_id: {self.match_id}")
            
            # 10. Criar pessoa para atleta
            self.athlete_person_id = str(uuid4())
            self.db.execute(text("""
                INSERT INTO persons (id, first_name, last_name, full_name, gender, birth_date)
                VALUES (:id, 'Atleta', 'Smoke', 'Atleta Smoke', 'feminino', :birth)
            """), {"id": self.athlete_person_id, "birth": date(2005, 1, 1)})
            print(f"   ✅ athlete_person_id: {self.athlete_person_id}")
            
            # 11. Criar atleta (conforme schema real: athlete_name, birth_date obrigatórios)
            self.athlete_id = str(uuid4())
            self.db.execute(text("""
                INSERT INTO athletes (
                    id, person_id, state,
                    athlete_name, birth_date
                ) VALUES (
                    :id, :person_id, 'ativa',
                    'Atleta Smoke Test', :birth_date
                )
            """), {
                "id": self.athlete_id,
                "person_id": self.athlete_person_id,
                "birth_date": date(2005, 1, 1)
            })
            print(f"   ✅ athlete_id: {self.athlete_id}")
            
            # 13. Criar team_registration (inscrição ativa na temporada)
            reg_id = str(uuid4())
            self.db.execute(text("""
                INSERT INTO team_registrations (id, athlete_id, team_id, start_at)
                VALUES (:id, :athlete_id, :team_id, :start)
            """), {
                "id": reg_id,
                "athlete_id": self.athlete_id,
                "team_id": self.team_id,
                "start": today - timedelta(days=30)
            })
            print(f"   ✅ team_registration_id: {reg_id}")
            
            self.db.commit()
            print("\n   ✅ Setup completo!")
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erro no setup: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_token(self) -> Optional[str]:
        """Faz login e obtém token"""
        try:
            resp = requests.post(
                f"{API_V1}/auth/login",
                data={"username": self.test_email, "password": self.test_password},
                timeout=10
            )
            if resp.status_code == 200:
                self.token = resp.json().get("access_token")
                return self.token
            print(f"❌ Login falhou: {resp.status_code} - {resp.text}")
            return None
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            return None
    
    def cleanup(self):
        """Remove dados de teste usando soft delete"""
        try:
            print_section("CLEANUP")
            reason = "Smoke test cleanup"
            now = datetime.now()
            
            # Hard delete em ordem reversa
            tables = [
                ("team_registrations", "athlete_id", self.athlete_id),
                ("match_roster", "match_id", self.match_id),
                ("match_teams", "match_id", self.match_id),
            ]
            
            for table, col, val in tables:
                if val:
                    try:
                        self.db.execute(text(f"DELETE FROM {table} WHERE {col} = :val"), {"val": val})
                    except:
                        pass
            
            # Soft delete nas tabelas com deleted_at
            soft_tables = [
                ("matches", self.match_id),
                ("seasons", self.season_id),
                ("teams", self.team_id),
                ("teams", self.opponent_team_id),
                ("athletes", self.athlete_id),
                ("org_memberships", self.membership_id),
                ("users", self.user_id),
                ("persons", self.person_id),
                ("persons", self.athlete_person_id),
            ]
            
            for table, val in soft_tables:
                if val:
                    try:
                        self.db.execute(text(f"""
                            UPDATE {table} SET deleted_at = :now, deleted_reason = :reason WHERE id = :id
                        """), {"id": val, "now": now, "reason": reason})
                    except:
                        pass
            
            self.db.commit()
            print("   ✅ Cleanup completo!")
        except Exception as e:
            self.db.rollback()
            print(f"⚠️ Erro no cleanup: {e}")
        finally:
            self.db.close()


class SmokeTestRunner:
    """Executa os smoke tests"""
    
    def __init__(self, setup: SmokeTestSetup):
        self.setup = setup
        self.results = {"passed": 0, "failed": 0}
        self.roster_entry_id: Optional[str] = None
    
    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.setup.token}"
        }
    
    # =========================================================================
    # SMOKE ESTRUTURAL
    # =========================================================================
    
    def test_structural_roster_get(self) -> bool:
        """GET roster - deve retornar 501 (não implementado) ou 200"""
        url = f"{API_V1}/teams/{self.setup.team_id}/matches/{self.setup.match_id}/roster"
        try:
            resp = requests.get(url, headers=self.get_headers(), timeout=10)
            # Esperado: 501 (não implementado) ou 200 (implementado)
            # Nunca 404
            if resp.status_code == 404:
                print_result("GET roster - estrutural", False, f"404 não permitido! {resp.text[:100]}")
                self.results["failed"] += 1
                return False
            elif resp.status_code in [200, 501]:
                print_result("GET roster - estrutural", True, f"Status: {resp.status_code}")
                self.results["passed"] += 1
                return True
            else:
                print_result("GET roster - estrutural", False, f"Status: {resp.status_code} - {resp.text[:100]}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("GET roster - estrutural", False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    def test_structural_teams_get(self) -> bool:
        """GET teams - deve retornar 501 ou 200"""
        url = f"{API_V1}/teams/{self.setup.team_id}/matches/{self.setup.match_id}/teams"
        try:
            resp = requests.get(url, headers=self.get_headers(), timeout=10)
            if resp.status_code == 404:
                print_result("GET teams - estrutural", False, f"404 não permitido!")
                self.results["failed"] += 1
                return False
            elif resp.status_code in [200, 501]:
                print_result("GET teams - estrutural", True, f"Status: {resp.status_code}")
                self.results["passed"] += 1
                return True
            else:
                print_result("GET teams - estrutural", False, f"Status: {resp.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("GET teams - estrutural", False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    def test_structural_403_wrong_team(self) -> bool:
        """Teste de escopo - team_id inválido deve retornar 403 ou 404"""
        fake_team_id = str(uuid4())
        url = f"{API_V1}/teams/{fake_team_id}/matches/{self.setup.match_id}/roster"
        try:
            resp = requests.get(url, headers=self.get_headers(), timeout=10)
            # Escopo errado: 403 ou 404 (team não existe)
            if resp.status_code in [403, 404]:
                print_result("GET roster - escopo inválido", True, f"Status: {resp.status_code} (correto)")
                self.results["passed"] += 1
                return True
            else:
                print_result("GET roster - escopo inválido", False, f"Esperado 403/404, got {resp.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("GET roster - escopo inválido", False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    # =========================================================================
    # SMOKE FUNCIONAL - MATCH ROSTER
    # =========================================================================
    
    def test_roster_post(self) -> bool:
        """POST - adicionar atleta ao roster"""
        url = f"{API_V1}/teams/{self.setup.team_id}/matches/{self.setup.match_id}/roster"
        payload = {
            "athlete_id": self.setup.athlete_id,
            "jersey_number": 10,
            "is_goalkeeper": False,
            "is_available": True
        }
        try:
            resp = requests.post(url, json=payload, headers=self.get_headers(), timeout=10)
            if resp.status_code == 201:
                data = resp.json()
                self.roster_entry_id = data.get("id")
                print_result("POST roster", True, f"roster_id: {self.roster_entry_id}")
                self.results["passed"] += 1
                return True
            elif resp.status_code == 501:
                print_result("POST roster", False, "501 - Não implementado ainda")
                self.results["failed"] += 1
                return False
            else:
                print_result("POST roster", False, f"Status: {resp.status_code} - {resp.text[:200]}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("POST roster", False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    def test_roster_get_list(self) -> bool:
        """GET - listar roster"""
        url = f"{API_V1}/teams/{self.setup.team_id}/matches/{self.setup.match_id}/roster"
        try:
            resp = requests.get(url, headers=self.get_headers(), timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                print_result("GET roster list", True, f"items: {len(data)}")
                self.results["passed"] += 1
                return True
            elif resp.status_code == 501:
                print_result("GET roster list", False, "501 - Não implementado ainda")
                self.results["failed"] += 1
                return False
            else:
                print_result("GET roster list", False, f"Status: {resp.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("GET roster list", False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    def test_roster_delete(self) -> bool:
        """DELETE - remover atleta do roster"""
        if not self.roster_entry_id:
            print_result("DELETE roster", False, "Sem roster_entry_id")
            self.results["failed"] += 1
            return False
        
        url = f"{API_V1}/teams/{self.setup.team_id}/matches/{self.setup.match_id}/roster/{self.setup.athlete_id}"
        try:
            resp = requests.delete(url, headers=self.get_headers(), timeout=10)
            if resp.status_code == 200:
                print_result("DELETE roster", True, "Removido com sucesso")
                self.results["passed"] += 1
                return True
            elif resp.status_code == 501:
                print_result("DELETE roster", False, "501 - Não implementado ainda")
                self.results["failed"] += 1
                return False
            else:
                print_result("DELETE roster", False, f"Status: {resp.status_code} - {resp.text[:100]}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("DELETE roster", False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    # =========================================================================
    # SMOKE FUNCIONAL - MATCH TEAMS
    # =========================================================================
    
    def test_teams_post(self) -> bool:
        """POST - adicionar equipe ao match_teams"""
        url = f"{API_V1}/teams/{self.setup.team_id}/matches/{self.setup.match_id}/teams"
        payload = {
            "team_id": str(self.setup.team_id),
            "is_home": True,
            "is_our_team": True
        }
        try:
            resp = requests.post(url, json=payload, headers=self.get_headers(), timeout=10)
            if resp.status_code == 201:
                data = resp.json()
                print_result("POST match teams", True, f"match_teams_id: {data.get('id')}")
                self.results["passed"] += 1
                return True
            elif resp.status_code == 409:
                print_result("POST match teams", True, f"409 - Já existe (ok)")
                self.results["passed"] += 1
                return True
            else:
                print_result("POST match teams", False, f"Status: {resp.status_code} - {resp.text[:100]}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("POST match teams", False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    def test_teams_get(self) -> bool:
        """GET - obter times do jogo"""
        url = f"{API_V1}/teams/{self.setup.team_id}/matches/{self.setup.match_id}/teams"
        try:
            resp = requests.get(url, headers=self.get_headers(), timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                print_result("GET match teams", True, f"items: {len(data)}")
                self.results["passed"] += 1
                return True
            elif resp.status_code == 501:
                print_result("GET match teams", False, "501 - Não implementado ainda")
                self.results["failed"] += 1
                return False
            else:
                print_result("GET match teams", False, f"Status: {resp.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("GET match teams", False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    def test_teams_patch(self) -> bool:
        """PATCH - atualizar dados do time no jogo"""
        url = f"{API_V1}/teams/{self.setup.team_id}/matches/{self.setup.match_id}/teams/home"
        payload = {"is_our_team": True}
        try:
            resp = requests.patch(url, json=payload, headers=self.get_headers(), timeout=10)
            if resp.status_code == 200:
                print_result("PATCH match teams", True, "Atualizado")
                self.results["passed"] += 1
                return True
            elif resp.status_code in [501, 404]:
                print_result("PATCH match teams", False, f"Status: {resp.status_code}")
                self.results["failed"] += 1
                return False
            elif resp.status_code == 422:
                print_result("PATCH match teams", True, "422 - Validação (esperado para side inválido)")
                self.results["passed"] += 1
                return True
            else:
                print_result("PATCH match teams", False, f"Status: {resp.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("PATCH match teams", False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    def run_structural_tests(self):
        """Executa apenas testes estruturais"""
        print_section("SMOKE ESTRUTURAL")
        self.test_structural_roster_get()
        self.test_structural_teams_get()
        self.test_structural_403_wrong_team()
    
    def run_functional_tests(self):
        """Executa testes funcionais"""
        print_section("SMOKE FUNCIONAL - ROSTER")
        self.test_roster_post()
        self.test_roster_get_list()
        self.test_roster_delete()
        
        print_section("SMOKE FUNCIONAL - TEAMS")
        self.test_teams_post()  # POST primeiro para criar a entrada
        self.test_teams_get()
        self.test_teams_patch()
    
    def print_summary(self):
        print_section("RESUMO")
        total = self.results["passed"] + self.results["failed"]
        print(f"  ✅ Passed:  {self.results['passed']}")
        print(f"  ❌ Failed:  {self.results['failed']}")
        print(f"  📊 Total:   {total}")
        
        if self.results["failed"] == 0:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
        else:
            print(f"\n⚠️  {self.results['failed']} teste(s) falharam")


def main():
    """Função principal"""
    setup = SmokeTestSetup()
    
    try:
        if not setup.setup():
            print("❌ Setup falhou. Abortando.")
            return False
        
        print_section("LOGIN")
        if not setup.get_token():
            print("❌ Login falhou. Abortando.")
            return False
        print("   ✅ Token obtido")
        
        runner = SmokeTestRunner(setup)
        
        # Primeiro: testes estruturais
        runner.run_structural_tests()
        
        # Se estrutural passou, rodar funcionais
        runner.run_functional_tests()
        
        runner.print_summary()
        return runner.results["failed"] == 0
        
    finally:
        setup.cleanup()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
