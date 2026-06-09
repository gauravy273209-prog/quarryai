from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse

router = APIRouter()


@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(
    organization_id: UUID,
    payload: AgentCreate,
    db: AsyncSession = Depends(get_db)
):
    agent = Agent(organization_id=organization_id, **payload.model_dump())
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    organization_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Agent).where(Agent.organization_id == organization_id)
    )
    return result.scalars().all()


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    organization_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.organization_id == organization_id
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    organization_id: UUID,
    payload: AgentUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.organization_id == organization_id
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(agent, key, value)
    await db.commit()
    await db.refresh(agent)
    return agent


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: UUID,
    organization_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.organization_id == organization_id
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    await db.delete(agent)
    await db.commit()