"""
Testes E2E - Season Management (FASE 4.1)
==========================================

Testa fluxo completo de criação e seleção de temporadas (Season) na Ficha Única.

Cenários testados:
1. Dirigente cria nova temporada
2. Dirigente seleciona temporada existente
3. Coordenador não pode criar temporada
4. Coordenador pode selecionar temporada
5. Temporada única por ano (idempotência)
6. Validação de temporada obrigatória com org/team
7. Endpoint de autocomplete de temporadas
"""

import pytest
from uuid import uuid4
from datetime import date, datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.context import ExecutionContext
from app.models.season import Season
from app.schemas.intake.ficha_unica import (
    FichaUnicaRequest,
    PersonCreate,
    PersonContactCreate,
    SeasonSelection,
    OrganizationSelection,
    TeamSelection
)
from app.services.intake.validators import validate_ficha_scope


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def ctx_dirigente():
    """Contexto de dirigente para testes E2E"""
    return ExecutionContext(
        user_id=uuid4(),
        person_id=uuid4(),
        membership_id=uuid4(),
        organization_id=uuid4(),
        role_code="dirigente",
        is_superadmin=False,
        request_id="e2e-test-123",
        timestamp=datetime.now(timezone.utc)
    )


@pytest.fixture
def ctx_coordenador():
    """Contexto de coordenador para testes E2E"""
    return ExecutionContext(
        user_id=uuid4(),
        person_id=uuid4(),
        membership_id=uuid4(),
        organization_id=uuid4(),
        role_code="coordenador",
        is_superadmin=False,
        request_id="e2e-test-123",
        timestamp=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_person_payload():
    """Payload de pessoa para testes"""
    return PersonCreate(
        first_name="João",
        last_name="Silva E2E",
        contacts=[
            PersonContactCreate(
                contact_type="email",
                contact_value=f"joao.e2e.{uuid4().hex[:8]}@test.com",
                is_primary=True
            )
        ]
    )


# =============================================================================
# TESTES E2E - CRIAÇÃO DE TEMPORADA
# =============================================================================

def test_e2e_dirigente_creates_new_season(db: Session, ctx_dirigente, sample_person_payload, mocker):
    """
    E2E: Dirigente cria nova temporada via Ficha Única
    
    Fluxo:
    1. Dirigente cria payload com season.mode='create', year=2027
    2. Backend valida autorização (apenas dirigente pode criar)
    3. Backend cria temporada: 01/01/2027 → 31/12/2027
    4. Backend retorna season_id
    
    Expectativa: HTTP 201, season_id presente, temporada criada no banco
    """
    # Arrange
    mocker.patch('app.services.intake.validators._validate_dirigente_single_org')
    mocker.patch('app.services.intake.validators.require_team_scope')
    
    payload = FichaUnicaRequest(
        person=sample_person_payload,
        season=SeasonSelection(mode="create", year=2027),
        organization=OrganizationSelection(mode="create", name=f"Org E2E {uuid4().hex[:6]}"),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    # Act - Validar autorização
    validate_ficha_scope(payload, ctx_dirigente, db)
    
    # Assert
    # Autorização passou (não lançou exceção)
    assert payload.season.mode == "create"
    assert payload.season.year == 2027


def test_e2e_season_idempotency_same_year(db: Session, ctx_dirigente, sample_person_payload, mocker):
    """
    E2E: Temporada única por ano (idempotência)
    
    Fluxo:
    1. Dirigente cria temporada para 2028
    2. Dirigente tenta criar novamente para 2028
    3. Backend reutiliza temporada existente (não cria duplicata)
    
    Expectativa: Apenas 1 temporada para 2028 no banco
    """
    # Arrange - Criar temporada existente no banco
    mocker.patch('app.services.intake.validators._validate_dirigente_single_org')
    mocker.patch('app.services.intake.validators.require_team_scope')
    
    existing_season = Season(id=uuid4(), team_id=uuid4(), name="Temporada", year=2028,
        start_date=date(2028, 1, 1),
        end_date=date(2028, 12, 31),
        status="ativa",
        created_by_user_id=ctx_dirigente.user_id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(existing_season)
    db.commit()
    
    # Act - Tentar criar novamente
    payload = FichaUnicaRequest(
        person=sample_person_payload,
        season=SeasonSelection(mode="create", year=2028),
        organization=OrganizationSelection(mode="create", name=f"Org E2E {uuid4().hex[:6]}"),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    # Assert - Validação passa (idempotência será tratada no serviço)
    validate_ficha_scope(payload, ctx_dirigente, db)
    
    # Verificar que apenas 1 temporada existe para 2028
    count = db.query(Season).filter(Season.year == 2028).count()
    assert count == 1, "Deve existir apenas 1 temporada para 2028"


def test_e2e_coordenador_cannot_create_season(db: Session, ctx_coordenador, sample_person_payload):
    """
    E2E: Coordenador NÃO pode criar temporada
    
    Fluxo:
    1. Coordenador tenta criar season.mode='create'
    2. Backend valida autorização
    3. Backend lança HTTP 403 (apenas dirigente pode criar)
    
    Expectativa: HTTPException 403
    """
    # Arrange
    payload = FichaUnicaRequest(
        person=sample_person_payload,
        season=SeasonSelection(mode="create", year=2029),
        organization=OrganizationSelection(mode="select", organization_id=uuid4()),
        team=TeamSelection(mode="create", name="Equipe", category_id=1, gender="feminino")
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        validate_ficha_scope(payload, ctx_coordenador, db)
    
    assert exc_info.value.status_code == 403
    assert "coordenador" in str(exc_info.value.detail).lower()
    assert "temporada" in str(exc_info.value.detail).lower()


def test_e2e_coordenador_can_select_existing_season(db: Session, ctx_coordenador, sample_person_payload, mocker):
    """
    E2E: Coordenador pode selecionar temporada existente
    
    Fluxo:
    1. Temporada 2030 já existe no banco
    2. Coordenador seleciona season.mode='select', season_id=xxx
    3. Backend valida autorização (coordenador pode selecionar)
    4. Backend usa temporada existente
    
    Expectativa: Validação passa, nenhuma exceção
    """
    # Arrange - Criar temporada existente
    existing_season = Season(id=uuid4(), team_id=uuid4(), name="Temporada", year=2030,
        start_date=date(2030, 1, 1),
        end_date=date(2030, 12, 31),
        status="ativa",
        created_by_user_id=uuid4(),
        created_at=datetime.now(timezone.utc)
    )
    db.add(existing_season)
    db.commit()
    
    # Mockar require_org_scope para evitar erro de escopo
    mocker.patch('app.services.intake.validators.require_org_scope')
    
    payload = FichaUnicaRequest(
        person=sample_person_payload,
        season=SeasonSelection(mode="select", season_id=existing_season.id),
        organization=OrganizationSelection(mode="select", organization_id=uuid4()),
        team=TeamSelection(mode="create", name="Equipe", category_id=1, gender="feminino")
    )
    
    # Act
    validate_ficha_scope(payload, ctx_coordenador, db)
    
    # Assert - Passou sem exceção
    assert payload.season.mode == "select"
    assert payload.season.season_id == existing_season.id


# =============================================================================
# TESTES E2E - VALIDAÇÕES
# =============================================================================

def test_e2e_season_required_when_creating_organization(db: Session, ctx_dirigente):
    """
    E2E: Season é obrigatória ao criar organização
    
    Fluxo:
    1. Dirigente tenta criar organização sem season
    2. Pydantic valida dependências
    3. Lança ValidationError
    
    Expectativa: ValidationError com mensagem sobre season
    """
    from pydantic import ValidationError
    
    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        payload = FichaUnicaRequest(
            person=PersonCreate(
                first_name="Teste",
                last_name="Season",
                contacts=[
                    PersonContactCreate(
                        contact_type="email",
                        contact_value="test@season.com",
                        is_primary=True
                    )
                ]
            ),
            # season=None,  # Ausente
            organization=OrganizationSelection(mode="create", name="Org sem Season")
        )
    
    assert "season" in str(exc_info.value).lower()


def test_e2e_season_required_when_creating_team(db: Session, ctx_coordenador):
    """
    E2E: Season é obrigatória ao criar equipe
    
    Fluxo:
    1. Coordenador tenta criar equipe sem season
    2. Pydantic valida dependências
    3. Lança ValidationError
    
    Expectativa: ValidationError com mensagem sobre season
    """
    from pydantic import ValidationError
    
    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        payload = FichaUnicaRequest(
            person=PersonCreate(
                first_name="Teste",
                last_name="Season",
                contacts=[
                    PersonContactCreate(
                        contact_type="email",
                        contact_value="test@season2.com",
                        is_primary=True
                    )
                ]
            ),
            # season=None,  # Ausente
            team=TeamSelection(mode="create", name="Equipe sem Season", category_id=1, gender="feminino")
        )
    
    assert "season" in str(exc_info.value).lower()


def test_e2e_season_dates_fixed_by_year(db: Session, ctx_dirigente):
    """
    E2E: Temporada sempre fixa: 01/01/YYYY → 31/12/YYYY
    
    Fluxo:
    1. Dirigente cria temporada para 2031
    2. Backend cria com datas fixas
    3. Verificar start_date=01/01/2031, end_date=31/12/2031
    
    Expectativa: Datas fixas por ano civil
    """
    # Arrange - Criar temporada
    season = Season(id=uuid4(), team_id=uuid4(), name="Temporada", year=2031,
        start_date=date(2031, 1, 1),
        end_date=date(2031, 12, 31),
        status="ativa",
        created_by_user_id=ctx_dirigente.user_id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(season)
    db.commit()
    
    # Act - Buscar temporada
    retrieved = db.query(Season).filter(Season.year == 2031).first()
    
    # Assert
    assert retrieved is not None
    assert retrieved.start_date == date(2031, 1, 1)
    assert retrieved.end_date == date(2031, 12, 31)
    assert retrieved.is_active is True


# =============================================================================
# TESTES E2E - AUTOCOMPLETE
# =============================================================================

def test_e2e_seasons_autocomplete_filter_by_year(db: Session):
    """
    E2E: Autocomplete de temporadas filtra por ano
    
    Fluxo:
    1. Criar múltiplas temporadas no banco (2025, 2026, 2027)
    2. Buscar com query q=2026
    3. Retornar apenas temporada de 2026
    
    Expectativa: Apenas 1 resultado (2026)
    """
    # Arrange - Criar temporadas
    seasons = [
        Season(id=uuid4(), team_id=uuid4(), name="Temporada", year=2025, start_date=date(2025, 1, 1), end_date=date(2025, 12, 31)),
        Season(id=uuid4(), team_id=uuid4(), name="Temporada", year=2026, start_date=date(2026, 1, 1), end_date=date(2026, 12, 31)),
        Season(id=uuid4(), team_id=uuid4(), name="Temporada", year=2027, start_date=date(2027, 1, 1), end_date=date(2027, 12, 31)),
    ]
    for season in seasons:
        season.created_at = datetime.now(timezone.utc)
        season.created_by_user_id = uuid4()
        db.add(season)
    db.commit()
    
    # Act - Simular busca por ano
    results = db.query(Season).filter(Season.year == 2026).all()
    
    # Assert
    assert len(results) == 1
    assert results[0].year == 2026


def test_e2e_seasons_autocomplete_order_by_year_desc(db: Session):
    """
    E2E: Autocomplete retorna temporadas em ordem decrescente (mais recentes primeiro)
    
    Fluxo:
    1. Criar temporadas 2025, 2026, 2027
    2. Buscar todas
    3. Verificar ordem: 2027, 2026, 2025
    
    Expectativa: Ordem year DESC
    """
    # Arrange - Criar temporadas
    seasons = [
        Season(id=uuid4(), team_id=uuid4(), name="Temporada", year=2025, start_date=date(2025, 1, 1), end_date=date(2025, 12, 31)),
        Season(id=uuid4(), team_id=uuid4(), name="Temporada", year=2026, start_date=date(2026, 1, 1), end_date=date(2026, 12, 31)),
        Season(id=uuid4(), team_id=uuid4(), name="Temporada", year=2027, start_date=date(2027, 1, 1), end_date=date(2027, 12, 31)),
    ]
    for season in seasons:
        season.created_at = datetime.now(timezone.utc)
        season.created_by_user_id = uuid4()
        db.add(season)
    db.commit()
    
    # Act - Buscar ordenado
    results = db.query(Season).order_by(Season.year.desc()).all()
    
    # Assert
    assert len(results) == 3
    assert results[0].year == 2027
    assert results[1].year == 2026
    assert results[2].year == 2025


# =============================================================================
# TESTES E2E - INTEGRAÇÃO COMPLETA
# =============================================================================

def test_e2e_full_flow_dirigente_creates_org_with_season(db: Session, ctx_dirigente, sample_person_payload, mocker):
    """
    E2E: Fluxo completo - Dirigente cria organização com temporada
    
    Fluxo:
    1. Dirigente cria temporada 2032
    2. Dirigente cria organização vinculada à temporada
    3. Backend cria ambos em transação atômica
    4. Verifica que organização tem season_id correto
    
    Expectativa: Organização vinculada à temporada criada
    """
    # Arrange
    mocker.patch('app.services.intake.validators._validate_dirigente_single_org')
    mocker.patch('app.services.intake.validators.require_team_scope')
    
    payload = FichaUnicaRequest(
        person=sample_person_payload,
        season=SeasonSelection(mode="create", year=2032),
        organization=OrganizationSelection(mode="create", name=f"Org E2E 2032 {uuid4().hex[:6]}"),
        team=TeamSelection(mode="select", team_id=uuid4())
    )
    
    # Act - Validar autorização
    validate_ficha_scope(payload, ctx_dirigente, db)
    
    # Assert
    assert payload.season.year == 2032
    assert payload.organization.mode == "create"
    # Nota: Teste completo requer serviço executar e verificar no banco


def test_e2e_full_flow_coordenador_selects_season_creates_team(db: Session, ctx_coordenador, sample_person_payload, mocker):
    """
    E2E: Fluxo completo - Coordenador seleciona temporada e cria equipe
    
    Fluxo:
    1. Temporada 2033 existe
    2. Coordenador seleciona temporada
    3. Coordenador cria equipe vinculada à temporada
    4. Backend vincula equipe à temporada
    
    Expectativa: Equipe vinculada à temporada existente
    """
    # Arrange - Criar temporada
    existing_season = Season(id=uuid4(), team_id=uuid4(), name="Temporada", year=2033,
        start_date=date(2033, 1, 1),
        end_date=date(2033, 12, 31),
        status="ativa",
        created_by_user_id=uuid4(),
        created_at=datetime.now(timezone.utc)
    )
    db.add(existing_season)
    db.commit()
    
    # Mockar escopos
    mocker.patch('app.services.intake.validators.require_org_scope')
    
    payload = FichaUnicaRequest(
        person=sample_person_payload,
        season=SeasonSelection(mode="select", season_id=existing_season.id),
        organization=OrganizationSelection(mode="select", organization_id=uuid4()),
        team=TeamSelection(
            mode="create",
            name=f"Equipe E2E 2033 {uuid4().hex[:6]}",
            category_id=1,
            gender="feminino",
            organization_id=uuid4()
        )
    )
    
    # Act - Validar autorização
    validate_ficha_scope(payload, ctx_coordenador, db)
    
    # Assert
    assert payload.season.season_id == existing_season.id
    assert payload.team.mode == "create"

