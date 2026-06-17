import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.agent import Agent
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse

router = APIRouter()

async def get_user_org_id(current_user: dict, db: AsyncSession) -> uuid.UUID:
    """Get the organization_id for the current Clerk user."""
    clerk_user_id = current_user.get("sub")
    result = await db.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found in database")
    return user.organization_id
@router.get("/internal/{clerk_user_id}/{agent_id}", response_model=AgentResponse)
async def get_agent_internal(
    clerk_user_id: str,
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.organization_id == user.organization_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent
@router.get("/", response_model=list[AgentResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    org_id = await get_user_org_id(current_user, db)
    result = await db.execute(select(Agent).where(Agent.organization_id == org_id))
    return result.scalars().all()

@router.post("/", response_model=AgentResponse)
async def create_agent(
    payload: AgentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    org_id = await get_user_org_id(current_user, db)
    agent = Agent(**payload.model_dump(), organization_id=org_id)
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    org_id = await get_user_org_id(current_user, db)
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.organization_id == org_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: uuid.UUID,
    payload: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    org_id = await get_user_org_id(current_user, db)
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.organization_id == org_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(agent, key, value)
    await db.commit()
    await db.refresh(agent)
    return agent

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    org_id = await get_user_org_id(current_user, db)
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.organization_id == org_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    await db.delete(agent)
    await db.commit()
    return {"message": "Agent deleted successfully"}
