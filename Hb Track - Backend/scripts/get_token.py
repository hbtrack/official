"""
Script simples para obter token do super admin
"""
import urllib.request
import urllib.parse
import json

# Dados de login
data = json.dumps({
    "email": "admin@hbtracking.com",
    "password": "Admin@123"
}).encode('utf-8')

# Faz requisição
req = urllib.request.Request(
    "http://localhost:8000/api/v1/auth/login",
    data=data,
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(result['access_token'])
except Exception as e:
    print(f"ERRO: {e}")
