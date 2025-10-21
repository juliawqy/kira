from fastapi import FastAPI
import logging

from backend.src.database.db_setup import Base, engine
from backend.src.database.models.task import Task  
from backend.src.database.models.parent_assignment import ParentAssignment
from backend.src.database.models.team import Team
from backend.src.api.v1.router import router as v1_router
from fastapi.middleware.cors import CORSMiddleware
from backend.src.database.models.project import Project, ProjectAssignment  
from backend.src.database.models.comment import Comment

Base.metadata.create_all(bind=engine)

# Configure logging so service INFO logs show up in the console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logging.getLogger("backend").setLevel(logging.INFO)
logging.getLogger("backend.src").setLevel(logging.INFO)

app = FastAPI(title="KIRA API")
app.include_router(v1_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in dev, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}
