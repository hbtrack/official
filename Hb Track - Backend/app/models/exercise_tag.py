from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import Base

class ExerciseTag(Base):
    __tablename__ = 'exercise_tags'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    parent_tag_id = Column(UUID(as_uuid=True), ForeignKey('exercise_tags.id'), nullable=True)
    description = Column(String(255))
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=False)
    suggested_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    approved_by_admin_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    parent = relationship('ExerciseTag', remote_side=[id], backref='children')
    # Optionally, add relationships to User if needed
