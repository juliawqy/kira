from fastapi import APIRouter
from backend.src.api.v1.routes.task_route import router as task_router
from backend.src.api.v1.routes.user_route import router as user_router
from backend.src.api.v1.routes.notification_route import router as notification_router




router = APIRouter(prefix="/kira/app/api/v1")

router.include_router(task_router)
router.include_router(user_router)
router.include_router(notification_router)

