from fastapi import APIRouter

from app.api.routes import circuits ,utils
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(utils.router)
api_router.include_router(circuits.router, prefix="/api/v1/circuits", tags=["circuits"])
