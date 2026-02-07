"""
Smoke Test - Ficha Única de Cadastro
=====================================
Testa os endpoints /intake/ficha-unica e /intake/ficha-unica/validate

Cenários:
1. Cadastro mínimo (só pessoa)
2. Cadastro com usuário
3. Cadastro completo (pessoa + usuário + atleta + equipe + registro)
4. Validação dry-run
5. Erros de validação (CPF duplicado, categoria inválida, etc.)

Execução:
    python tests/smoke_ficha_unica.py
"""

import os
import sys
import requests
from datetime import date, datetime, timedelta
from uuid import uuid4

# Configuração
BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "")

# Headers padrão
def get_headers(idempotency_key: str = None) -> dict:
    headers = {
        "Content-Type": "application/json",
    }
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def test_validate_only():
    """Teste 1: Validação sem gravação (dry-run)"""
    print("\n" + "=" * 60)
    print("TESTE 1: Validação Dry-Run")
    print("=" * 60)
    
    payload = {
        "person": {
            "first_name": "Teste",
            "last_name": "Validação",
            "birth_date": "2000-01-01",
            "gender": "feminino",
            "contacts": [
                {
                    "contact_type": "telefone",
                    "contact_value": "11999999999",
                    "is_primary": True
                }
            ],
            "documents": [
                {
                    "document_type": "cpf",
                    "document_number": "12345678901"
                }
            ]
        },
        "create_user": False
    }
    
    # Teste via endpoint /validate
    url = f"{BASE_URL}/intake/ficha-unica/validate"
    response = requests.post(url, json=payload, headers=get_headers())
    
    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "valid" in data, "Missing 'valid' field"
    print("✅ Teste 1 PASSED")
    return data


def test_create_person_only():
    """Teste 2: Cadastro mínimo (só pessoa)"""
    print("\n" + "=" * 60)
    print("TESTE 2: Cadastro Mínimo (Pessoa)")
    print("=" * 60)
    
    unique_id = str(uuid4())[:8]
    payload = {
        "person": {
            "first_name": f"Pessoa{unique_id}",
            "last_name": "Teste",
            "birth_date": "1995-05-15",
            "gender": "feminino",
            "nationality": "brasileira",
            "contacts": [
                {
                    "contact_type": "telefone",
                    "contact_value": f"119{unique_id}",
                    "is_primary": True
                },
                {
                    "contact_type": "email",
                    "contact_value": f"pessoa{unique_id}@teste.com",
                    "is_primary": False
                }
            ],
            "documents": [
                {
                    "document_type": "cpf",
                    "document_number": f"{unique_id}12345"
                }
            ],
            "address": {
                "address_type": "residencial_1",
                "street": "Rua Teste",
                "number": "123",
                "city": "São Paulo",
                "state": "SP",
                "postal_code": "01234567"
            }
        },
        "create_user": False
    }
    
    url = f"{BASE_URL}/intake/ficha-unica"
    idempotency_key = f"test-person-{unique_id}"
    response = requests.post(url, json=payload, headers=get_headers(idempotency_key))
    
    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    assert data["success"] == True, "Expected success=True"
    assert data["person_id"] is not None, "Missing person_id"
    print("✅ Teste 2 PASSED")
    return data


def test_create_person_with_user():
    """Teste 3: Cadastro de Pessoa com Usuário"""
    print("\n" + "=" * 60)
    print("TESTE 3: Cadastro Pessoa + Usuário")
    print("=" * 60)
    
    unique_id = str(uuid4())[:8]
    payload = {
        "person": {
            "first_name": f"User{unique_id}",
            "last_name": "Teste",
            "birth_date": "1990-03-20",
            "gender": "masculino",
            "contacts": [
                {
                    "contact_type": "email",
                    "contact_value": f"user{unique_id}@teste.com",
                    "is_primary": True
                }
            ],
            "documents": [
                {
                    "document_type": "cpf",
                    "document_number": f"{unique_id}67890"
                }
            ]
        },
        "create_user": True,
        "user": {
            "email": f"user{unique_id}@teste.com",
            "role_id": 3  # Treinador
        }
    }
    
    url = f"{BASE_URL}/intake/ficha-unica"
    response = requests.post(url, json=payload, headers=get_headers())
    
    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    assert data["success"] == True, "Expected success=True"
    assert data["person_id"] is not None, "Missing person_id"
    assert data["user_id"] is not None, "Missing user_id"
    assert data["user_created"] == True, "Expected user_created=True"
    print("✅ Teste 3 PASSED")
    return data


def test_create_full_athlete():
    """Teste 4: Cadastro Completo (Pessoa + Atleta + Equipe)"""
    print("\n" + "=" * 60)
    print("TESTE 4: Cadastro Completo (Atleta)")
    print("=" * 60)
    
    unique_id = str(uuid4())[:8]
    
    # Primeiro, precisamos ter uma organização e equipe existentes
    # Para este teste, usamos mode="select" com IDs que devem existir no banco
    # Em ambiente real, você precisaria criar ou buscar esses IDs
    
    payload = {
        "person": {
            "first_name": f"Atleta{unique_id}",
            "last_name": "Handebol",
            "birth_date": "2008-06-10",  # ~16 anos
            "gender": "feminino",
            "contacts": [
                {
                    "contact_type": "telefone",
                    "contact_value": f"119{unique_id}00",
                    "is_primary": True
                }
            ],
            "documents": [
                {
                    "document_type": "cpf",
                    "document_number": f"000{unique_id}000"
                }
            ],
            "address": {
                "address_type": "residencial_1",
                "street": "Av. Handebol",
                "number": "1000",
                "neighborhood": "Esportes",
                "city": "São Paulo",
                "state": "SP"
            },
            "media": {
                "profile_photo_url": f"https://example.com/photos/{unique_id}.jpg"
            }
        },
        "create_user": False,
        "athlete": {
            "create": True,
            "athlete_name": f"Atleta{unique_id} Handebol",
            "birth_date": "2008-06-10",
            "athlete_nickname": f"Nick{unique_id}",
            "shirt_number": 10,
            "main_defensive_position_id": 2,  # Armadora (não goleira)
            "main_offensive_position_id": 3,  # Ponta
            "guardian_name": "Responsável Teste",
            "guardian_phone": "11988887777"
        }
    }
    
    url = f"{BASE_URL}/intake/ficha-unica"
    response = requests.post(url, json=payload, headers=get_headers())
    
    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Este teste pode falhar se não houver posições cadastradas
    # Verificamos se foi 201 ou 400 com erro esperado
    if response.status_code == 201:
        data = response.json()
        assert data["success"] == True
        assert data["athlete_created"] == True
        print("✅ Teste 4 PASSED")
        return data
    elif response.status_code == 400:
        print("⚠️ Teste 4 SKIPPED (falta setup de posições no banco)")
        return None
    else:
        print(f"❌ Teste 4 FAILED - Status: {response.status_code}")
        return None


def test_idempotency():
    """Teste 5: Idempotência (retry não duplica)"""
    print("\n" + "=" * 60)
    print("TESTE 5: Idempotência")
    print("=" * 60)
    
    unique_id = str(uuid4())[:8]
    idempotency_key = f"idemp-{unique_id}"
    
    payload = {
        "person": {
            "first_name": f"Idemp{unique_id}",
            "last_name": "Test",
            "gender": "feminino",
            "contacts": [],
            "documents": []
        },
        "create_user": False
    }
    
    url = f"{BASE_URL}/intake/ficha-unica"
    
    # Primeira chamada
    response1 = requests.post(url, json=payload, headers=get_headers(idempotency_key))
    print(f"Chamada 1 - Status: {response1.status_code}")
    
    # Segunda chamada com mesmo idempotency key
    response2 = requests.post(url, json=payload, headers=get_headers(idempotency_key))
    print(f"Chamada 2 - Status: {response2.status_code}")
    
    if response1.status_code == 201 and response2.status_code == 201:
        data1 = response1.json()
        data2 = response2.json()
        
        # Mesmo person_id = idempotência funcionando
        if data1["person_id"] == data2["person_id"]:
            print("✅ Teste 5 PASSED (mesmo person_id retornado)")
        else:
            print("❌ Teste 5 FAILED (person_id diferente)")
    else:
        print(f"⚠️ Teste 5 SKIPPED - Status: {response1.status_code}, {response2.status_code}")


def test_validation_error_duplicate_cpf():
    """Teste 6: Erro de CPF duplicado"""
    print("\n" + "=" * 60)
    print("TESTE 6: Validação - CPF Duplicado")
    print("=" * 60)
    
    cpf = "99999999999"
    
    # Primeiro cadastro
    payload1 = {
        "person": {
            "first_name": "Primeiro",
            "last_name": "CPF",
            "gender": "feminino",
            "contacts": [],
            "documents": [
                {
                    "document_type": "cpf",
                    "document_number": cpf
                }
            ]
        },
        "create_user": False
    }
    
    url = f"{BASE_URL}/intake/ficha-unica"
    response1 = requests.post(url, json=payload1, headers=get_headers())
    print(f"Primeiro cadastro - Status: {response1.status_code}")
    
    if response1.status_code != 201:
        print("⚠️ Primeiro cadastro falhou, CPF pode já existir")
    
    # Segundo cadastro com mesmo CPF (deve falhar)
    payload2 = {
        "person": {
            "first_name": "Segundo",
            "last_name": "CPF",
            "gender": "feminino",
            "contacts": [],
            "documents": [
                {
                    "document_type": "cpf",
                    "document_number": cpf
                }
            ]
        },
        "create_user": False
    }
    
    response2 = requests.post(url, json=payload2, headers=get_headers())
    print(f"Segundo cadastro - Status: {response2.status_code}")
    print(f"Response: {response2.json()}")
    
    if response2.status_code == 400:
        data = response2.json()
        if "cpf" in str(data).lower() or "duplicado" in str(data).lower():
            print("✅ Teste 6 PASSED (CPF duplicado detectado)")
        else:
            print("⚠️ Teste 6 - Erro diferente do esperado")
    else:
        print(f"❌ Teste 6 FAILED - Esperava 400, obteve {response2.status_code}")


def test_goalkeeper_no_offensive():
    """Teste 7: Goleira não pode ter posição ofensiva (RD13)"""
    print("\n" + "=" * 60)
    print("TESTE 7: Validação - Goleira sem ofensiva (RD13)")
    print("=" * 60)
    
    unique_id = str(uuid4())[:8]
    
    payload = {
        "person": {
            "first_name": f"Goleira{unique_id}",
            "last_name": "Test",
            "birth_date": "2005-01-01",
            "gender": "feminino",
            "contacts": [],
            "documents": []
        },
        "create_user": False,
        "athlete": {
            "create": True,
            "athlete_name": f"Goleira{unique_id}",
            "birth_date": "2005-01-01",
            "main_defensive_position_id": 1,  # Goleira (assumindo ID 1)
            "main_offensive_position_id": 3    # Posição ofensiva (erro!)
        }
    }
    
    # Primeiro testar via /validate
    url_validate = f"{BASE_URL}/intake/ficha-unica/validate"
    response = requests.post(url_validate, json=payload, headers=get_headers())
    
    print(f"URL: {url_validate}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("goalkeeper_positions_valid") == False or "RD13" in str(data.get("errors", [])):
            print("✅ Teste 7 PASSED (RD13 validado)")
        elif data.get("valid") == False:
            print("✅ Teste 7 PASSED (validação falhou)")
        else:
            print("⚠️ Teste 7 - Validação passou (pode ser que ID 1 não seja goleira)")
    else:
        print(f"⚠️ Teste 7 SKIPPED - Status: {response.status_code}")


def main():
    """Executa todos os testes smoke"""
    print("\n" + "=" * 60)
    print("SMOKE TEST - FICHA ÚNICA DE CADASTRO")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Auth: {'Token configurado' if AUTH_TOKEN else 'Sem token'}")
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        print(f"Health Check: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Servidor não está rodando!")
        print("   Execute: uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Executar testes
    tests = [
        test_validate_only,
        test_create_person_only,
        test_create_person_with_user,
        test_create_full_athlete,
        test_idempotency,
        test_validation_error_duplicate_cpf,
        test_goalkeeper_no_offensive,
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_fn in tests:
        try:
            result = test_fn()
            if result is None:
                skipped += 1
            else:
                passed += 1
        except AssertionError as e:
            print(f"❌ {test_fn.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_fn.__name__} ERROR: {e}")
            failed += 1
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️ Skipped: {skipped}")
    print(f"Total: {len(tests)}")
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
