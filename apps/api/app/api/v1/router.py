from fastapi import APIRouter
from app.api.v1.endpoints import organizations, agents, phone_numbers, calls, webhooks, analytics, twilio_voice

api_router = APIRouter()

api_router.include_router(organizations.router, prefix='/organizations', tags=['organizations'])
api_router.include_router(agents.router, prefix='/agents', tags=['agents'])
api_router.include_router(phone_numbers.router, prefix='/phone-numbers', tags=['phone-numbers'])
api_router.include_router(calls.router, prefix='/calls', tags=['calls'])
api_router.include_router(webhooks.router, prefix='/webhooks', tags=['webhooks'])
api_router.include_router(analytics.router, tags=['analytics'])
api_router.include_router(twilio_voice.router, prefix='/twilio', tags=['twilio'])
