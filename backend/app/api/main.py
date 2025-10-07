from fastapi import APIRouter

from app.api.routes import circuits, utils

api_router = APIRouter()
api_router.include_router(utils.router)
api_router.include_router(circuits.router, prefix="/api/v1/circuits", tags=["circuits"])
