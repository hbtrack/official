"""
Script de Verificação FASE 2 - Backend: Modelos e Schemas

Verifica se todos os componentes da FASE 2 do FICHA.MD foram implementados corretamente.

Checklist FASE 2:
- [ ] Modelo IdempotencyKey criado
- [ ] Schemas Pydantic criados
- [ ] Validações implementadas
- [ ] Imports organizados em __init__.py
- [ ] Tipos e literais corretos
"""
import sys
from datetime import date

def check_idempotency_model():
    """Verifica modelo IdempotencyKey"""
    print("\n=== Verificando Modelo IdempotencyKey ===")
    try:
        from app.models.idempotency_key import IdempotencyKey
        
        # Verificar campos obrigatórios
        required_columns = ['id', 'key', 'endpoint', 'request_hash', 'response_json', 'status_code', 'created_at']
        columns = [c.name for c in IdempotencyKey.__table__.columns]
        
        for col in required_columns:
            if col in columns:
                print(f"  ✅ Coluna '{col}' presente")
            else:
                print(f"  ❌ Coluna '{col}' AUSENTE")
                return False
        
        # Verificar tablename
        if IdempotencyKey.__tablename__ == 'idempotency_keys':
            print(f"  ✅ __tablename__ = 'idempotency_keys'")
        else:
            print(f"  ❌ __tablename__ incorreto: {IdempotencyKey.__tablename__}")
            return False
        
        # Verificar export em __init__
        from app.models import IdempotencyKey as IK
        print(f"  ✅ IdempotencyKey exportado em app.models")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


def check_schemas():
    """Verifica schemas Pydantic"""
    print("\n=== Verificando Schemas Pydantic ===")
    try:
        from app.schemas.intake import (
            PersonCreate, PersonContactCreate, PersonDocumentCreate,
            PersonAddressCreate, PersonMediaCreate, UserCreate,
            OrganizationSelection, MembershipCreate, TeamSelection,
            AthleteCreate, RegistrationCreate, FichaUnicaRequest,
            FichaUnicaResponse, FichaUnicaDryRunResponse, ValidationResult
        )
        
        schemas = [
            'PersonCreate', 'PersonContactCreate', 'PersonDocumentCreate',
            'PersonAddressCreate', 'PersonMediaCreate', 'UserCreate',
            'OrganizationSelection', 'MembershipCreate', 'TeamSelection',
            'AthleteCreate', 'RegistrationCreate', 'FichaUnicaRequest',
            'FichaUnicaResponse', 'FichaUnicaDryRunResponse', 'ValidationResult'
        ]
        
        for schema in schemas:
            print(f"  ✅ Schema '{schema}' importado")
        
        return True
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False


def check_utility_functions():
    """Verifica funções utilitárias"""
    print("\n=== Verificando Funções Utilitárias ===")
    try:
        from app.schemas.intake import normalize_cpf, normalize_email, normalize_phone, validate_cpf
        
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
        
        # Testar validate_cpf com CPF válido (gerado artificialmente)
        cpf_valido = "52998224725"  # CPF válido de teste
        if validate_cpf(cpf_valido):
            print(f"  ✅ validate_cpf('52998224725') = True (CPF válido)")
        else:
            print(f"  ❌ validate_cpf deveria retornar True para CPF válido")
            return False
        
        # Testar validate_cpf com CPF inválido
        cpf_invalido = "11111111111"
        if not validate_cpf(cpf_invalido):
            print(f"  ✅ validate_cpf('11111111111') = False (CPF inválido)")
        else:
            print(f"  ❌ validate_cpf deveria retornar False para CPF inválido")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


def check_validations():
    """Verifica validações Pydantic"""
    print("\n=== Verificando Validações Pydantic ===")
    try:
        from app.schemas.intake import PersonCreate, PersonContactCreate, PersonDocumentCreate
        from pydantic import ValidationError
        
        # Testar validação de contatos obrigatórios
        try:
            person = PersonCreate(
                first_name="Maria",
                last_name="Silva",
                contacts=[]  # Lista vazia - deve falhar
            )
            print(f"  ❌ Validação de contatos não funcionou - deveria rejeitar lista vazia")
            return False
        except ValidationError as e:
            if "Ao menos um contato é obrigatório" in str(e):
                print(f"  ✅ Validação 'ao menos um contato obrigatório' funcionando")
            else:
                print(f"  ⚠️ Validação de contatos falhou, mas com mensagem diferente: {e}")
        
        # Testar validação de email obrigatório
        try:
            person = PersonCreate(
                first_name="Maria",
                last_name="Silva",
                contacts=[
                    PersonContactCreate(contact_type="telefone", contact_value="11987654321")
                ]  # Sem email - deve falhar
            )
            print(f"  ❌ Validação de email não funcionou - deveria rejeitar sem email")
            return False
        except ValidationError as e:
            if "Ao menos um e-mail é obrigatório" in str(e):
                print(f"  ✅ Validação 'ao menos um email obrigatório' funcionando")
            else:
                print(f"  ⚠️ Validação de email falhou, mas com mensagem diferente: {e}")
        
        # Testar validação de CPF
        try:
            doc = PersonDocumentCreate(
                document_type="cpf",
                document_number="111.111.111-11"  # CPF inválido
            )
            print(f"  ❌ Validação de CPF não funcionou - deveria rejeitar CPF inválido")
            return False
        except ValidationError as e:
            if "CPF inválido" in str(e):
                print(f"  ✅ Validação de CPF inválido funcionando")
            else:
                print(f"  ⚠️ Validação de CPF falhou, mas com mensagem diferente: {e}")
        
        # Testar PersonCreate válido
        person = PersonCreate(
            first_name="Maria",
            last_name="Silva",
            birth_date=date(2000, 1, 1),
            gender="feminino",
            contacts=[
                PersonContactCreate(contact_type="email", contact_value="maria@email.com", is_primary=True),
                PersonContactCreate(contact_type="telefone", contact_value="11987654321")
            ]
        )
        print(f"  ✅ PersonCreate válido criado com sucesso")
        print(f"     - full_name: {person.full_name}")
        print(f"     - contatos: {len(person.contacts)}")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_dry_run_response():
    """Verifica FichaUnicaDryRunResponse"""
    print("\n=== Verificando FichaUnicaDryRunResponse ===")
    try:
        from app.schemas.intake import FichaUnicaDryRunResponse, ValidationResult
        
        # Criar instância válida
        dry_run = FichaUnicaDryRunResponse(
            valid=True,
            warnings=["Atleta será cadastrada em categoria acima da natural"],
            errors=[],
            preview={
                "person": {"first_name": "Maria", "last_name": "Silva"},
                "user_will_be_created": True,
                "organization_will_be_created": False,
                "team_will_be_created": False,
                "athlete_will_be_created": True
            },
            validation_details=ValidationResult(
                valid=True,
                errors=[],
                warnings=["Atleta em categoria acima"],
                cpf_available=True,
                email_available=True
            )
        )
        
        print(f"  ✅ FichaUnicaDryRunResponse criado com sucesso")
        print(f"     - valid: {dry_run.valid}")
        print(f"     - warnings: {dry_run.warnings}")
        print(f"     - preview keys: {list(dry_run.preview.keys())}")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


def main():
    print("=" * 60)
    print("VERIFICAÇÃO FASE 2 - Backend: Modelos e Schemas")
    print("=" * 60)
    
    results = {
        "IdempotencyKey Model": check_idempotency_model(),
        "Schemas Pydantic": check_schemas(),
        "Funções Utilitárias": check_utility_functions(),
        "Validações Pydantic": check_validations(),
        "FichaUnicaDryRunResponse": check_dry_run_response()
    }
    
    print("\n" + "=" * 60)
    print("RESUMO FASE 2")
    print("=" * 60)
    
    all_passed = True
    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ FASE 2 COMPLETA - Todos os componentes verificados!")
    else:
        print("❌ FASE 2 INCOMPLETA - Alguns componentes falharam")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
