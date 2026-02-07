"""Verificar senha do superadmin"""
import bcrypt

# Hash do banco
hash_banco = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgdXnGV8W"

# Testar diferentes senhas
senhas_testar = [
    "Admin@123!",
    "Admin@123",
    "admin@123!",
    "admin@123"
]

print("\n" + "="*70)
print("VERIFICAÇÃO DE SENHA DO SUPERADMIN")
print("="*70)
print(f"\nHash no banco: {hash_banco}\n")

for senha in senhas_testar:
    try:
        valido = bcrypt.checkpw(senha.encode('utf-8'), hash_banco.encode('utf-8'))
        status = "✅ CORRETO!" if valido else "❌ Incorreto"
        print(f"{status} - Senha: {senha}")
        if valido:
            print(f"\n{'='*70}")
            print(f"CREDENCIAIS VÁLIDAS:")
            print(f"   Email: adm@handballtrack.app")
            print(f"   Senha: {senha}")
            print(f"{'='*70}\n")
    except Exception as e:
        print(f"❌ Erro ao testar '{senha}': {e}")
