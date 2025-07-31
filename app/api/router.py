from fastapi import APIRouter
from app.api.v1.endpoints import welcome_controller
router = APIRouter()
router.include_router(welcome_controller.router, prefix="/welcome", tags=["Welcome"])
