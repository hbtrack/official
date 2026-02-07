from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

class ExerciseFavorite(Base):
    __tablename__ = 'exercise_favorites'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey('exercises.id'), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship('User', backref='exercise_favorites')
    exercise = relationship('Exercise', backref='favorited_by')
