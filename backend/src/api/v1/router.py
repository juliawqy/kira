from fastapi import APIRouter
from .routes.task_route import router as task_router
from .routes.user_route import router as user_router

router = APIRouter(prefix="/kira/app/api/v1")

router.include_router(task_router)
router.include_router(user_router)
