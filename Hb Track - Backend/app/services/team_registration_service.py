"""
TeamRegistrationService – Gestão de inscrições atleta↔equipe.

Regras:
- RDB10: Períodos (start_at, end_at) não podem sobrepor para mesma pessoa+equipe+temporada
- R16/RD1-RD2: Categoria compatível com idade (validação futura)
- R38: Atleta deve ter equipe para atuar na temporada
- R13 V1.1: Ao dispensar atleta, encerra participações vigentes
- RF5.2/R37: Temporada bloqueada impede criação/edição (validação futura)
- R15: Validação de gênero (persons.gender vs teams.gender)

TODO: Validações completas requerem migration para adicionar start_at/end_at.
"""

from datetime import date, datetime, timezone
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.team_registration import TeamRegistration
from app.models.athlete import Athlete
from app.models.person import Person
from app.models.team import Team
from app.models.category import Category
from app.models.season import Season


class TeamRegistrationService:
    """
    Serviço para gestão de inscrições de atletas em equipes.
    
    Implementa RDB10 (não-sobreposição de períodos) e suporta
    R13 V1.1 (encerramento automático ao dispensar atleta).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ───────────────────────────────────────────────────────────────────
    # READ
    # ───────────────────────────────────────────────────────────────────

    async def list_by_athlete(
        self,
        athlete_id: UUID,
        *,
        season_id: Optional[UUID] = None,
        active_only: bool = False,
    ) -> Sequence[TeamRegistration]:
        """
        Lista inscrições de um atleta.

        Args:
            athlete_id: UUID do atleta
            season_id: Filtrar por temporada (opcional)
            active_only: Se True, retorna apenas inscrições ativas (end_at IS NULL)

        Returns:
            Lista de TeamRegistration ordenada por created_at DESC
        """
        stmt = select(TeamRegistration).options(
            selectinload(TeamRegistration.athlete)
        ).where(
            TeamRegistration.athlete_id == athlete_id
        )

        if season_id and hasattr(TeamRegistration, "season_id"):
            stmt = stmt.where(TeamRegistration.season_id == season_id)

        # Filtrar apenas inscrições ativas (RDB10)
        if active_only:
            today = date.today()
            stmt = stmt.where(
                or_(
                    TeamRegistration.end_at.is_(None),
                    TeamRegistration.end_at >= today,
                )
            )

        stmt = stmt.order_by(TeamRegistration.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_by_team(
        self,
        team_id: UUID,
        *,
        active_only: bool = False,
    ) -> Sequence[TeamRegistration]:
        """
        Lista inscrições em uma equipe.

        Args:
            team_id: UUID da equipe
            active_only: Se True, retorna apenas inscrições ativas

        Returns:
            Lista de TeamRegistration ordenada por created_at DESC
        """
        stmt = select(TeamRegistration).options(
            selectinload(TeamRegistration.athlete)
        ).where(
            TeamRegistration.team_id == team_id
        )

        # Filtrar apenas inscrições ativas (RDB10)
        if active_only:
            today = date.today()
            stmt = stmt.where(
                or_(
                    TeamRegistration.end_at.is_(None),
                    TeamRegistration.end_at >= today,
                )
            )

        stmt = stmt.order_by(TeamRegistration.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, registration_id: UUID) -> Optional[TeamRegistration]:
        """
        Busca inscrição por ID.

        Args:
            registration_id: UUID da inscrição

        Returns:
            TeamRegistration ou None se não encontrado
        """
        stmt = select(TeamRegistration).where(TeamRegistration.id == registration_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ───────────────────────────────────────────────────────────────────
    # CREATE
    # ───────────────────────────────────────────────────────────────────

    async def create(
        self,
        *,
        athlete_id: UUID,
        season_id: UUID,
        category_id: int,
        team_id: UUID,
        organization_id: UUID,
        created_by_membership_id: UUID,
        role: Optional[str] = None,
        start_at: Optional[date] = None,
        end_at: Optional[date] = None,
    ) -> TeamRegistration:
        """
        Cria nova inscrição (atleta↔equipe na temporada).

        Regras:
        - RDB10: Valida não-sobreposição de período
        - R38: Associação imediata exigida para atuação
        - R16: Categoria compatível com idade (TODO: validar no serviço)

        Args:
            athlete_id: UUID do atleta
            season_id: UUID da temporada
            category_id: ID da categoria (int)
            team_id: UUID da equipe
            organization_id: UUID da organização
            created_by_membership_id: UUID do membership criador
            role: Papel/posição na equipe (opcional)
            start_at: Data de início (default: hoje)
            end_at: Data de término (opcional, NULL = ativo)

        Returns:
            TeamRegistration criado

        Raises:
            ValueError: "period_overlap" se RDB10 violado
            ValueError: "invalid_date_range" se end_at < start_at
        """
        # Default start_at para hoje
        if start_at is None:
            start_at = date.today()

        # Validar ordem das datas
        if end_at is not None and end_at < start_at:
            raise ValueError("invalid_date_range")

        # RDB10: Verificar sobreposição de período
        if await self._has_overlapping_period(
            athlete_id=athlete_id,
            team_id=team_id,
            season_id=season_id,
            start_at=start_at,
            end_at=end_at,
        ):
            raise ValueError("period_overlap")

        # R15: Validar gênero do atleta vs gênero da equipe
        await self._validate_gender_compatibility(athlete_id=athlete_id, team_id=team_id)

        # R15: Validar categoria vs birth_date do atleta
        await self._validate_category_eligibility(
            athlete_id=athlete_id,
            team_id=team_id,
            season_id=season_id,
        )

        registration_kwargs = {
            "athlete_id": athlete_id,
            "team_id": team_id,
            "start_at": start_at,
            "end_at": end_at,
        }

        # Campos opcionais que só são aplicados se existirem na tabela
        for field_name, field_value in [
            ("season_id", season_id),
            ("category_id", category_id),
            ("organization_id", organization_id),
            ("created_by_membership_id", created_by_membership_id),
            ("role", role),
        ]:
            if hasattr(TeamRegistration, field_name):
                registration_kwargs[field_name] = field_value

        registration = TeamRegistration(**registration_kwargs)

        self.db.add(registration)
        await self.db.flush()
        await self.db.refresh(registration)
        return registration

    # ───────────────────────────────────────────────────────────────────
    # UPDATE
    # ───────────────────────────────────────────────────────────────────

    async def update(
        self,
        registration_id: UUID,
        *,
        end_at: Optional[date] = None,
        role: Optional[str] = None,
    ) -> Optional[TeamRegistration]:
        """
        Atualiza inscrição existente.

        Campos editáveis: end_at, role
        Campos imutáveis: athlete_id, season_id, category_id, team_id, organization_id

        Regras:
        - RDB10: Não reabrir período encerrado
        - R37/RF5.2: Temporada bloqueada impede edição (TODO)

        Args:
            registration_id: UUID da inscrição
            end_at: Nova data de término (opcional)
            role: Novo papel/posição (opcional)

        Returns:
            TeamRegistration atualizado ou None se não encontrado

        Raises:
            ValueError: "cannot_reopen_ended" se tentar reabrir período encerrado
            ValueError: "invalid_date_range" se end_at < start_at
        """
        registration = await self.get_by_id(registration_id)
        if not registration:
            return None

        # RDB10: Não permitir reabrir período encerrado
        if registration.end_at is not None and end_at is None:
            raise ValueError("cannot_reopen_ended")
        
        # Validar ordem das datas
        if end_at is not None and end_at < registration.start_at:
            raise ValueError("invalid_date_range")
        
        if end_at is not None:
            registration.end_at = end_at

        if role is not None:
            registration.role = role

        await self.db.flush()
        await self.db.refresh(registration)
        return registration

    async def end_registration(
        self,
        registration_id: UUID,
        end_at: Optional[date] = None,
    ) -> Optional[TeamRegistration]:
        """
        Encerra uma inscrição (define end_at).

        Usado para:
        - Encerramento manual de inscrição
        - R13 V1.1: Encerramento automático ao dispensar atleta

        Args:
            registration_id: UUID da inscrição
            end_at: Data de término (default: hoje)

        Returns:
            TeamRegistration atualizado ou None se não encontrado
        """
        if end_at is None:
            end_at = date.today()

        registration = await self.get_by_id(registration_id)
        if not registration:
            return None

        registration.end_at = end_at

        await self.db.flush()
        await self.db.refresh(registration)
        return registration

    # ───────────────────────────────────────────────────────────────────
    # R13 V1.1: Encerramento automático ao dispensar atleta
    # ───────────────────────────────────────────────────────────────────

    async def close_active_registrations(
        self,
        athlete_id: UUID,
        *,
        season_id: Optional[UUID] = None,
        end_at: Optional[date] = None,
    ) -> int:
        """
        Encerra todas as inscrições ativas de um atleta.

        Usado pelo AthleteService quando estado muda para "dispensada" (R13 V1.1).

        Args:
            athlete_id: UUID do atleta
            season_id: Se informado, encerra apenas da temporada especificada
            end_at: Data de término (default: hoje)

        Returns:
            Quantidade de inscrições encerradas
        """
        if end_at is None:
            end_at = date.today()

        # Buscar inscrições ativas
        stmt = select(TeamRegistration).where(
            TeamRegistration.athlete_id == athlete_id
        )

        if season_id and hasattr(TeamRegistration, "season_id"):
            stmt = stmt.where(TeamRegistration.season_id == season_id)

        # Apenas inscrições ativas (end_at IS NULL ou futuro)
        today = date.today()
        stmt = stmt.where(
            or_(
                TeamRegistration.end_at.is_(None),
                TeamRegistration.end_at >= today,
            )
        )

        result = await self.db.execute(stmt)
        active_registrations = result.scalars().all()

        count = 0
        for reg in active_registrations:
            if reg.end_at is None or reg.end_at >= today:
                reg.end_at = end_at
                count += 1

        await self.db.flush()
        return count

    # ───────────────────────────────────────────────────────────────────
    # RDB10: Validação de sobreposição de período
    # ───────────────────────────────────────────────────────────────────

    async def _has_overlapping_period(
        self,
        athlete_id: UUID,
        team_id: UUID,
        season_id: UUID,
        start_at: date,
        end_at: Optional[date],
        *,
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        """
        Verifica se existe sobreposição de período (RDB10).

        Dois períodos [A_start, A_end] e [B_start, B_end] se sobrepõem se:
        - A_start <= B_end AND A_end >= B_start
        - Considerando NULL como infinito (sem fim)

        Args:
            athlete_id: UUID do atleta
            team_id: UUID da equipe
            season_id: UUID da temporada
            start_at: Data de início do novo período
            end_at: Data de término do novo período (None = sem fim)
            exclude_id: UUID de inscrição a excluir (para updates)

        Returns:
            True se há sobreposição, False caso contrário
        """
        # Query base: mesma pessoa + equipe + temporada
        conditions = [
            TeamRegistration.athlete_id == athlete_id,
            TeamRegistration.team_id == team_id,
        ]

        if season_id and hasattr(TeamRegistration, "season_id"):
            conditions.append(TeamRegistration.season_id == season_id)

        stmt = select(TeamRegistration).where(and_(*conditions))

        # Excluir registro específico (para updates)
        if exclude_id:
            stmt = stmt.where(TeamRegistration.id != exclude_id)

        # ─────────────────────────────────────────────────────────────
        # Lógica de sobreposição (RDB10):
        # Novo período: [start_at, end_at]
        # Existente:    [existing.start_at, existing.end_at]
        #
        # Sobrepõe se:
        #   new_start <= existing_end AND new_end >= existing_start
        #
        # Com NULL = infinito:
        #   - Se new_end IS NULL: sempre >= existing_start
        #   - Se existing_end IS NULL: new_start sempre <= existing_end
        # ─────────────────────────────────────────────────────────────
        
        overlap_conditions = []
        
        # Condição 1: new_start <= existing_end (ou existing_end IS NULL)
        overlap_conditions.append(
            or_(
                TeamRegistration.end_at.is_(None),
                TeamRegistration.end_at >= start_at,
            )
        )
        
        # Condição 2: new_end >= existing_start (ou new_end IS NULL)
        if end_at is None:
            # new_end é infinito, sempre >= existing_start
            pass  # Condição sempre verdadeira, não precisa adicionar
        else:
            overlap_conditions.append(
                TeamRegistration.start_at <= end_at
            )
        
        stmt = stmt.where(and_(*overlap_conditions))

        result = await self.db.execute(stmt)
        existing = result.scalars().first()

        # Se há registro existente com overlap, retornar True
        return existing is not None

    # ───────────────────────────────────────────────────────────────────
    # Helpers
    # ───────────────────────────────────────────────────────────────────

    async def get_active_by_athlete_season(
        self,
        athlete_id: UUID,
        season_id: UUID,
    ) -> Sequence[TeamRegistration]:
        """
        Retorna inscrições ativas de um atleta em uma temporada.

        Útil para R38 (verificar se atleta tem equipe na temporada).

        Args:
            athlete_id: UUID do atleta
            season_id: UUID da temporada

        Returns:
            Lista de inscrições ativas
        """
        if not hasattr(TeamRegistration, "season_id"):
            return []

        stmt = select(TeamRegistration).where(
            and_(
                TeamRegistration.athlete_id == athlete_id,
                TeamRegistration.season_id == season_id,
            )
        )

        # Filtrar apenas inscrições ativas (end_at IS NULL ou futuro)
        today = date.today()
        stmt = stmt.where(
            or_(
                TeamRegistration.end_at.is_(None),
                TeamRegistration.end_at >= today,
            )
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def has_active_registration(
        self,
        athlete_id: UUID,
        season_id: UUID,
    ) -> bool:
        """
        Verifica se atleta tem inscrição ativa na temporada (R38).

        Args:
            athlete_id: UUID do atleta
            season_id: UUID da temporada

        Returns:
            True se tem inscrição ativa, False caso contrário
        """
        if not hasattr(TeamRegistration, "season_id"):
            return False

        registrations = await self.get_active_by_athlete_season(athlete_id, season_id)
        return len(registrations) > 0

    # ───────────────────────────────────────────────────────────────────
    # R15: Validação de Gênero
    # ───────────────────────────────────────────────────────────────────

    async def _validate_gender_compatibility(
        self,
        athlete_id: UUID,
        team_id: UUID,
    ) -> None:
        """
        Valida compatibilidade de gênero entre atleta e equipe (R15).

        Regra:
        - persons.gender deve ser compatível com teams.gender
        - teams.gender='misto' aceita qualquer gênero
        - teams.gender='masculino' requer persons.gender='masculino'
        - teams.gender='feminino' requer persons.gender='feminino'
        
        Args:
            athlete_id: UUID do atleta
            team_id: UUID da equipe

        Raises:
            ValueError: "gender_incompatible" se gênero do atleta for incompatível com a equipe
            ValueError: "athlete_not_found" se atleta não existir
            ValueError: "team_not_found" se equipe não existir
            ValueError: "person_not_found" se pessoa do atleta não existir
            ValueError: "athlete_gender_not_set" se gênero da pessoa não estiver definido
        """
        # Buscar atleta
        stmt_athlete = select(Athlete).where(Athlete.id == athlete_id)
        result = await self.db.execute(stmt_athlete)
        athlete = result.scalar_one_or_none()
        
        if not athlete:
            raise ValueError("athlete_not_found")
        
        # Buscar pessoa (para obter gênero)
        stmt_person = select(Person).where(Person.id == athlete.person_id)
        result = await self.db.execute(stmt_person)
        person = result.scalar_one_or_none()
        
        if not person:
            raise ValueError("person_not_found")
        
        # Validar se gênero está definido
        if not person.gender:
            raise ValueError("athlete_gender_not_set")
        
        # Buscar equipe
        stmt_team = select(Team).where(Team.id == team_id)
        result = await self.db.execute(stmt_team)
        team = result.scalar_one_or_none()
        
        if not team:
            raise ValueError("team_not_found")
        
        # Equipes mistas aceitam qualquer gênero
        if team.gender == "misto":
            return
        
        # Validar compatibilidade
        person_gender = person.gender.lower().strip()
        team_gender = team.gender.lower().strip()
        
        if person_gender != team_gender:
            raise ValueError("gender_incompatible")

    # ───────────────────────────────────────────────────────────────────
    # R15: Validação de Categoria
    # ───────────────────────────────────────────────────────────────────

    async def _validate_category_eligibility(
        self,
        athlete_id: UUID,
        team_id: UUID,
        season_id: UUID,
    ) -> None:
        """
        Valida compatibilidade de categoria entre atleta e equipe (R15).

        CANÔNICO: idade = ano_temporada - ano_nascimento
        categoria_natural = menor categoria onde idade <= max_age

        Regra:
        - Atleta pode jogar na sua categoria natural ou ACIMA
        - Atleta NUNCA pode jogar em categoria abaixo da natural
        - Se categoria_natural.max_age > categoria_equipe.max_age → BLOQUEIO
        
        Args:
            athlete_id: UUID do atleta
            team_id: UUID da equipe
            season_id: UUID da temporada

        Raises:
            ValueError: "athlete_not_found" se atleta não existir
            ValueError: "team_not_found" se equipe não existir
            ValueError: "season_not_found" se temporada não existir
            ValueError: "category_not_found" se categoria da equipe não existir
            ValueError: "category_violation" se atleta não pode jogar na categoria
        """
        if season_id is None:
            # Schema legado sem temporada associada; não há validação possível
            return

        # Buscar atleta
        stmt_athlete = select(Athlete).where(Athlete.id == athlete_id)
        result = await self.db.execute(stmt_athlete)
        athlete = result.scalar_one_or_none()
        
        if not athlete:
            raise ValueError("athlete_not_found")
        
        # Buscar equipe com sua categoria
        stmt_team = select(Team).where(Team.id == team_id)
        result = await self.db.execute(stmt_team)
        team = result.scalar_one_or_none()
        
        if not team:
            raise ValueError("team_not_found")
        
        # Buscar temporada para obter o ano
        stmt_season = select(Season).where(Season.id == season_id)
        result = await self.db.execute(stmt_season)
        season = result.scalar_one_or_none()
        
        if not season:
            raise ValueError("season_not_found")
        
        # Buscar categoria da equipe
        stmt_team_category = select(Category).where(Category.id == team.category_id)
        result = await self.db.execute(stmt_team_category)
        team_category = result.scalar_one_or_none()
        
        if not team_category:
            raise ValueError("category_not_found")
        
        # Calcular idade do atleta na temporada
        # CANÔNICO: idade = ano_temporada - ano_nascimento
        season_year = season.start_date.year if season.start_date else date.today().year
        athlete_age = season_year - athlete.birth_date.year
        
        # Calcular categoria natural do atleta
        # CANÔNICO: menor categoria onde idade <= max_age
        stmt_natural_category = (
            select(Category)
            .where(Category.max_age >= athlete_age)
            .order_by(Category.max_age.asc())
        )
        result = await self.db.execute(stmt_natural_category)
        natural_category = result.scalar_one_or_none()
        
        # Se não encontrou categoria (atleta muito velho), usar a maior categoria disponível
        if not natural_category:
            stmt_max_category = (
                select(Category)
                .order_by(Category.max_age.desc())
            )
            result = await self.db.execute(stmt_max_category)
            natural_category = result.scalar_one_or_none()
        
        if not natural_category:
            # Sistema sem categorias configuradas - permitir
            return
        
        # VALIDAÇÃO R15: categoria_natural.max_age <= categoria_equipe.max_age
        # Se atleta é de categoria mais alta (max_age maior), não pode jogar em categoria menor
        if natural_category.max_age > team_category.max_age:
            raise ValueError(
                f"category_violation:athlete_age={athlete_age},"
                f"natural_category={natural_category.name}(max_age={natural_category.max_age}),"
                f"team_category={team_category.name}(max_age={team_category.max_age})"
            )
