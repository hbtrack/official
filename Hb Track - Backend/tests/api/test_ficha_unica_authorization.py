"""
Testes de Autorização - Ficha Única
===================================
FASE 4 - FICHA.MD Seção 4.1

Valida matriz de autorização para criação via Ficha Única:

+-------------+----------------+---------------+-----------------+
| Papel       | Criar Org      | Criar Equipe  | Vincular Atleta |
+-------------+----------------+---------------+-----------------+
| superadmin  | ✅ Sim         | ✅ Sim        | ✅ Sim          |
| dirigente   | ✅ Sim         | ✅ Sim        | ✅ Sim          |
| coordenador | ❌ Não         | ✅ Sim        | ✅ Sim          |
| treinador   | ❌ Não         | ❌ Não        | ✅ Sim          |
+-------------+----------------+---------------+-----------------+

Testes validam:
- R25: Papéis e permissões
- R34: Escopo organizacional
- validate_ficha_scope(): Autorização baseada em papel
"""

import pytest
from uuid import uuid4
from fastapi import HTTPException
from app.services.intake.validators import validate_ficha_scope
from app.schemas.intake.ficha_unica import (
    FichaUnicaRequest,
    OrganizationSelection,
    TeamSelection,
    SeasonSelection,
    PersonCreate,
    UserCreate
)
from app.core.context import ExecutionContext


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_db(mocker):
    """Mock de sessão do banco"""
    return mocker.MagicMock()


@pytest.fixture
def ctx_superadmin():
    """Contexto de superadmin"""
    return ExecutionContext(
        user_id=uuid4(),
        email="superadmin@test.com",
        person_id=uuid4(),
        membership_id=None,
        organization_id=uuid4(),
        role_code="admin",
        is_superadmin=True
    )


@pytest.fixture
def ctx_dirigente():
    """Contexto de dirigente"""
    return ExecutionContext(
        user_id=uuid4(),
        email="dirigente@test.com",
        person_id=uuid4(),
        membership_id=uuid4(),
        organization_id=uuid4(),
        role_code="dirigente",
        is_superadmin=False
    )


@pytest.fixture
def ctx_coordenador():
    """Contexto de coordenador"""
    return ExecutionContext(
        user_id=uuid4(),
        email="coordenador@test.com",
        person_id=uuid4(),
        membership_id=uuid4(),
        organization_id=uuid4(),
        role_code="coordenador",
        is_superadmin=False
    )


@pytest.fixture
def ctx_treinador():
    """Contexto de treinador"""
    return ExecutionContext(
        user_id=uuid4(),
        email="treinador@test.com",
        person_id=uuid4(),
        membership_id=uuid4(),
        organization_id=uuid4(),
        role_code="treinador",
        is_superadmin=False
    )


# =============================================================================
# TESTES: SUPERADMIN (BYPASS COMPLETO)
# =============================================================================

def test_superadmin_can_create_organization(ctx_superadmin, mock_db):
    """Superadmin pode criar organização"""
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="create", year=2026),
        organization=OrganizationSelection(mode="create", name="Nova Org"),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    # Não deve lançar exceção
    validate_ficha_scope(payload, ctx_superadmin, mock_db)


def test_superadmin_can_create_team(ctx_superadmin, mock_db):
    """Superadmin pode criar equipe"""
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="select", organization_id=uuid4()),
        team=TeamSelection(mode="create", name="Nova Equipe", category_id=1, gender="feminino")
    )
    
    # Não deve lançar exceção
    validate_ficha_scope(payload, ctx_superadmin, mock_db)


# =============================================================================
# TESTES: DIRIGENTE (ACESSO COMPLETO)
# =============================================================================

def test_dirigente_can_create_organization(ctx_dirigente, mock_db, mocker):
    """Dirigente pode criar organização"""
    # Mockar a validação de org única para evitar query no banco
    mocker.patch('app.services.intake.validators._validate_dirigente_single_org')
    mocker.patch('app.services.intake.validators.require_team_scope')
    
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="create", year=2026),
        organization=OrganizationSelection(mode="create", name="Nova Org"),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    validate_ficha_scope(payload, ctx_dirigente, mock_db)


def test_dirigente_can_create_team(ctx_dirigente, mock_db, mocker):
    """Dirigente pode criar equipe"""
    # Mock require_org_scope (sem exceção)
    mocker.patch('app.services.intake.validators.require_org_scope')
    
    org_id = uuid4()
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="select", organization_id=org_id),
        team=TeamSelection(
            mode="create",
            name="Nova Equipe",
            category_id=1,
            gender="feminino",
            organization_id=org_id
        )
    )
    
    validate_ficha_scope(payload, ctx_dirigente, mock_db)


# =============================================================================
# TESTES: COORDENADOR (NÃO PODE CRIAR ORG)
# =============================================================================

def test_coordenador_cannot_create_organization(ctx_coordenador, mock_db):
    """Coordenador NÃO pode criar organização"""
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="create", name="Nova Org"),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    with pytest.raises(HTTPException) as exc_info:
        validate_ficha_scope(payload, ctx_coordenador, mock_db)
    
    assert exc_info.value.status_code == 403
    assert "coordenador" in str(exc_info.value.detail).lower()


def test_coordenador_can_create_team(ctx_coordenador, mock_db, mocker):
    """Coordenador pode criar equipe"""
    mocker.patch('app.services.intake.validators.require_org_scope')
    
    org_id = uuid4()
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="select", organization_id=org_id),
        team=TeamSelection(
            mode="create",
            name="Nova Equipe",
            category_id=1,
            gender="feminino",
            organization_id=org_id
        )
    )
    
    validate_ficha_scope(payload, ctx_coordenador, mock_db)


def test_coordenador_can_select_existing_organization(ctx_coordenador, mock_db, mocker):
    """Coordenador pode selecionar organização existente (com validação de escopo)"""
    mocker.patch('app.services.intake.validators.require_org_scope')
    mocker.patch('app.services.intake.validators.require_team_scope')
    
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="select", organization_id=uuid4()),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    validate_ficha_scope(payload, ctx_coordenador, mock_db)


# =============================================================================
# TESTES: TREINADOR (APENAS VINCULAR ATLETA)
# =============================================================================

def test_treinador_cannot_create_organization(ctx_treinador, mock_db):
    """Treinador NÃO pode criar organização"""
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="create", name="Nova Org"),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    with pytest.raises(HTTPException) as exc_info:
        validate_ficha_scope(payload, ctx_treinador, mock_db)
    
    assert exc_info.value.status_code == 403


def test_treinador_cannot_create_team(ctx_treinador, mock_db, mocker):
    """Treinador NÃO pode criar equipe"""
    mocker.patch('app.services.intake.validators.require_org_scope')
    
    org_id = uuid4()
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="select", organization_id=org_id),
        team=TeamSelection(
            mode="create",
            name="Nova Equipe",
            category_id=1,
            gender="feminino",
            organization_id=org_id
        )
    )
    
    with pytest.raises(HTTPException) as exc_info:
        validate_ficha_scope(payload, ctx_treinador, mock_db)
    
    assert exc_info.value.status_code == 403
    assert "treinador" in str(exc_info.value.detail).lower()


def test_treinador_can_register_athlete_in_existing_team(ctx_treinador, mock_db, mocker):
    """Treinador pode vincular atleta em equipe existente"""
    mocker.patch('app.services.intake.validators.require_org_scope')
    mocker.patch('app.services.intake.validators.require_team_scope')
    
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="select", organization_id=uuid4()),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    validate_ficha_scope(payload, ctx_treinador, mock_db)


# =============================================================================
# TESTES: VALIDAÇÃO DE DADOS
# =============================================================================

def test_organization_select_requires_organization_id(ctx_dirigente, mock_db):
    """organization.mode='select' requer organization_id"""
    from pydantic import ValidationError
    
    # Pydantic valida antes de chamar validate_ficha_scope
    with pytest.raises(ValidationError) as exc_info:
        payload = FichaUnicaRequest(
            person=PersonCreate(first_name="João", last_name="Silva"),
            season=SeasonSelection(mode="select", season_id=uuid4()),
            organization=OrganizationSelection(mode="select", organization_id=None),
            team=TeamSelection(mode="select", team_id=uuid4())
        )
    
    assert "organization_id" in str(exc_info.value).lower()


def test_team_select_requires_team_id(ctx_dirigente, mock_db, mocker):
    """team.mode='select' requer team_id"""
    from pydantic import ValidationError
    
    # Pydantic valida antes de chamar validate_ficha_scope
    with pytest.raises(ValidationError) as exc_info:
        payload = FichaUnicaRequest(
            person=PersonCreate(first_name="João", last_name="Silva"),
            season=SeasonSelection(mode="select", season_id=uuid4()),
            organization=OrganizationSelection(mode="select", organization_id=uuid4()),
            team=TeamSelection(mode="select", team_id=None)
        )
    
    assert "team_id" in str(exc_info.value).lower()


def test_team_create_with_org_select_requires_org_id(ctx_dirigente, mock_db, mocker):
    """team.mode='create' + organization.mode='select' requer team.organization_id"""
    mocker.patch('app.services.intake.validators.require_org_scope')
    
    org_id = uuid4()
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="select", organization_id=org_id),
        team=TeamSelection(mode="create", name="Nova Equipe", category_id=1, gender="feminino", organization_id=None)
    )
    
    with pytest.raises(HTTPException) as exc_info:
        validate_ficha_scope(payload, ctx_dirigente, mock_db)
    
    assert exc_info.value.status_code == 400
    assert "team.organization_id" in str(exc_info.value.detail).lower()


# =============================================================================
# TESTES: ESCOPO ORGANIZACIONAL
# =============================================================================

def test_validate_org_scope_called_when_selecting_organization(ctx_coordenador, mock_db, mocker):
    """Valida que require_org_scope é chamado ao selecionar organização"""
    mock_require_org = mocker.patch('app.services.intake.validators.require_org_scope')
    mocker.patch('app.services.intake.validators.require_team_scope')
    
    org_id = uuid4()
    team_id = uuid4()
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="select", organization_id=org_id),
        team=TeamSelection(mode="select", team_id=team_id)
    )
    
    validate_ficha_scope(payload, ctx_coordenador, mock_db)
    
    # Verifica que require_org_scope foi chamado
    mock_require_org.assert_called_once_with(org_id, ctx_coordenador)


def test_validate_team_scope_called_when_selecting_team(ctx_treinador, mock_db, mocker):
    """Valida que require_team_scope é chamado ao selecionar equipe"""
    mocker.patch('app.services.intake.validators.require_org_scope')
    mock_require_team = mocker.patch('app.services.intake.validators.require_team_scope')
    
    team_id = uuid4()
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="select", organization_id=uuid4()),
        team=TeamSelection(mode="select", team_id=team_id)
    )
    
    validate_ficha_scope(payload, ctx_treinador, mock_db)
    
    # Verifica que require_team_scope foi chamado
    mock_require_team.assert_called_once_with(team_id, ctx_treinador, mock_db)

# =============================================================================
# TESTES: VALIDAÇÃO DE ROLE_ID (CRIAÇÃO DE USUÁRIOS)
# =============================================================================

def test_superadmin_can_create_dirigente_user(ctx_superadmin, mock_db):
    """Superadmin pode criar usuário com papel dirigente"""
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        create_user=True,
        user=UserCreate(email="dirigente@test.com", role_id=1),  # 1 = dirigente
        season=SeasonSelection(mode="create", year=2026),
        organization=OrganizationSelection(mode="create", name="Nova Org"),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    # Não deve lançar exceção
    validate_ficha_scope(payload, ctx_superadmin, mock_db)


def test_dirigente_cannot_create_dirigente_user(ctx_dirigente, mock_db, mocker):
    """Dirigente NÃO pode criar outro dirigente"""
    mocker.patch('app.services.intake.validators._validate_dirigente_single_org')
    
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        create_user=True,
        user=UserCreate(email="outro@test.com", role_id=1),  # 1 = dirigente
        season=SeasonSelection(mode="create", year=2026),
        organization=OrganizationSelection(mode="create", name="Nova Org"),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    with pytest.raises(HTTPException) as exc_info:
        validate_ficha_scope(payload, ctx_dirigente, mock_db)
    
    assert exc_info.value.status_code == 403
    assert "dirigente" in str(exc_info.value.detail).lower()
    assert "superadmin" in str(exc_info.value.detail).lower()


def test_dirigente_can_create_coordenador_user(ctx_dirigente, mock_db, mocker):
    """Dirigente pode criar coordenador"""
    mocker.patch('app.services.intake.validators._validate_dirigente_single_org')
    mocker.patch('app.services.intake.validators.require_team_scope')
    
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        create_user=True,
        user=UserCreate(email="coord@test.com", role_id=2),  # 2 = coordenador
        season=SeasonSelection(mode="create", year=2026),
        organization=OrganizationSelection(mode="create", name="Nova Org"),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    # Não deve lançar exceção
    validate_ficha_scope(payload, ctx_dirigente, mock_db)


def test_coordenador_cannot_create_dirigente_user(ctx_coordenador, mock_db):
    """Coordenador NÃO pode criar dirigente"""
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        create_user=True,
        user=UserCreate(email="dirigente@test.com", role_id=1),
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="select", organization_id=uuid4()),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    with pytest.raises(HTTPException) as exc_info:
        validate_ficha_scope(payload, ctx_coordenador, mock_db)
    
    assert exc_info.value.status_code == 403


def test_coordenador_cannot_create_coordenador_user(ctx_coordenador, mock_db):
    """Coordenador NÃO pode criar outro coordenador"""
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        create_user=True,
        user=UserCreate(email="coord@test.com", role_id=2),
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="select", organization_id=uuid4()),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    with pytest.raises(HTTPException) as exc_info:
        validate_ficha_scope(payload, ctx_coordenador, mock_db)
    
    assert exc_info.value.status_code == 403


def test_coordenador_can_create_treinador_user(ctx_coordenador, mock_db, mocker):
    """Coordenador pode criar treinador"""
    mocker.patch('app.services.intake.validators.require_org_scope')
    mocker.patch('app.services.intake.validators.require_team_scope')
    
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        create_user=True,
        user=UserCreate(email="trei@test.com", role_id=3),  # 3 = treinador
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="select", organization_id=uuid4()),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    # Não deve lançar exceção
    validate_ficha_scope(payload, ctx_coordenador, mock_db)


def test_treinador_cannot_create_treinador_user(ctx_treinador, mock_db, mocker):
    """Treinador NÃO pode criar outro treinador"""
    mocker.patch('app.services.intake.validators.require_team_scope')
    
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        create_user=True,
        user=UserCreate(email="trei@test.com", role_id=3),
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="select", organization_id=uuid4()),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    with pytest.raises(HTTPException) as exc_info:
        validate_ficha_scope(payload, ctx_treinador, mock_db)
    
    assert exc_info.value.status_code == 403


def test_treinador_can_create_atleta_user(ctx_treinador, mock_db, mocker):
    """Treinador pode criar atleta"""
    mocker.patch('app.services.intake.validators.require_org_scope')
    mocker.patch('app.services.intake.validators.require_team_scope')
    
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        create_user=True,
        user=UserCreate(email="atl@test.com", role_id=4),  # 4 = atleta
        season=SeasonSelection(mode="select", season_id=uuid4()),
        organization=OrganizationSelection(mode="select", organization_id=uuid4()),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    # Não deve lançar exceção
    validate_ficha_scope(payload, ctx_treinador, mock_db)


# =============================================================================
# TESTES: DIRIGENTE - ORGANIZAÇÃO ÚNICA
# =============================================================================

def test_dirigente_can_create_first_organization(ctx_dirigente, mock_db, mocker):
    """Dirigente pode criar sua primeira organização"""
    # Mockar a validação de org única para evitar query no banco
    mocker.patch('app.services.intake.validators._validate_dirigente_single_org')
    mocker.patch('app.services.intake.validators.require_team_scope')
    
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="create", year=2026),
        organization=OrganizationSelection(mode="create", name="Primeira Org"),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    # Não deve lançar exceção
    validate_ficha_scope(payload, ctx_dirigente, mock_db)


def test_dirigente_cannot_create_second_organization(ctx_dirigente, mock_db, mocker):
    """Dirigente NÃO pode criar segunda organização"""
    # Mockar para lançar exceção (já tem 1 org criada)
    def mock_validate_single_org(ctx, db):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "FORBIDDEN",
                "message": "Dirigente já criou uma organização. Apenas 1 organização permitida por dirigente.",
                "constraint": "Dirigente - Organização única"
            }
        )
    
    mocker.patch('app.services.intake.validators._validate_dirigente_single_org', side_effect=mock_validate_single_org)
    mocker.patch('app.services.intake.validators.require_team_scope')
    
    payload = FichaUnicaRequest(
        person=PersonCreate(first_name="João", last_name="Silva"),
        season=SeasonSelection(mode="create", year=2026),
        organization=OrganizationSelection(mode="create", name="Segunda Org"),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    with pytest.raises(HTTPException) as exc_info:
        validate_ficha_scope(payload, ctx_dirigente, mock_db)
    
    assert exc_info.value.status_code == 403
    assert "já criou" in str(exc_info.value.detail).lower()
    assert "organização" in str(exc_info.value.detail).lower()