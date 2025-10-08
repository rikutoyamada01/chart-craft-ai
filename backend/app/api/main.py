from fastapi import APIRouter

from app.api.routes import circuits, items, login, private, users, utils

api_router = APIRouter()
api_router.include_router(utils.router, tags=["utils"])
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(circuits.router, prefix="/circuits", tags=["circuits"])
api_router.include_router(private.router, tags=["private"])
