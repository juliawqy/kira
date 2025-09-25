from fastapi import FastAPI
from database.db_setup import Base, engine
from database.models.task import Task  
from database.models.parent_assignment import ParentAssignment
from api.v1.router import router as v1_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="KIRA API")
app.include_router(v1_router)

@app.get("/health")
def health():
    return {"status": "ok"}
