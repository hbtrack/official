"""
Service Athlete - Lógica de negócio para atletas.

Regras:
- R12: Papel atleta permanente
- R13/R14: Estados e impactos
- R38: Atleta deve ter equipe
- RF16: Alteração auditável
"""
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone, date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.models.athlete import Athlete, AthleteState
# NOTE: AthleteStateHistory model não implementado ainda - código comentado
# from app.models.athlete_state import AthleteStateHistory
from app.models.membership import Membership
from app.models.organization import Organization


class AthleteService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_athletes(
        self,
        organization_id: UUID,
        *,
        state: Optional[AthleteState] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
        include_deleted: bool = False
    ) -> tuple[list[Athlete], int]:
        """Lista atletas com filtros."""
        query = select(Athlete).where(Athlete.organization_id == organization_id)
        
        if state:
            query = query.where(Athlete.state == state.value)
        
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (Athlete.athlete_name.ilike(search_filter)) |
                (Athlete.athlete_nickname.ilike(search_filter))
            )
        
        if not include_deleted:
            query = query.where(Athlete.deleted_at.is_(None))
        
        # Count total - usar with_only_columns para evitar produto cartesiano
        count_query = query.with_only_columns(func.count()).order_by(None)
        total = await self.db.scalar(count_query) or 0
        
        query = query.offset((page - 1) * limit).limit(limit)
        query = query.order_by(Athlete.athlete_name.asc())
        
        result = await self.db.scalars(query)
        return list(result.all()), total
    
    async def get_by_id(self, athlete_id: UUID) -> Optional[Athlete]:
        """Busca atleta por ID."""
        return await self.db.get(Athlete, athlete_id)
    
    async def create(
        self,
        organization_id: UUID,
        full_name: str,
        *,
        nickname: Optional[str] = None,
        birth_date: Optional[date] = None,
        position: Optional[str] = None,
        created_by_membership_id: Optional[UUID] = None,
        person_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
        season_id: Optional[UUID] = None,
    ) -> Athlete:
        """
        Cria atleta (registro base).
        
        Regras:
        - R12: Papel atleta permanente
        - R38: Associação à equipe é feita via team_registrations
        """
        # Garantir person_id: se não fornecido, criar registro em persons
        if person_id is None:
            pid = str(uuid4())
            await self.db.execute(
                text("""
                INSERT INTO persons (id, full_name)
                VALUES (:id, :full_name)
                """),
                {"id": pid, "full_name": full_name},
            )
            await self.db.flush()
            person_id = pid

        # Inferir created_by_membership_id quando ausente: buscar vínculo ativo na organização
        if created_by_membership_id is None:
            m = await self.db.scalar(
                select(Membership.id).where(
                    Membership.organization_id == str(organization_id),
                    Membership.status == 'ativo'
                ).limit(1)
            )
            if m:
                created_by_membership_id = m
            else:
                # Tentar vínculo do owner da organização
                org = await self.db.get(Organization, organization_id)
                owner_uid = getattr(org, "owner_user_id", None)
                if owner_uid:
                    m2 = await self.db.scalar(
                        select(Membership.id).where(
                            Membership.organization_id == str(organization_id),
                            Membership.user_id == str(owner_uid),
                        ).limit(1)
                    )
                    if m2:
                        created_by_membership_id = m2

        # Se ainda não há created_by_membership_id, criar um membership fallback mínimo
        if created_by_membership_id is None:
            mid = str(uuid4())
            self.db.execute(
                text("""
                INSERT INTO membership (id, organization_id, role_id, status, start_date)
                VALUES (:id, :org_id, :role_id, 'ativo', current_date)
                """),
                {"id": mid, "org_id": str(organization_id), "role_id": 3},
            )
            self.db.flush()
            created_by_membership_id = mid

        athlete = Athlete(
            organization_id=organization_id,
            athlete_name=full_name,
            athlete_nickname=nickname,
            birth_date=birth_date,
            state=AthleteState.ATIVA.value,
            person_id=person_id,
        )
        self.db.add(athlete)
        await self.db.flush()
        
        # NOTE: AthleteStateHistory não implementado - código comentado
        # # Criar estado inicial no histórico
        # initial_state = AthleteStateHistory(
        #     athlete_id=athlete.id,
        #     state=AthleteState.ATIVA.value,
        #     reason="Cadastro inicial",
        # )
        # self.db.add(initial_state)
        # await self.db.flush()
        
        # R38: Se team_id fornecido, criar team_registration automaticamente
        if team_id:
            # Buscar dados da equipe para obter season_id e category_id
            result = await self.db.execute(
                text("SELECT season_id, category_id FROM teams WHERE id = :tid"),
                {"tid": str(team_id)}
            )
            team = result.fetchone()
            
            if team:
                team_season_id = team[0]
                team_category_id = team[1]
                
                # Criar team_registration
                await self.db.execute(
                    text("""
                        INSERT INTO team_registrations 
                        (team_id, athlete_id, season_id, category_id, organization_id, 
                         created_by_membership_id, start_at)
                        VALUES (:team_id, :athlete_id, :season_id, :category_id, :org_id, 
                                :membership_id, CURRENT_DATE)
                    """),
                    {
                        "team_id": str(team_id),
                        "athlete_id": str(athlete.id),
                        "season_id": str(team_season_id) if team_season_id else str(season_id) if season_id else None,
                        "category_id": team_category_id,
                        "org_id": str(organization_id),
                        "membership_id": str(created_by_membership_id),
                    }
                )
                await self.db.flush()
                
                # Criar membership para a atleta (role_id = 5)
                await self.db.execute(
                    text("""
                        INSERT INTO membership 
                        (person_id, organization_id, role_id, season_id, is_active)
                        VALUES (:person_id, :org_id, 5, :season_id, true)
                    """),
                    {
                        "person_id": str(person_id),
                        "org_id": str(organization_id),
                        "season_id": str(team_season_id) if team_season_id else str(season_id) if season_id else None,
                    }
                )
                await self.db.flush()
        
        return athlete
    
    async def update(self, athlete_id: UUID, **kwargs) -> Optional[Athlete]:
        """
        Atualiza dados editáveis (não estado).
        
        Campos editáveis: athlete_name, athlete_nickname, birth_date
        """
        allowed_fields = {"athlete_name", "athlete_nickname", "birth_date"}

        athlete = await self.get_by_id(athlete_id)
        if athlete is None:
            return None

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(athlete, field, value)

        await self.db.flush()
        return athlete
    
    # NOTE: AthleteStateHistory não implementado - métodos change_state e get_state_history comentados
    # async def change_state(
    #     self,
    #     athlete: Athlete,
    #     new_state: AthleteState,
    #     *,
    #     reason: Optional[str] = None,
    #     notes: Optional[str] = None,
    # ) -> AthleteStateHistory:
    #     """
    #     Altera estado da atleta (R13/RF16).
    #     
    #     Regras:
    #     - R13: Estados válidos
    #     - R14: Impacto nos relatórios
    #     - RF16: Alteração auditável (histórico)
    #     - Complemento V1.1: "dispensada" encerra team_registrations
    #     
    #     Raises:
    #         ValueError("invalid_state_transition"): transição inválida
    #     """
    #     now = datetime.now(timezone.utc)
    #     
    #     # Validar transição (ex: não pode ir de dispensada para ativa sem reativação)
    #     # Por simplicidade, permitimos todas as transições na V1
    #     
    #     # Encerrar estado atual
    #     current_state = await self._get_active_state(athlete.id)
    #     if current_state:
    #         current_state.ended_at = now
    #     
    #     # Criar novo estado
    #     new_state_record = AthleteStateHistory(
    #         athlete_id=athlete.id,
    #         state=new_state.value,
    #         reason=reason,
    #         notes=notes,
    #         started_at=now,
    #     )
    #     self.db.add(new_state_record)
    #     
    #     # Atualizar estado no registro base
    #     athlete.state = new_state.value
    #     
    #     # R13 Complemento V1.1: Se dispensada, encerrar team_registrations
    #     if new_state == AthleteState.DISPENSADA:
    #         await self._close_active_registrations(athlete.id)
    #     
    #     await self.db.flush()
    #     return new_state_record
    
    # async def _get_active_state(self, athlete_id: UUID) -> Optional[AthleteStateHistory]:
    #     """Retorna estado ativo atual."""
    #     query = select(AthleteStateHistory).where(
    #         AthleteStateHistory.athlete_id == athlete_id,
    #         AthleteStateHistory.ended_at.is_(None)
    #     )
    #     return await self.db.scalar(query)
    
    async def _close_active_registrations(self, athlete_id: UUID) -> None:
        """
        Encerra team_registrations vigentes (R13 V1.1).
        
        TODO: Integrar com TeamRegistrationService.close_active_registrations()
        quando o serviço for convertido para async ou quando houver
        sessão async disponível.
        
        Alternativa: Chamar diretamente via query sync:
        
        from app.models.team_registration import TeamRegistration
        from datetime import date
        
        stmt = select(TeamRegistration).where(
            TeamRegistration.athlete_id == athlete_id
        )
        registrations = self.db.scalars(stmt).all()
        today = date.today()
        for reg in registrations:
            # reg.end_at = today  # Quando coluna existir
            pass
        """
        # Placeholder até migration adicionar start_at/end_at
        pass
    
    # async def get_state_history(self, athlete_id: UUID) -> list[AthleteStateHistory]:
    #     """Retorna histórico de estados."""
    #     query = select(AthleteStateHistory).where(
    #         AthleteStateHistory.athlete_id == athlete_id
    #     ).order_by(AthleteStateHistory.started_at.desc())
    #     
    #     result = await self.db.scalars(query)
    #     return list(result.all())

    async def soft_delete(
        self,
        athlete: Athlete,
        *,
        reason: Optional[str] = None,
    ) -> Athlete:
        """
        Soft delete da atleta (R29).

        Args:
            athlete: Atleta a deletar
            reason: Motivo do delete (opcional)

        Regras: R29 - sem delete físico
        """
        if athlete.deleted_at is not None:
            raise ValueError("already_deleted")

        athlete.deleted_at = datetime.now(timezone.utc)
        athlete.deleted_reason = reason
        athlete.state = AthleteState.DISPENSADA.value
        await self.db.flush()
        return athlete