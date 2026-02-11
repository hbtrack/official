"""
Model: Person (R1) - V1.2 Normalizado

Referências RAG:
- R1: Pessoa é entidade raiz (pode ser atleta ou não)
- RDB2: PKs são UUID v4 server-generated
- RDB3: Timestamps em UTC
- RDB4: Soft delete obrigatório

V1.2: Estrutura normalizada
- persons: identidade básica (nome, gênero, nascimento)
- person_contacts: telefone, email, whatsapp (1:N)
- person_addresses: endereços residenciais (1:N)
- person_documents: CPF, RG, CNH, passaporte (1:N)
- person_media: fotos de perfil e documentos (1:N)
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Person(Base):
    """
    Model Person - Pessoas/Entidades físicas do sistema (V1.2 Normalizado)

    Representa uma pessoa física no sistema (R1). Pode ser vinculada a um usuário
    e assumir diferentes papéis através de memberships.
    
    V1.2: Dados especializados movidos para tabelas dedicadas:
    - Contatos → person_contacts
    - Endereços → person_addresses
    - Documentos → person_documents
    - Mídias → person_media
    """
    __tablename__ = "persons"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.persons
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_persons_deleted_reason'),
        CheckConstraint("gender IS NULL OR (gender::text = ANY (ARRAY['masculino'::character varying, 'feminino'::character varying, 'outro'::character varying, 'prefiro_nao_dizer'::character varying]::text[]))", name='ck_persons_gender'),
        Index('ix_persons_birth_date', 'birth_date', unique=False),
        Index('ix_persons_deleted_at', 'deleted_at', unique=False),
        Index('ix_persons_first_name', 'first_name', unique=False),
        Index('ix_persons_first_name_trgm', 'first_name', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),
        Index('ix_persons_full_name_trgm', 'full_name', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),
        Index('ix_persons_last_name', 'last_name', unique=False),
        Index('ix_persons_last_name_trgm', 'last_name', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    full_name: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    birth_date: Mapped[Optional[date]] = mapped_column(sa.Date(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    first_name: Mapped[str] = mapped_column(sa.String(length=100), nullable=False)
    last_name: Mapped[str] = mapped_column(sa.String(length=100), nullable=False)
    gender: Mapped[Optional[str]] = mapped_column(sa.String(length=20), nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(sa.String(length=100), nullable=True, server_default=sa.text("'brasileira'::character varying"))
    notes: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    # HB-AUTOGEN:END
    # PK (RDB2)

    # Dados básicos (R1) - V1.2 Normalizado

    # Soft delete (RDB4)

    # Timestamps (RDB3)

    # Relationships - User
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="person",
        uselist=False,
        lazy="selectin",
    )
    
    # Relationships - V1.2 Normalized tables
    contacts: Mapped[List["PersonContact"]] = relationship(
        "PersonContact",
        back_populates="person",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    addresses: Mapped[List["PersonAddress"]] = relationship(
        "PersonAddress",
        back_populates="person",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    documents: Mapped[List["PersonDocument"]] = relationship(
        "PersonDocument",
        back_populates="person",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    media: Mapped[List["PersonMedia"]] = relationship(
        "PersonMedia",
        back_populates="person",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Person(id={self.id}, full_name={self.full_name!r})>"
    
    @property
    def primary_phone(self) -> Optional[str]:
        """Retorna o telefone primário da pessoa"""
        for contact in self.contacts:
            if contact.contact_type == 'telefone' and contact.is_primary and not contact.deleted_at:
                return contact.contact_value
        return None
    
    @property
    def primary_email(self) -> Optional[str]:
        """Retorna o email primário da pessoa"""
        for contact in self.contacts:
            if contact.contact_type == 'email' and contact.is_primary and not contact.deleted_at:
                return contact.contact_value
        return None
    
    @property
    def cpf(self) -> Optional[str]:
        """Retorna o CPF da pessoa (compatibilidade)"""
        for doc in self.documents:
            if doc.document_type == 'cpf' and not doc.deleted_at:
                return doc.document_number
        return None
    
    @property
    def primary_address(self) -> Optional["PersonAddress"]:
        """Retorna o endereço primário da pessoa"""
        for addr in self.addresses:
            if addr.is_primary and not addr.deleted_at:
                return addr
        return None
    
    @property
    def profile_photo(self) -> Optional[str]:
        """Retorna a URL da foto de perfil primária"""
        for media in self.media:
            if media.media_type == 'foto_perfil' and media.is_primary and not media.deleted_at:
                return media.file_url
        # Se não tiver primária, retorna a primeira foto de perfil
        for media in self.media:
            if media.media_type == 'foto_perfil' and not media.deleted_at:
                return media.file_url
        return None


class PersonContact(Base):
    """
    Model PersonContact - Contatos da pessoa (V1.2)
    
    Suporta múltiplos contatos por pessoa:
    - telefone
    - email
    - whatsapp
    - outro
    """
    __tablename__ = "person_contacts"
    
    __table_args__ = (
        CheckConstraint(
            "contact_type IN ('telefone', 'email', 'whatsapp', 'outro')",
            name='ck_person_contacts_type'
        ),
        CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_person_contacts_deleted_reason'
        ),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    
    
    # Timestamps
    
    # Soft delete
    
    # Relationships
    person: Mapped["Person"] = relationship("Person", back_populates="contacts")
    
    def __repr__(self) -> str:
        return f"<PersonContact(id={self.id}, type={self.contact_type}, value={self.contact_value!r})>"


class PersonAddress(Base):
    """
    Model PersonAddress - Endereços da pessoa (V1.2)
    
    Suporta múltiplos endereços por pessoa:
    - residencial_1
    - residencial_2
    - comercial
    - outro
    """
    __tablename__ = "person_addresses"
    

# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.person_addresses
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_person_addresses_deleted_reason'),
        CheckConstraint("address_type::text = ANY (ARRAY['residencial_1'::character varying, 'residencial_2'::character varying, 'comercial'::character varying, 'outro'::character varying]::text[])", name='ck_person_addresses_type'),
        Index('ix_person_addresses_city_state', 'city', 'state', unique=False),
        Index('ix_person_addresses_created_by_user_id', 'created_by_user_id', unique=False),
        Index('ix_person_addresses_deleted_at', 'deleted_at', unique=False),
        Index('ix_person_addresses_person_id', 'person_id', unique=False),
        Index('uq_person_addresses_primary', 'person_id', unique=True, postgresql_where=sa.text('((is_primary = true) AND (deleted_at IS NULL))')),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    person_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('persons.id', name='person_addresses_person_id_fkey', ondelete='CASCADE'), nullable=False)
    address_type: Mapped[str] = mapped_column(sa.String(length=50), nullable=False)
    street: Mapped[str] = mapped_column(sa.String(length=200), nullable=False)
    number: Mapped[Optional[str]] = mapped_column(sa.String(length=20), nullable=True)
    complement: Mapped[Optional[str]] = mapped_column(sa.String(length=100), nullable=True)
    neighborhood: Mapped[Optional[str]] = mapped_column(sa.String(length=100), nullable=True)
    city: Mapped[str] = mapped_column(sa.String(length=100), nullable=False)
    state: Mapped[str] = mapped_column(sa.String(length=2), nullable=False)
    postal_code: Mapped[Optional[str]] = mapped_column(sa.String(length=10), nullable=True)
    country: Mapped[str] = mapped_column(sa.String(length=100), nullable=False, server_default=sa.text("'Brasil'::character varying"))
    is_primary: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('false'))
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    created_by_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_person_addresses_created_by_user', ondelete='SET NULL'), nullable=True)
    # HB-AUTOGEN:END

    
    # Timestamps
    
    # Soft delete
    
    # Relationships
    person: Mapped["Person"] = relationship("Person", back_populates="addresses")
    
    def __repr__(self) -> str:
        return f"<PersonAddress(id={self.id}, type={self.address_type}, city={self.city!r})>"


class PersonDocument(Base):
    """
    Model PersonDocument - Documentos oficiais da pessoa (V1.2)
    
    Suporta múltiplos documentos por pessoa:
    - cpf
    - rg
    - cnh
    - passaporte
    - certidao_nascimento
    - titulo_eleitor
    - outro
    """
    __tablename__ = "person_documents"
    
    __table_args__ = (
        CheckConstraint(
            "document_type IN ('cpf', 'rg', 'cnh', 'passaporte', 'certidao_nascimento', 'titulo_eleitor', 'outro')",
            name='ck_person_documents_type'
        ),
        CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_person_documents_deleted_reason'
        ),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    
    
    # Timestamps
    
    # Soft delete
    
    # Relationships
    person: Mapped["Person"] = relationship("Person", back_populates="documents")
    
    def __repr__(self) -> str:
        return f"<PersonDocument(id={self.id}, type={self.document_type}, number={self.document_number!r})>"


class PersonMedia(Base):
    """
    Model PersonMedia - Mídias da pessoa (V1.2)
    
    Suporta múltiplas mídias por pessoa:
    - foto_perfil
    - foto_documento
    - video
    - outro
    """
    __tablename__ = "person_media"
    
    __table_args__ = (
        CheckConstraint(
            "media_type IN ('foto_perfil', 'foto_documento', 'video', 'outro')",
            name='ck_person_media_type'
        ),
        CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_person_media_deleted_reason'
        ),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    
    
    # Timestamps
    
    # Soft delete
    
    # Relationships
    person: Mapped["Person"] = relationship("Person", back_populates="media")
    
    def __repr__(self) -> str:
        return f"<PersonMedia(id={self.id}, type={self.media_type}, file={self.file_name!r})>"
