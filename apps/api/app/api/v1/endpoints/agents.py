import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.agent import Agent
from app.models.user import User
from app.models.organization import Organization
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse

router = APIRouter()


async def get_or_create_user(current_user: dict, db: AsyncSession) -> User:
    """Get existing user or auto-create on first login (upsert)."""
    clerk_user_id = current_user.get("sub", "")
    email = current_user.get("email", "") or current_user.get("primary_email", "") or ""

    result = await db.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    user = result.scalar_one_or_none()
    if user:
        return user

    # First time this user hits the API — auto-create org + user
    org_result = await db.execute(select(Organization).limit(1))
    org = org_result.scalar_one_or_none()
    if not org:
        org = Organization(name="Default Organization", slug="default-org", plan="free")
        db.add(org)
        await db.flush()

    user = User(
        organization_id=org.id,
        clerk_user_id=clerk_user_id,
        email=email,
        full_name=current_user.get("name", "") or "",
        role="member",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_org_id(current_user: dict, db: AsyncSession) -> uuid.UUID:
    user = await get_or_create_user(current_user, db)
    return user.organization_id


@router.get("/internal/{clerk_user_id}/{agent_id}", response_model=AgentResponse)
async def get_agent_internal(
    clerk_user_id: str,
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Verify the caller is the same user they claim to be
    if current_user.get("sub") != clerk_user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    org_id = await get_user_org_id(current_user, db)
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.organization_id == org_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.get("/", response_model=list[AgentResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    org_id = await get_user_org_id(current_user, db)
    result = await db.execute(select(Agent).where(Agent.organization_id == org_id))
    return result.scalars().all()


@router.post("/", response_model=AgentResponse)
async def create_agent(
    payload: AgentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
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
    current_user: dict = Depends(get_current_user),
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
    current_user: dict = Depends(get_current_user),
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
    current_user: dict = Depends(get_current_user),
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
