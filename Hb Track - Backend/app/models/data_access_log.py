"""
Model: DataAccessLog

Tabela data_access_logs para auditoria LGPD.

Criada em: Step 3 (migration 0036_lgpd_gamif_infra.py)

Regra LGPD: Registra apenas staff reading outros, NÃO self-access.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.athlete import Athlete


class DataAccessLog(Base):
    """
    Log de acesso a dados sensíveis para compliance LGPD.
    
    Registra quando staff acessa dados de atletas/wellness.
    NÃO registra quando atleta acessa próprios dados (self-access).
    """
    __tablename__ = "data_access_logs"
    
    # PK
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )
    
    # FK para usuário que acessou
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    # Tipo de entidade acessada
    entity_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )
    
    # ID da entidade acessada
    entity_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False
    )
    
    # FK para atleta (se acesso for relacionado a atleta específico)
    athlete_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("athletes.id"),
        nullable=True,
        index=True
    )
    
    # Timestamp do acesso
    accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        index=True
    )
    
    # IP address do acesso
    ip_address: Mapped[Optional[str]] = mapped_column(
        INET,
        nullable=True
    )
    
    # User agent
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="selectin"
    )
    
    athlete: Mapped[Optional["Athlete"]] = relationship(
        "Athlete",
        foreign_keys=[athlete_id],
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<DataAccessLog {self.id} user={self.user_id} entity={self.entity_type}:{self.entity_id}>"
