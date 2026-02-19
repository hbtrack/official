"""
Testar login do superadmin
"""
from __future__ import annotations

import requests


def test_login_superadmin():
    """Testa login do usuário superadmin via API."""
    BASE_URL = "http://localhost:8000"
    
    # Dados de login
    login_data = {
        "username": "adm@handballtrack.app",
        "password": "Admin@123!"
    }
    
    print("\n" + "="*70)
    print("TESTE DE LOGIN SUPERADMIN")
    print("="*70)
    print(f"\nEmail: {login_data['username']}")
    print(f"Senha: {login_data['password']}\n")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"Status: {response.status_code}")
    
    # Assert para pytest
    assert response.status_code == 200, f"Login falhou com status {response.status_code}: {response.text}"
    
    data = response.json()
    assert "access_token" in data, "Response missing access_token"
    assert "token_type" in data, "Response missing token_type"
    
    print("\n[OK] LOGIN BEM-SUCEDIDO!")
    print(f"\nToken: {data.get('access_token', 'N/A')[:50]}...")
    print(f"Token Type: {data.get('token_type', 'N/A')}")
    print("="*70 + "\n")
