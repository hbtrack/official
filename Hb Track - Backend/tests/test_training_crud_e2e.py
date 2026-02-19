"""
Script de Teste End-to-End para Training Sessions
=================================================

Testa POST/PATCH/DELETE/RESTORE com usuário que tenha membership ativo.

Requisitos:
- Usuário com membership ativo (ctx.membership_id presente)
- Escopo de equipe válido

Execução: python tests/test_training_crud_e2e.py
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
from datetime import datetime, timedelta, date
from uuid import uuid4
from typing import Optional, Dict, Any

from sqlalchemy import text
from app.core.db import SessionLocal

# Configuração
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1 = f"{BASE_URL}/api/v1"


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


class TestSetup:
    """Cria e gerencia dados de teste"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.org_id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.person_id: Optional[str] = None
        self.membership_id: Optional[str] = None
        self.team_id: Optional[str] = None
        self.season_id: Optional[str] = None
        self.token: Optional[str] = None
        self.test_email = f"test_coach_{datetime.now().strftime('%H%M%S')}@hbtest.com"
        self.test_password = "TestCoach@123"
    
    def setup(self) -> bool:
        """Cria todos os dados necessários para o teste"""
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
            
            # 3. Criar person para o coach
            self.person_id = str(uuid4())
            self.db.execute(text("""
                INSERT INTO persons (id, first_name, last_name, full_name, gender)
                VALUES (:id, 'Coach', 'de Teste', 'Coach de Teste', 'masculino')
            """), {"id": self.person_id})
            print(f"   ✅ person_id: {self.person_id}")
            
            # 4. Criar user
            self.user_id = str(uuid4())
            # Hash bcrypt para "TestCoach@123" gerado com passlib
            password_hash = "$2b$12$EsdHCilSlLFjBgbvPll3le.MVCGl5JK2DCA9YeOBebnaLWr1F60e."
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
            print(f"   ✅ email: {self.test_email}")
            
            # 5. Obter role_id para coordenador (pode criar, atualizar, excluir e restaurar)
            role = self.db.execute(text(
                "SELECT id FROM roles WHERE code = 'coordenador' LIMIT 1"
            )).fetchone()
            if not role:
                print("❌ Papel 'coordenador' não encontrado")
                return False
            role_id = role[0]
            print(f"   ✅ role_id (coordenador): {role_id}")
            
            # 6. Criar membership ativo (CRÍTICO para ctx.membership_id)
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

            # 7. Criar equipe
            self.team_id = str(uuid4())
            self.db.execute(text("""
                INSERT INTO teams (id, organization_id, name, category_id, gender, is_our_team)
                VALUES (:id, :org_id, 'Equipe E2E Test', :cat_id, 'feminino', true)
            """), {"id": self.team_id, "org_id": self.org_id, "cat_id": category_id})
            print(f"   ✅ team_id: {self.team_id}")

            # 7.1. Garantir vínculo ativo entre usuário e equipe (team_memberships)
            self.team_membership_id = str(uuid4())
            self.db.execute(text("""
                INSERT INTO team_memberships (id, person_id, team_id, org_membership_id, start_at, status, end_at, deleted_at)
                VALUES (:id, :person_id, :team_id, :org_membership_id, NOW(), 'ativo', NULL, NULL)
            """), {
                "id": self.team_membership_id,
                "person_id": self.person_id,
                "team_id": self.team_id,
                "org_membership_id": self.membership_id
            })
            print(f"   ✅ team_membership_id: {self.team_membership_id}")

            # 8. Criar temporada
            self.season_id = str(uuid4())
            today = date.today()
            self.db.execute(text("""
                INSERT INTO seasons (id, team_id, name, year, start_date, end_date)
                VALUES (:id, :team_id, 'Season E2E Test', :year, :start, :end)
            """), {
                "id": self.season_id,
                "team_id": self.team_id,
                "year": today.year,
                "start": today,
                "end": today + timedelta(days=180)
            })
            print(f"   ✅ season_id: {self.season_id}")
            
            self.db.commit()
            print("\n   ✅ Setup completo!")
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erro no setup: {e}")
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
        """Remove dados de teste usando soft delete ou hard delete conforme permitido"""
        try:
            print_section("CLEANUP - Removendo Dados de Teste")
            
            reason = "E2E Test cleanup"
            now = datetime.now()
            
            # Soft delete para tabelas que bloqueiam hard delete
            if self.season_id:
                self.db.execute(text("""
                    UPDATE seasons SET deleted_at = :now, deleted_reason = :reason WHERE id = :id
                """), {"id": self.season_id, "now": now, "reason": reason})
                
            if self.team_id:
                self.db.execute(text("""
                    UPDATE teams SET deleted_at = :now, deleted_reason = :reason WHERE id = :id
                """), {"id": self.team_id, "now": now, "reason": reason})
            
            if self.membership_id:
                self.db.execute(text("""
                    UPDATE org_memberships SET deleted_at = :now, deleted_reason = :reason WHERE id = :id
                """), {"id": self.membership_id, "now": now, "reason": reason})
            
            if self.user_id:
                self.db.execute(text("""
                    UPDATE users SET deleted_at = :now, deleted_reason = :reason WHERE id = :id
                """), {"id": self.user_id, "now": now, "reason": reason})
            
            if self.person_id:
                self.db.execute(text("""
                    UPDATE persons SET deleted_at = :now, deleted_reason = :reason WHERE id = :id
                """), {"id": self.person_id, "now": now, "reason": reason})
            
            self.db.commit()
            print("   ✅ Cleanup completo (soft delete)!")
        except Exception as e:
            self.db.rollback()
            print(f"⚠️ Erro no cleanup: {e}")
        finally:
            self.db.close()


class TrainingCRUDTest:
    """Testes CRUD de Training Sessions"""
    
    def __init__(self, setup: TestSetup):
        self.setup = setup
        self.training_id: Optional[str] = None
        self.results = {"passed": 0, "failed": 0}
    
    def get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.setup.token}"
        }
    
    def test_post_create_training(self) -> bool:
        """POST - Criar sessão de treino"""
        print_section("TEST 1: POST - Criar Treino")
        
        session_at = (datetime.now() + timedelta(hours=2)).isoformat()
        payload = {
            "session_at": session_at,
            "session_type": "quadra",
            "main_objective": "Teste E2E - Criação de treino"
        }
        
        url = f"{API_V1}/teams/{self.setup.team_id}/trainings"
        print(f"   URL: {url}")
        print(f"   Payload: {payload}")
        
        try:
            resp = requests.post(url, json=payload, headers=self.get_headers(), timeout=10)
            
            if resp.status_code == 201:
                data = resp.json()
                self.training_id = data.get("id")
                print_result("POST /teams/{team_id}/trainings", True, f"training_id: {self.training_id}")
                self.results["passed"] += 1
                return True
            else:
                print_result("POST /teams/{team_id}/trainings", False, f"Status: {resp.status_code} - {resp.text[:200]}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("POST /teams/{team_id}/trainings", False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    def test_get_training(self) -> bool:
        """GET - Obter treino criado"""
        print_section("TEST 2: GET - Obter Treino")
        
        if not self.training_id:
            print_result("GET /teams/{team_id}/trainings/{id}", False, "Sem training_id (POST falhou)")
            self.results["failed"] += 1
            return False
        
        url = f"{API_V1}/teams/{self.setup.team_id}/trainings/{self.training_id}"
        
        try:
            resp = requests.get(url, headers=self.get_headers(), timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                print_result("GET /teams/{team_id}/trainings/{id}", True, f"session_at: {data.get('session_at')}")
                self.results["passed"] += 1
                return True
            else:
                print_result("GET /teams/{team_id}/trainings/{id}", False, f"Status: {resp.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("GET /teams/{team_id}/trainings/{id}", False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    def test_patch_update_training(self) -> bool:
        """PATCH - Atualizar treino"""
        print_section("TEST 3: PATCH - Atualizar Treino")
        
        if not self.training_id:
            print_result("PATCH /teams/{team_id}/trainings/{id}", False, "Sem training_id")
            self.results["failed"] += 1
            return False
        
        new_session_at = (datetime.now() + timedelta(hours=4)).isoformat()
        payload = {
            "session_at": new_session_at
        }
        
        url = f"{API_V1}/teams/{self.setup.team_id}/trainings/{self.training_id}"
        
        try:
            resp = requests.patch(url, json=payload, headers=self.get_headers(), timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                print_result("PATCH /teams/{team_id}/trainings/{id}", True, f"Updated session_at")
                self.results["passed"] += 1
                return True
            else:
                print_result("PATCH /teams/{team_id}/trainings/{id}", False, f"Status: {resp.status_code} - {resp.text[:200]}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("PATCH /teams/{team_id}/trainings/{id}", False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    def test_delete_training(self) -> bool:
        """DELETE - Soft delete do treino"""
        print_section("TEST 4: DELETE - Excluir Treino (soft delete)")
        
        if not self.training_id:
            print_result("DELETE /teams/{team_id}/trainings/{id}", False, "Sem training_id")
            self.results["failed"] += 1
            return False
        
        url = f"{API_V1}/teams/{self.setup.team_id}/trainings/{self.training_id}?reason=Teste E2E delete"
        
        try:
            resp = requests.delete(url, headers=self.get_headers(), timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                deleted_at = data.get("deleted_at")
                print_result("DELETE /teams/{team_id}/trainings/{id}", True, f"deleted_at: {deleted_at}")
                self.results["passed"] += 1
                return True
            else:
                print_result("DELETE /teams/{team_id}/trainings/{id}", False, f"Status: {resp.status_code} - {resp.text[:200]}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("DELETE /teams/{team_id}/trainings/{id}", False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    def test_restore_training(self) -> bool:
        """POST restore - Restaurar treino excluído"""
        print_section("TEST 5: POST - Restaurar Treino")
        
        if not self.training_id:
            print_result("POST /teams/{team_id}/trainings/{id}/restore", False, "Sem training_id")
            self.results["failed"] += 1
            return False
        
        url = f"{API_V1}/teams/{self.setup.team_id}/trainings/{self.training_id}/restore"
        
        try:
            resp = requests.post(url, headers=self.get_headers(), timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                deleted_at = data.get("deleted_at")
                print_result("POST /teams/{team_id}/trainings/{id}/restore", True, f"deleted_at: {deleted_at} (deve ser null)")
                self.results["passed"] += 1
                return True
            else:
                print_result("POST /teams/{team_id}/trainings/{id}/restore", False, f"Status: {resp.status_code} - {resp.text[:200]}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("POST /teams/{team_id}/trainings/{id}/restore", False, f"Exception: {e}")
            self.results["failed"] += 1
            return False
    
    def run_all_tests(self):
        """Executa todos os testes CRUD"""
        print("\n" + "="*60)
        print("  TESTE E2E: TRAINING SESSIONS CRUD")
        print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("="*60)
        
        self.test_post_create_training()
        self.test_get_training()
        self.test_patch_update_training()
        self.test_delete_training()
        self.test_restore_training()
        
        # Resumo
        print("\n" + "="*60)
        print("  RESUMO DOS TESTES")
        print("="*60)
        total = self.results["passed"] + self.results["failed"]
        print(f"  ✅ Passed:  {self.results['passed']}")
        print(f"  ❌ Failed:  {self.results['failed']}")
        print(f"  📊 Total:   {total}")
        print("="*60)
        
        if self.results["failed"] == 0:
            print("\n🎉 TODOS OS TESTES CRUD PASSARAM!")
        else:
            print(f"\n⚠️  {self.results['failed']} teste(s) falharam")
        
        return self.results["failed"] == 0


def main():
    """Função principal"""
    setup = TestSetup()
    
    try:
        # 1. Setup
        if not setup.setup():
            print("❌ Setup falhou. Abortando testes.")
            return False
        
        # 2. Login
        print_section("LOGIN - Obtendo Token")
        token = setup.get_token()
        if not token:
            print("❌ Login falhou. Abortando testes.")
            return False
        print(f"   ✅ Token obtido com sucesso")
        
        # 3. Verificar contexto
        print_section("VERIFICAR CONTEXTO")
        resp = requests.get(
            f"{API_V1}/auth/context",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if resp.status_code == 200:
            ctx = resp.json()
            print(f"   user_id: {ctx.get('user_id')}")
            print(f"   role_code: {ctx.get('role_code')}")
            print(f"   organization_id: {ctx.get('organization_id')}")
            print(f"   membership_id: {ctx.get('membership_id')}")
            
            if not ctx.get('membership_id'):
                print("⚠️ AVISO: membership_id não presente no contexto!")
        else:
            print(f"❌ Falha ao obter contexto: {resp.status_code}")
        
        # 4. Rodar testes CRUD
        test = TrainingCRUDTest(setup)
        success = test.run_all_tests()
        
        return success
        
    finally:
        # 5. Cleanup
        setup.cleanup()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
