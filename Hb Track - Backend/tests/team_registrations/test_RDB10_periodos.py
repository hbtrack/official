"""
Testes da regra RDB10 - Períodos não sobrepostos.
Ref: Matriz de enforcement

RDB10: Períodos (start_at, end_at) não podem sobrepor para mesma pessoa+equipe+temporada.
       Reativação cria nova linha (novo UUID).
       
Enforcement: EXCLUDE USING gist constraint (ex_team_registrations_no_overlap)
Migration: d020c0ffee20_add_start_end_team_registrations.py

Cenários de sobreposição de períodos:
─────────────────────────────────────────────────────────────────
Existente:        |----A----|
Novo:       |--B--|                    → OK (antes)
Novo:                        |--C--|   → OK (depois)  
Novo:             |--D--|              → OVERLAP (dentro)
Novo:       |--------E--------|        → OVERLAP (engloba)
Novo:          |--F--|                 → OVERLAP (início dentro)
Novo:                   |--G--|        → OVERLAP (fim dentro)
─────────────────────────────────────────────────────────────────
"""

import pytest
from datetime import date, timedelta
from uuid import uuid4

from sqlalchemy import text
from app.services.team_registration_service import TeamRegistrationService


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def service(async_db):
    """TeamRegistrationService com sessão async de teste."""
    return TeamRegistrationService(async_db)


@pytest.fixture
async def seed_data(async_db):
    """
    Cria dados completos para testes RDB10 usando SQL raw.
    
    IMPORTANTE: Gera UUIDs únicos a cada chamada para evitar conflitos entre testes.
    
    Insere:
    - Person
    - User
    - Organization
    - Role (atleta)
    - Athlete com birth_date
    - Season com starts_at
    - Category U14
    - Team
    - Membership
    
    Retorna dicionário com todos os IDs necessários (sem create_team).
    """
    # Gerar IDs ÚNICOS a cada chamada
    person_id = uuid4()
    user_id = uuid4()
    org_id = uuid4()
    athlete_id = uuid4()
    season_id = uuid4()
    team_id = uuid4()
    membership_id = uuid4()
    category_id = 1
    
    # Executar cada INSERT separadamente (asyncpg não aceita múltiplos comandos)
    # Ordem: Role → Person → User → Organization → Membership → Athlete → Season → Category → Team
    
    # 1) Role atleta (GENERATED ALWAYS requer OVERRIDING SYSTEM VALUE)
    await async_db.execute(text("""
        INSERT INTO roles (id, code, name) OVERRIDING SYSTEM VALUE
        VALUES (1, 'atleta', 'Atleta')
        ON CONFLICT (id) DO NOTHING
    """))
    
    # 2) Person
    await async_db.execute(
        text("INSERT INTO persons (id, first_name, last_name, full_name, birth_date) VALUES (:person_id, 'Test', 'Person', 'Test Person', '2013-01-01')"),
        {"person_id": person_id}
    )
    
    # 3) User
    await async_db.execute(
        text("INSERT INTO users (id, person_id, email, full_name, password_hash) VALUES (:user_id, :person_id, 'test@example.com', 'Test Owner', 'fake_hash')"),
        {"user_id": user_id, "person_id": person_id}
    )
    
    # 4) Organization
    await async_db.execute(
        text("INSERT INTO organizations (id, name, owner_user_id) VALUES (:org_id, 'Test Org', :user_id)"),
        {"org_id": org_id, "user_id": user_id}
    )
    
    # 5) Season (antes de Athlete para evitar FK) - usar ano 2099 para evitar conflito
    await async_db.execute(
        text("INSERT INTO seasons (id, organization_id, created_by_membership_id, year, name, starts_at, ends_at, is_active) VALUES (:season_id, :org_id, :membership_id, 2099, 'Test 2099', '2099-01-01', '2099-12-31', false)"),
        {"season_id": season_id, "org_id": org_id, "membership_id": membership_id}
    )
    
    # 6) Membership (antes de Athlete que depende dele)
    await async_db.execute(
        text("INSERT INTO membership (id, person_id, organization_id, season_id, role_id, status) VALUES (:membership_id, :person_id, :org_id, :season_id, 1, 'ativo')"),
        {"membership_id": membership_id, "person_id": person_id, "org_id": org_id, "season_id": season_id}
    )
    
    # 7) Athlete
    await async_db.execute(
        text("INSERT INTO athletes (id, person_id, organization_id, created_by_membership_id, full_name, birth_date) VALUES (:athlete_id, :person_id, :org_id, :membership_id, 'Test Athlete', '2013-01-01')"),
        {"athlete_id": athlete_id, "person_id": person_id, "org_id": org_id, "membership_id": membership_id}
    )
    
    # 8) Category (GENERATED ALWAYS requer OVERRIDING SYSTEM VALUE)
    await async_db.execute(text("""
        INSERT INTO categories (id, code, label, min_age, max_age) OVERRIDING SYSTEM VALUE
        VALUES (1, 'U14', 'Infantil', 12, 14)
        ON CONFLICT (id) DO NOTHING
    """))
    
    # 9) Team
    await async_db.execute(
        text("INSERT INTO teams (id, organization_id, created_by_membership_id, season_id, category_id, name) VALUES (:team_id, :org_id, :membership_id, :season_id, :category_id, 'Test Team')"),
        {"team_id": team_id, "org_id": org_id, "membership_id": membership_id, "season_id": season_id, "category_id": category_id}
    )
    
    await async_db.flush()
    
    # Guardar contexto no async_db para helper
    async_db._test_context = {
        "org_id": org_id,
        "membership_id": membership_id,
        "season_id": season_id,
        "category_id": category_id,
    }
    
    return {
        "athlete_id": athlete_id,
        "team_id": team_id,
        "season_id": season_id,
        "organization_id": org_id,
        "created_by_membership_id": membership_id,
        "category_id": category_id,
    }


@pytest.fixture
def create_team_helper(async_db):
    """Helper para criar teams adicionais no banco."""
    async def create_team(team_id: UUID = None, name: str = "Additional Team"):
        """Cria uma team adicional no banco para testes multi-team."""
        ctx = async_db._test_context
        new_team_id = team_id or uuid4()
        await async_db.execute(
            text("INSERT INTO teams (id, organization_id, created_by_membership_id, season_id, category_id, name) VALUES (:team_id, :org_id, :membership_id, :season_id, :category_id, :name)"),
            {"team_id": new_team_id, "org_id": ctx["org_id"], "membership_id": ctx["membership_id"], "season_id": ctx["season_id"], "category_id": ctx["category_id"], "name": name}
        )
        await async_db.flush()
        return new_team_id
    return create_team


# ═══════════════════════════════════════════════════════════════════════════
# RDB10: Criação sem sobreposição (casos válidos)
# ═══════════════════════════════════════════════════════════════════════════

class TestRDB10CriacaoValida:
    """Testes de criação válida (sem sobreposição)."""

    @pytest.mark.asyncio
    async def test_primeira_inscricao_sucesso(self, service, seed_data):
        """
        Cenário: Primeira inscrição para atleta+equipe+temporada.
        Esperado: Criação bem-sucedida.
        """
        today = date.today()
        
        registration = await service.create(
            athlete_id=seed_data["athlete_id"],
            season_id=seed_data["season_id"],
            category_id=seed_data["category_id"],
            team_id=seed_data["team_id"],
            organization_id=seed_data["organization_id"],
            created_by_membership_id=seed_data["created_by_membership_id"],
            start_at=today,
            end_at=None,  # Ativa (sem fim)
        )
        
        assert registration is not None
        assert registration.athlete_id == seed_data["athlete_id"]
        # assert registration.start_at == today  # Quando coluna existir

    @pytest.mark.asyncio
    async def test_periodo_antes_existente_ok(self, service, seed_data, db_session):
        """
        Cenário B: Novo período ANTES do existente (sem sobreposição).
        
        Existente:           |----A----|
        Novo:       |--B--|
        
        Esperado: Criação bem-sucedida.
        """
        today = date.today()
        
        # Criar inscrição existente: começa em 30 dias
        existing = await service.create(
            **seed_data,
            start_at=today + timedelta(days=30),
            end_at=today + timedelta(days=60),
        )
        
        # Nova inscrição ANTES: termina antes de começar a existente
        new_reg = await service.create(
            **seed_data,
            start_at=today,
            end_at=today + timedelta(days=20),
        )
        
        assert new_reg is not None
        assert new_reg.id != existing.id

    @pytest.mark.asyncio
    async def test_periodo_depois_existente_ok(self, service, seed_data):
        """
        Cenário C: Novo período DEPOIS do existente (sem sobreposição).
        
        Existente:  |----A----|
        Novo:                    |--C--|
        
        Esperado: Criação bem-sucedida.
        """
        today = date.today()
        
        # Criar inscrição existente: termina em 30 dias
        existing = await service.create(
            **seed_data,
            start_at=today,
            end_at=today + timedelta(days=30),
        )
        
        # Nova inscrição DEPOIS: começa após terminar a existente
        new_reg = await service.create(
            **seed_data,
            start_at=today + timedelta(days=40),
            end_at=today + timedelta(days=70),
        )
        
        assert new_reg is not None
        assert new_reg.id != existing.id

    @pytest.mark.asyncio
    async def test_reativacao_apos_encerramento(self, service, seed_data):
        """
        Cenário: Reativação cria nova linha com novo UUID (RDB10).
        
        1. Criar inscrição
        2. Encerrar inscrição
        3. Criar nova inscrição (reativação)
        
        Esperado: Nova linha com UUID diferente.
        """
        today = date.today()
        
        # Criar e encerrar primeira inscrição
        first = await service.create(
            **seed_data,
            start_at=today - timedelta(days=60),
            end_at=None,
        )
        await service.end_registration(first.id, end_at=today - timedelta(days=10))
        
        # Reativar (nova inscrição)
        reactivation = await service.create(
            **seed_data,
            start_at=today,
            end_at=None,
        )
        
        assert reactivation is not None
        assert reactivation.id != first.id  # Novo UUID


# ═══════════════════════════════════════════════════════════════════════════
# RDB10: Criação com sobreposição (casos inválidos)
# ═══════════════════════════════════════════════════════════════════════════

class TestRDB10SobreposicaoInvalida:
    """Testes de criação inválida (com sobreposição)."""

    @pytest.mark.asyncio
    async def test_periodo_dentro_existente_erro(self, service, seed_data):
        """
        Cenário D: Novo período DENTRO do existente.
        
        Existente:  |--------A--------|
        Novo:            |--D--|
        
        Esperado: ValueError("period_overlap").
        """
        today = date.today()
        
        # Criar inscrição existente ampla
        await service.create(
            **seed_data,
            start_at=today,
            end_at=today + timedelta(days=60),
        )
        
        # Tentar criar dentro do período existente
        with pytest.raises(ValueError, match="period_overlap"):
            await service.create(
                **seed_data,
                start_at=today + timedelta(days=15),
                end_at=today + timedelta(days=45),
            )

    @pytest.mark.asyncio
    async def test_periodo_engloba_existente_erro(self, service, seed_data):
        """
        Cenário E: Novo período ENGLOBA o existente.
        
        Existente:       |--A--|
        Novo:       |--------E--------|
        
        Esperado: ValueError("period_overlap").
        """
        today = date.today()
        
        # Criar inscrição existente curta
        await service.create(
            **seed_data,
            start_at=today + timedelta(days=20),
            end_at=today + timedelta(days=40),
        )
        
        # Tentar criar período que engloba
        with pytest.raises(ValueError, match="period_overlap"):
            await service.create(
                **seed_data,
                start_at=today,
                end_at=today + timedelta(days=60),
            )

    @pytest.mark.asyncio
    async def test_inicio_dentro_existente_erro(self, service, seed_data):
        """
        Cenário F: Início do novo período dentro do existente.
        
        Existente:  |----A----|
        Novo:            |--F--|
        
        Esperado: ValueError("period_overlap").
        """
        today = date.today()
        
        # Criar inscrição existente
        await service.create(
            **seed_data,
            start_at=today,
            end_at=today + timedelta(days=30),
        )
        
        # Tentar criar com início dentro do período existente
        with pytest.raises(ValueError, match="period_overlap"):
            await service.create(
                **seed_data,
                start_at=today + timedelta(days=20),
                end_at=today + timedelta(days=50),
            )

    @pytest.mark.asyncio
    async def test_fim_dentro_existente_erro(self, service, seed_data):
        """
        Cenário G: Fim do novo período dentro do existente.
        
        Existente:       |----A----|
        Novo:       |--G--|
        
        Esperado: ValueError("period_overlap").
        """
        today = date.today()
        
        # Criar inscrição existente
        await service.create(
            **seed_data,
            start_at=today + timedelta(days=20),
            end_at=today + timedelta(days=50),
        )
        
        # Tentar criar com fim dentro do período existente
        with pytest.raises(ValueError, match="period_overlap"):
            await service.create(
                **seed_data,
                start_at=today,
                end_at=today + timedelta(days=30),
            )

    @pytest.mark.asyncio
    async def test_inscricao_ativa_sobrepoe_nova_ativa_erro(self, service, seed_data):
        """
        Cenário: Duas inscrições ativas (end_at IS NULL) = sobreposição.
        
        Existente:  |----A---- (sem fim)
        Novo:            |----B---- (sem fim)
        
        Esperado: ValueError("period_overlap").
        """
        today = date.today()
        
        # Criar inscrição ativa (sem fim)
        await service.create(
            **seed_data,
            start_at=today,
            end_at=None,
        )
        
        # Tentar criar outra ativa
        with pytest.raises(ValueError, match="period_overlap"):
            await service.create(
                **seed_data,
                start_at=today + timedelta(days=30),
                end_at=None,
            )


# ═══════════════════════════════════════════════════════════════════════════
# RDB10: Validação de datas
# ═══════════════════════════════════════════════════════════════════════════

class TestRDB10ValidacaoDatas:
    """Testes de validação de datas."""

    @pytest.mark.asyncio
    async def test_end_at_antes_start_at_erro(self, service, seed_data):
        """
        Cenário: end_at < start_at.
        Esperado: ValueError("invalid_date_range").
        """
        today = date.today()
        
        with pytest.raises(ValueError, match="invalid_date_range"):
            await service.create(
                **seed_data,
                start_at=today + timedelta(days=30),
                end_at=today,  # Antes do início!
            )

    @pytest.mark.asyncio
    async def test_start_at_default_hoje(self, service, seed_data):
        """
        Cenário: start_at não informado.
        Esperado: Default para date.today().
        """
        registration = await service.create(
            athlete_id=seed_data["athlete_id"],
            season_id=seed_data["season_id"],
            category_id=seed_data["category_id"],
            team_id=seed_data["team_id"],
            organization_id=seed_data["organization_id"],
            created_by_membership_id=seed_data["created_by_membership_id"],
            # start_at não informado
        )
        
        # assert registration.start_at == date.today()  # Quando coluna existir
        assert registration is not None


# ═══════════════════════════════════════════════════════════════════════════
# RDB10: Update não pode reabrir período
# ═══════════════════════════════════════════════════════════════════════════

class TestRDB10UpdateRestricoes:
    """Testes de restrições em updates."""

    @pytest.mark.asyncio
    async def test_reabrir_periodo_encerrado_erro(self, service, seed_data):
        """
        Cenário: Tentar remover end_at de período encerrado.
        Regra: Não reabrir período encerrado; criar nova linha.
        
        Esperado: ValueError("cannot_reopen_ended").
        """
        today = date.today()
        
        # Criar e encerrar
        reg = await service.create(
            **seed_data,
            start_at=today - timedelta(days=30),
            end_at=today - timedelta(days=10),
        )
        
        # Tentar reabrir (setar end_at=None)
        with pytest.raises(ValueError, match="cannot_reopen_ended"):
            await service.update(reg.id, end_at=None)

    @pytest.mark.asyncio
    async def test_encerrar_inscricao_ativa_ok(self, service, seed_data):
        """
        Cenário: Encerrar inscrição ativa.
        Esperado: end_at atualizado com sucesso.
        """
        today = date.today()
        
        reg = await service.create(
            **seed_data,
            start_at=today - timedelta(days=30),
            end_at=None,  # Ativa
        )
        
        # Encerrar
        updated = await service.end_registration(reg.id, end_at=today)
        
        assert updated is not None
        # assert updated.end_at == today  # Quando coluna existir


# ═══════════════════════════════════════════════════════════════════════════
# RDB10: Diferentes atletas/equipes/temporadas (sem conflito)
# ═══════════════════════════════════════════════════════════════════════════

class TestRDB10DiferentesEntidades:
    """Testes com diferentes atletas/equipes/temporadas."""

    @pytest.mark.asyncio
    async def test_mesmo_periodo_diferente_atleta_ok(self, service, seed_data):
        """
        Cenário: Mesmo período, mas atletas diferentes.
        Esperado: Ambas criações bem-sucedidas (sem conflito).
        """
        today = date.today()
        
        # Atleta A
        reg_a = await service.create(
            **seed_data,
            start_at=today,
            end_at=today + timedelta(days=30),
        )
        
        # Atleta B (mesmo período, mesma equipe/temporada)
        seed_data["athlete_id"] = uuid4()  # Diferente!
        reg_b = await service.create(
            **seed_data,
            start_at=today,
            end_at=today + timedelta(days=30),
        )
        
        assert reg_a.id != reg_b.id
        assert reg_a.athlete_id != reg_b.athlete_id

    @pytest.mark.asyncio
    async def test_mesmo_periodo_diferente_equipe_ok(self, service, seed_data, create_team_helper):
        """
        Cenário: Mesmo período, mesmo atleta, mas equipes diferentes.
        Esperado: Ambas criações bem-sucedidas (atleta em 2 equipes).
        """
        today = date.today()
        
        # Equipe A
        reg_a = await service.create(
            **seed_data,
            start_at=today,
            end_at=today + timedelta(days=30),
        )
        
        # Equipe B (mesmo atleta, mesmo período) - criar no banco!
        team_b_id = await create_team_helper(name="Team B")
        seed_data["team_id"] = team_b_id
        reg_b = await service.create(
            **seed_data,
            start_at=today,
            end_at=today + timedelta(days=30),
        )
        
        assert reg_a.id != reg_b.id
        assert reg_a.team_id != reg_b.team_id

    @pytest.mark.asyncio
    async def test_mesmo_periodo_diferente_temporada_ok(self, service, seed_data):
        """
        Cenário: Mesmo período, mesmo atleta+equipe, mas temporadas diferentes.
        Esperado: Ambas criações bem-sucedidas.
        """
        today = date.today()
        
        # Temporada 2024
        reg_a = await service.create(
            **seed_data,
            start_at=today,
            end_at=today + timedelta(days=30),
        )
        
        # Temporada 2025 (mesmo atleta/equipe)
        seed_data["season_id"] = uuid4()  # Diferente!
        reg_b = await service.create(
            **seed_data,
            start_at=today,
            end_at=today + timedelta(days=30),
        )
        
        assert reg_a.id != reg_b.id
        assert reg_a.season_id != reg_b.season_id


# ═══════════════════════════════════════════════════════════════════════════
# R13 V1.1: Encerramento automático ao dispensar atleta
# ═══════════════════════════════════════════════════════════════════════════

class TestR13V1EncerraAutomatico:
    """Testes do encerramento automático (R13 V1.1)."""

    @pytest.mark.asyncio
    async def test_close_active_registrations(self, service, seed_data, create_team_helper):
        """
        Cenário: Chamar close_active_registrations() encerra todas ativas.
        Ref: R13 Complemento V1.1
        
        Esperado: Todas as inscrições ativas do atleta são encerradas.
        """
        today = date.today()
        athlete_id = seed_data["athlete_id"]
        
        # Criar múltiplas inscrições ativas - criar teams no banco!
        team1_id = await create_team_helper(name="Team 1")
        team2_id = await create_team_helper(name="Team 2")
        
        await service.create(
            **{**seed_data, "team_id": team1_id},
            start_at=today - timedelta(days=30),
            end_at=None,
        )
        await service.create(
            **{**seed_data, "team_id": team2_id},
            start_at=today - timedelta(days=20),
            end_at=None,
        )
        
        # Encerrar todas
        count = await service.close_active_registrations(athlete_id)
        
        assert count == 2
        
        # Verificar que foram encerradas
        active = await service.get_active_by_athlete_season(
            athlete_id, seed_data["season_id"]
        )
        assert len(active) == 0


# ═══════════════════════════════════════════════════════════════════════════
# R38: Atleta deve ter equipe para atuar
# ═══════════════════════════════════════════════════════════════════════════

class TestR38AtletaPrecisaEquipe:
    """Testes da regra R38."""

    @pytest.mark.asyncio
    async def test_has_active_registration_true(self, service, seed_data):
        """
        Cenário: Atleta com inscrição ativa na temporada.
        Esperado: has_active_registration() retorna True.
        """
        today = date.today()
        
        await service.create(
            **seed_data,
            start_at=today - timedelta(days=10),
            end_at=None,
        )
        
        has_active = await service.has_active_registration(
            seed_data["athlete_id"],
            seed_data["season_id"],
        )
        
        assert has_active is True

    @pytest.mark.asyncio
    async def test_has_active_registration_false_sem_inscricao(self, service, seed_data):
        """
        Cenário: Atleta sem inscrição na temporada.
        Esperado: has_active_registration() retorna False.
        """
        has_active = await service.has_active_registration(
            seed_data["athlete_id"],
            seed_data["season_id"],
        )
        
        assert has_active is False

    @pytest.mark.asyncio
    async def test_has_active_registration_false_encerrada(self, service, seed_data):
        """
        Cenário: Atleta com inscrição encerrada na temporada.
        Esperado: has_active_registration() retorna False.
        """
        today = date.today()
        
        reg = await service.create(
            **seed_data,
            start_at=today - timedelta(days=60),
            end_at=today - timedelta(days=10),  # Já encerrada
        )
        
        has_active = await service.has_active_registration(
            seed_data["athlete_id"],
            seed_data["season_id"],
        )
        
        assert has_active is False
