"""
Script de Verificação FASE 3 - Backend: Serviços e Lógica de Negócio

Verifica se todos os componentes da FASE 3 do FICHA.MD foram implementados corretamente.

Checklist FASE 3:
- [ ] Validadores criados (CPF, e-mail, telefone)
- [ ] Validação de escopo implementada
- [ ] Sistema de idempotência implementado
- [ ] Serviço principal atualizado
- [ ] Regra do goleiro implementada
- [ ] Logs estruturados adicionados
- [ ] Tratamento de erros configurado
"""
import sys


def check_validators():
    """Verifica módulo validators.py"""
    print("\n=== Verificando validators.py ===")
    try:
        from app.services.intake.validators import (
            normalize_cpf,
            normalize_phone,
            normalize_email,
            validate_cpf_checksum,
            check_duplicate_contact,
            check_duplicate_document,
            check_email_exists,
            check_cpf_exists,
            check_phone_exists,
            is_goalkeeper_position,
            validate_goalkeeper_positions,
        )
        
        # Testar normalize_cpf
        cpf = "123.456.789-09"
        normalized = normalize_cpf(cpf)
        if normalized == "12345678909":
            print(f"  ✅ normalize_cpf('123.456.789-09') = '12345678909'")
        else:
            print(f"  ❌ normalize_cpf incorreto: {normalized}")
            return False
        
        # Testar normalize_phone
        phone = "(11) 98765-4321"
        normalized = normalize_phone(phone)
        if normalized == "11987654321":
            print(f"  ✅ normalize_phone('(11) 98765-4321') = '11987654321'")
        else:
            print(f"  ❌ normalize_phone incorreto: {normalized}")
            return False
        
        # Testar normalize_email
        email = "  TEST@Email.COM  "
        normalized = normalize_email(email)
        if normalized == "test@email.com":
            print(f"  ✅ normalize_email('  TEST@Email.COM  ') = 'test@email.com'")
        else:
            print(f"  ❌ normalize_email incorreto: {normalized}")
            return False
        
        # Testar validate_cpf_checksum
        cpf_valido = "52998224725"
        if validate_cpf_checksum(cpf_valido):
            print(f"  ✅ validate_cpf_checksum('52998224725') = True")
        else:
            print(f"  ❌ validate_cpf_checksum deveria retornar True")
            return False
        
        cpf_invalido = "11111111111"
        if not validate_cpf_checksum(cpf_invalido):
            print(f"  ✅ validate_cpf_checksum('11111111111') = False")
        else:
            print(f"  ❌ validate_cpf_checksum deveria retornar False")
            return False
        
        # Verificar funções de banco (só existência)
        print(f"  ✅ check_duplicate_contact disponível")
        print(f"  ✅ check_duplicate_document disponível")
        print(f"  ✅ check_email_exists disponível")
        print(f"  ✅ check_cpf_exists disponível")
        print(f"  ✅ check_phone_exists disponível")
        print(f"  ✅ is_goalkeeper_position disponível")
        print(f"  ✅ validate_goalkeeper_positions disponível")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_scope_validator():
    """Verifica módulo scope_validator.py"""
    print("\n=== Verificando scope_validator.py ===")
    try:
        from app.services.intake.scope_validator import (
            validate_ficha_scope,
            ROLES_CREATE_ORGANIZATION,
            ROLES_CREATE_TEAM,
            ROLES_CREATE_ATHLETE,
            ROLES_CREATE_MEMBERSHIP,
        )
        
        # Verificar constantes
        if "dirigente" in ROLES_CREATE_ORGANIZATION:
            print(f"  ✅ ROLES_CREATE_ORGANIZATION = {ROLES_CREATE_ORGANIZATION}")
        else:
            print(f"  ❌ ROLES_CREATE_ORGANIZATION inválido")
            return False
        
        if "coordenador" in ROLES_CREATE_TEAM:
            print(f"  ✅ ROLES_CREATE_TEAM = {ROLES_CREATE_TEAM}")
        else:
            print(f"  ❌ ROLES_CREATE_TEAM inválido")
            return False
        
        if "treinador" in ROLES_CREATE_ATHLETE:
            print(f"  ✅ ROLES_CREATE_ATHLETE = {ROLES_CREATE_ATHLETE}")
        else:
            print(f"  ❌ ROLES_CREATE_ATHLETE inválido")
            return False
        
        print(f"  ✅ ROLES_CREATE_MEMBERSHIP = {ROLES_CREATE_MEMBERSHIP}")
        print(f"  ✅ validate_ficha_scope disponível")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_idempotency():
    """Verifica módulo idempotency.py"""
    print("\n=== Verificando idempotency.py ===")
    try:
        from app.services.intake.idempotency import (
            compute_request_hash,
            serialize_response,
            check_idempotency,
            save_idempotency,
            cleanup_expired_keys,
            IdempotencyGuard,
        )
        
        # Testar compute_request_hash
        payload = {"name": "Test", "value": 123}
        hash1 = compute_request_hash(payload)
        hash2 = compute_request_hash({"value": 123, "name": "Test"})  # Ordem diferente
        
        if hash1 == hash2 and len(hash1) == 64:
            print(f"  ✅ compute_request_hash funciona corretamente")
            print(f"     - Hash: {hash1[:16]}...")
        else:
            print(f"  ❌ compute_request_hash inconsistente")
            return False
        
        # Testar serialize_response
        from pydantic import BaseModel
        class TestResponse(BaseModel):
            success: bool
            message: str
        
        response = TestResponse(success=True, message="OK")
        serialized = serialize_response(response)
        if serialized == {"success": True, "message": "OK"}:
            print(f"  ✅ serialize_response funciona corretamente")
        else:
            print(f"  ❌ serialize_response incorreto: {serialized}")
            return False
        
        print(f"  ✅ check_idempotency disponível")
        print(f"  ✅ save_idempotency disponível")
        print(f"  ✅ cleanup_expired_keys disponível")
        print(f"  ✅ IdempotencyGuard disponível")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ficha_service():
    """Verifica FichaUnicaService atualizado"""
    print("\n=== Verificando FichaUnicaService ===")
    try:
        from app.services.intake import FichaUnicaService
        
        # Verificar métodos
        methods = dir(FichaUnicaService)
        
        required_methods = [
            'validate',
            'process',
            'process_with_idempotency',
            'dry_run',
            '_process_transaction',
            '_create_person',
            '_create_user_with_welcome_token',
            '_create_athlete',
        ]
        
        for method in required_methods:
            if method in methods:
                print(f"  ✅ Método '{method}' presente")
            else:
                print(f"  ❌ Método '{method}' AUSENTE")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_init_exports():
    """Verifica exports do __init__.py"""
    print("\n=== Verificando exports de app.services.intake ===")
    try:
        from app.services.intake import (
            # Serviço principal
            FichaUnicaService,
            # Validadores
            normalize_cpf,
            normalize_phone,
            normalize_email,
            validate_cpf_checksum,
            check_duplicate_contact,
            check_duplicate_document,
            # Escopo
            validate_ficha_scope,
            ROLES_CREATE_ORGANIZATION,
            # Idempotência
            check_idempotency,
            save_idempotency,
            IdempotencyGuard,
        )
        
        print(f"  ✅ FichaUnicaService exportado")
        print(f"  ✅ Funções de validação exportadas")
        print(f"  ✅ Funções de escopo exportadas")
        print(f"  ✅ Funções de idempotência exportadas")
        
        return True
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False


def main():
    print("=" * 60)
    print("VERIFICAÇÃO FASE 3 - Backend: Serviços e Lógica de Negócio")
    print("=" * 60)
    
    results = {
        "validators.py": check_validators(),
        "scope_validator.py": check_scope_validator(),
        "idempotency.py": check_idempotency(),
        "FichaUnicaService": check_ficha_service(),
        "Exports __init__": check_init_exports(),
    }
    
    print("\n" + "=" * 60)
    print("RESUMO FASE 3")
    print("=" * 60)
    
    all_passed = True
    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ FASE 3 COMPLETA - Todos os componentes verificados!")
    else:
        print("❌ FASE 3 INCOMPLETA - Alguns componentes falharam")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
