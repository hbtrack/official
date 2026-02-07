"""
Script para testar login do super admin e obter tokens
"""
import requests
import json

# Configuração
API_URL = "http://localhost:8000/api/v1"
EMAIL = "admin@hbtracking.com"
PASSWORD = "Admin@123"

# Faz login
response = requests.post(
    f"{API_URL}/auth/login",
    json={
        "email": EMAIL,
        "password": PASSWORD
    }
)

print("=" * 60)
print("LOGIN DO SUPER ADMIN")
print("=" * 60)
print()

if response.status_code == 200:
    data = response.json()
    print("OK LOGIN BEM-SUCEDIDO!")
    print()
    print("Dados do usuario:")
    print(f"  - User ID: {data['user_id']}")
    print(f"  - Email: {data['email']}")
    print(f"  - Nome: {data.get('full_name', 'N/A')}")
    print(f"  - Role: {data['role_code']}")
    print(f"  - Superadmin: {data['is_superadmin']}")
    print()
    print("Token de acesso:")
    print(f"  {data['access_token']}")
    print()
    print("Adicione ao .env.example:")
    print(f"  SUPER_ADMIN_TOKEN={data['access_token']}")
    print()
    print("=" * 60)
else:
    print("ERRO NO LOGIN!")
    print(f"  Status: {response.status_code}")
    print(f"  Resposta: {response.text}")
    print()
    print("=" * 60)
