from fastapi import FastAPI
from api.v1.router import router as v1_router

app = FastAPI(title="Kira API", version="0.1.0")

app.include_router(v1_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok"}
