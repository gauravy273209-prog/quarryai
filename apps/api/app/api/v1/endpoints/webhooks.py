from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from svix.webhooks import Webhook, WebhookVerificationError
from app.db.session import get_db
from app.models.user import User
from app.models.organization import Organization
from app.core.config import settings

router = APIRouter()

@router.post("/clerk")
async def clerk_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    headers = dict(request.headers)

    try:
        wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
        event = wh.verify(payload, headers)
    except WebhookVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event.get("type")
    data = event.get("data", {})

    if event_type == "user.created":
        clerk_user_id = data.get("id")
        email = data.get("email_addresses", [{}])[0].get("email_address", "")
        first_name = data.get("first_name", "") or ""
        last_name = data.get("last_name", "") or ""
        full_name = f"{first_name} {last_name}".strip()

        result = await db.execute(select(Organization).limit(1))
        org = result.scalar_one_or_none()

        if not org:
            org = Organization(
                name="Default Organization",
                slug="default-org",
                plan="free"
            )
            db.add(org)
            await db.flush()

        existing = await db.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        if not existing.scalar_one_or_none():
            user = User(
                organization_id=org.id,
                clerk_user_id=clerk_user_id,
                email=email,
                full_name=full_name,
                role="member"
            )
            db.add(user)
            await db.commit()

    return {"status": "ok"}