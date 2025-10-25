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
app.include_router(v1_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for development
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}
