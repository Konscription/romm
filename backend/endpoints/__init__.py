from fastapi import FastAPI

from backend.endpoints.cheat_types import router as cheat_types_router
from backend.endpoints.user import router as user_router


def init_routers(app: FastAPI):
    """Initialize all routers"""
    app.include_router(user_router)
    app.include_router(cheat_types_router)
