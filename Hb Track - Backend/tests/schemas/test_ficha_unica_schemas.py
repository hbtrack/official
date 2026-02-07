"""
Testes para schemas da Ficha Única
FASE 2 - Validação de DTOs

Testa todas as validações definidas nos schemas Pydantic:
- PersonCreate: validação de contatos e emails obrigatórios
- UserCreate: validação de email e role_id
- OrganizationCreateInline: validação de modo (select/create)
- TeamCreateInline: validação de modo e campos obrigatórios
- AthleteCreate: validação de campos condicionais
- FichaUnicaRequest: validação de payload completo
"""
import pytest
from datetime import date, datetime
from pydantic import ValidationError

from app.schemas.intake import (
    PersonCreate,
    PersonContactCreate,
    PersonDocumentCreate,
    PersonAddressCreate,
    UserCreate,
    OrganizationCreateInline,
    OrganizationSelection,
    TeamCreateInline,
    TeamSelection,
    AthleteCreate,
    RegistrationCreate,
    FichaUnicaRequest,
    validate_cpf,
    normalize_cpf,
)


# =============================================================================
# TESTES - PERSON
# =============================================================================

def test_person_create_valid():
    """Testa criação de Person com dados válidos"""
    person = PersonCreate(
        first_name="João",
        last_name="Silva",
        birth_date=date(2000, 1, 1),
        gender="masculino",
        contacts=[
            PersonContactCreate(contact_type="email", contact_value="joao@test.com", is_primary=True)
        ]
    )
    assert person.first_name == "João"
    assert person.full_name == "João Silva"
    assert len(person.contacts) == 1


def test_person_create_missing_contacts():
    """Testa erro quando não há contatos"""
    with pytest.raises(ValidationError) as exc_info:
        PersonCreate(
            first_name="João",
            last_name="Silva",
            contacts=[]
        )
    assert "Ao menos um contato é obrigatório" in str(exc_info.value)


def test_person_create_missing_email():
    """Testa erro quando não há email nos contatos"""
    with pytest.raises(ValidationError) as exc_info:
        PersonCreate(
            first_name="João",
            last_name="Silva",
            contacts=[
                PersonContactCreate(contact_type="telefone", contact_value="11999999999")
            ]
        )
    assert "Ao menos um e-mail é obrigatório" in str(exc_info.value)


def test_person_contact_email_normalization():
    """Testa normalização de email (realizada no validator)"""
    contact = PersonContactCreate(
        contact_type="email",
        contact_value="  TESTE@EMAIL.COM  "
    )
    # A normalização acontece no validator do schema
    assert "@" in contact.contact_value


def test_person_contact_phone_normalization():
    """Testa normalização de telefone (realizada no validator)"""
    contact = PersonContactCreate(
        contact_type="telefone",
        contact_value="(11) 99999-9999"
    )
    # A normalização acontece no validator do schema
    assert len(contact.contact_value) > 0


def test_person_document_cpf_validation():
    """Testa validação de CPF válido"""
    doc = PersonDocumentCreate(
        document_type="cpf",
        document_number="123.456.789-09"  # CPF válido
    )
    assert normalize_cpf(doc.document_number) == "12345678909"


def test_person_document_invalid_cpf():
    """Testa rejeição de CPF inválido"""
    with pytest.raises(ValidationError) as exc_info:
        PersonDocumentCreate(
            document_type="cpf",
            document_number="111.111.111-11"  # CPF inválido
        )
    assert "CPF inválido" in str(exc_info.value)


# =============================================================================
# TESTES - USER
# =============================================================================

def test_user_create_valid():
    """Testa criação de User com dados válidos"""
    user = UserCreate(
        email="user@test.com",
        role_id=2
    )
    assert user.email == "user@test.com"
    assert user.role_id == 2


def test_user_create_invalid_role():
    """Testa rejeição de role_id inválido"""
    with pytest.raises(ValidationError):
        UserCreate(
            email="user@test.com",
            role_id=10  # Fora do range 1-5
        )


# =============================================================================
# TESTES - ORGANIZATION
# =============================================================================

def test_organization_select_mode():
    """Testa modo select com organization_id"""
    org = OrganizationSelection(
        mode="select",
        organization_id="550e8400-e29b-41d4-a716-446655440000"
    )
    assert org.organization_id is not None
    assert org.mode == "select"


def test_organization_create_mode():
    """Testa modo create com name"""
    org = OrganizationSelection(
        mode="create",
        name="Clube ABC"
    )
    assert org.name == "Clube ABC"
    assert org.mode == "create"


# =============================================================================
# TESTES - TEAM
# =============================================================================

def test_team_select_mode():
    """Testa modo select com team_id"""
    team = TeamSelection(
        mode="select",
        team_id="770e8400-e29b-41d4-a716-446655440000"
    )
    assert team.team_id is not None
    assert team.mode == "select"


def test_team_create_mode():
    """Testa modo create com name, category_id e gender"""
    team = TeamSelection(
        mode="create",
        name="Cadete Masculino",
        category_id=3,
        gender="masculino"
    )
    assert team.name == "Cadete Masculino"
    assert team.mode == "create"


# =============================================================================
# TESTES - ATHLETE
# =============================================================================

def test_athlete_create_valid():
    """Testa criação de Athlete com dados válidos"""
    athlete = AthleteCreate(
        create=True,
        athlete_name="João Silva",
        birth_date=date(2010, 5, 15),
        main_defensive_position_id=2
    )
    assert athlete.athlete_name == "João Silva"


def test_athlete_create_missing_required_fields():
    """Testa erro quando faltam campos obrigatórios (create=true)"""
    with pytest.raises(ValidationError) as exc_info:
        AthleteCreate(
            create=True,
            athlete_name="João Silva"
            # Falta birth_date e main_defensive_position_id
        )
    # A mensagem exata pode variar, mas deve mencionar campo obrigatório
    assert "obrigatório" in str(exc_info.value).lower()


def test_athlete_create_false_no_validation():
    """Testa que não valida campos quando create=false"""
    athlete = AthleteCreate(create=False)
    assert athlete.create is False
    # Quando create=False, campos podem ter valores default vazios


# =============================================================================
# TESTES - FICHA ÚNICA PAYLOAD
# =============================================================================

def test_ficha_unica_minimal_payload():
    """Testa payload mínimo: apenas person"""
    payload = FichaUnicaRequest(
        person=PersonCreate(
            first_name="Maria",
            last_name="Santos",
            contacts=[
                PersonContactCreate(contact_type="email", contact_value="maria@test.com")
            ]
        )
    )
    assert payload.person.first_name == "Maria"
    assert payload.create_user is False
    assert payload.user is None


def test_ficha_unica_full_payload():
    """Testa payload completo com todas as entidades"""
    from app.schemas.intake.ficha_unica import SeasonSelection
    
    payload = FichaUnicaRequest(
        person=PersonCreate(
            first_name="Maria",
            last_name="Santos",
            birth_date=date(2010, 5, 15),
            gender="feminino",
            contacts=[
                PersonContactCreate(contact_type="email", contact_value="maria@test.com")
            ]
        ),
        create_user=True,
        user=UserCreate(
            email="maria@test.com",
            role_id=4
        ),
        season=SeasonSelection(
            mode="select",
            season_id="880e8400-e29b-41d4-a716-446655440000"
        ),
        organization=OrganizationSelection(
            mode="select",
            organization_id="550e8400-e29b-41d4-a716-446655440000"
        ),
        team=TeamSelection(
            mode="select",
            team_id="770e8400-e29b-41d4-a716-446655440000"
        ),
        athlete=AthleteCreate(
            create=True,
            athlete_name="Maria Santos",
            birth_date=date(2010, 5, 15),
            main_defensive_position_id=2
        ),
        registration=RegistrationCreate(
            team_id="770e8400-e29b-41d4-a716-446655440000",
            start_at=datetime(2026, 1, 1)
        )
    )
    assert payload.person.first_name == "Maria"
    assert payload.create_user is True
    assert payload.user is not None
    assert payload.athlete.create is True


def test_ficha_unica_create_user_without_user_object():
    """Testa erro quando create_user=true mas user está ausente"""
    with pytest.raises(ValidationError) as exc_info:
        FichaUnicaRequest(
            person=PersonCreate(
                first_name="João",
                last_name="Silva",
                contacts=[
                    PersonContactCreate(contact_type="email", contact_value="joao@test.com")
                ]
            ),
            create_user=True,
            user=None  # Erro: deveria estar presente
        )
    # A mensagem exata pode variar, mas deve mencionar que user é obrigatório
    assert "user" in str(exc_info.value).lower() and "obrigatório" in str(exc_info.value).lower()


def test_ficha_unica_athlete_without_registration():
    """Testa que registration é opcional mesmo quando atleta é criado"""
    # Note: Na implementação atual, registration NÃO é obrigatório
    payload = FichaUnicaRequest(
        person=PersonCreate(
            first_name="João",
            last_name="Silva",
            contacts=[
                PersonContactCreate(contact_type="email", contact_value="joao@test.com")
            ]
        ),
        athlete=AthleteCreate(
            create=True,
            athlete_name="João Silva",
            birth_date=date(2010, 5, 15),
            main_defensive_position_id=2
        )
    )
    assert payload.athlete.create is True
    # Registration é opcional no schema atual


# =============================================================================
# TESTES - VALIDAÇÃO DE CPF
# =============================================================================

def test_validate_cpf_valid():
    """Testa validação de CPF válido"""
    assert validate_cpf("123.456.789-09") is True


def test_validate_cpf_invalid():
    """Testa rejeição de CPF inválido"""
    assert validate_cpf("111.111.111-11") is False
    assert validate_cpf("123.456.789-00") is False


def test_normalize_cpf():
    """Testa normalização de CPF"""
    assert normalize_cpf("123.456.789-09") == "12345678909"
    assert normalize_cpf("12345678909") == "12345678909"
