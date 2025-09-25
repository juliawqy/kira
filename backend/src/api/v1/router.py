from fastapi import APIRouter
from .routes.task_route import router as task_router
from .routes.team_route import router as team_router


router = APIRouter(prefix="/kira/app/api/v1")

router.include_router(task_router)
router.include_router(team_router)

