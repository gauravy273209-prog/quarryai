from fastapi import APIRouter
from app.api.v1.endpoints import organizations, agents

api_router = APIRouter()

api_router.include_router(
    organizations.router,
    prefix="/organizations",
    tags=["organizations"]
)

api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["agents"]
)