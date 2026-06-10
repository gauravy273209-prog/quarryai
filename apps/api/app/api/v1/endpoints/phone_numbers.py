from fastapi import APIRouter, Depends, HTTPException
from twilio.rest import Client
from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.agent import Agent
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

router = APIRouter()

def get_twilio_client():
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        raise HTTPException(status_code=500, detail="Twilio credentials not configured")
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

@router.get("/available")
async def list_available_numbers(
    country: str = "US",
    current_user: dict = Depends(get_current_user)
):
    """List available phone numbers from Twilio"""
    client = get_twilio_client()
    numbers = client.available_phone_numbers(country).local.list(
        voice_enabled=True,
        limit=10
    )
    return [
        {
            "phone_number": n.phone_number,
            "friendly_name": n.friendly_name,
            "locality": n.locality,
            "region": n.region,
        }
        for n in numbers
    ]

@router.post("/agents/{agent_id}/assign-phone")
async def assign_phone_number(
    agent_id: uuid.UUID,
    phone_number: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Assign a phone number to an agent"""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.phone_number = phone_number
    await db.commit()
    await db.refresh(agent)
    return {"message": "Phone number assigned", "agent_id": str(agent_id), "phone_number": phone_number}