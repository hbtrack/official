from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class ExerciseTagBase(BaseModel):
    name: str
    parent_tag_id: Optional[UUID] = None
    description: Optional[str] = None
    display_order: Optional[int] = 0
    is_active: Optional[bool] = False

class ExerciseTagCreate(ExerciseTagBase):
    pass

class ExerciseTagUpdate(ExerciseTagBase):
    pass

class ExerciseTagResponse(ExerciseTagBase):
    id: UUID
    approved_by_admin_id: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    suggested_by_user_id: Optional[UUID] = None
    children: Optional[List['ExerciseTagResponse']] = None

    class Config:
        from_attributes = True

ExerciseTagResponse.update_forward_refs()
