from fastapi import APIRouter

from app.api.routers import agents, chat, utils

api_router = APIRouter()
api_router.include_router(agents.router)
api_router.include_router(chat.router)
api_router.include_router(utils.router)
