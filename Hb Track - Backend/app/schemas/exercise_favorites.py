from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class ExerciseFavoriteCreate(BaseModel):
    exercise_id: UUID

class ExerciseFavoriteResponse(BaseModel):
    user_id: UUID
    exercise_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
