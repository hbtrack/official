"""
Model Athlete - Atletas do sistema.

Regras:
- R6: Atletas vinculam-se via team_registrations (vínculo esportivo)
- R12: Papel atleta permanente no histórico
- R13/R14: Estados (ativa, lesionada, dispensada) - via athlete_state_history
- RF1.1: Atleta pode ser cadastrada sem equipe (vínculo opcional)
- R32: Atleta sem team_registration não opera
- RDB4: Soft delete obrigatório
- RDB7: Histórico de estados dedicado
- RD13: Goleiras não têm posição ofensiva

ESTRUTURA CANÔNICA (V1.2 Normalizada - 31/12/2025):
- id (uuid, PK)
- person_id (uuid, FK, NOT NULL)
- organization_id (uuid, FK, NULL) - DERIVADO automaticamente de team_registrations
- state (varchar, NOT NULL) - 'ativa', 'dispensada', 'arquivada'
- injured (boolean, NOT NULL)
- medical_restriction (boolean, NOT NULL)
- suspended_until (date, NULL)
- load_restricted (boolean, NOT NULL)
- athlete_name (varchar, NOT NULL)
- birth_date (date, NOT NULL)
- athlete_nickname, shirt_number (NULL)
- main_defensive_position_id, secondary_defensive_position_id (FK, NULL)
- main_offensive_position_id, secondary_offensive_position_id (FK, NULL)
- schooling_id (FK, NULL)
- guardian_name, guardian_phone (NULL)
- athlete_photo_path (NULL)
- registered_at (timestamptz, NOT NULL)
- athlete_age_at_registration (int, NULL)
- created_at, updated_at (timestamptz, NOT NULL)
- deleted_at (timestamptz, NULL), deleted_reason (text, NULL)

CAMPOS REMOVIDOS (usar tabelas normalizadas):
- athlete_rg, athlete_cpf → person_documents
- athlete_phone, athlete_email → person_contacts
- zip_code, street, neighborhood, city, state_address, address_number, address_complement → person_addresses
"""
from datetime import datetime, timezone, date
from typing import Optional, TYPE_CHECKING
from uuid import uuid4
from enum import Enum

from sqlalchemy import String, Date, DateTime, ForeignKey, Text, CheckConstraint, Integer, Boolean, text
from sqlalchemy.schema import FetchedValue
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.person import Person
    from app.models.team_registration import TeamRegistration


class AthleteState(str, Enum):
    """
    Estados possíveis do atleta (R12, REGRAS.md V1.2).
    
    IMPORTANTE: 'lesionada' NÃO é um estado - é uma flag (injured=true).
    Estados base são: ativa, dispensada, arquivada.
    """
    ATIVA = "ativa"
    DISPENSADA = "dispensada"
    ARQUIVADA = "arquivada"


class Athlete(Base):
    """
    Representa um atleta no sistema.

    Estrutura real do banco de dados V1.2.
    """
    __tablename__ = "athletes"

    __table_args__ = (
        CheckConstraint(
            "((state)::text = ANY ((ARRAY['ativa'::character varying,"
            "'dispensada'::character varying,"
            "'arquivada'::character varying])::text[]))",
            name="ck_athletes_state"
        ),
        CheckConstraint(
            "((shirt_number IS NULL) OR ((shirt_number >= 1) AND (shirt_number <= 99)))",
            name="ck_athletes_shirt_number"
        ),
        CheckConstraint(
            "(((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR "
            "((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))",
            name="ck_athletes_deleted_reason",
        ),
    )

    # ==================== IDENTIFICAÇÃO (SISTEMA) ====================
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("public.gen_random_uuid()"),
    )

    person_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", name="fk_athletes_person_id", ondelete="RESTRICT"),
        nullable=False
    )
    
    # CANÔNICO: organization_id é DERIVADO automaticamente de team_registrations
    # - Quando atleta tem vínculo ativo: organization_id = teams.organization_id
    # - Quando atleta sem vínculo ativo: organization_id = NULL
    # - Campo desnormalizado intencionalmente para facilitar queries
    # - NUNCA editar manualmente; sempre atualizado por lógica de negócio
    organization_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", name="fk_athletes_organization_id", ondelete="RESTRICT"),
        nullable=True
    )

    # ==================== STATUS E CONDIÇÃO ====================
    state: Mapped[str] = mapped_column(
        String(20),
        default=AthleteState.ATIVA.value,
        server_default=text("'ativa'::character varying"),
        nullable=False
    )
    
    injured: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)
    medical_restriction: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)
    suspended_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    load_restricted: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)

    # ==================== DADOS PESSOAIS ====================
    athlete_name: Mapped[str] = mapped_column(String(100), nullable=False)
    athlete_nickname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)

    # ==================== NÚMERO DA CAMISA ====================
    shirt_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # NOTA: Documentos (RG, CPF) estão em person_documents
    # NOTA: Contatos (telefone, email) estão em person_contacts

    # ==================== POSIÇÕES (FK PARA TABELAS AUXILIARES) ====================
    main_defensive_position_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("defensive_positions.id", name="fk_athletes_main_defensive_position_id", ondelete="SET NULL"),
        nullable=True
    )

    secondary_defensive_position_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("defensive_positions.id", name="fk_athletes_secondary_defensive_position_id", ondelete="SET NULL"),
        nullable=True
    )

    main_offensive_position_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("offensive_positions.id", name="fk_athletes_main_offensive_position_id", ondelete="SET NULL"),
        nullable=True
    )

    secondary_offensive_position_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("offensive_positions.id", name="fk_athletes_secondary_offensive_position_id", ondelete="SET NULL"),
        nullable=True
    )

    # ==================== ESCOLARIDADE ====================
    schooling_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("schooling_levels.id", name="fk_athletes_schooling_id", ondelete="SET NULL"),
        nullable=True
    )

    # ==================== RESPONSÁVEL ====================
    guardian_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    guardian_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # NOTA: Endereços estão em person_addresses

    # ==================== FOTO ====================
    athlete_photo_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ==================== TIMESTAMPS E REGISTRO ====================
    registered_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False
    )

    athlete_age_at_registration: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Idade no momento do registro (calculado automaticamente por trigger)"
        # trigger preenche em INSERT/UPDATE
        , server_default=FetchedValue()
        , server_onupdate=FetchedValue()
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        server_onupdate=FetchedValue(),  # trigger trg_set_updated_at
        nullable=False
    )

    # ==================== SOFT DELETE ====================
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ==================== RELATIONSHIPS ====================
    team_registrations: Mapped[list["TeamRegistration"]] = relationship(
        "TeamRegistration",
        back_populates="athlete",
        lazy="selectin"
    )
    
    wellness_posts = relationship(
        "WellnessPost",
        back_populates="athlete",
        lazy="selectin"
    )

    person: Mapped["Person"] = relationship(
        "Person",
        lazy="selectin",
    )
    
    medical_cases = relationship(
        "MedicalCase",
        back_populates="athlete",
        lazy="selectin"
    )

    # ==================== HELPERS ====================
    @property
    def is_active_athlete(self) -> bool:
        """Retorna True se atleta não foi soft-deleted."""
        return self.deleted_at is None

    @property
    def current_state(self) -> AthleteState:
        """Retorna o estado atual como enum."""
        return AthleteState(self.state)

    @property
    def is_goalkeeper(self) -> bool:
        """Retorna True se a posição defensiva principal é goleira (id=5)."""
        return self.main_defensive_position_id == 5

    def calculate_age(self, reference_date: Optional[date] = None) -> int:
        """
        Calcula idade da atleta em uma data de referência.

        Args:
            reference_date: Data de referência (padrão: hoje)

        Returns:
            Idade em anos completos
        """
        if reference_date is None:
            reference_date = date.today()

        age = reference_date.year - self.birth_date.year

        # Ajustar se ainda não fez aniversário no ano de referência
        if (reference_date.month, reference_date.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1

        return age

    @property
    def current_age(self) -> int:
        """Calcula idade atual."""
        return self.calculate_age()

    def __repr__(self) -> str:
        return f"<Athlete {self.athlete_name} ({self.state})>"
