"""
Script de Teste - Endpoints FASE 4

Testa os endpoints:
- GET /api/v1/media/sign-upload
- GET /api/v1/media/validate-url
- GET /api/v1/intake/organizations/autocomplete
- GET /api/v1/intake/teams/autocomplete

Uso:
    cd "Hb Track - Backend"
    python scripts/test_fase4_endpoints.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def get_token():
    """Obtém token de autenticação."""
    print("\n📝 Obtendo token de autenticação...")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data={
            "username": "admin@hbtracking.com",
            "password": "HBTrack@2024!"
        }
    )
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"✅ Token obtido: {token[:50]}...")
        return token
    else:
        print(f"❌ Erro ao obter token: {response.status_code}")
        print(response.text)
        return None


def test_media_sign_upload(token):
    """Testa endpoint /media/sign-upload."""
    print("\n" + "=" * 60)
    print("1. TESTE: GET /api/v1/media/sign-upload")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/media/sign-upload",
        headers=headers,
        params={"media_type": "photo", "entity_type": "athlete"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ cloud_name: {data.get('cloud_name')}")
        print(f"✅ api_key: {data.get('api_key')}")
        print(f"✅ timestamp: {data.get('timestamp')}")
        print(f"✅ signature: {data.get('signature')[:30]}...")
        print(f"✅ folder: {data.get('folder')}")
        return True
    else:
        print(f"❌ Erro: {response.text}")
        return False


def test_media_validate_url(token):
    """Testa endpoint /media/validate-url."""
    print("\n" + "=" * 60)
    print("2. TESTE: GET /api/v1/media/validate-url")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # URL válida do Cloudinary
    test_url = "https://res.cloudinary.com/di5qmyhsx/image/upload/v123456/test.jpg"
    
    response = requests.get(
        f"{BASE_URL}/api/v1/media/validate-url",
        headers=headers,
        params={"url": test_url}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ valid: {data.get('valid')}")
        print(f"✅ url: {data.get('url')}")
        print(f"✅ cloud_name: {data.get('cloud_name')}")
        return True
    else:
        print(f"❌ Erro: {response.text}")
        return False


def test_organizations_autocomplete(token):
    """Testa endpoint /intake/organizations/autocomplete."""
    print("\n" + "=" * 60)
    print("3. TESTE: GET /api/v1/intake/organizations/autocomplete")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/intake/organizations/autocomplete",
        headers=headers,
        params={"q": "clube", "limit": 5}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Organizações encontradas: {len(data)}")
        for org in data[:3]:
            print(f"   - {org.get('name')} (id: {org.get('id')[:8]}...)")
        return True
    else:
        print(f"❌ Erro: {response.text}")
        return False


def test_teams_autocomplete(token):
    """Testa endpoint /intake/teams/autocomplete."""
    print("\n" + "=" * 60)
    print("4. TESTE: GET /api/v1/intake/teams/autocomplete")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Primeiro buscar uma organização
    org_response = requests.get(
        f"{BASE_URL}/api/v1/organizations",
        headers=headers,
        params={"page_size": 1}
    )
    
    if org_response.status_code != 200:
        print("❌ Não foi possível obter organizações")
        return False
    
    orgs = org_response.json()
    if not orgs.get("items"):
        print("⚠️ Nenhuma organização encontrada, criando teste sem org_id")
        return False
    
    org_id = orgs["items"][0]["id"]
    print(f"📋 Usando organização: {org_id[:8]}...")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/intake/teams/autocomplete",
        headers=headers,
        params={"organization_id": org_id, "q": "", "limit": 5}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Equipes encontradas: {len(data)}")
        for team in data[:3]:
            print(f"   - {team.get('name')} (gender: {team.get('gender')})")
        return True
    else:
        print(f"❌ Erro: {response.text}")
        return False


def test_ficha_unica_validate(token):
    """Testa endpoint /intake/ficha-unica/validate."""
    print("\n" + "=" * 60)
    print("5. TESTE: POST /api/v1/intake/ficha-unica/validate")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Payload mínimo para teste
    payload = {
        "person": {
            "first_name": "Teste",
            "last_name": "Validacao",
            "cpf": "12345678901",
            "birth_date": "2000-01-01",
            "gender": "masculino",
            "email": "teste@validacao.com",
            "phone": "11999999999"
        },
        "create_user": False,
        "create_athlete": False
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/intake/ficha-unica/validate",
        headers=headers,
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ is_valid: {data.get('is_valid')}")
        if data.get("errors"):
            print(f"   Erros: {len(data.get('errors'))}")
            for err in data.get("errors", [])[:3]:
                print(f"   - {err.get('field')}: {err.get('message')}")
        if data.get("warnings"):
            print(f"   Warnings: {len(data.get('warnings'))}")
        return True
    else:
        print(f"❌ Erro: {response.text}")
        return False


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 70)
    print("      TESTE ENDPOINTS FASE 4 - FICHA ÚNICA")
    print("=" * 70)
    
    # Obter token
    token = get_token()
    if not token:
        print("\n❌ Falha ao obter token. Servidor está rodando?")
        return 1
    
    results = []
    
    # Executar testes
    results.append(("Media Sign Upload", test_media_sign_upload(token)))
    results.append(("Media Validate URL", test_media_validate_url(token)))
    results.append(("Organizations Autocomplete", test_organizations_autocomplete(token)))
    results.append(("Teams Autocomplete", test_teams_autocomplete(token)))
    results.append(("Ficha Única Validate", test_ficha_unica_validate(token)))
    
    # Resumo
    print("\n" + "=" * 70)
    print("                         RESUMO")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "-" * 70)
    print(f"  Total: {passed} passou, {failed} falhou")
    print("-" * 70)
    
    if failed == 0:
        print("\n🎉 TODOS OS ENDPOINTS FASE 4 FUNCIONANDO!")
        return 0
    else:
        print(f"\n⚠️ {failed} ENDPOINT(S) COM PROBLEMA")
        return 1


if __name__ == "__main__":
    exit(main())
