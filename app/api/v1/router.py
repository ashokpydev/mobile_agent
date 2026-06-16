from fastapi import APIRouter

from app.api.v1 import agent, analysis, health, privacy

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(privacy.router, prefix="/privacy", tags=["privacy"])
