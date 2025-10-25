from fastapi import FastAPI

from backend.src.database.db_setup import Base, engine
from backend.src.database.models.task import Task  
from backend.src.database.models.parent_assignment import ParentAssignment
from backend.src.database.models.team import Team
from backend.src.database.models.team_assignment import TeamAssignment
from backend.src.database.models.user import User
from backend.src.database.models.department import Department
from backend.src.database.models.project import Project, ProjectAssignment  
from backend.src.database.models.comment import Comment
from backend.src.api.v1.router import router as v1_router
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="KIRA API")

# Add CORS middleware BEFORE including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],  # explicit origins
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(v1_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle preflight OPTIONS requests"""
    return {"message": "OK"}
