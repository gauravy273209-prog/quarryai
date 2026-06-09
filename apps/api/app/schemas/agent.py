from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    voice_id: Optional[str] = None
    language: Optional[str] = "en"


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    voice_id: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None


class AgentResponse(AgentBase):
    id: UUID
    organization_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True