from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.models.base import Base


class Exercise(Base):
    """
    Banco de exercícios com tags hierárquicas.

    Constraints (definidos na migração 0036):
    - PK: id
    - FK: organization_id → organizations (CASCADE)
    - FK: created_by_user_id → users (CASCADE)
    - GIN INDEX: idx_exercises_tags em tag_ids
    """
    __tablename__ = 'exercises'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey('organizations.id', ondelete='CASCADE'),
        nullable=False
    )
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    tag_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False, server_default='{}')
    category = Column(String(100), nullable=True)
    media_url = Column(String(500), nullable=True)
    created_by_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship('User', backref='created_exercises', foreign_keys=[created_by_user_id])
    organization = relationship('Organization', backref='exercises')
    session_usages = relationship(
        'SessionExercise',
        back_populates='exercise',
        lazy='selectin'
    )
