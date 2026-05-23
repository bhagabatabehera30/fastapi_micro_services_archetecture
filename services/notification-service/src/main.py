from fastapi import FastAPI
from src.presentation.routers import jobs

app = FastAPI(
    title="Notification Service API",
    version="1.0.0",
    docs_url="/api/v1/jobs/docs",
    openapi_url="/api/v1/jobs/openapi.json"
)

app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "notification-service"}
