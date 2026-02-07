"""
Service Athlete V2 - Lógica de negócio para atletas (PÓS RDB AJUSTES).

ATUALIZADO: 2025-12-27 - Conforme REGRAS_SISTEMAS.md V1.1

Implementa:
- R12: Papel atleta permanente no histórico
- R13/R14: Estados e impactos (ativa, lesionada, dispensada)
- R38: Atleta deve ter equipe na temporada
- RD1/RD2: Categoria sazonal (calculada e fixada em team_registrations)
- RD13: Goleiras não têm posição ofensiva
- RDB4: Soft delete obrigatório
- RDB5: Auditoria imutável
- RDB7: Histórico de estados dedicado
- RF16: Alteração auditável
"""
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone, date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, or_

from app.models.athlete import Athlete, AthleteState
from app.models.athlete_state_history import AthleteStateHistory
from app.models.team_registration import TeamRegistration
from app.models.membership import Membership
from app.models.season import Season
from app.models.team import Team
from app.models.person import Person

from app.services.provisioning_service import (
    calculate_category_id,
    find_institutional_team,
    resolve_role_id,
    select_current_or_next_season,
)

from app.schemas.athletes_v2 import (
    AthleteCreate,
    AthleteUpdate,
    AthleteResponse,
    AthleteStateHistoryResponse,
    ChangeStateRequest,
    AthletePaginatedResponse,
    AthleteStateEnum,
)


class AthleteServiceV2:
    """
    Serviço para gerenciar atletas conforme REGRAS_SISTEMAS.md V1.1.

    Principais responsabilidades:
    - Criar atleta com validação RD13 (goleira sem posição ofensiva)
    - Calcular e fixar category_id em team_registrations (RD1/RD2)
    - Gerenciar estados com histórico (RDB7)
    - Soft delete com auditoria (RDB4/RDB5)
    - Retornar campos calculados (athlete_age, athlete_age_at_registration)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================================
    # LISTAR ATLETAS
    # =========================================================================

    async def list_athletes(
        self,
        organization_id: UUID,
        *,
        state: Optional[AthleteStateEnum] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
        include_deleted: bool = False
    ) -> AthletePaginatedResponse:
        """
        Lista atletas com filtros.

        Args:
            organization_id: UUID da organização
            state: Filtrar por estado (ativa, lesionada, dispensada)
            search: Busca por nome ou apelido
            page: Página (1-indexed)
            limit: Itens por página
            include_deleted: Incluir atletas soft-deleted

        Returns:
            AthletePaginatedResponse com items, page, limit, total
        """
        query = (
            select(Athlete)
            .options(
                selectinload(Athlete.team_registrations).selectinload(TeamRegistration.season)
            )
            .where(Athlete.organization_id == organization_id)
        )

        if state:
            query = query.where(Athlete.state == state.value)

        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    Athlete.athlete_name.ilike(search_filter),
                    Athlete.athlete_nickname.ilike(search_filter)
                )
            )

        if not include_deleted:
            query = query.where(Athlete.deleted_at.is_(None))

        # Total count - usar with_only_columns para evitar produto cartesiano
        count_query = query.with_only_columns(func.count()).order_by(None)
        total = await self.db.scalar(count_query) or 0

        # Paginação
        query = query.offset((page - 1) * limit).limit(limit)
        query = query.order_by(Athlete.athlete_name.asc())

        result = await self.db.scalars(query)
        athletes = list(result.all())

        # Converter para response schemas
        items = [await self._to_response(athlete) for athlete in athletes]

        return AthletePaginatedResponse(
            items=items,
            page=page,
            limit=limit,
            total=total
        )

    # =========================================================================
    # BUSCAR ATLETA POR ID
    # =========================================================================

    async def get_by_id(self, athlete_id: UUID, include_deleted: bool = False) -> Optional[AthleteResponse]:
        """
        Busca atleta por ID.

        Args:
            athlete_id: UUID da atleta
            include_deleted: Incluir soft-deleted

        Returns:
            AthleteResponse ou None se não encontrado
        """
        query = (
            select(Athlete)
            .options(
                selectinload(Athlete.team_registrations).selectinload(TeamRegistration.season)
            )
            .where(Athlete.id == athlete_id)
        )

        if not include_deleted:
            query = query.where(Athlete.deleted_at.is_(None))

        athlete = await self.db.scalar(query)

        if athlete is None:
            return None

        return await self._to_response(athlete)

    # =========================================================================
    # CRIAR ATLETA
    # =========================================================================

    async def create_athlete(
        self,
        organization_id: UUID,
        data: AthleteCreate,
        created_by_membership_id: UUID
    ) -> AthleteResponse:
        """
        Cria nova atleta com vinculos automaticos.

        Implementa:
        - RD13: Validacao goleira sem posicao ofensiva (schema)
        - RD1/RD2: Calcular e fixar category_id em team_registrations
        - R38/R39: Criar team_registration automaticamente (equipe institucional)
        - R6/R9: Criar membership da atleta na temporada
        - RDB7: Criar estado inicial no historico

        Raises:
            ValueError: Se validacao falhar
        """
        birth_date_obj = datetime.strptime(data.birth_date, '%Y-%m-%d').date()

        person = Person(
            full_name=data.athlete_name.strip(),
            birth_date=birth_date_obj,
            cpf=data.athlete_cpf,
            phone=data.athlete_phone,
            email=data.athlete_email,
        )
        self.db.add(person)
        await self.db.flush()

        team = None
        if data.team_id:
            team = await self.db.get(Team, data.team_id)
            if team is None:
                raise ValueError('team_not_found')
            if str(team.organization_id) != str(organization_id):
                raise ValueError('team_org_mismatch')
            season = await self.db.get(Season, team.season_id)
            if season is None:
                raise ValueError('season_not_found')
        else:
            selection = await select_current_or_next_season(self.db, str(organization_id))
            season = selection.season

        season_start = season.starts_at or date.today()
        category_id = await calculate_category_id(
            self.db,
            birth_date=birth_date_obj,
            season_start=season_start,
        )

        if team is None:
            team = await find_institutional_team(
                self.db,
                organization_id=str(organization_id),
                season_id=str(season.id),
                category_id=category_id,
            )
        elif team.category_id and team.category_id != category_id:
            raise ValueError('team_category_mismatch')

        athlete = Athlete(
            organization_id=organization_id,
            created_by_membership_id=created_by_membership_id,
            person_id=person.id,
            athlete_name=data.athlete_name.strip(),
            athlete_nickname=data.athlete_nickname,
            birth_date=birth_date_obj,
            shirt_number=data.shirt_number,
            main_defensive_position_id=data.main_defensive_position_id,
            secondary_defensive_position_id=data.secondary_defensive_position_id,
            main_offensive_position_id=data.main_offensive_position_id,
            secondary_offensive_position_id=data.secondary_offensive_position_id,
            athlete_rg=data.athlete_rg,
            athlete_cpf=data.athlete_cpf,
            athlete_phone=data.athlete_phone,
            athlete_email=data.athlete_email,
            guardian_name=data.guardian_name,
            guardian_phone=data.guardian_phone,
            schooling_id=data.schooling_id,
            zip_code=data.zip_code,
            street=data.street,
            neighborhood=data.neighborhood,
            city=data.city,
            address_state=data.address_state,
            address_number=data.address_number,
            address_complement=data.address_complement,
            state=AthleteState.ATIVA.value,
        )

        self.db.add(athlete)
        await self.db.flush()

        initial_state = AthleteStateHistory(
            athlete_id=athlete.id,
            state=AthleteState.ATIVA.value,
            effective_from=datetime.now(timezone.utc),
            effective_until=None,
            changed_by_membership_id=created_by_membership_id,
            reason='Cadastro inicial',
        )
        self.db.add(initial_state)

        start_date = date.today()
        if season.starts_at and season.starts_at > start_date:
            start_date = season.starts_at

        role_id = await resolve_role_id(self.db, 'atleta')
        existing_membership = await self.db.scalar(
            select(Membership).where(
                Membership.organization_id == str(organization_id),
                Membership.person_id == str(person.id),
                Membership.season_id == season.id,
            )
        )
        if existing_membership:
            if existing_membership.role_id != role_id:
                raise ValueError('membership_role_conflict')
            membership = existing_membership
        else:
            membership = Membership(
                organization_id=str(organization_id),
                user_id=None,
                person_id=str(person.id),
                role_id=role_id,
                status='ativo',
                season_id=season.id,
                start_date=start_date,
            )
            self.db.add(membership)

        team_registration = TeamRegistration(
            athlete_id=athlete.id,
            team_id=team.id,
            season_id=season.id,
            category_id=category_id,
            organization_id=organization_id,
            created_by_membership_id=created_by_membership_id,
            start_at=start_date,
            end_at=None,
        )
        self.db.add(team_registration)

        await self.db.flush()
        await self.db.commit()

        return await self._to_response(athlete)

    # =========================================================================
    # ATUALIZAR ATLETA
    # =========================================================================

    async def update_athlete(
        self,
        athlete_id: UUID,
        data: AthleteUpdate,
        updated_by_membership_id: UUID
    ) -> Optional[AthleteResponse]:
        """
        Atualiza dados da atleta.

        Implementa:
        - RD13: Validação goleira sem posição ofensiva
        - RF16: Alteração auditável (através de updated_at trigger)

        Args:
            athlete_id: UUID da atleta
            data: AthleteUpdate com campos parciais
            updated_by_membership_id: UUID do membership que fez a alteração

        Returns:
            AthleteResponse atualizado ou None se não encontrado

        Raises:
            ValueError: Se validação RD13 falhar
        """
        athlete = await self.db.get(Athlete, athlete_id)
        if athlete is None or athlete.deleted_at is not None:
            return None

        # Atualizar apenas campos fornecidos
        update_data = data.model_dump(exclude_unset=True)

        # Validar RD13: se mudou posição defensiva para goleira, bloquear ofensiva
        if 'main_defensive_position_id' in update_data or 'main_offensive_position_id' in update_data:
            new_defensive = update_data.get('main_defensive_position_id', athlete.main_defensive_position_id)
            new_offensive = update_data.get('main_offensive_position_id', athlete.main_offensive_position_id)

            if new_defensive == 5 and new_offensive is not None:
                raise ValueError('Goleiras (defensive_position_id=5) não podem ter posição ofensiva (RD13)')
            if new_defensive != 5 and new_offensive is None:
                raise ValueError('Atletas de linha devem ter posição ofensiva principal (RD13)')

        # Converter birth_date se fornecido
        if 'birth_date' in update_data:
            update_data['birth_date'] = datetime.strptime(update_data['birth_date'], '%Y-%m-%d').date()

        # Aplicar atualizações
        for field, value in update_data.items():
            setattr(athlete, field, value)

        await self.db.flush()
        await self.db.commit()

        return await self._to_response(athlete)

    # =========================================================================
    # MUDAR ESTADO
    # =========================================================================

    async def change_state(
        self,
        athlete_id: UUID,
        request: ChangeStateRequest,
        changed_by_membership_id: UUID
    ) -> AthleteStateHistoryResponse:
        """
        Altera estado da atleta com histórico.

        Implementa:
        - R13: Estados válidos (ativa, lesionada, dispensada)
        - R14: Impacto nos relatórios
        - RDB7: Histórico de estados dedicado
        - RF16: Alteração auditável
        - R13 Complemento: Ao dispensar, soft-delete team_registrations

        Args:
            athlete_id: UUID da atleta
            request: ChangeStateRequest com novo estado e motivo
            changed_by_membership_id: UUID do membership que fez a mudança

        Returns:
            AthleteStateHistoryResponse do novo estado

        Raises:
            ValueError: Se atleta não encontrado
        """
        athlete = await self.db.get(Athlete, athlete_id)
        if athlete is None or athlete.deleted_at is not None:
            raise ValueError(f"Atleta {athlete_id} não encontrado")

        now = datetime.now(timezone.utc)

        # 1. Encerrar estado atual no histórico
        current_history = await self.db.scalar(
            select(AthleteStateHistory).where(
                AthleteStateHistory.athlete_id == athlete_id,
                AthleteStateHistory.effective_until.is_(None)
            )
        )

        if current_history:
            current_history.effective_until = now

        # 2. Criar novo estado no histórico
        new_history = AthleteStateHistory(
            athlete_id=athlete_id,
            state=request.state.value,
            effective_from=now,
            effective_until=None,  # Estado atual
            changed_by_membership_id=changed_by_membership_id,
            reason=request.reason,
        )
        self.db.add(new_history)

        # 3. Atualizar estado no registro base
        athlete.state = request.state.value

        # 4. R13 Complemento: Se dispensada, soft-delete team_registrations
        if request.state == AthleteStateEnum.DISPENSADA:
            result = await self.db.scalars(
                select(TeamRegistration).where(
                    TeamRegistration.athlete_id == athlete_id,
                    TeamRegistration.end_at.is_(None)
                )
            )
            active_registrations = result.all()

            for reg in active_registrations:
                reg.end_at = date.today()

        await self.db.flush()
        await self.db.commit()

        return AthleteStateHistoryResponse.model_validate(new_history)

    # =========================================================================
    # HISTÓRICO DE ESTADOS
    # =========================================================================

    async def get_state_history(self, athlete_id: UUID) -> list[AthleteStateHistoryResponse]:
        """
        Retorna histórico completo de estados da atleta.

        Args:
            athlete_id: UUID da atleta

        Returns:
            Lista de AthleteStateHistoryResponse ordenada por data (mais recente primeiro)
        """
        result = await self.db.scalars(
            select(AthleteStateHistory)
            .where(AthleteStateHistory.athlete_id == athlete_id)
            .order_by(AthleteStateHistory.changed_at.desc())
        )
        history = result.all()

        return [AthleteStateHistoryResponse.model_validate(h) for h in history]

    # =========================================================================
    # SOFT DELETE
    # =========================================================================

    async def soft_delete(
        self,
        athlete_id: UUID,
        reason: str,
        deleted_by_membership_id: UUID
    ) -> Optional[AthleteResponse]:
        """
        Soft delete da atleta.

        Implementa:
        - RDB4: Soft delete obrigatório
        - R13: Mudar estado para "dispensada"
        - RDB5: Auditoria (via trigger)

        Args:
            athlete_id: UUID da atleta
            reason: Motivo do delete
            deleted_by_membership_id: UUID do membership que deletou

        Returns:
            AthleteResponse ou None se não encontrado

        Raises:
            ValueError: Se já soft-deleted
        """
        athlete = await self.db.get(Athlete, athlete_id)
        if athlete is None:
            return None

        if athlete.deleted_at is not None:
            raise ValueError(f"Atleta {athlete_id} já foi deletada em {athlete.deleted_at}")

        # 1. Soft delete
        athlete.deleted_at = datetime.now(timezone.utc)
        athlete.deleted_reason = reason

        # 2. Mudar estado para dispensada (acionará triggers)
        athlete.state = AthleteState.DISPENSADA.value

        await self.db.flush()
        await self.db.commit()

        return await self._to_response(athlete)

    # =========================================================================
    # HELPERS PRIVADOS
    # =========================================================================

    def _calculate_category(self, birth_date: date, season_start: date) -> int:
        return calculate_category_id(self.db, birth_date=birth_date, season_start=season_start)

    async def _to_response(self, athlete: Athlete) -> AthleteResponse:
        """
        Converte model Athlete para AthleteResponse.

        Calcula campos derivados:
        - athlete_age: idade atual (runtime)
        - athlete_age_at_registration: lido do banco (calculado por trigger)
        - category_id: busca na team_registration ativa da temporada atual
        - is_goalkeeper: True se posição defensiva = 5

        Args:
            athlete: Model Athlete

        Returns:
            AthleteResponse com todos os campos
        """
        # Buscar category_id da team_registration ativa da temporada atual
        category_id = None
        today = date.today()
        active_registration = await self.db.scalar(
            select(TeamRegistration)
            .join(Season, TeamRegistration.season_id == Season.id)
            .where(
                TeamRegistration.athlete_id == athlete.id,
                or_(
                    TeamRegistration.end_at.is_(None),
                    TeamRegistration.end_at >= today,
                ),
                Season.deleted_at.is_(None),
                Season.canceled_at.is_(None),
                Season.interrupted_at.is_(None),
                Season.start_date.is_not(None),
                Season.end_date.is_not(None),
                Season.start_date <= today,
                Season.end_date >= today,
            )
            .limit(1)
        )

        if not active_registration:
            active_registration = await self.db.scalar(
                select(TeamRegistration)
                .join(Season, TeamRegistration.season_id == Season.id)
                .where(
                    TeamRegistration.athlete_id == athlete.id,
                    Season.deleted_at.is_(None),
                    Season.canceled_at.is_(None),
                    Season.interrupted_at.is_(None),
                )
                .order_by(Season.start_date.desc().nullslast(), Season.created_at.desc())
                .limit(1)
            )


        if active_registration:
            category_id = active_registration.category_id

        return AthleteResponse(
            # Identificação
            id=athlete.id,
            organization_id=athlete.organization_id,
            person_id=athlete.person_id,

            # Dados pessoais
            athlete_name=athlete.athlete_name,
            athlete_nickname=athlete.athlete_nickname,
            birth_date=athlete.birth_date,

            # Timestamps
            registered_at=athlete.registered_at,
            created_at=athlete.created_at,
            updated_at=athlete.updated_at,

            # Número da camisa
            shirt_number=athlete.shirt_number,

            # Posições
            main_defensive_position_id=athlete.main_defensive_position_id,
            secondary_defensive_position_id=athlete.secondary_defensive_position_id,
            main_offensive_position_id=athlete.main_offensive_position_id,
            secondary_offensive_position_id=athlete.secondary_offensive_position_id,

            # Documentos
            athlete_rg=athlete.athlete_rg,
            athlete_cpf=athlete.athlete_cpf,

            # Contatos
            athlete_phone=athlete.athlete_phone,
            athlete_email=athlete.athlete_email,

            # Responsável
            guardian_name=athlete.guardian_name,
            guardian_phone=athlete.guardian_phone,

            # Escolaridade
            schooling_id=athlete.schooling_id,

            # Endereço
            zip_code=athlete.zip_code,
            street=athlete.street,
            neighborhood=athlete.neighborhood,
            city=athlete.city,
            address_state=athlete.address_state,
            address_number=athlete.address_number,
            address_complement=athlete.address_complement,

            # Status
            state=AthleteStateEnum(athlete.state),
            is_active=athlete.is_active,
            deleted_at=athlete.deleted_at,
            deleted_reason=athlete.deleted_reason,

            # Campos calculados
            athlete_age_at_registration=athlete.athlete_age_at_registration,  # Lido do banco (trigger)
            athlete_age=athlete.current_age,  # Calculado em runtime via property
            category_id=category_id,  # Via team_registrations
            is_goalkeeper=athlete.is_goalkeeper,  # Via property
        )
