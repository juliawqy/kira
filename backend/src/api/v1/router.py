from fastapi import APIRouter
<<<<<<< HEAD
from .routes.task_route import router as task_router
=======
from backend.src.api.v1.routes.task_route import router as task_router
from backend.src.api.v1.routes.user_route import router as user_router
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f

router = APIRouter(prefix="/kira/app/api/v1")

router.include_router(task_router)
<<<<<<< HEAD
=======
router.include_router(user_router)
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
