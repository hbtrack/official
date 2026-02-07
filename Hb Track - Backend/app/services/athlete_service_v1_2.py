"""
Service Athlete V1.2 - Lógica de negócio para atletas conforme REGRAS.md V1.2.

Implementa:
- R6: Atletas vinculam-se via team_registrations, não via organization_id
- R7: Múltiplos team_registrations ativos simultâneos permitidos
- R12: Estado base + flags de restrição
- R13/R14: Estados (ativa, dispensada, arquivada) + flags (injured, suspended_until, etc.)
- R32/RF1.1: Atleta pode ser cadastrada sem equipe (vínculo opcional no POST)
- RDB10: team_registrations com start_at/end_at
- RDB17: Lookup tables (positions, schooling)
- RD13: Goleiras não têm posição ofensiva
"""
import re
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime, timezone, date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_

from app.models.athlete import Athlete, AthleteState
from app.models.team_registration import TeamRegistration
from app.models.team import Team
from app.models.person import Person, PersonContact, PersonDocument, PersonAddress
from app.models.category import Category

from app.schemas.athletes_v2 import (
    AthleteCreate,
    AthleteUpdate,
    AthleteResponse,
    AthletePaginatedResponse,
    AthleteStateEnum,
)


def normalize_cpf(cpf: str) -> str:
    """Remove formatação do CPF, mantendo apenas os 11 dígitos."""
    return re.sub(r'\D', '', cpf)


class AthleteServiceV1_2:
    """
    Serviço para gerenciar atletas conforme REGRAS.md V1.2.
    
    Principais mudanças V1.2:
    - Atleta NÃO tem organization_id (vínculo via team_registrations → teams)
    - Múltiplos team_registrations ativos permitidos
    - Cadastro sem equipe é válido (RF1.1)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================================
    # LISTAR ATLETAS (por organização via team_registrations)
    # =========================================================================

    async def list_athletes(
        self,
        organization_id: UUID,
        *,
        state: Optional[AthleteStateEnum] = None,
        search: Optional[str] = None,
        team_id: Optional[UUID] = None,
        has_team: Optional[bool] = None,
        page: int = 1,
        limit: int = 50,
        include_deleted: bool = False
    ) -> AthletePaginatedResponse:
        """
        Lista atletas de uma organização.
        
        V1.2 (Opção B - REGRAS.md):
        - Por padrão mostra TODAS as atletas da organização (com ou sem equipe)
        - Filtro has_team:
          - True: apenas atletas COM team_registration ativo
          - False: apenas atletas SEM team_registration ativo  
          - None: todas as atletas
        - RF1.1: Atleta pode existir sem equipe
        - R32: Atleta sem equipe não opera, mas aparece na lista
        """
        # Subquery para atletas COM team_registration ativo na organização
        subq_athletes_with_team = (
            select(TeamRegistration.athlete_id)
            .join(Team, Team.id == TeamRegistration.team_id)
            .where(
                Team.organization_id == organization_id,
                TeamRegistration.end_at.is_(None),  # Apenas ativos
                TeamRegistration.deleted_at.is_(None)
            )
        )
        
        if team_id:
            subq_athletes_with_team = subq_athletes_with_team.where(TeamRegistration.team_id == team_id)
        
        # Query principal baseada no filtro has_team
        if has_team is True:
            # Apenas atletas COM equipe ativa
            query = select(Athlete).where(Athlete.id.in_(subq_athletes_with_team))
        elif has_team is False:
            # Apenas atletas SEM equipe ativa
            # Atletas que pertencem à organização mas não têm team_registration ativo
            query = select(Athlete).where(
                Athlete.organization_id == organization_id,
                ~Athlete.id.in_(subq_athletes_with_team)
            )
        else:
            # TODAS as atletas da organização (com ou sem equipe)
            # Union: atletas com team_registration ativo OU atletas da organização diretamente
            query = select(Athlete).where(
                or_(
                    Athlete.id.in_(subq_athletes_with_team),
                    Athlete.organization_id == organization_id
                )
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

        # Converter para response
        items = [await self._to_response(athlete, organization_id) for athlete in athletes]

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
        """Busca atleta por ID."""
        query = select(Athlete).where(Athlete.id == athlete_id)

        if not include_deleted:
            query = query.where(Athlete.deleted_at.is_(None))

        athlete = await self.db.scalar(query)
        
        if not athlete:
            return None
            
        return await self._to_response(athlete)

    # =========================================================================
    # CRIAR ATLETA (RF1.1: equipe opcional)
    # =========================================================================

    async def create_athlete(
        self,
        organization_id: UUID,
        data: AthleteCreate,
        created_by_membership_id: Optional[UUID] = None,
    ) -> AthleteResponse:
        """
        Cria atleta conforme RF1.1 e REGRAS.md V1.2.
        
        Fluxo V1.2 (estrutura normalizada):
        1. Criar Person (dados básicos: nome, nascimento)
        2. Criar PersonDocument (CPF, RG)
        3. Criar PersonContact (telefone, email)
        4. Criar Athlete
        5. Se team_id informado, criar TeamRegistration (sem category_id - RDB10)
        
        Validações:
        - RD13: Goleira (defensive_position_id=5) não pode ter posição ofensiva
        - R38: Se team_id informado, validar pertence à organization_id
        """
        # Validar RD13: Goleira sem posição ofensiva
        if data.main_defensive_position_id == 5:  # Goleira
            if data.main_offensive_position_id or data.secondary_offensive_position_id:
                raise ValueError("goleira_no_offensive_position")
        else:
            # Não-goleira DEVE ter posição ofensiva
            if not data.main_offensive_position_id:
                raise ValueError("non_goalkeeper_requires_offensive_position")

        # Normalizar CPF (remover formatação - apenas 11 dígitos)
        cpf_normalizado = normalize_cpf(data.athlete_cpf)
        
        # Criar person (V1.2: estrutura normalizada)
        birth_date = datetime.strptime(data.birth_date, "%Y-%m-%d").date()
        
        # Extrair first_name e last_name do full_name
        name_parts = data.athlete_name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        person = Person(
            id=str(uuid4()),
            full_name=data.athlete_name,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            gender=data.gender,  # CANÔNICO: Gênero obrigatório para validação R15
        )
        self.db.add(person)
        await self.db.flush()
        
        # Criar PersonDocument para CPF (V1.2: normalizado)
        cpf_doc = PersonDocument(
            id=str(uuid4()),
            person_id=person.id,
            document_type='cpf',
            document_number=cpf_normalizado,
            is_verified=False,
        )
        self.db.add(cpf_doc)
        
        # Criar PersonDocument para RG (V1.2: normalizado)
        rg_doc = PersonDocument(
            id=str(uuid4()),
            person_id=person.id,
            document_type='rg',
            document_number=data.athlete_rg,
            is_verified=False,
        )
        self.db.add(rg_doc)
        
        # Criar PersonContact para telefone (V1.2: normalizado)
        phone_contact = PersonContact(
            id=str(uuid4()),
            person_id=person.id,
            contact_type='telefone',
            contact_value=data.athlete_phone,
            is_primary=True,
            is_verified=False,
        )
        self.db.add(phone_contact)
        
        # Criar PersonContact para email se informado
        if data.athlete_email:
            email_contact = PersonContact(
                id=str(uuid4()),
                person_id=person.id,
                contact_type='email',
                contact_value=data.athlete_email,
                is_primary=True,
                is_verified=False,
            )
            self.db.add(email_contact)
        
        # Criar PersonAddress se informado (V1.2: normalizado)
        zip_code = getattr(data, 'zip_code', None)
        street = getattr(data, 'street', None)
        city = getattr(data, 'city', None)
        if zip_code or street or city:
            address = PersonAddress(
                id=str(uuid4()),
                person_id=person.id,
                address_type='residencial_1',
                postal_code=zip_code,
                street=street or 'Não informado',
                number=getattr(data, 'address_number', None),
                complement=getattr(data, 'address_complement', None),
                neighborhood=getattr(data, 'neighborhood', None),
                city=city or 'Não informado',
                state=getattr(data, 'address_state', None) or 'XX',
                country='Brasil',
                is_primary=True,
            )
            self.db.add(address)

        # Criar athlete (V1.2: campos normalizados - sem documentos/contatos/endereço diretos)
        athlete = Athlete(
            id=uuid4(),
            person_id=person.id,
            organization_id=organization_id,  # V1.2: rastreia qual organização cadastrou
            state=AthleteState.ATIVA.value,
            injured=False,
            medical_restriction=False,
            load_restricted=False,
            athlete_name=data.athlete_name,
            athlete_nickname=data.athlete_nickname,
            birth_date=birth_date,
            # V1.2 CANÔNICO: Documentos (CPF, RG) em person_documents
            # V1.2 CANÔNICO: Contatos (telefone, email) em person_contacts
            # V1.2 CANÔNICO: Endereço em person_addresses
            shirt_number=data.shirt_number,
            main_defensive_position_id=data.main_defensive_position_id,
            secondary_defensive_position_id=data.secondary_defensive_position_id,
            main_offensive_position_id=data.main_offensive_position_id,
            secondary_offensive_position_id=data.secondary_offensive_position_id,
            schooling_id=getattr(data, 'schooling_id', None),
            guardian_name=getattr(data, 'guardian_name', None),
            guardian_phone=getattr(data, 'guardian_phone', None),
        )
        self.db.add(athlete)
        await self.db.flush()

        # RF1.1: Criar team_registration SOMENTE se team_id informado
        if data.team_id:
            # Validar que team pertence à organização
            team = await self.db.scalar(
                select(Team).where(
                    Team.id == data.team_id,
                    Team.organization_id == organization_id,
                    Team.deleted_at.is_(None)
                )
            )
            if not team:
                raise ValueError("team_not_found")

            # RDB10: TeamRegistration NÃO tem category_id (V1.2)
            registration = TeamRegistration(
                id=uuid4(),
                athlete_id=athlete.id,
                team_id=data.team_id,
                start_at=datetime.now(timezone.utc),
            )
            self.db.add(registration)

        await self.db.commit()
        await self.db.refresh(athlete)

        return await self._to_response(athlete, organization_id)

    # =========================================================================
    # ATUALIZAR ATLETA
    # =========================================================================

    async def update_athlete(
        self,
        athlete_id: UUID,
        data: AthleteUpdate,
        updated_by_membership_id: Optional[UUID] = None,
    ) -> Optional[AthleteResponse]:
        """Atualiza atleta."""
        athlete = await self.db.scalar(
            select(Athlete).where(
                Athlete.id == athlete_id,
                Athlete.deleted_at.is_(None)
            )
        )
        
        if not athlete:
            return None

        # Validar RD13 se alterando posições
        update_data = data.model_dump(exclude_unset=True)
        
        new_defensive = update_data.get('main_defensive_position_id', athlete.main_defensive_position_id)
        new_offensive = update_data.get('main_offensive_position_id', athlete.main_offensive_position_id)
        
        if new_defensive == 5 and new_offensive:  # Goleira com posição ofensiva
            raise ValueError("goleira_no_offensive_position")

        # Aplicar updates
        for field, value in update_data.items():
            if hasattr(athlete, field):
                setattr(athlete, field, value)

        athlete.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(athlete)

        return await self._to_response(athlete)

    # =========================================================================
    # MUDAR ESTADO (R12, R13)
    # =========================================================================

    async def change_state(
        self,
        athlete_id: UUID,
        new_state: AthleteStateEnum,
        reason: Optional[str] = None,
        changed_by_membership_id: Optional[UUID] = None,
    ) -> Optional[AthleteResponse]:
        """
        Altera o estado de uma atleta.
        
        CANÔNICO (R12, R13):
        - Estados válidos: ativa, dispensada, arquivada
        - Ao mudar para 'dispensada', ENCERRA automaticamente todos os team_registrations ativos
        - 'lesionada' NÃO é estado, é flag (injured=true)
        
        Args:
            athlete_id: UUID do atleta
            new_state: Novo estado (ativa, dispensada, arquivada)
            reason: Motivo da mudança (obrigatório para dispensada/arquivada)
            changed_by_membership_id: Membership que fez a mudança (auditoria)
            
        Returns:
            AthleteResponse atualizado ou None se não encontrado
            
        Raises:
            ValueError: "reason_required" se dispensada/arquivada sem motivo
        """
        athlete = await self.db.scalar(
            select(Athlete).where(
                Athlete.id == athlete_id,
                Athlete.deleted_at.is_(None)
            )
        )
        
        if not athlete:
            return None
        
        # Validar que motivo é obrigatório para dispensada/arquivada
        if new_state in (AthleteStateEnum.DISPENSADA, AthleteStateEnum.ARQUIVADA):
            if not reason:
                raise ValueError("reason_required")
        
        old_state = athlete.state
        athlete.state = new_state.value
        athlete.updated_at = datetime.now(timezone.utc)
        
        # R13: Se mudando para 'dispensada', encerrar todos os team_registrations ativos
        if new_state == AthleteStateEnum.DISPENSADA:
            closed_count = await self._close_active_registrations(athlete_id)
            # Também limpar organization_id derivado
            athlete.organization_id = None
        
        await self.db.commit()
        await self.db.refresh(athlete)
        
        return await self._to_response(athlete)
    
    async def _close_active_registrations(self, athlete_id: UUID) -> int:
        """
        Encerra todos os team_registrations ativos de uma atleta.
        
        CANÔNICO (R13 V1.1): Chamado quando estado muda para 'dispensada'.
        
        Args:
            athlete_id: UUID do atleta
            
        Returns:
            Quantidade de registrations encerrados
        """
        result = await self.db.execute(
            TeamRegistration.__table__.update()
            .where(
                TeamRegistration.athlete_id == athlete_id,
                TeamRegistration.end_at.is_(None)
            )
            .values(end_at=date.today())
            .returning(TeamRegistration.id)
        )
        return len(list(result))

    # =========================================================================
    # SOFT DELETE
    # =========================================================================

    async def soft_delete(
        self,
        athlete_id: UUID,
        reason: str = "Exclusão manual",
        deleted_by_membership_id: Optional[UUID] = None,
    ) -> bool:
        """Soft delete de atleta (RDB4)."""
        athlete = await self.db.scalar(
            select(Athlete).where(
                Athlete.id == athlete_id,
                Athlete.deleted_at.is_(None)
            )
        )
        
        if not athlete:
            return False

        athlete.deleted_at = datetime.now(timezone.utc)
        athlete.deleted_reason = reason
        
        # Encerrar todos os team_registrations ativos
        await self.db.execute(
            TeamRegistration.__table__.update()
            .where(
                TeamRegistration.athlete_id == athlete_id,
                TeamRegistration.end_at.is_(None)
            )
            .values(end_at=datetime.now(timezone.utc))
        )
        
        await self.db.commit()
        return True

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _calculate_age(self, birth_date: date, reference_date: Optional[date] = None) -> int:
        """Calcula idade em anos completos."""
        if reference_date is None:
            reference_date = date.today()
        
        age = reference_date.year - birth_date.year
        if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

    async def _to_response(self, athlete: Athlete, organization_id: Optional[UUID] = None) -> AthleteResponse:
        """Converte Athlete para AthleteResponse."""
        # Buscar team_registrations ativos
        result = await self.db.scalars(
            select(TeamRegistration)
            .where(
                TeamRegistration.athlete_id == athlete.id,
                TeamRegistration.end_at.is_(None),
                TeamRegistration.deleted_at.is_(None)
            )
        )
        registrations = result.all()
        
        # V1.2 (Opção B): usar organization_id do modelo Athlete (sempre presente)
        # Se não fornecido como parâmetro, buscar do modelo
        if not organization_id:
            organization_id = athlete.organization_id
        
        # Fallback: determinar via team_registrations se ainda não tiver
        if not organization_id and registrations:
            team = await self.db.scalar(select(Team).where(Team.id == registrations[0].team_id))
            organization_id = team.organization_id if team else None

        # Buscar documentos da pessoa (CPF, RG)
        athlete_cpf = None
        athlete_rg = None
        if athlete.person_id:
            cpf_doc = await self.db.scalar(
                select(PersonDocument).where(
                    PersonDocument.person_id == athlete.person_id,
                    PersonDocument.document_type == 'cpf',
                    PersonDocument.deleted_at.is_(None)
                )
            )
            rg_doc = await self.db.scalar(
                select(PersonDocument).where(
                    PersonDocument.person_id == athlete.person_id,
                    PersonDocument.document_type == 'rg',
                    PersonDocument.deleted_at.is_(None)
                )
            )
            athlete_cpf = cpf_doc.document_number if cpf_doc else None
            athlete_rg = rg_doc.document_number if rg_doc else None
        
        # Buscar contatos da pessoa (telefone, email)
        athlete_phone = None
        athlete_email = None
        if athlete.person_id:
            phone_contact = await self.db.scalar(
                select(PersonContact).where(
                    PersonContact.person_id == athlete.person_id,
                    PersonContact.contact_type == 'telefone',
                    PersonContact.deleted_at.is_(None)
                )
            )
            email_contact = await self.db.scalar(
                select(PersonContact).where(
                    PersonContact.person_id == athlete.person_id,
                    PersonContact.contact_type == 'email',
                    PersonContact.deleted_at.is_(None)
                )
            )
            athlete_phone = phone_contact.contact_value if phone_contact else None
            athlete_email = email_contact.contact_value if email_contact else None
        
        # Buscar endereço principal da pessoa
        address = None
        if athlete.person_id:
            address = await self.db.scalar(
                select(PersonAddress).where(
                    PersonAddress.person_id == athlete.person_id,
                    PersonAddress.is_primary == True,
                    PersonAddress.deleted_at.is_(None)
                )
            )

        # CANÔNICO: Buscar gênero de persons.gender
        person_gender = None
        if athlete.person_id:
            person = await self.db.get(Person, athlete.person_id)
            person_gender = person.gender if person else None

        return AthleteResponse(
            id=athlete.id,
            person_id=athlete.person_id,
            organization_id=organization_id,
            state=AthleteStateEnum(athlete.state),
            injured=athlete.injured,
            medical_restriction=athlete.medical_restriction,
            suspended_until=athlete.suspended_until,
            load_restricted=athlete.load_restricted,
            athlete_name=athlete.athlete_name,
            athlete_nickname=athlete.athlete_nickname,
            birth_date=athlete.birth_date,
            gender=person_gender,  # CANÔNICO: Gênero de persons.gender
            athlete_rg=athlete_rg,
            athlete_cpf=athlete_cpf,
            athlete_phone=athlete_phone,
            athlete_email=athlete_email,
            shirt_number=athlete.shirt_number,
            main_defensive_position_id=athlete.main_defensive_position_id,
            secondary_defensive_position_id=athlete.secondary_defensive_position_id,
            main_offensive_position_id=athlete.main_offensive_position_id,
            secondary_offensive_position_id=athlete.secondary_offensive_position_id,
            schooling_id=athlete.schooling_id,
            guardian_name=athlete.guardian_name,
            guardian_phone=athlete.guardian_phone,
            # Campos de endereço agora vem de person_addresses
            zip_code=address.postal_code if address else None,
            street=address.street if address else None,
            neighborhood=address.neighborhood if address else None,
            city=address.city if address else None,
            address_state=address.state if address else None,
            address_number=address.number if address else None,
            address_complement=address.complement if address else None,
            athlete_photo_path=athlete.athlete_photo_path,
            athlete_age=athlete.current_age,
            athlete_age_at_registration=athlete.athlete_age_at_registration,
            registered_at=athlete.registered_at,
            created_at=athlete.created_at,
            updated_at=athlete.updated_at,
            deleted_at=athlete.deleted_at,
            # team_registrations será None por enquanto
            team_registrations=None,
        )

    # =========================================================================
    # ESTATÍSTICAS PARA DASHBOARD (FASE 2)
    # =========================================================================

    async def get_stats(self, organization_id: UUID) -> dict:
        """
        Retorna estatísticas de atletas para dashboard.
        
        REGRAS:
        - R12: Estados operacionais (ativa, dispensada, arquivada)
        - R13: Flags de restrição (injured, medical_restriction, suspended_until, load_restricted)
        - RF1.1: Atletas sem equipe (em captação)
        """
        from datetime import date as date_type
        
        # Subquery para atletas com team_registration ativo na organização
        subq_with_team = (
            select(TeamRegistration.athlete_id)
            .join(Team, Team.id == TeamRegistration.team_id)
            .where(
                Team.organization_id == organization_id,
                TeamRegistration.end_at.is_(None),
                TeamRegistration.deleted_at.is_(None)
            )
        )
        
        # Todos os atletas da organização
        all_athletes_query = select(Athlete).where(
            or_(
                Athlete.id.in_(subq_with_team),
                Athlete.organization_id == organization_id
            ),
            Athlete.deleted_at.is_(None)
        )
        
        result = await self.db.scalars(all_athletes_query)
        all_athletes = list(result.all())
        
        # IDs de atletas com equipe
        result_with_team = await self.db.scalars(subq_with_team)
        athletes_with_team_ids = set(result_with_team.all())
        
        today = date_type.today()
        
        # Contadores
        total = len(all_athletes)
        em_captacao = 0
        lesionadas = 0
        suspensas = 0
        ativas = 0
        dispensadas = 0
        arquivadas = 0
        com_restricao_medica = 0
        carga_restrita = 0
        por_categoria = {}
        
        for athlete in all_athletes:
            # Em captação: sem team_registration ativo
            if athlete.id not in athletes_with_team_ids:
                em_captacao += 1
            
            # Flags
            if athlete.injured:
                lesionadas += 1
            if athlete.suspended_until and athlete.suspended_until >= today:
                suspensas += 1
            if athlete.medical_restriction:
                com_restricao_medica += 1
            if athlete.load_restricted:
                carga_restrita += 1
            
            # Estados
            if athlete.state == AthleteState.ATIVA:
                ativas += 1
            elif athlete.state == AthleteState.DISPENSADA:
                dispensadas += 1
            elif athlete.state == AthleteState.ARQUIVADA:
                arquivadas += 1
            
            # Por categoria (baseado na equipe ativa via team_registrations)
            # Buscar categoria da equipe ativa do atleta
            active_reg = await self.db.scalar(
                select(TeamRegistration).where(
                    TeamRegistration.athlete_id == athlete.id,
                    TeamRegistration.end_at.is_(None),
                    TeamRegistration.deleted_at.is_(None)
                )
            )
            if active_reg:
                team = await self.db.scalar(select(Team).where(Team.id == active_reg.team_id))
                if team and team.category_id:
                    cat = await self.db.get(Category, team.category_id)
                    if cat:
                        cat_name = cat.name
                        por_categoria[cat_name] = por_categoria.get(cat_name, 0) + 1
        
        return {
            "total": total,
            "em_captacao": em_captacao,
            "lesionadas": lesionadas,
            "suspensas": suspensas,
            "ativas": ativas,
            "dispensadas": dispensadas,
            "arquivadas": arquivadas,
            "com_restricao_medica": com_restricao_medica,
            "carga_restrita": carga_restrita,
            "por_categoria": por_categoria,
        }
