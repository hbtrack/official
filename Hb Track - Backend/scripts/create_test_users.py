#!/usr/bin/env python3
"""
Criar usuários de teste para smoke test
"""

import requests
import json
from uuid import uuid4
import random

BASE_URL = "http://localhost:8000/api/v1"

def gerar_cpf_valido():
    cpf = [random.randint(0, 9) for _ in range(9)]
    for _ in range(2):
        val = sum((len(cpf) + 1 - i) * v for i, v in enumerate(cpf)) % 11
        cpf.append(0 if val < 2 else 11 - val)
    return ''.join(map(str, cpf))

def login_superadmin():
    r = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin@hbtracking.com", "password": "Admin@123"},
        timeout=15
    )
    if r.ok:
        return r.json()["access_token"]
    print(f"Erro no login: {r.status_code} - {r.text}")
    return None

def create_user_via_ficha(token: str, email: str, role_id: int, name: str):
    """Cria um usuário via Ficha Única"""
    unique_id = str(uuid4())[:8]
    
    payload = {
        "person": {
            "first_name": name.split()[0],
            "last_name": " ".join(name.split()[1:]) or "Teste",
            "birth_date": "1990-01-15",
            "gender": "masculino",
            "contacts": [
                {
                    "contact_type": "email",
                    "contact_value": email,
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
        "create_user": True,
        "user": {
            "email": email,
            "role_id": role_id
        }
    }
    
    r = requests.post(
        f"{BASE_URL}/intake/ficha-unica",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=15
    )
    
    return r.status_code, r.json() if r.ok else r.text

def set_password(email: str, password: str):
    """Define senha para um usuário (via reset token)"""
    # TODO: Implementar via admin ou banco
    pass

def main():
    print("=== Criando usuários de teste ===\n")
    
    token = login_superadmin()
    if not token:
        print("Falha no login do superadmin")
        return
    
    print("✓ Login superadmin OK\n")
    
    # Usuários a criar: (email, role_id, nome)
    # role_id: 1=dirigente, 2=coordenador, 3=treinador, 4=atleta
    users = [
        ("dirigente@teste.com", 1, "Dirigente Teste"),
        ("coordenador@teste.com", 2, "Coordenador Teste"),
        ("treinador@teste.com", 3, "Treinador Teste"),
        ("atleta@teste.com", 4, "Atleta Teste"),
    ]
    
    for email, role_id, name in users:
        print(f"Criando {name} ({email})...", end=" ")
        status, result = create_user_via_ficha(token, email, role_id, name)
        
        if status == 201:
            print(f"✓ Criado! user_id={result.get('user_id', 'N/A')}")
        elif status == 400 and "já cadastrado" in str(result):
            print("⚠ Já existe")
        else:
            print(f"✗ Erro {status}: {str(result)[:100]}")
    
    print("\n=== Usuários de teste criados ===")
    print("\nNOTA: Para definir senhas, use o reset_admin_pwd.py ou banco diretamente")

if __name__ == "__main__":
    main()
