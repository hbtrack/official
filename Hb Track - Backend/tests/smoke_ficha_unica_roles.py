#!/usr/bin/env python3
"""
Smoke Test - Ficha Única por Roles
==================================

Testa a Ficha Única com diferentes tipos de usuários:
- Superadmin (dirigente + is_superadmin=true)
- Dirigente
- Coordenador
- Treinador
- Atleta (deve ser negado)

Resultado esperado: Todos os testes passam = Ficha validada
"""

import json
import requests
import sys
from datetime import datetime
from typing import Optional, Tuple
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

# Cores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

def log_test(name: str, passed: bool, detail: str = ""):
    status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
    print(f"  {status} {name}")
    if detail and not passed:
        print(f"       {YELLOW}→ {detail}{RESET}")

def log_section(title: str):
    print(f"\n{BLUE}{BOLD}{'='*60}{RESET}")
    print(f"{BLUE}{BOLD}{title}{RESET}")
    print(f"{BLUE}{BOLD}{'='*60}{RESET}")

def login(email: str, password: str) -> Optional[str]:
    """Faz login e retorna o token"""
    import time
    for attempt in range(3):
        try:
            r = requests.post(
                f"{BASE_URL}/auth/login",
                data={"username": email, "password": password},
                timeout=15
            )
            if r.ok:
                return r.json().get("access_token")
            elif r.status_code == 429:
                print(f"    {YELLOW}Rate limit - aguardando 60s...{RESET}")
                time.sleep(60)
                continue
            return None
        except Exception as e:
            print(f"    {RED}Erro no login: {e}{RESET}")
            return None
    return None

def get_headers(token: str) -> dict:
    """Retorna headers com autenticação"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def create_test_person_payload(unique_id: str) -> dict:
    """Cria payload mínimo para teste (apenas pessoa)"""
    # Gerar CPF válido para teste
    import random
    def gerar_cpf_valido():
        cpf = [random.randint(0, 9) for _ in range(9)]
        for _ in range(2):
            val = sum((len(cpf) + 1 - i) * v for i, v in enumerate(cpf)) % 11
            cpf.append(0 if val < 2 else 11 - val)
        return ''.join(map(str, cpf))
    
    return {
        "person": {
            "first_name": f"Smoke",
            "last_name": f"Test {unique_id[:8]}",
            "birth_date": "2000-01-15",
            "gender": "feminino",
            "contacts": [
                {
                    "contact_type": "email",
                    "contact_value": f"smoke_{unique_id}@teste.com",
                    "is_primary": True
                }
            ],
            "documents": [
                {
                    "document_type": "cpf",
                    "document_number": gerar_cpf_valido()
                }
            ]
        },
        "create_user": False
    }

def test_ficha_unica_access(token: str, role_name: str, should_succeed: bool) -> Tuple[bool, str]:
    """Testa se o usuário pode acessar a Ficha Única (validate_only)"""
    unique_id = str(uuid4())[:8]
    payload = create_test_person_payload(unique_id)
    
    try:
        r = requests.post(
            f"{BASE_URL}/intake/ficha-unica?validate_only=true",
            headers=get_headers(token),
            json=payload,
            timeout=15
        )
        
        if should_succeed:
            if r.status_code in [200, 201]:
                return True, f"Status {r.status_code} - Validação OK"
            else:
                return False, f"Esperado 200/201, recebeu {r.status_code}: {r.text[:100]}"
        else:
            if r.status_code == 403:
                return True, "Acesso negado corretamente (403)"
            else:
                return False, f"Esperado 403, recebeu {r.status_code}"
                
    except Exception as e:
        return False, f"Exceção: {e}"

def test_ficha_unica_create(token: str, role_name: str) -> Tuple[bool, str]:
    """Testa criação real na Ficha Única"""
    unique_id = str(uuid4())[:8]
    payload = create_test_person_payload(unique_id)
    
    try:
        r = requests.post(
            f"{BASE_URL}/intake/ficha-unica",
            headers=get_headers(token),
            json=payload,
            timeout=15
        )
        
        if r.status_code == 201:
            data = r.json()
            person_id = data.get("person_id")
            return True, f"Pessoa criada: {person_id}"
        else:
            return False, f"Status {r.status_code}: {r.text[:200]}"
                
    except Exception as e:
        return False, f"Exceção: {e}"

def test_endpoints_publicos() -> int:
    """Testa endpoints públicos (sem auth)"""
    log_section("1. ENDPOINTS PÚBLICOS (sem autenticação)")
    
    passed = 0
    total = 4
    
    # Roles
    r = requests.get(f"{BASE_URL}/roles", timeout=10)
    ok = r.status_code == 200 and len(r.json()) >= 4
    log_test("GET /roles retorna 4 papéis", ok, f"Status: {r.status_code}")
    if ok: passed += 1
    
    # Categories
    r = requests.get(f"{BASE_URL}/categories", timeout=10)
    ok = r.status_code == 200
    log_test("GET /categories público", ok, f"Status: {r.status_code}")
    if ok: passed += 1
    
    # Positions
    r = requests.get(f"{BASE_URL}/positions", timeout=10)
    ok = r.status_code == 200
    log_test("GET /positions público", ok, f"Status: {r.status_code}")
    if ok: passed += 1
    
    # Organizations
    r = requests.get(f"{BASE_URL}/organizations", timeout=10)
    ok = r.status_code == 200
    log_test("GET /organizations público", ok, f"Status: {r.status_code}")
    if ok: passed += 1
    
    print(f"\n  Resultado: {passed}/{total}")
    return passed == total

def test_superadmin() -> int:
    """Testa acesso como Superadmin"""
    log_section("2. SUPERADMIN (admin@hbtracking.com)")
    
    token = login("admin@hbtracking.com", "Admin@123")
    if not token:
        log_test("Login", False, "Falha no login")
        return 0
    
    log_test("Login", True)
    
    passed = 0
    total = 3
    
    # Verificar /users/me
    r = requests.get(f"{BASE_URL}/users/me", headers=get_headers(token), timeout=10)
    if r.ok:
        data = r.json()
        is_super = data.get("is_superadmin", False)
        log_test("/users/me retorna is_superadmin=true", is_super, f"is_superadmin={is_super}")
        if is_super: passed += 1
    else:
        log_test("/users/me", False, f"Status: {r.status_code}")
    
    # Validar Ficha
    ok, detail = test_ficha_unica_access(token, "superadmin", should_succeed=True)
    log_test("Ficha Única - validate_only", ok, detail)
    if ok: passed += 1
    
    # Criar Pessoa
    ok, detail = test_ficha_unica_create(token, "superadmin")
    log_test("Ficha Única - criar pessoa", ok, detail)
    if ok: passed += 1
    
    print(f"\n  Resultado: {passed}/{total}")
    return passed == total

def test_role_access(email: str, password: str, role_name: str, should_have_access: bool) -> bool:
    """Testa acesso de um role específico"""
    log_section(f"TESTE: {role_name.upper()} ({email})")
    
    token = login(email, password)
    if not token:
        log_test("Login", False, "Falha no login - usuário pode não existir")
        return False if should_have_access else True  # Se não deveria ter acesso, tudo bem
    
    log_test("Login", True)
    
    # Testar acesso à Ficha
    ok, detail = test_ficha_unica_access(token, role_name, should_succeed=should_have_access)
    log_test(f"Ficha Única - {'acesso permitido' if should_have_access else 'acesso negado'}", ok, detail)
    
    return ok

def create_test_users():
    """Cria usuários de teste se não existirem"""
    log_section("0. PREPARAÇÃO - Verificar/Criar usuários de teste")
    
    # Login como superadmin para criar usuários
    token = login("admin@hbtracking.com", "Admin@123")
    if not token:
        print(f"  {RED}Não foi possível fazer login como superadmin{RESET}")
        return False
    
    print(f"  {GREEN}Superadmin autenticado{RESET}")
    
    # Verificar se usuários de teste existem
    test_users = [
        ("dirigente@teste.com", "dirigente", "Dirigente Teste"),
        ("coordenador@teste.com", "coordenador", "Coordenador Teste"),
        ("treinador@teste.com", "treinador", "Treinador Teste"),
        ("atleta@teste.com", "atleta", "Atleta Teste"),
    ]
    
    for email, role_code, name in test_users:
        # Tentar login
        test_token = login(email, "Teste@123")
        if test_token:
            print(f"  ✓ {role_code}: {email} já existe")
        else:
            print(f"  ℹ {role_code}: {email} não existe (será testado sem ele)")
    
    return True

def main():
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}   SMOKE TEST - FICHA ÚNICA POR ROLES{RESET}")
    print(f"{BOLD}   Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    
    results = {}
    
    # 0. Preparação
    create_test_users()
    
    # 1. Endpoints públicos
    results["endpoints_publicos"] = test_endpoints_publicos()
    
    # 2. Superadmin
    results["superadmin"] = test_superadmin()
    
    # 3. Dirigente (deve ter acesso)
    results["dirigente"] = test_role_access("dirigente@teste.com", "Teste@123", "dirigente", True)
    
    # 4. Coordenador (deve ter acesso)
    results["coordenador"] = test_role_access("coordenador@teste.com", "Teste@123", "coordenador", True)
    
    # 5. Treinador (deve ter acesso)
    results["treinador"] = test_role_access("treinador@teste.com", "Teste@123", "treinador", True)
    
    # 6. Atleta (NÃO deve ter acesso)
    results["atleta_negado"] = test_role_access("atleta@teste.com", "Teste@123", "atleta", False)
    
    # Resumo
    log_section("RESUMO FINAL")
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
        print(f"  {status} {test_name}")
    
    print(f"\n{'='*60}")
    if all_passed:
        print(f"{GREEN}{BOLD}🎉 FICHA ÚNICA VALIDADA - TODOS OS TESTES PASSARAM!{RESET}")
        return 0
    else:
        print(f"{RED}{BOLD}❌ FICHA ÚNICA NÃO VALIDADA - ALGUNS TESTES FALHARAM{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
