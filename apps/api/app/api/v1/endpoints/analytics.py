from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.call import Call
from app.models.agent import Agent
from app.models.user import User

router = APIRouter()

@router.get("/analytics/summary")
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Get user's org
    clerk_user_id = current_user.get("sub")
    user_result = await db.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        return {"total_calls": 0, "avg_duration_seconds": 0, "total_talk_time_seconds": 0, "per_agent": []}

    org_id = user.organization_id

    # Total calls for this org
    total_calls_result = await db.execute(
        select(func.count(Call.id))
        .join(Agent, Call.agent_id == Agent.id)
        .where(Agent.organization_id == org_id)
    )
    total_calls = total_calls_result.scalar() or 0

    # Average duration
    avg_result = await db.execute(
        select(func.avg(Call.duration_seconds))
        .join(Agent, Call.agent_id == Agent.id)
        .where(Agent.organization_id == org_id)
    )
    avg_duration = avg_result.scalar() or 0

    # Total talk time
    total_result = await db.execute(
        select(func.sum(Call.duration_seconds))
        .join(Agent, Call.agent_id == Agent.id)
        .where(Agent.organization_id == org_id)
    )
    total_time = total_result.scalar() or 0

    # Per-agent stats for this org
    per_agent_result = await db.execute(
        select(
            Agent.name,
            func.count(Call.id).label("call_count"),
            func.avg(Call.duration_seconds).label("avg_duration")
        )
        .outerjoin(Call, Call.agent_id == Agent.id)
        .where(Agent.organization_id == org_id)
        .group_by(Agent.id, Agent.name)
    )
    per_agent = [
        {
            "agent_name": row.name,
            "call_count": row.call_count or 0,
            "avg_duration": round(row.avg_duration or 0, 1)
        }
        for row in per_agent_result.all()
    ]

    return {
        "total_calls": total_calls,
        "avg_duration_seconds": round(avg_duration, 1),
        "total_talk_time_seconds": total_time,
        "per_agent": per_agent
    }