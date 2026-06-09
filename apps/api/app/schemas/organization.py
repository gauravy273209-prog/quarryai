from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class OrganizationBase(BaseModel):
    name: str
    slug: str
    plan: Optional[str] = "free"


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationResponse(OrganizationBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True