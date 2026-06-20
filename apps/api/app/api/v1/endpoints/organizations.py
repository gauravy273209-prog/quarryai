from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.organization import Organization
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse
)

router = APIRouter()


@router.post('/', response_model=OrganizationResponse, status_code=201)
async def create_organization(
    payload: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    org = Organization(**payload.model_dump())
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@router.get('/', response_model=List[OrganizationResponse])
async def list_organizations(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    '''List organizations. Users can only see their own organization.'''
    from app.models.user import User
    clerk_user_id = current_user.get('sub')
    user_result = await db.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    result = await db.execute(
        select(Organization).where(Organization.id == user.organization_id)
    )
    return result.scalars().all()


@router.get('/{org_id}', response_model=OrganizationResponse)
async def get_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from app.models.user import User
    clerk_user_id = current_user.get('sub')
    user_result = await db.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    user = user_result.scalar_one_or_none()
    if not user or user.organization_id != org_id:
        raise HTTPException(status_code=403, detail='Access denied')
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail='Organization not found')
    return org


@router.put('/{org_id}', response_model=OrganizationResponse)
async def update_organization(
    org_id: UUID,
    payload: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from app.models.user import User
    clerk_user_id = current_user.get('sub')
    user_result = await db.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    user = user_result.scalar_one_or_none()
    if not user or user.organization_id != org_id:
        raise HTTPException(status_code=403, detail='Access denied')
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail='Organization not found')
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(org, key, value)
    await db.commit()
    await db.refresh(org)
    return org
