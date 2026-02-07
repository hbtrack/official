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
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Column, String, Date, Text, DateTime, Boolean, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    # PK (RDB2)
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    # Dados básicos (R1) - V1.2 Normalizado
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), server_default="brasileira", nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Soft delete (RDB4)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps (RDB3)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

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
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    
    person_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False
    )
    
    contact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    contact_value: Mapped[str] = mapped_column(String(200), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
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
    
    __table_args__ = (
        CheckConstraint(
            "address_type IN ('residencial_1', 'residencial_2', 'comercial', 'outro')",
            name='ck_person_addresses_type'
        ),
        CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_person_addresses_deleted_reason'
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    
    person_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False
    )
    
    address_type: Mapped[str] = mapped_column(String(50), nullable=False)
    street: Mapped[str] = mapped_column(String(200), nullable=False)
    number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    complement: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    neighborhood: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    postal_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    country: Mapped[str] = mapped_column(String(100), server_default="Brasil", nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
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
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    
    person_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False
    )
    
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    document_number: Mapped[str] = mapped_column(String(100), nullable=False)
    issuing_authority: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    issue_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    document_file_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
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
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    
    person_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False
    )
    
    media_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    person: Mapped["Person"] = relationship("Person", back_populates="media")
    
    def __repr__(self) -> str:
        return f"<PersonMedia(id={self.id}, type={self.media_type}, file={self.file_name!r})>"
