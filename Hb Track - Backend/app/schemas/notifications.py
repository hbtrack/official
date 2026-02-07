"""
Schemas para notificações.

Step 14: Pydantic schemas para requests/responses de notificações.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NotificationResponse(BaseModel):
    """Response de uma notificação."""
    id: UUID
    type: str = Field(..., description="Tipo: team_assignment, coach_removal, invite, etc")
    message: str
    notification_data: Optional[dict] = Field(None, description="Dados adicionais (team_id, team_name, etc)")
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Response paginado de notificações."""
    items: list[NotificationResponse]
    total: int = Field(..., description="Total de notificações (lidas + não lidas)")
    unread_count: int = Field(..., description="Contador de não lidas")
    page: int
    limit: int
