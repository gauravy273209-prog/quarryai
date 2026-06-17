import json
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.call import Call
from app.models.agent import Agent
from app.models.user import User

router = APIRouter()

class CallResponse(BaseModel):
    id: str
    agent_id: Optional[str]
    agent_name: str
    stream_sid: Optional[str]
    status: str
    duration_seconds: Optional[int]
    transcript: list
    started_at: Optional[datetime]
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True

@router.get("/", response_model=list[CallResponse])
async def list_calls(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Get user's org
    clerk_user_id = current_user.get("sub")
    user_result = await db.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        return []

    # Get calls for this org only
    result = await db.execute(
        select(Call)
        .options(selectinload(Call.agent))
        .join(Agent, Call.agent_id == Agent.id)
        .where(Agent.organization_id == user.organization_id)
        .order_by(Call.started_at.desc())
        .limit(50)
    )
    calls = result.scalars().all()

    response = []
    for call in calls:
        transcript = []
        if call.transcript:
            try:
                transcript = json.loads(call.transcript)
            except:
                transcript = []
        response.append(CallResponse(
            id=str(call.id),
            agent_id=str(call.agent_id) if call.agent_id else None,
            agent_name=call.agent.name if call.agent else "Unknown",
            stream_sid=call.stream_sid,
            status=call.status,
            duration_seconds=call.duration_seconds,
            transcript=transcript,
            started_at=call.started_at,
            ended_at=call.ended_at,
        ))
    return response