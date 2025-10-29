from fastapi import APIRouter
from app.api.v1.endpoints import welcome_controller
from app.api.v1.endpoints import user_controller
from app.api.v1.endpoints import signatureimage_controller
router = APIRouter()
router.include_router(welcome_controller.router, prefix="/welcome", tags=["Welcome"])
router.include_router(user_controller.router, prefix="/users", tags=["Users"])

router.include_router(signatureimage_controller.router, prefix="/signatures", tags=["Signatures"])
